import os
import asyncio
from pathlib import Path
from typing import Tuple, Set
from rich.console import Console
from src.config import Config

# Initialize Rich console for this service
console = Console()

# SOTA: Hardcoded Universal Pre-filter
# These directories are mathematically guaranteed to be noise and will NEVER be sent to the AI.
HARDCODED_EXCLUSIONS = {
    'node_modules', '.git', 'dist', 'build', '.angular', 
    'venv', '.venv', 'env', '__pycache__', 'target', 
    'coverage', '.next', '.nuxt', 'out', '.idea', '.vscode'
}

# SOTA: Smart Truncation Limit
MAX_ITEMS_PER_DIR = 30

class AsyncFileSystemService:
    """Single Responsibility: Traversing and reading the file system concurrently with Smart Truncation."""
    
    @staticmethod
    def generate_directory_tree(root_path: Path, exclusions: Set[str] = None) -> str:
        """Generates a string representation of the directory tree with Smart Truncation."""
        if exclusions is None:
            exclusions = set()
            
        tree = []
        for root, dirs, files in os.walk(root_path):
            current_path = Path(root)
            is_root = (current_path == root_path)
            
            # 1. PRE-FILTERING: Strip out universal noise, AI exclusions, and hidden folders dynamically
            dirs[:] = [d for d in dirs if not d.startswith('.') 
                       and d not in HARDCODED_EXCLUSIONS 
                       and d not in exclusions]
            
            # Filter files similarly
            valid_files = [f for f in files if not f.startswith('.') and f not in exclusions]
            
            # Calculate indentation level safely
            level = len(current_path.relative_to(root_path).parts)
            indent = ' ' * 4 * level
            
            # Append current directory name
            if is_root:
                tree.append(f"{current_path.name}/")
            else:
                tree.append(f"{indent}{current_path.name}/")
                
            subindent = ' ' * 4 * (level + 1)
            
            # 2. SMART TRUNCATION ALGORITHM
            total_items = len(dirs) + len(valid_files)
            
            # If the folder is huge and it's NOT the root project folder, collapse it!
            if not is_root and total_items > MAX_ITEMS_PER_DIR:
                tree.append(f"{subindent}[... {total_items} items safely collapsed to preserve token limits ...]")
                # CRITICAL: Clear the dirs list in-place so os.walk DOES NOT traverse deeper into this massive folder
                dirs[:] = [] 
                continue
            
            # 3. Standard file listing if not truncated
            for f in valid_files:
                tree.append(f"{subindent}{f}")
                
        return "\n".join(tree)

    @staticmethod
    async def read_file_content_async(file_path: Path) -> Tuple[Path, str]:
        """Safely reads text content from a file asynchronously without blocking."""
        def _blocking_read():
            try:
                if file_path.stat().st_size > Config.MAX_FILE_SIZE_BYTES:
                    return f"// [SKIPPED] File exceeds size limit ({Config.MAX_FILE_SIZE_BYTES} bytes)"
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                return "// [SKIPPED] Binary or unsupported text encoding."
            except Exception as e:
                console.print(f"[bold red]Error reading {file_path}: {e}[/bold red]")
                return f"// [ERROR] Could not read file: {e}"

        # Offloads the blocking file I/O to a background thread pool automatically
        content = await asyncio.to_thread(_blocking_read)
        return file_path, content