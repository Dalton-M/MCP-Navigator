"""
Configuration management for MCP Stack Composer
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Groq API settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_API_BASE = "https://api.groq.com/openai/v1"
    GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # Updated: llama-3.1-70b-versatile was decommissioned
    
    # MCP-specific API keys
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
    
    # MCP server settings (for local Docker MCP servers)
    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "3000"))
    
    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    TEST_DATA_DIR = PROJECT_ROOT / "tests" / "test_data"
    
    # MCP catalog path
    MCP_CATALOG_PATH = DATA_DIR / "mcp_catalog.json"
    
    # Mock mode (fallback when API keys are not available)
    USE_MOCK_MODE = not bool(GROQ_API_KEY)
    
    @classmethod
    def validate(cls):
        """Validate essential configuration"""
        if cls.USE_MOCK_MODE:
            print("⚠️  Running in MOCK MODE (no Groq API key detected)")
        
        # Create directories if they don't exist
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        return True

