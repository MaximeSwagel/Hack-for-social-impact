# Hack-for-social-impact
AI powered care platform for youth homelessness

## Homeless Resource Chatbot

An AI-powered chatbot that helps homeless individuals discover and connect to resources they may be eligible for.

## Setup

### 1. Install Dependencies

#### Deep-Research (Node.js)
```bash
cd deep-research
npm install
```

#### Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys

Create a `.env` file in the root directory with your API keys:

```bash
OPENAI_API_KEY=your_openai_api_key
FIRECRAWL_KEY=your_firecrawl_api_key
DEEP_RESEARCH_API_URL=http://localhost:3051
```

That's it! No need to configure multiple env files.

### 3. Start Deep-Research API Server

In one terminal, start the deep-research API server using the Python startup script:
```bash
python start_api.py
```

Or if you prefer to start it directly with npm (you'll need to set env vars manually):
```bash
cd deep-research
OPENAI_KEY=$OPENAI_API_KEY FIRECRAWL_KEY=$FIRECRAWL_KEY npm run api
```

The server will run on http://localhost:3051

## Usage

### As a Function (for Chatbot Integration)

```python
from resource_finder import list_eligible_resources

# Your chatbot conversation history
conversation = [
    {"role": "user", "content": "I'm homeless in San Francisco and need shelter"},
    {"role": "assistant", "content": "I can help you find resources. Are you under 25?"},
    {"role": "user", "content": "Yes, I'm 19 and identify as LGBTQ"}
]

# Get resources
report = list_eligible_resources(conversation, breadth=4, depth=2)
print(report)
```

### Test the Example

```bash
python resource_finder.py
```

## Function Reference

### `list_eligible_resources(conversation_history, breadth=4, depth=2)`

Main function to discover and list eligible resources for homeless individuals.

**Parameters:**
- `conversation_history` (List[Dict]): List of conversation messages with 'role' and 'content'
- `breadth` (int): Number of parallel search queries (default: 4, recommended: 3-10)
- `depth` (int): Research depth for follow-up exploration (default: 2, recommended: 1-5)

**Returns:**
- `str`: Markdown formatted report with resources, eligibility, and contact information

**Example:**
```python
conversation = [
    {"role": "user", "content": "I need help finding shelter in Seattle"},
    {"role": "assistant", "content": "I can help. Do you have any children with you?"},
    {"role": "user", "content": "Yes, I have 2 kids aged 5 and 7"}
]

resources = list_eligible_resources(conversation)
```

## How It Works

1. **Conversation Analysis**: Uses OpenAI to analyze the conversation history and extract:
   - Location
   - Primary needs (shelter, food, healthcare, etc.)
   - Special circumstances (age, LGBTQ+, veteran status, family status, etc.)
   - Urgency level

2. **Query Optimization**: Generates a focused search query optimized for resource discovery
   - Example: "Search for emergency shelter and food assistance for LGBTQ youth in San Francisco"

3. **Deep Research**: Calls the deep-research API which:
   - Generates multiple search queries
   - Uses Firecrawl to search and scrape web resources
   - Iteratively refines the search based on findings
   - Compiles comprehensive information

4. **Resource Report**: Returns markdown report with:
   - List of relevant resources
   - Service details and eligibility requirements
   - Contact information (address, phone, website)
   - How each resource can help with their specific situation
   - Source URLs for verification

## Adjusting Search Parameters

- **Higher Breadth (5-10)**: More parallel searches, finds more diverse resources (slower, more API calls)
- **Lower Breadth (2-3)**: Faster, fewer resources, lower cost
- **Higher Depth (3-5)**: Deeper follow-up research, more comprehensive (much slower)
- **Lower Depth (1-2)**: Quick results, good for urgent needs

Recommended for production: `breadth=4, depth=2` (balanced)
Recommended for testing: `breadth=3, depth=1` (faster)

## Architecture

```
Conversation History
        ↓
OpenAI Analysis (extract needs/location/circumstances)
        ↓
Optimized Search Query
        ↓
Deep-Research API
        ↓
Firecrawl (Web Search & Scraping)
        ↓
Markdown Resource Report
```

## Error Handling

The function will raise exceptions for:
- Empty conversation history
- Failed OpenAI API calls
- Deep-research API unavailable (check if server is running)
- Network timeouts (default: 5 minutes)

## Privacy & Security

- Minimal data collection
- No conversation history is stored
- All processing happens in memory
- API calls are ephemeral

## Next Steps

To integrate into your chatbot:
1. Add `list_eligible_resources` to your function calling schema
2. Pass the conversation history when the user requests resources
3. Display the markdown report to the user
4. Consider caching results for similar queries
