# Quick Start Guide

## Single .env File Setup

All configuration is now in one place: **`.env`** in the root directory.

### Current Configuration

Your `.env` file contains:
```
OPENAI_API_KEY=sk-proj-...
FIRECRAWL_KEY=fc-4e38...
DEEP_RESEARCH_API_URL=http://localhost:3051
```

### How It Works

The `start_api.py` script:
1. Loads variables from root `.env` file
2. Passes them to the deep-research Node.js process
3. No need for `deep-research/.env.local` anymore!

## Running the System

### Step 1: Start the API Server

```bash
python start_api.py
```

This will:
- Load your API keys from `.env`
- Start the deep-research API on port 3051
- Keep running until you press Ctrl+C

### Step 2: Test the Resource Finder

In another terminal:

```bash
python resource_finder.py
```

Or use it in your code:

```python
from resource_finder import list_eligible_resources

conversation = [
    {"role": "user", "content": "I need shelter in San Francisco"},
    {"role": "user", "content": "I'm 19 and LGBTQ"}
]

report = list_eligible_resources(conversation)
print(report)
```

## Files Created

- **`start_api.py`** - Starts deep-research API using root .env
- **`test_setup.py`** - Verifies your .env configuration
- **`resource_finder.py`** - Main function for chatbot integration
- **`.env`** - Single source of truth for all API keys

## Removed

- ~~`deep-research/.env.local`~~ - No longer needed!

## Verify Setup

```bash
python test_setup.py
```

Should show all green checkmarks ✓
