import json
import time
from typing import Set
from google import genai
from google.genai import types
from rich.console import Console
from src.config import Config

# Initialize Rich console for beautiful terminal UI
console = Console()

class GeminiFilterService:
    """Single Responsibility: Communicating with AI to identify noise with built-in resilience."""
    
    def __init__(self):
        if not Config.API_KEY:
            console.print("[bold red]✖ ValueError: GEMINI_API_KEY is missing from Config.[/bold red]")
            raise ValueError("GEMINI_API_KEY is missing from Config.")
        
        self.client = genai.Client(api_key=Config.API_KEY)

    def identify_exclusions(self, directory_tree: str) -> Set[str]:
        """Asks Gemini to identify non-essential paths with retry logic and live spinners."""
        prompt = f"""
        Analyze the following project directory tree. 
        Identify all directories and files that do NOT contain essential, proprietary source code.
        You must exclude: dependencies (e.g., node_modules, venv), build outputs (dist, build, target), 
        lock files (package-lock.json, poetry.lock), binary assets, and IDE configs (.vscode, .idea).
        
        Return a strict JSON object containing a single key "excluded_paths" which maps to an array of exact folder or file names to ignore.
        
        Directory Tree:
        {directory_tree}
        """
        
        max_retries = 3
        base_delay = 2 # seconds
        
        for attempt in range(1, max_retries + 1):
            # The console.status block creates the live spinning animation
            with console.status(f"[bold cyan]🧠 AI Analysis in progress... (Attempt {attempt}/{max_retries})[/bold cyan]", spinner="bouncingBar"):
                try:
                    response = self.client.models.generate_content(
                        model=Config.MODEL_NAME,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                        )
                    )
                    data = json.loads(response.text)
                    exclusions = set(data.get("excluded_paths", []))
                    
                    console.print(f"[bold green]✓ Gemini successfully identified {len(exclusions)} paths to exclude.[/bold green]")
                    return exclusions
                    
                except Exception as e:
                    error_msg = str(e)
                    # Check if the error is a rate limit or quota exhaustion (429)
                    if "429" in error_msg or "Quota" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                        if attempt < max_retries:
                            delay = base_delay ** attempt
                            console.print(f"[bold yellow]⚠ API Rate limit hit (429). Exponential backoff: Retrying in {delay} seconds...[/bold yellow]")
                            time.sleep(delay)
                        else:
                            console.print("[bold red]✖ Critical: Max retries exceeded for AI Filtering. Proceeding with an empty exclusion list to prevent pipeline crash.[/bold red]")
                            return set()
                    else:
                        # For any other unknown errors (JSON parsing, network down, etc.)
                        console.print(f"[bold red]✖ AI Filtering failed unexpectedly: {e}[/bold red]")
                        console.print("[dim yellow]Falling back to empty exclusion list.[/dim yellow]")
                        return set()
        
        return set()