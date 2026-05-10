"""
@file main.py
@description SOTA Zero-Friction Bootstrapper. Supports Headless (Invisible) execution for native 2-click Windows VBS integration.
@layer Core Logic / Side Effect
@dependencies None (Standard Library strictly for Level 1 Bootstrapping)
"""

import os
import sys
import subprocess
import platform
import argparse
import urllib.request
import zipfile
import io
import shutil
import threading
import time
import webbrowser
import socket
from pathlib import Path

# ==========================================
# LEVEL 1: SOTA BOOTSTRAPPER ENGINE
# ==========================================

GITHUB_VERSION_URL = "https://raw.githubusercontent.com/Med-Gh-TN/Crawlable/main/VERSION"
GITHUB_ZIP_URL = "https://github.com/Med-Gh-TN/Crawlable/archive/refs/heads/main.zip"

# Detect if the VBS script launched us in hidden mode
HEADLESS_MODE = "--headless" in sys.argv

def get_hidden_kwargs() -> dict:
    """Returns kwargs to prevent black terminal boxes from flashing on Windows during subprocess calls."""
    kwargs = {}
    if platform.system() == "Windows" and HEADLESS_MODE:
        kwargs["creationflags"] = 0x08000000 # CREATE_NO_WINDOW constant
    return kwargs

def is_in_venv() -> bool:
    return sys.prefix != sys.base_prefix

def get_venv_python() -> Path:
    if platform.system() == "Windows":
        return Path(".venv") / "Scripts" / "python.exe"
    return Path(".venv") / "bin" / "python"

def perform_ota_zip_update():
    if not HEADLESS_MODE: print("[Crawlable] 📥 Downloading latest release payload from GitHub...")
    req = urllib.request.Request(GITHUB_ZIP_URL, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req, timeout=10.0) as response:
        with zipfile.ZipFile(io.BytesIO(response.read())) as z:
            temp_dir = Path(".ota_update_tmp")
            z.extractall(temp_dir)
            extracted_root = temp_dir / "Crawlable-main"
            
            if not HEADLESS_MODE: print("[Crawlable] 🔄 Patching local files...")
            shutil.copytree(extracted_root, ".", dirs_exist_ok=True)
            shutil.rmtree(temp_dir)

def check_for_updates(python_exe: Path) -> bool:
    if not HEADLESS_MODE: print("[Crawlable] ⚙️  Validating version with upstream repository...")
    version_file = Path("VERSION")
    if not version_file.exists():
        return False

    try:
        local_version = version_file.read_text(encoding="utf-8").strip()
        req = urllib.request.Request(GITHUB_VERSION_URL, headers={'Cache-Control': 'no-cache'})
        
        with urllib.request.urlopen(req, timeout=2.0) as response:
            remote_version = response.read().decode("utf-8").strip()

        if remote_version != local_version and remote_version > local_version:
            if not HEADLESS_MODE:
                print("\n" + "="*60)
                print(f" 🚀 UPDATE AVAILABLE!  (Current: v{local_version} → Latest: v{remote_version})")
                print("="*60)
            
            # If Headless (Invisible UI), auto-update silently if possible, else skip.
            if HEADLESS_MODE:
                if Path(".git").exists():
                    subprocess.run(["git", "pull"], check=True, **get_hidden_kwargs())
                    if Path("requirements.txt").exists():
                        subprocess.run([str(python_exe), "-m", "pip", "install", "-q", "-r", "requirements.txt"], **get_hidden_kwargs())
                    return True
                return False
            
            # Interactive Terminal UI
            choice = input(" Would you like to auto-update now? [Y/n]: ").strip().lower()
            if choice in ['', 'y', 'yes']:
                try:
                    if Path(".git").exists():
                        print("\n[Crawlable] 📦 Executing native Git sync...")
                        subprocess.run(["git", "pull"], check=True, **get_hidden_kwargs())
                    else:
                        print("\n[Crawlable] 📦 No Git detected. Executing Universal OTA Patch...")
                        perform_ota_zip_update()

                    if Path("requirements.txt").exists():
                        print("[Crawlable] ⚙️  Rebuilding dependencies...")
                        subprocess.run([str(python_exe), "-m", "pip", "install", "-q", "-r", "requirements.txt"], **get_hidden_kwargs())
                    
                    print("[Crawlable] ✅ Update successful! Restarting...\n")
                    return True
                except Exception as e:
                    print(f"\n[Crawlable] ⚠ Update failed: {e}")
                    print("[Crawlable] Proceeding with current version...\n")
            else:
                print("\n[Crawlable] Skipping update...\n")
        else:
            if not HEADLESS_MODE: print("[Crawlable] ✅ Version is up to date.")
            
    except Exception:
        if not HEADLESS_MODE: print("[Crawlable] ⚠ Could not reach GitHub. Proceeding offline.")
        
    return False

