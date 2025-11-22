#!/usr/bin/env python3
"""
Convenience script to run MCP Stack Composer
"""
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run main
from app.main import main

if __name__ == "__main__":
    main()

