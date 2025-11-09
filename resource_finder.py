"""
Homeless Resource Finder - Function for Chatbot Agent

This module provides a function to discover and match resources for homeless individuals
based on conversation history. It uses an intermediate LLM call to optimize the search query,
then leverages the deep-research tool to find comprehensive, up-to-date resources.
"""

import os
import json
from typing import List, Dict
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Deep-research API configuration
DEEP_RESEARCH_API_URL = os.getenv("DEEP_RESEARCH_API_URL", "http://localhost:3051")


def extract_search_query_from_conversation(conversation_history: List[Dict[str, str]]) -> str:
    """
    Analyzes conversation history and generates an optimized search query for resource discovery.

    Args:
        conversation_history: List of message dicts with 'role' and 'content' keys

    Returns:
        Optimized search query string for resource discovery
    """
    system_prompt = """You are an expert at analyzing conversations with homeless individuals to identify their needs and circumstances.

Your task is to analyze the conversation history and extract key information to create a focused search query for finding relevant resources.

Extract and consider:
- Location (city, state, county)
- Primary needs (shelter, food, healthcare, employment, legal aid, etc.)
- Special circumstances (veteran status, LGBTQ+, age, family status, disabilities, mental health, substance abuse)
- Urgency level (immediate emergency vs. long-term planning)

Generate a single, comprehensive search query that will help find the most relevant resources for this person's situation.

Format your search query to be specific and actionable. For example:
"Search for emergency shelter and food assistance for LGBTQ youth in San Francisco"
"Find veteran housing programs and job training services in Los Angeles County"
"Locate family shelters and childcare assistance in Seattle area"

Return ONLY the search query, nothing else."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Conversation history:\n{json.dumps(conversation_history, indent=2)}\n\nGenerate the search query:"}
            ],
            temperature=0.3,
            max_tokens=200
        )

        search_query = response.choices[0].message.content.strip()
        return search_query

    except Exception as e:
        raise Exception(f"Failed to extract search query: {str(e)}")


def call_deep_research(query: str, breadth: int = 1, depth: int = 2) -> str:
    """
    Calls the deep-research API to generate a comprehensive resource report.

    Args:
        query: Search query for resource discovery
        breadth: Number of parallel searches (default: 4)
        depth: Research depth/iterations (default: 2)

    Returns:
        Markdown formatted report with resources
    """
    try:
        response = requests.post(
            f"{DEEP_RESEARCH_API_URL}/api/generate-report",
            json={
                "query": query,
                "breadth": breadth,
                "depth": depth
            },
            headers={"Content-Type": "application/json"},
            timeout=600  # 10 minute timeout for research
        )

        response.raise_for_status()
        result = response.json()

        return result.get("reportMarkdown", "")

    except requests.exceptions.ConnectionError:
        raise Exception(
            "Could not connect to deep-research API. "
            "Make sure the server is running: cd deep-research && npm run api"
        )
    except requests.exceptions.Timeout:
        raise Exception("Deep-research request timed out. The query may be too complex.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Deep-research API error: {str(e)}")


def list_eligible_resources(conversation_history: List[Dict[str, str]],
                           breadth: int = 1,
                           depth: int = 2) -> str:
    """
    Main function to discover and list eligible resources for homeless individuals.

    This function is designed to be called by a chatbot agent using function calling capabilities.
    It analyzes the conversation history to understand the person's needs and circumstances,
    then searches for relevant resources using web search and scraping.

    Args:
        conversation_history: List of conversation messages, each with:
            - 'role': 'user' or 'assistant'
            - 'content': message text
        breadth: Number of parallel search queries to execute (default: 4, recommended: 3-10)
        depth: Research depth for follow-up exploration (default: 2, recommended: 1-5)

    Returns:
        Markdown formatted report containing:
        - List of eligible resources
        - Details about each resource (services, location, contact info)
        - Eligibility requirements
        - How each resource can help with their specific situation
        - Source URLs for verification

    Example:
        >>> conversation = [
        ...     {"role": "user", "content": "I'm homeless in San Francisco and need shelter"},
        ...     {"role": "assistant", "content": "I can help you find resources. Are you under 25?"},
        ...     {"role": "user", "content": "Yes, I'm 19 and identify as LGBTQ"}
        ... ]
        >>> report = list_eligible_resources(conversation)
        >>> print(report)

    Raises:
        Exception: If search query extraction fails or deep-research API is unavailable
    """
    # Validate input
    if not conversation_history or len(conversation_history) == 0:
        raise ValueError("conversation_history cannot be empty")

    # Step 1: Extract optimized search query from conversation
    print("Analyzing conversation to identify needs...")
    search_query = extract_search_query_from_conversation(conversation_history)
    print(f"Generated search query: {search_query}")

    # Step 2: Call deep-research to find resources
    print(f"Searching for resources (breadth={breadth}, depth={depth})...")
    resource_report = call_deep_research(search_query, breadth=breadth, depth=depth)

    return resource_report


if __name__ == "__main__":
    # Example usage for testing
    example_conversation = [
        {"role": "user", "content": "Hi, I need help. I'm homeless and don't know where to go."},
        {"role": "assistant", "content": "I'm here to help you find resources. Can you tell me what city you're currently in?"},
        {"role": "user", "content": "I'm in San Francisco."},
        {"role": "assistant", "content": "Thank you. What are your most urgent needs right now? For example, shelter, food, medical care, or something else?"},
        {"role": "user", "content": "I need a place to sleep tonight and I haven't eaten in a day. Also, I'm 19 years old and I'm LGBTQ."},
        {"role": "assistant", "content": "I understand. Let me search for resources that can help you with emergency shelter and food, especially those that support LGBTQ youth in San Francisco."},
    ]

    try:
        report = list_eligible_resources(example_conversation)
        print("\n" + "="*80)
        print("RESOURCE REPORT")
        print("="*80)
        print(report)
    except Exception as e:
        print(f"Error: {e}")
