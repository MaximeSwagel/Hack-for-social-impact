#!/usr/bin/env python3
"""
Startup script for deep-research API server.
Loads environment variables from root .env file and starts the Node.js API server.
"""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from root .env file
root_dir = Path(__file__).parent
env_file = root_dir / ".env"

if not env_file.exists():
    print(f"Error: {env_file} not found")
    print("Please create a .env file in the root directory with:")
    print("  OPENAI_API_KEY=your_key")
    print("  FIRECRAWL_KEY=your_key")
    sys.exit(1)

load_dotenv(env_file)

# Get required environment variables
openai_key = os.getenv("OPENAI_API_KEY")
firecrawl_key = os.getenv("FIRECRAWL_KEY")

if not openai_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    sys.exit(1)

if not firecrawl_key:
    print("Error: FIRECRAWL_KEY not found in .env file")
    sys.exit(1)

# Prepare environment for Node.js process
env = os.environ.copy()
env["OPENAI_KEY"] = openai_key
env["FIRECRAWL_KEY"] = firecrawl_key

# Optional environment variables
if os.getenv("FIRECRAWL_BASE_URL"):
    env["FIRECRAWL_BASE_URL"] = os.getenv("FIRECRAWL_BASE_URL")

if os.getenv("CONCURRENCY_LIMIT"):
    env["CONCURRENCY_LIMIT"] = os.getenv("CONCURRENCY_LIMIT")

# Start the deep-research API server
deep_research_dir = root_dir / "deep-research"
os.chdir(deep_research_dir)

print("Starting deep-research API server...")
print(f"Using environment variables from: {env_file}")
print(f"API will run on: http://localhost:3051")
print("\nPress Ctrl+C to stop the server\n")

try:
    # Use npx tsx directly to avoid .env.local requirement
    subprocess.run(
        ["npx", "tsx", "src/api.ts"],
        env=env,
        check=True
    )
except KeyboardInterrupt:
    print("\n\nShutting down API server...")
    sys.exit(0)
except subprocess.CalledProcessError as e:
    print(f"\nError starting API server: {e}")
    sys.exit(1)
