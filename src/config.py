import os
import logging
from pathlib import Path

# ==========================================
# CENTRALIZED LOGGING & CONFIGURATION
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger("Crawlable")

class Config:
    """Centralized configuration for the pipeline."""
    API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key
    MODEL_NAME = "gemini-2.5-flash"
    MAX_FILE_SIZE_BYTES = 1024 * 500  # Skip files larger than 500KB
    
    # Base directory where all versioned runs will be saved
    BASE_OUTPUT_DIR = Path("./Crawlable_output")
    
    # Path to the static prompt file you want injected into every run
    # We will create an 'assets' folder inside 'src' to hold this
    PROMPT_FILE_PATH = Path("./src/assets/prompt.txt")