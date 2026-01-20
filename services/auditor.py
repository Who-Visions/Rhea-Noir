import os
from typing import List, Dict, Optional
import fnmatch

class ProjectAuditor:
    """
    Rhea's eyes for inspecting codebase structures.
    Scans a target directory, maps the tree, and reads key files.
    """
    
    IGNORE_PATTERNS = [
        "node_modules", ".git", ".next", "dist", "build", ".venv", "venv", 
        "__pycache__", ".DS_Store", "*.log", "*.lock", "package-lock.json",
        "yarn.lock", "pnpm-lock.yaml"
    ]
    
    CRITICAL_FILES = [
        "package.json", "tsconfig.json", "next.config.ts", "next.config.js",
        "tailwind.config.ts", "tailwind.config.js", ".env.local.example",
        "README.md"
    ]

    def __init__(self, root_path: str):
        self.root_path = root_path

    def should_ignore(self, name: str) -> bool:
        for pattern in self.IGNORE_PATTERNS:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False

    def scan_structure(self, max_depth: int = 3) -> str:
        """Generates a markdown tree of the project."""
        tree_lines = []
        
        for root, dirs, files in os.walk(self.root_path):
            # Filtering ignored dirs
            dirs[:] = [d for d in dirs if not self.should_ignore(d)]
            
            level = root.replace(self.root_path, '').count(os.sep)
            if level > max_depth:
                continue
                
            indent = '  ' * level
            tree_lines.append(f"{indent}- {os.path.basename(root)}/")
            
            subindent = '  ' * (level + 1)
            for f in files:
                if not self.should_ignore(f):
                    tree_lines.append(f"{subindent}- {f}")
                    
        return "\n".join(tree_lines)

    def read_critical_files(self) -> Dict[str, str]:
        """Reads content of configuration and manifest files."""
        data = {}
        for root, dirs, files in os.walk(self.root_path):
            # Prune ignored directories in-place
            dirs[:] = [d for d in dirs if not self.should_ignore(d)]
            
            for f in files:
                if f in self.CRITICAL_FILES:
                    path = os.path.join(root, f)
                    try:
                        with open(path, "r", encoding="utf-8") as file:
                            # relative path key
                            rel_path = os.path.relpath(path, self.root_path)
                            data[rel_path] = file.read()
                    except Exception as e:
                        data[f] = f"<Error reading file: {e}>"
        return data

    def generate_audit_context(self) -> str:
        """Compiles everything into a prompt context for Gemini."""
        tree = self.scan_structure()
        files = self.read_critical_files()
        
        context = f"""# Project Audit Context
        
## File Structure
```
{tree}
```

## Critical Configuration Files
"""
        for path, content in files.items():
            context += f"\n### {path}\n```\n{content}\n```\n"
            
        return context
