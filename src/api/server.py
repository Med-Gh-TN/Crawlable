"""
@file src/api/server.py
@description FastAPI backend serving the Tailwind UI and orchestrating live SSE extraction streams via non-blocking threadpools.
@layer Core Logic
@dependencies fastapi, src.services.*
"""

import json
import asyncio
import shutil
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse

from src.config import Config
from src.services.file_system import AsyncFileSystemService
from src.services.ai_filter import GeminiFilterService
from src.services.extractor import AsyncCodeExtractorService

app = FastAPI(title="Crawlable Localhost API")

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serves the Tailwind CSS Web Dashboard."""
    ui_path = Path("src/ui/index.html")
    if not ui_path.exists():
        return HTMLResponse("<h1>Error: UI File Not Found</h1><p>Ensure src/ui/index.html exists.</p>", status_code=404)
    return ui_path.read_text(encoding="utf-8")

@app.get("/api/extract")
async def extract_codebase(target_path: str):
    """
    SOTA Streaming Endpoint: Orchestrates the pipeline and streams real-time updates 
    to the frontend via Server-Sent Events (SSE).
    """
    async def event_generator():
        def emit_log(msg: str):
            """Formats a standard log message for SSE."""
            return f"data: {json.dumps({'type': 'log', 'message': msg})}\n\n"
        
        def emit_error(msg: str):
            """Formats a fatal error message for SSE."""
            return f"data: {json.dumps({'type': 'error', 'message': msg})}\n\n"
        
        try:
            target_dir = Path(target_path).resolve()
            if not target_dir.exists() or not target_dir.is_dir():
                yield emit_error(f"Invalid directory path: {target_dir}")
                return

            loop = asyncio.get_running_loop()

            # Phase 1: Structural Crawl (Offloaded to prevent Event Loop freezing)
            yield emit_log(f"Phase 1: Generating structural map of {target_dir}...")
            raw_tree = await loop.run_in_executor(
                None, AsyncFileSystemService.generate_directory_tree, target_dir
            )
            yield emit_log(f"Mapped ~{len(raw_tree.split(chr(10)))} items (pre-AI).")

            # Phase 2: AI Filtering (Offloaded to threadpool)
            yield emit_log("Phase 2: Requesting Gemini AI analysis for exclusions and configs...")
            ai_service = GeminiFilterService()
            exclusions, config_files = await loop.run_in_executor(
                None, ai_service.analyze_project_structure, raw_tree
            )
            
            yield emit_log(f"AI targeted {len(exclusions)} patterns for exclusion.")
            yield emit_log(f"AI isolated {len(config_files)} high-signal config files.")

            # Phase 3: Concurrent Extraction
            yield emit_log("Phase 3: Extracting filtered source code and configs concurrently...")
            code, code_count = await AsyncCodeExtractorService.extract_core_codebase_async(target_dir, exclusions)
            conf, conf_count = await AsyncCodeExtractorService.extract_specific_files_async(target_dir, config_files)

            # Phase 4: Output Generation
            yield emit_log("Phase 4: Writing versioned output artifacts to disk...")
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            output_folder_name = f"{target_dir.name}_{timestamp}"
            run_output_dir = Config.BASE_OUTPUT_DIR / output_folder_name
            run_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Re-generate filtered tree for the roadmap (Offloaded to prevent freezing)
            filtered_tree = await loop.run_in_executor(
                None, AsyncFileSystemService.generate_directory_tree, target_dir, exclusions
            )
            
            (run_output_dir / "project_roadmap.txt").write_text(filtered_tree, encoding='utf-8')
            (run_output_dir / "source_code.txt").write_text(code, encoding='utf-8')
            
            if conf:
                (run_output_dir / "overall_config.txt").write_text(conf, encoding='utf-8')
            
            if Config.PROMPT_FILE_PATH.exists():
                shutil.copy2(Config.PROMPT_FILE_PATH, run_output_dir / Config.PROMPT_FILE_PATH.name)
                yield emit_log("Injected static prompt artifact successfully.")

            # Final Completion Event
            payload = {
                'type': 'complete',
                'output_dir': str(run_output_dir),
                'exclusions_count': len(exclusions),
                'code_files_count': code_count,
                'config_files_count': conf_count
            }
            yield f"data: {json.dumps(payload)}\n\n"

        except BaseException as e:
            # Catch BaseException to ensure absolutely nothing unhandled drops the connection silently
            yield emit_error(f"Internal Runtime Fault: {str(e)}")

    return StreamingResponse(event_generator(), media_type="text/event-stream")