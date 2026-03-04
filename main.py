import argparse
from src.config import logger
from src.core.pipeline import CrowablePipeline

# ==========================================
# ENTRY POINT
# ==========================================
def main():
    parser = argparse.ArgumentParser(description="Crowable: AI-Powered Codebase Extractor")
    parser.add_argument("path", help="Path to the target project directory")
    args = parser.parse_args()
    
    try:
        pipeline = CrowablePipeline(args.path)
        pipeline.run()
    except Exception as e:
        logger.critical(f"Pipeline execution halted: {e}")

if __name__ == "__main__":
    main()