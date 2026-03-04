import os
import asyncio
from pathlib import Path
from typing import Set, Tuple
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.console import Console
from src.services.file_system import AsyncFileSystemService, HARDCODED_EXCLUSIONS

# Initialize Rich console for this service
console = Console()

class AsyncCodeExtractorService:
    """Single Responsibility: Building artifacts concurrently based on AI rules with a live UI."""
    
    @staticmethod
    async def extract_core_codebase_async(root_path: Path, exclusions: Set[str]) -> Tuple[str, int]:
        """Performs a deep crawl and fires off concurrent read tasks, returning the text and file count."""
        file_paths_to_read = []
        
        # 1. Double Protection Crawl
        for root, dirs, files in os.walk(root_path):
            # Apply AI Exclusions AND Hardcoded Exclusions dynamically to protect the extractor
            dirs[:] = [d for d in dirs if not d.startswith('.') 
                       and d not in HARDCODED_EXCLUSIONS 
                       and d not in exclusions]
            
            for file in files:
                if file in exclusions or file in HARDCODED_EXCLUSIONS or file.startswith('.'):
                    continue
                
                file_path = Path(root) / file
                file_paths_to_read.append(file_path)
                
        total_files = len(file_paths_to_read)
        
        if total_files == 0:
            console.print("[bold yellow]⚠ No valid source files found to extract.[/bold yellow]")
            return "", 0

        # 2. Asynchronous Execution with SOTA Live Progress Bar
        results = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=False, # Keeps the completed bar on screen when finished
        ) as progress:
            
            # Register the progress task
            task_id = progress.add_task("[bold cyan]Extracting source code...", total=total_files)
            
            # Helper function to read the file and advance the progress bar when done
            async def read_and_update(fp: Path):
                res = await AsyncFileSystemService.read_file_content_async(fp)
                progress.advance(task_id)
                return res
                
            # Queue and execute all tasks concurrently
            tasks = [read_and_update(fp) for fp in file_paths_to_read]
            results = await asyncio.gather(*tasks)
        
        # 3. Reassemble the final document
        consolidated_code = []
        for file_path, content in results:
            relative_path = file_path.relative_to(root_path)
            consolidated_code.append(f"\n{'='*60}\n--- File: {relative_path} ---\n{'='*60}\n")
            consolidated_code.append(content)
                
        return "".join(consolidated_code), total_files