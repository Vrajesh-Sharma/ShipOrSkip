import os
import requests
import json

class ScoutAgent:
    def __init__(self):
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            self.headers["Authorization"] = f"token {token}"
        print("🕵️ [BACKEND] ScoutAgent initialized.")

    def run(self, repo_url: str):
        print(f"🕵️ [BACKEND] ScoutAgent started processing URL: {repo_url}")
        try:
            # 1. Parse URL
            clean_url = repo_url.split("?")[0].rstrip("/")
            parts = clean_url.split("/")
            if len(parts) < 5:
                print("❌ [BACKEND] ScoutAgent Error: Invalid URL format.")
                return {"error": "Invalid URL format. Use https://github.com/owner/repo"}
            
            owner, repo = parts[-2], parts[-1]
            print(f"🕵️ [BACKEND] Identified Repo: {owner}/{repo}")
            base_url = f"https://api.github.com/repos/{owner}/{repo}"

            # 2. Fetch Metadata
            print("🕵️ [BACKEND] Fetching metadata form GitHub API...")
            resp = requests.get(base_url, headers=self.headers)
            if resp.status_code == 404:
                print("❌ [BACKEND] Error 404: Repo not found or private.")
                return {"error": "Repo not found or Private. Make sure it's public."}
            if resp.status_code == 403:
                print("❌ [BACKEND] Error 403: Rate limit exceeded.")
                return {"error": "GitHub API Rate Limit Exceeded. Try again later."}
            
            data = resp.json()

            # 3. Fetch File Structure (Limited to top 40)
            print("🕵️ [BACKEND] Fetching file structure...")
            tree_url = f"{base_url}/git/trees/{data['default_branch']}?recursive=1"
            tree_resp = requests.get(tree_url, headers=self.headers)
            tree_data = tree_resp.json()
            all_files = [item['path'] for item in tree_data.get("tree", [])]
            structure = all_files[:40]

            # 4. Fetch Key Code Files (Limit 3 files, max 2500 chars each)
            print("🕵️ [BACKEND] Fetching key code files...")
            code_content = ""
            # Priority order for fetching
            priority_files = ['README.md', 'app.py', 'main.py', 'index.js', 'package.json', 'requirements.txt', 'Dockerfile']
            
            found_count = 0
            files_read = []
            for file_path in all_files:
                if found_count >= 3: break # Hard limit to save context window
                
                # Check if it's a priority file OR an interesting code file extension
                if file_path in priority_files or file_path.endswith(('.py', '.js', '.ts', '.rs', '.go', '.java', '.c')):
                   # Avoid deep directories for better context usage
                   if "/" in file_path and file_path not in priority_files: continue

                   raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{data['default_branch']}/{file_path}"
                   try:
                       file_resp = requests.get(raw_url, timeout=5)
                       if file_resp.status_code == 200:
                           content = file_resp.text[:2500] # Truncate huge files
                           code_content += f"\n\n--- START FILE: {file_path} ---\n{content}\n--- END FILE: {file_path} ---\n"
                           files_read.append(file_path)
                           found_count += 1
                   except Exception as e:
                       print(f"⚠️ [BACKEND] Could not read {file_path}: {e}")
                       continue
            
            print(f"🕵️ [BACKEND] ScoutAgent finished. Read files: {files_read}")

            # Compile the data package for the Roaster
            scout_data = {
                "owner": owner, # IMPORTANT: Passing owner explicitly now
                "repo_name": data.get('name'),
                "description": data.get('description', 'No description provided.'),
                "language": data.get('language'),
                "stars": data.get('stargazers_count'),
                "file_structure_sample": structure,
                "file_contents": code_content
            }
            
            return {"success": True, "data": scout_data}

        except Exception as e:
            print(f"❌ [BACKEND] ScoutAgent Critical Error: {str(e)}")
            return {"error": f"Scout failed unexpectedly: {str(e)}"}