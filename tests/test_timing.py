#!/usr/bin/env python3
"""
Timed test of the resource_finder function to measure performance of each step.
"""

import time
from resource_finder import extract_search_query_from_conversation, call_deep_research

# Example conversation
example_conversation = [
    {"role": "user", "content": "Hi, I need help. I'm homeless and don't know where to go."},
    {"role": "assistant", "content": "I'm here to help you find resources. Can you tell me what city you're currently in?"},
    {"role": "user", "content": "I'm in San Francisco."},
    {"role": "assistant", "content": "Thank you. What are your most urgent needs right now? For example, shelter, food, medical care, or something else?"},
    {"role": "user", "content": "I need a place to sleep tonight and I haven't eaten in a day. Also, I'm 19 years old and I'm LGBTQ."},
    {"role": "assistant", "content": "I understand. Let me search for resources that can help you with emergency shelter and food, especially those that support LGBTQ youth in San Francisco."},
]

print("="*80)
print("TIMED PERFORMANCE TEST")
print("="*80)
print()

# Step 1: Extract search query from conversation
print("Step 1: Analyzing conversation with OpenAI...")
start_time = time.time()
search_query = extract_search_query_from_conversation(example_conversation)
query_time = time.time() - start_time
print(f"✓ Completed in {query_time:.2f} seconds")
print(f"  Generated query: \"{search_query}\"")
print()

# Step 2: Call deep-research API
print("Step 2: Running deep-research (breadth=3, depth=1)...")
start_time = time.time()
try:
    resource_report = call_deep_research(search_query, breadth=3, depth=1)
    research_time = time.time() - start_time
    print(f"✓ Completed in {research_time:.2f} seconds")
    print(f"  Report length: {len(resource_report)} characters")
    print()

    # Total time
    total_time = query_time + research_time

    print("="*80)
    print("TIMING SUMMARY")
    print("="*80)
    print(f"Step 1 - Conversation Analysis (OpenAI): {query_time:.2f}s ({query_time/total_time*100:.1f}%)")
    print(f"Step 2 - Deep Research (Firecrawl):      {research_time:.2f}s ({research_time/total_time*100:.1f}%)")
    print(f"-" * 80)
    print(f"Total Time:                              {total_time:.2f}s")
    print("="*80)
    print()

    # Show first 500 chars of report
    if resource_report:
        print("Report Preview (first 500 characters):")
        print("-" * 80)
        print(resource_report[:500])
        if len(resource_report) > 500:
            print("...")
    else:
        print("⚠ Report is empty (Firecrawl content issue)")

except Exception as e:
    research_time = time.time() - start_time
    print(f"✗ Failed after {research_time:.2f} seconds")
    print(f"  Error: {e}")
    print()
    print("="*80)
    print("TIMING SUMMARY (PARTIAL)")
    print("="*80)
    print(f"Step 1 - Conversation Analysis (OpenAI): {query_time:.2f}s")
    print(f"Step 2 - Deep Research (Firecrawl):      {research_time:.2f}s (failed)")
    print("="*80)