def ensure_environment_and_handoff():
    if not HEADLESS_MODE: print(f"\n[Crawlable] ⚙️  Host OS Detected: {platform.system()}")
    python_exe = get_venv_python()
    
    if not python_exe.exists():
        if not HEADLESS_MODE: print("[Crawlable] ⚙️  Initializing isolated virtual environment (.venv)...")
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True, **get_hidden_kwargs())
        if not HEADLESS_MODE: print("[Crawlable] ✅ Virtual environment constructed.")

    if Path("requirements.txt").exists():
        if not HEADLESS_MODE: print("[Crawlable] ⚙️  Verifying dependencies...")
        subprocess.run([str(python_exe), "-m", "pip", "install", "-q", "-r", "requirements.txt"], **get_hidden_kwargs())

    needs_restart = check_for_updates(python_exe)
    
    if needs_restart:
        cmd = [sys.executable] + sys.argv
        if platform.system() != "Windows":
            os.execv(sys.executable, cmd)
        else:
            sys.exit(subprocess.call(cmd, **get_hidden_kwargs()))

    if not HEADLESS_MODE: print("[Crawlable] 🚀 Bootstrapper complete. Booting up Web Dashboard...\n")
    cmd = [str(python_exe), sys.argv[0]] + sys.argv[1:]
    
    if platform.system() != "Windows":
        os.execv(str(python_exe), cmd)
    else:
        sys.exit(subprocess.call(cmd, **get_hidden_kwargs()))

# ==========================================
# LEVEL 2: APPLICATION ENTRY POINT (WEB DASHBOARD)
# ==========================================

def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def run_application():
    import uvicorn
    from rich.console import Console
    
    dynamic_port = get_free_port()
    dashboard_url = f"http://127.0.0.1:{dynamic_port}"
    
    # We only print to the terminal if the user ran this manually without --headless
    if not HEADLESS_MODE:
        console = Console()
        console.print("\n[bold blue]========================================[/bold blue]")
        console.print("[bold cyan]      🦅 Crawlable - Web Dashboard      [/bold cyan]")
        console.print("[bold blue]========================================[/bold blue]\n")
        console.print(f"[bold green]✓ Starting SOTA Localhost Server on port {dynamic_port}...[/bold green]")
        console.print(f"[dim]If your browser does not open automatically, navigate to: {dashboard_url}[/dim]\n")

    def open_browser():
        time.sleep(1.5)
        webbrowser.open(dashboard_url)

    threading.Thread(target=open_browser, daemon=True).start()

    # Parse args to cleanly absorb the --headless flag without throwing errors
    parser = argparse.ArgumentParser(description="Crawlable: AI-Powered Codebase Extractor")
    parser.add_argument("path", nargs="?", default=None, help="Path to the target project directory")
    parser.add_argument("--headless", action="store_true", help="Run strictly invisibly in the background")
    args = parser.parse_args()

    # Launch ASGI server
    try:
        uvicorn.run("src.api.server:app", host="127.0.0.1", port=dynamic_port, log_level="critical", reload=False)
    except KeyboardInterrupt:
        if not HEADLESS_MODE: print("\nShutting down Crawlable Web Dashboard...")

# ==========================================
# LIFECYCLE ROUTER
# ==========================================

if __name__ == "__main__":
    if not is_in_venv():
        ensure_environment_and_handoff()
    else:
        run_application()