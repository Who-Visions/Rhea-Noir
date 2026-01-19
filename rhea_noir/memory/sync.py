"""
Memory Sync - Background synchronization between SQLite and BigQuery
Implements lazy loading: starts fast, syncs after 60 seconds
"""

import threading
import time
from typing import Optional, Callable

from .short_term import ShortTermMemory
from .long_term import BigQueryMemory


class MemorySync:
    """Lazy background sync between local SQLite and cloud BigQuery"""
    
    def __init__(
        self,
        stm: ShortTermMemory,
        ltm: Optional[BigQueryMemory] = None,
        initial_delay: int = 60,
        sync_interval: int = 300,  # 5 minutes
        on_sync_complete: Optional[Callable] = None
    ):
        """
        Initialize memory sync.
        
        Args:
            stm: Short-term memory (SQLite)
            ltm: Long-term memory (BigQuery) - created lazily if None
            initial_delay: Seconds to wait before first cloud sync (default: 60)
            sync_interval: Seconds between syncs (default: 300 = 5 minutes)
            on_sync_complete: Optional callback when sync completes
        """
        self.stm = stm
        self._ltm = ltm
        self.initial_delay = initial_delay
        self.sync_interval = sync_interval
        self.on_sync_complete = on_sync_complete
        
        self._sync_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_sync: Optional[float] = None
        self._sync_count = 0
        self._is_running = False
    
    @property
    def ltm(self) -> BigQueryMemory:
        """Lazy-load long-term memory"""
        if self._ltm is None:
            self._ltm = BigQueryMemory()
        return self._ltm
    
    def start(self):
        """Start background sync thread"""
        if self._is_running:
            return
        
        self._stop_event.clear()
        self._sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._sync_thread.start()
        self._is_running = True
    
    def stop(self):
        """Stop background sync"""
        self._stop_event.set()
        if self._sync_thread:
            self._sync_thread.join(timeout=5)
        self._is_running = False
    
    def _sync_loop(self):
        """Background sync loop with lazy start"""
        # Wait for initial delay (60 seconds default)
        # This allows CLI to start instantly
        for _ in range(self.initial_delay):
            if self._stop_event.is_set():
                return
            time.sleep(1)
        
        # Do first sync
        self._do_sync()
        
        # Continue syncing at interval
        while not self._stop_event.is_set():
            # Wait for sync interval
            for _ in range(self.sync_interval):
                if self._stop_event.is_set():
                    return
                time.sleep(1)
            
            self._do_sync()
    
    def _do_sync(self):
        """Perform sync: push local → cloud"""
        try:
            # Get unsynced memories
            unsynced = self.stm.get_unsynced()
            
            if unsynced:
                # Push to cloud
                count = self.ltm.store(unsynced)
                
                if count > 0:
                    # Mark as synced locally
                    synced_ids = [m["id"] for m in unsynced[:count]]
                    self.stm.mark_synced(synced_ids)
                    self._sync_count += count
            
            self._last_sync = time.time()
            
            # Callback if provided
            if self.on_sync_complete:
                self.on_sync_complete(self._sync_count)
                
        except Exception as e:
            # Silently handle sync errors (don't crash CLI)
            pass
    
    def force_sync(self) -> int:
        """Force immediate sync, returns count synced"""
        unsynced = self.stm.get_unsynced()
        
        if not unsynced:
            return 0
        
        count = self.ltm.store(unsynced)
        
        if count > 0:
            synced_ids = [m["id"] for m in unsynced[:count]]
            self.stm.mark_synced(synced_ids)
            self._sync_count += count
        
        self._last_sync = time.time()
        return count
    
    def pull_from_cloud(self, limit: int = 100) -> int:
        """Pull recent memories from cloud to local (for new device sync)"""
        if not self.ltm.initialized:
            return 0
        
        try:
            cloud_memories = self.ltm.get_recent(limit=limit)
            imported = 0
            
            for mem in cloud_memories:
                # Check if already exists locally
                existing = self.stm.recall(mem["content"][:50], limit=1)
                if not existing:
                    # Import to local
                    self.stm.store(
                        role=mem["role"],
                        content=mem["content"],
                        keywords=mem.get("keywords", []),
                        session_id=mem.get("session_id")
                    )
                    imported += 1
            
            return imported
        except Exception:
            return 0
    
    def get_status(self) -> dict:
        """Get sync status"""
        return {
            "is_running": self._is_running,
            "last_sync": self._last_sync,
            "total_synced": self._sync_count,
            "pending": len(self.stm.get_unsynced()) if self.stm else 0,
        }
