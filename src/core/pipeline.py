"""
@file src/core/pipeline.py
@description Wires the Lego blocks together to execute the full workflow, generating source code and config artifacts.
@layer State Persistence / Side Effect
@dependencies src.services.*
"""

import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.config import Config, logger
from src.services.file_system import AsyncFileSystemService
from src.services.ai_filter import GeminiFilterService
from src.services.extractor import AsyncCodeExtractorService

# Initialize Rich console for dashboard UI
console = Console()

class CrowablePipeline:
    """Wires the Lego blocks together to execute the full workflow with a SOTA UI."""
    
    def __init__(self, target_directory: str):
        self.target_dir = Path(target_directory)
        self.ai_service = GeminiFilterService()
        
    def run(self):
        console.rule("[bold blue]CROWABLE SOTA PIPELINE INITIALIZING[/bold blue]")
        
        if not self.target_dir.exists() or not self.target_dir.is_dir():
            console.print(f"[bold red]✖ Target directory {self.target_dir} is invalid.[/bold red]")
            return

        # Step 1: Structural Crawl (Unfiltered)
        console.print(f"\n[bold cyan]Phase 1:[/bold cyan] Generating structural map of [yellow]{self.target_dir}[/yellow]...")
        raw_tree = AsyncFileSystemService.generate_directory_tree(self.target_dir)
        total_mapped_items = len(raw_tree.split('\n'))
        console.print(f"[dim]Mapped ~{total_mapped_items} items (pre-AI).[/dim]")

        # Step 2: Intelligent Filtering & Config Identification
        console.print("\n[bold cyan]Phase 2:[/bold cyan] Requesting AI analysis for exclusions and configs...")
        exclusions, config_files = self.ai_service.analyze_project_structure(raw_tree)
        
        if exclusions:
            sample_exclusions = ', '.join(list(exclusions)[:5])
            console.print(f"[dim]AI targeted {len(exclusions)} patterns for exclusion (e.g., {sample_exclusions}...)[/dim]")
        else:
            console.print("[dim]No paths identified for exclusion by AI.[/dim]")
            
        if config_files:
            console.print(f"[dim]AI isolated {len(config_files)} high-signal config/dependency files for LLM context.[/dim]")

        # Step 3: Targeted Extraction (Async)
        console.print("\n[bold cyan]Phase 3:[/bold cyan] Extracting filtered source code concurrently...")
        
        # We run both extraction jobs sequentially in the event loop to preserve terminal output order
        async def run_extractions():
            code, code_count = await AsyncCodeExtractorService.extract_core_codebase_async(self.target_dir, exclusions)
            conf, conf_count = await AsyncCodeExtractorService.extract_specific_files_async(self.target_dir, config_files)
            return code, code_count, conf, conf_count
            
        source_code, extracted_count, config_code, config_count = asyncio.run(run_extractions())

        # Step 4: Versioned Output Generation
        console.print("\n[bold cyan]Phase 4:[/bold cyan] Writing versioned output artifacts...")
        
        # Format: ProjectName_YYYY-MM-DD_HH-MM
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        project_name = self.target_dir.name
        output_folder_name = f"{project_name}_{timestamp}"
        
        # Create dynamic run directory inside the base output dir
        run_output_dir = Config.BASE_OUTPUT_DIR / output_folder_name
        run_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate the FILTERED roadmap for the final output
        console.print("[dim]Generating clean, filtered project roadmap...[/dim]")
        filtered_tree = AsyncFileSystemService.generate_directory_tree(self.target_dir, exclusions)
        
        # Write artifacts to disk
        roadmap_path = run_output_dir / "project_roadmap.txt"
        roadmap_path.write_text(filtered_tree, encoding='utf-8')
        
        source_path = run_output_dir / "source_code.txt"
        source_path.write_text(source_code, encoding='utf-8')
        
        # Write the new overall config artifact (Roadmap excluded per request)
        if config_code:
            config_path = run_output_dir / "overall_config.txt"
            config_path.write_text(config_code, encoding='utf-8')
            console.print("[dim]Generated overall_config.txt successfully.[/dim]")
        
        # Gracefully copy the static prompt file
        prompt_status = "[red]Skipped (File Missing)[/red]"
        if Config.PROMPT_FILE_PATH.exists():
            try:
                destination = run_output_dir / Config.PROMPT_FILE_PATH.name
                shutil.copy2(Config.PROMPT_FILE_PATH, destination)
                prompt_status = "[green]Injected successfully[/green]"
            except Exception as e:
                prompt_status = f"[red]Failed ({e})[/red]"
                console.print(f"[bold red]✖ Failed to copy prompt file: {e}[/bold red]")
        
        # ==========================================
        # FINAL SOTA DASHBOARD SUMMARY
        # ==========================================
        console.print("\n")
        table = Table(title="[bold green]Pipeline Execution Summary[/bold green]", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")

        table.add_row("Total Items Mapped", str(total_mapped_items))
        table.add_row("AI Exclusions Applied", str(len(exclusions)))
        table.add_row("Core Files Extracted", str(extracted_count))
        table.add_row("Config Files Extracted", str(config_count))
        table.add_row("Prompt File Status", prompt_status)
        table.add_row("Output Directory", f"[yellow]{run_output_dir}[/yellow]")

        console.print(Panel(table, border_style="green", expand=False))
        console.rule("[bold blue]PIPELINE COMPLETE[/bold blue]")