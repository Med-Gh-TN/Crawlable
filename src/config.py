"""
@file src/config.py
@description Centralized configuration and hyperparameter control panel for the Crawlable SOTA pipeline.
@layer State Persistence
"""

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
    
    # 🔒 SECURITY: Prefers environment variables, falls back to hardcoded for local dev.
    API_KEY = os.getenv("GEMINI_API_KEY", "PLACEHOLDER_API_KEY   - REPLACE WITH ENV VAR IN PRODUCTION")
    
    # ==========================================
    # SOTA MULTI-MODEL FALLBACK ENGINE
    # ==========================================
    # The pipeline will attempt these models in exact order.
    FALLBACK_MODELS = [
        "gemma-4-31b-it",
        "gemma-4-26b-a4b-it",
        "gemma-3-27b-it"
    ]
    
    # Resilience Hyperparameters
    AI_MAX_RETRIES = 3      # Maximum attempts per model (for 429 Rate Limits)
    AI_BASE_DELAY = 2       # Base seconds for exponential backoff
    
    # ==========================================
    # EXTRACTION LIMITS
    # ==========================================
    MAX_FILE_SIZE_BYTES = 1024 * 500  # Skip files larger than 500KB
    
    # Base directory where all versioned runs will be saved
    BASE_OUTPUT_DIR = Path("./Crawlable_output")
    
    # Path to the static prompt file you want injected into every run
    PROMPT_FILE_PATH = Path("./src/assets/prompt.txt")