"""
@file src/services/ai_filter.py
@description Communicates with Gemini API to intelligently identify noise and config files, utilizing a SOTA Multi-Model Fallback Engine.
@layer Core Logic
@dependencies src.config.Config
"""

import json
import re
import time
from typing import Set, Tuple
from google import genai
from google.genai import types
from rich.console import Console
from src.config import Config

# Initialize Rich console for beautiful terminal UI
console = Console()

class GeminiFilterService:
    """Single Responsibility: Communicating with AI to identify noise and config files with cascading model resilience."""
    
    def __init__(self):
        if not Config.API_KEY:
            console.print("[bold red]✖ ValueError: GEMINI_API_KEY is missing from Config.[/bold red]")
            raise ValueError("GEMINI_API_KEY is missing from Config.")
        
        self.client = genai.Client(api_key=Config.API_KEY)

    def analyze_project_structure(self, directory_tree: str) -> Tuple[Set[str], Set[str]]:
        """Asks AI to identify non-essential paths and config files, cascading through FALLBACK_MODELS on failure."""
        prompt = f"""
        Analyze the following project directory tree to identify its tech stack and structure. 
        
        TASK 1: EXCLUSIONS
        Identify all directories and files that do NOT contain essential, proprietary source code.
        You must exclude: dependencies (e.g., node_modules, venv), build outputs (dist, build, target), 
        lock files (package-lock.json, poetry.lock), binary assets, and IDE configs (.vscode, .idea).
        
        TASK 2: CRITICAL CONFIGURATIONS
        Dynamically identify the high-signal configuration and dependency files based on the tech stack.
        Examples: docker-compose.yml, Dockerfile, requirements.txt, package.json, pyproject.toml, Makefile, etc.
        SECURITY RULE: NEVER include raw '.env' files, .pem keys, or files containing live secrets. 
        You MAY include '.env.example' or '.env.template'.

        Return a strict JSON object containing EXACTLY two keys:
        1. "excluded_paths": An array of exact folder or file names to ignore.
        2. "config_files": An array of exact relative file paths for the critical config files identified.
        
        Directory Tree:
        {directory_tree}
        """
        
        # SOTA: Outer loop iterates over the fallback models dynamically assigned in Config
        for model_name in Config.FALLBACK_MODELS:
            console.print(f"\n[dim cyan]➜ Booting AI Core: Attempting extraction via [bold]{model_name}[/bold]...[/dim cyan]")
            
            # Inner loop handles 429 Rate Limits for the current model
            for attempt in range(1, Config.AI_MAX_RETRIES + 1):
                with console.status(f"[bold cyan]🧠 Neural Analysis via {model_name} (Attempt {attempt}/{Config.AI_MAX_RETRIES})[/bold cyan]", spinner="bouncingBar"):
                    try:
                        response = self.client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                            )
                        )
                        
                        # Defensive parsing: strip Markdown formatting if the LLM hallucinates it
                        raw_text = response.text.strip()
                        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                        if json_match:
                            raw_text = json_match.group(0)
                            
                        data = json.loads(raw_text)
                        exclusions = set(data.get("excluded_paths", []))
                        config_files = set(data.get("config_files", []))
                        
                        console.print(f"[bold green]✓ {model_name} isolated {len(exclusions)} exclusion rules and {len(config_files)} config files.[/bold green]")
                        return exclusions, config_files
                        
                    except Exception as e:
                        error_msg = str(e)
                        
                        # Handle Rate Limit (429) -> Backoff and Retry SAME model
                        if "429" in error_msg or "Quota" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                            if attempt < Config.AI_MAX_RETRIES:
                                delay = Config.AI_BASE_DELAY ** attempt
                                console.print(f"[bold yellow]⚠ {model_name} rate limit hit (429). Backoff: Retrying in {delay}s...[/bold yellow]")
                                time.sleep(delay)
                                continue # Loop back to attempt the same model again
                            else:
                                console.print(f"[bold red]✖ {model_name} max retries exhausted due to rate limits.[/bold red]")
                                break # Break inner loop, cascade to next model
                        
                        # Handle Server Crash (500) or Parsing Failure -> Immediately cascade
                        else:
                            console.print(f"[bold magenta]⚠ {model_name} failed unexpectedly: {e}[/bold magenta]")
                            break # Break inner loop, cascade to next model
            
            # If we broke out of the inner loop, we notify the user we are cascading
            console.print(f"[dim yellow]➜ Cascading to next available AI model...[/dim yellow]")
        
        # If the outer loop finishes, ALL models have failed.
        console.print("[bold red]✖ CRITICAL FAULT: All fallback models exhausted. Degrading to Python-only baseline.[/bold red]")
        return set(), set()