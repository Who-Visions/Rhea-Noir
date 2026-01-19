"""
Gemini File Search (RAG) Skill for Rhea-Noir
Semantic search over documents using Gemini's File Search API
"""
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List


class FileSearchSkill:
    """Skill for Gemini File Search (RAG) operations."""
    
    name = "filesearch"
    version = "1.0.0"
    description = "Gemini File Search - semantic search over your documents"
    
    def __init__(self):
        self._client = None
    
    def _get_client(self):
        """Get Gemini client."""
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client()
            except ImportError:
                raise ImportError("google-genai not installed. Run: pip install google-genai")
        return self._client
    
    def _success(self, data: Any) -> Dict:
        """Return success response."""
        return {"success": True, "data": data}
    
    def _error(self, message: str) -> Dict:
        """Return error response."""
        return {"success": False, "error": message}
    
    def _wait_for_operation(self, operation, timeout: int = 300):
        """Wait for an async operation to complete."""
        client = self._get_client()
        start = time.time()
        while not operation.done:
            if time.time() - start > timeout:
                raise TimeoutError(f"Operation timed out after {timeout}s")
            time.sleep(5)
            operation = client.operations.get(operation)
        return operation
    
    def create_store(self, display_name: str) -> Dict:
        """
        Create a new file search store.
        
        Args:
            display_name: Human-readable name for the store
            
        Returns:
            Dict with store name and details
        """
        try:
            client = self._get_client()
            store = client.file_search_stores.create(
                config={'display_name': display_name}
            )
            return self._success({
                "name": store.name,
                "display_name": display_name,
                "message": "File search store created successfully"
            })
        except Exception as e:
            return self._error(str(e))
    
    def upload_file(
        self,
        store_name: str,
        file_path: str,
        display_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        max_tokens_per_chunk: int = 200,
        max_overlap_tokens: int = 20
    ) -> Dict:
        """
        Upload and index a file to the store.
        
        Args:
            store_name: Name of the file search store
            file_path: Path to the file to upload
            display_name: Optional display name for the file
            metadata: Optional key-value metadata for filtering
            max_tokens_per_chunk: Maximum tokens per chunk
            max_overlap_tokens: Token overlap between chunks
            
        Returns:
            Dict with upload status
        """
        try:
            client = self._get_client()
            path = Path(file_path)
            
            if not path.exists():
                return self._error(f"File not found: {file_path}")
            
            config = {
                'display_name': display_name or path.name,
                'chunking_config': {
                    'white_space_config': {
                        'max_tokens_per_chunk': max_tokens_per_chunk,
                        'max_overlap_tokens': max_overlap_tokens
                    }
                }
            }
            
            # Add custom metadata if provided
            if metadata:
                custom_metadata = []
                for key, value in metadata.items():
                    if isinstance(value, (int, float)):
                        custom_metadata.append({"key": key, "numeric_value": value})
                    else:
                        custom_metadata.append({"key": key, "string_value": str(value)})
                config['custom_metadata'] = custom_metadata
            
            operation = client.file_search_stores.upload_to_file_search_store(
                file=str(path),
                file_search_store_name=store_name,
                config=config
            )
            
            # Wait for indexing to complete
            self._wait_for_operation(operation)
            
            return self._success({
                "file": path.name,
                "store": store_name,
                "message": "File uploaded and indexed successfully"
            })
        except Exception as e:
            return self._error(str(e))
    
    def import_file(
        self,
        store_name: str,
        file_path: str,
        display_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        Upload file via Files API then import to store.
        
        Args:
            store_name: Name of the file search store
            file_path: Path to the file
            display_name: Optional display name
            metadata: Optional metadata for filtering
            
        Returns:
            Dict with import status
        """
        try:
            client = self._get_client()
            path = Path(file_path)
            
            if not path.exists():
                return self._error(f"File not found: {file_path}")
            
            # Upload to Files API first
            uploaded_file = client.files.upload(
                file=str(path),
                config={'name': display_name or path.name}
            )
            
            # Build import config
            import_kwargs = {
                'file_search_store_name': store_name,
                'file_name': uploaded_file.name
            }
            
            if metadata:
                custom_metadata = []
                for key, value in metadata.items():
                    if isinstance(value, (int, float)):
                        custom_metadata.append({"key": key, "numeric_value": value})
                    else:
                        custom_metadata.append({"key": key, "string_value": str(value)})
                import_kwargs['custom_metadata'] = custom_metadata
            
            operation = client.file_search_stores.import_file(**import_kwargs)
            self._wait_for_operation(operation)
            
            return self._success({
                "file": path.name,
                "store": store_name,
                "message": "File imported and indexed successfully"
            })
        except Exception as e:
            return self._error(str(e))
    
    def query(
        self,
        store_name: str,
        question: str,
        model: str = "gemini-3-flash-preview",
        metadata_filter: Optional[str] = None
    ) -> Dict:
        """
        Query the file search store with semantic search.
        
        Args:
            store_name: Name of the file search store
            question: Question or query text
            model: Gemini model to use
            metadata_filter: Optional filter (e.g., 'author="John"')
            
        Returns:
            Dict with answer and citations
        """
        try:
            from google.genai import types
            client = self._get_client()
            
            file_search_config = {
                'file_search_store_names': [store_name]
            }
            if metadata_filter:
                file_search_config['metadata_filter'] = metadata_filter
            
            response = client.models.generate_content(
                model=model,
                contents=question,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(**file_search_config)
                        )
                    ]
                )
            )
            
            # Extract citations if available
            citations = None
            if response.candidates and response.candidates[0].grounding_metadata:
                citations = response.candidates[0].grounding_metadata
            
            return self._success({
                "answer": response.text,
                "citations": citations,
                "model": model,
                "store": store_name
            })
        except Exception as e:
            return self._error(str(e))
    
    def query_structured(
        self,
        store_name: str,
        question: str,
        response_schema: Any,
        model: str = "gemini-3-flash-preview",
        metadata_filter: Optional[str] = None
    ) -> Dict:
        """
        Query with structured output (Pydantic model).
        
        Args:
            store_name: Name of the file search store
            question: Question or query text
            response_schema: Pydantic model class for response
            model: Gemini model to use
            metadata_filter: Optional filter
            
        Returns:
            Dict with parsed structured response
        """
        try:
            from google.genai import types
            client = self._get_client()
            
            file_search_config = {
                'file_search_store_names': [store_name]
            }
            if metadata_filter:
                file_search_config['metadata_filter'] = metadata_filter
            
            response = client.models.generate_content(
                model=model,
                contents=question,
                config=types.GenerateContentConfig(
                    tools=[
                        types.Tool(
                            file_search=types.FileSearch(**file_search_config)
                        )
                    ],
                    response_mime_type="application/json",
                    response_json_schema=response_schema.model_json_schema()
                )
            )
            
            # Parse response
            result = response_schema.model_validate_json(response.text)
            
            return self._success({
                "result": result.model_dump(),
                "raw_text": response.text,
                "model": model
            })
        except Exception as e:
            return self._error(str(e))
    
    def list_stores(self) -> Dict:
        """
        List all file search stores.
        
        Returns:
            Dict with list of stores
        """
        try:
            client = self._get_client()
            stores = []
            for store in client.file_search_stores.list():
                stores.append({
                    "name": store.name,
                    "display_name": getattr(store, 'display_name', None)
                })
            return self._success({
                "stores": stores,
                "count": len(stores)
            })
        except Exception as e:
            return self._error(str(e))
    
    def list_documents(self, store_name: str) -> Dict:
        """
        List documents in a file search store.
        
        Args:
            store_name: Name of the store
            
        Returns:
            Dict with list of documents
        """
        try:
            client = self._get_client()
            documents = []
            for doc in client.file_search_stores.documents.list(parent=store_name):
                documents.append({
                    "name": doc.name,
                    "display_name": getattr(doc, 'display_name', None)
                })
            return self._success({
                "documents": documents,
                "count": len(documents),
                "store": store_name
            })
        except Exception as e:
            return self._error(str(e))
    
    def delete_store(self, store_name: str, force: bool = False) -> Dict:
        """
        Delete a file search store.
        
        Args:
            store_name: Name of the store to delete
            force: Force delete even if store has documents
            
        Returns:
            Dict with deletion status
        """
        try:
            client = self._get_client()
            client.file_search_stores.delete(
                name=store_name,
                config={'force': force}
            )
            return self._success({
                "message": f"Store '{store_name}' deleted successfully"
            })
        except Exception as e:
            return self._error(str(e))
    
    def delete_document(self, document_name: str) -> Dict:
        """
        Delete a document from a store.
        
        Args:
            document_name: Full document name (includes store path)
            
        Returns:
            Dict with deletion status
        """
        try:
            client = self._get_client()
            client.file_search_stores.documents.delete(name=document_name)
            return self._success({
                "message": f"Document '{document_name}' deleted successfully"
            })
        except Exception as e:
            return self._error(str(e))
    
    def get_store(self, store_name: str) -> Dict:
        """
        Get details of a specific store.
        
        Args:
            store_name: Name of the store
            
        Returns:
            Dict with store details
        """
        try:
            client = self._get_client()
            store = client.file_search_stores.get(name=store_name)
            return self._success({
                "name": store.name,
                "display_name": getattr(store, 'display_name', None)
            })
        except Exception as e:
            return self._error(str(e))


# Singleton instance
skill = FileSearchSkill()
