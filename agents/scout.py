# import os
# import requests

# class ScoutAgent:
#     def __init__(self):
#         self.headers = {"Accept": "application/vnd.github.v3+json"}
#         token = os.getenv("GITHUB_TOKEN")
#         if token:
#             self.headers["Authorization"] = f"token {token}"

#     def run(self, repo_url: str):
#         """
#         Fetches repository metadata, file structure, and key code files.
#         """
#         try:
#             # 1. Clean URL logic
#             clean_url = repo_url.split("?")[0].rstrip("/")
#             parts = clean_url.split("/")
#             if len(parts) < 5: 
#                 return {"error": "Invalid URL. Use format: https://github.com/owner/repo"}
            
#             owner, repo = parts[-2], parts[-1]
#             base_url = f"https://api.github.com/repos/{owner}/{repo}"

#             # 2. Fetch Metadata
#             resp = requests.get(base_url, headers=self.headers)
#             if resp.status_code == 404: 
#                 return {"error": "Repository not found or is Private."}
#             if resp.status_code == 403: 
#                 return {"error": "GitHub API Rate Limit Exceeded."}
            
#             data = resp.json()

#             # 3. Fetch File Tree
#             tree_url = f"{base_url}/git/trees/{data['default_branch']}?recursive=1"
#             tree_resp = requests.get(tree_url, headers=self.headers)
#             tree_data = tree_resp.json()
            
#             # 4. File Filtering
#             all_files = [item['path'] for item in tree_data.get("tree", [])]
#             structure = all_files[:40]  # Increased limit slightly
            
#             # 5. Fetch Key Code Content
#             code_content = ""
#             # Priority files to read
#             priority_files = ['app.py', 'main.py', 'index.js', 'package.json', 'requirements.txt', 'Dockerfile', 'README.md']
            
#             found_count = 0
#             for file_path in all_files:
#                 if found_count >= 3: break # Limit to 3 files to save context
                
#                 if file_path in priority_files or file_path.endswith(('.py', '.js', '.ts', '.rs', '.go')):
#                     raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{data['default_branch']}/{file_path}"
#                     file_resp = requests.get(raw_url)
                    
#                     if file_resp.status_code == 200:
#                         content = file_resp.text[:2500] # Truncate large files
#                         code_content += f"\n--- FILE: {file_path} ---\n{content}\n"
#                         found_count += 1

#             # Return a formatted string for the LLM
#             summary = f"""
#             REPO ANALYSIS DATA:
#             Name: {data.get('name')}
#             Description: {data.get('description', 'No description')}
#             Stars: {data.get('stargazers_count')}
#             Language: {data.get('language')}
#             Structure (Top 40 files): {structure}
            
#             KEY CODE CONTENT:
#             {code_content}
#             """
#             return {"success": True, "data": summary}

#         except Exception as e:
#             return {"error": f"Scout failed: {str(e)}"}

import os
import requests

class ScoutAgent:
    def __init__(self):
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            self.headers["Authorization"] = f"token {token}"

    def run(self, repo_url: str):
        try:
            # 1. Parse URL
            clean_url = repo_url.split("?")[0].rstrip("/")
            parts = clean_url.split("/")
            if len(parts) < 5: return {"error": "Invalid URL format."}
            owner, repo = parts[-2], parts[-1]
            base_url = f"https://api.github.com/repos/{owner}/{repo}"

            # 2. Fetch Metadata
            resp = requests.get(base_url, headers=self.headers)
            if resp.status_code == 404: return {"error": "Repo not found or Private."}
            if resp.status_code == 403: return {"error": "GitHub Rate Limit Exceeded."}
            data = resp.json()

            # 3. Fetch File Structure
            tree_url = f"{base_url}/git/trees/{data['default_branch']}?recursive=1"
            tree_resp = requests.get(tree_url, headers=self.headers)
            all_files = [item['path'] for item in tree_resp.json().get("tree", [])]
            structure = all_files[:40]

            # 4. Fetch Key Files
            code_content = ""
            priority_files = ['app.py', 'main.py', 'index.js', 'package.json', 'requirements.txt', 'Dockerfile', 'README.md']
            found_count = 0
            
            for f in all_files:
                if found_count >= 3: break
                if f in priority_files or f.endswith(('.py', '.js', '.ts', '.rs', '.go')):
                    raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{data['default_branch']}/{f}"
                    file_resp = requests.get(raw_url)
                    if file_resp.status_code == 200:
                        code_content += f"\n--- FILE: {f} ---\n{file_resp.text[:2500]}\n"
                        found_count += 1

            summary = f"""
            REPO: {data.get('name')}
            DESC: {data.get('description')}
            LANG: {data.get('language')}
            STARS: {data.get('stargazers_count')}
            FILES: {structure}
            CODE: {code_content}
            """
            return {"success": True, "data": summary}

        except Exception as e:
            return {"error": str(e)}