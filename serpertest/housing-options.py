from serpapi import GoogleSearch
import json

params = {
  "q": "Youth Homeless Shelters near me",
  "location": "San Francisco, California, United States",
  "hl": "en",
  "gl": "us",
  "google_domain": "google.com",
  "api_key": "d40e46afc787c09ad3643f17bb126b995a11f616b49859a0ccafeb96f1905fbc"
}

search = GoogleSearch(params)
results = search.get_dict()

file_path = "research_results.json"
with open(file_path, "w") as f:
    json.dump(results, f, indent=4)
