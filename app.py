import os
import json
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Headers for GitHub API
headers = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    headers["Authorization"] = f"token {GITHUB_TOKEN}"

def get_github_data(repo_url):
    """Fetches metadata, file structure, and key code snippets."""
    try:
        if not repo_url.startswith("https://github.com/"):
            return None, "Invalid URL. Must start with https://github.com/"
        
        clean_url = repo_url.split("?")[0].rstrip("/")
        parts = clean_url.split("/")
        if len(parts) < 5:
            return None, "Invalid URL format."
            
        owner, repo = parts[-2], parts[-1]
    except Exception:
        return None, "Could not parse URL."

    base_url = f"https://api.github.com/repos/{owner}/{repo}"
    
    # 1. Basic Metadata
    resp = requests.get(base_url, headers=headers)
    if resp.status_code == 404:
        return None, "Repo not found or Private. Public repos only."
    elif resp.status_code == 403:
        return None, "API Rate limit exceeded."
    elif resp.status_code != 200:
        return None, f"GitHub API Error: {resp.status_code}"

    data = resp.json()
    if data.get("private") is True:
        return None, "Private repositories are not supported."

    # 2. Languages
    lang_resp = requests.get(f"{base_url}/languages", headers=headers)
    languages = lang_resp.json() if lang_resp.status_code == 200 else {}

    # 3. README
    readme_content = ""
    readme_resp = requests.get(f"{base_url}/readme", headers=headers)
    if readme_resp.status_code == 200:
        download_url = readme_resp.json().get("download_url")
        if download_url:
            readme_content = requests.get(download_url).text[:6000] # Increased limit

    # 4. File Structure (Tree) & Key Code Snippets
    # We fetch the git tree to see folder structure
    tree_url = f"{base_url}/git/trees/{data['default_branch']}?recursive=1"
    tree_resp = requests.get(tree_url, headers=headers)
    
    file_structure = []
    code_snippets = ""
    
    if tree_resp.status_code == 200:
        tree_data = tree_resp.json().get("tree", [])
        # Limit to top 30 files to avoid overwhelming the prompt
        file_structure = [item['path'] for item in tree_data[:30]]
        
        # Smart File Fetching: Look for interesting code files
        interesting_files = [f for f in tree_data if f['path'].endswith(('.py', '.js', '.ts', '.jsx', '.tsx', 'go', 'rs', 'java'))]
        
        # Take up to 2 code files to analyze coding style
        for file_obj in interesting_files[:2]:
            # Get raw content
            raw_resp = requests.get(f"https://raw.githubusercontent.com/{owner}/{repo}/{data['default_branch']}/{file_obj['path']}")
            if raw_resp.status_code == 200:
                code_snippets += f"\n--- FILE: {file_obj['path']} ---\n{raw_resp.text[:1000]}\n"

    return {
        "name": data.get("name"),
        "description": data.get("description", "No description."),
        "stars": data.get("stargazers_count"),
        "forks": data.get("forks_count"),
        "open_issues": data.get("open_issues_count"),
        "languages": languages,
        "readme": readme_content,
        "structure": file_structure, # Pass this to AI
        "code_snippets": code_snippets # Pass this to AI
    }, None

def analyze_with_gemini(repo_data):
    """Sends data to Gemini Flash for the roast/review."""
    
    # Heuristics for the prompt context
    has_readme = bool(repo_data['readme'])
    top_lang = max(repo_data['languages'], key=repo_data['languages'].get) if repo_data['languages'] else "Unknown"
    
    system_prompt = f"""
    You are a Senior Staff Engineer. You are strictly honest, slightly cynical, but deep down you want the junior dev to succeed.
    
    Analyze this GitHub project:
    - Name: {repo_data['name']}
    - Description: {repo_data['description']}
    - Primary Languages: {repo_data['languages']}
    - File Structure (First 30 files): {repo_data['structure']}
    - README Snippet: {repo_data['readme'][:2000]}...
    - CODE SNIPPETS (Style Check): {repo_data['code_snippets']}
    
    Your Task:
    1. README: If missing, roast them.
    2. ARCHITECTURE: Look at the file structure. Is it messy? Are they putting everything in root?
    3. CODE QUALITY: Look at the 'CODE SNIPPETS'. Are they using comments? Weird variable names?
    4. VERDICT: Be fair.
    
    Output strictly valid JSON
    {{
        "roast": ["string", "string"],
        "good_things": ["string", "string"],
        "issues": ["string", "string"],
        "suggestions": ["string", "string"],
        "verdict": "Ship It" | "Almost There" | "Skip It"
    }}
    """

    model = genai.GenerativeModel('gemini-2.5-flash') # Using 1.5 Flash as standard, replace with 2.5 if available
    response = model.generate_content(system_prompt, generation_config={"response_mime_type": "application/json"})
    
    try:
        return json.loads(response.text)
    except Exception as e:
        return {
            "verdict": "Skip It", 
            "roast": ["The code broke my JSON parser. That's how bad it is."],
            "good_things": [], 
            "issues": ["AI Generation Failed"], 
            "suggestions": ["Try again."]
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    repo_url = data.get('repo_url')
    
    if not repo_url:
        return jsonify({"error": "URL is required"}), 400

    # Step 1: Fetch Data
    repo_data, error = get_github_data(repo_url)
    if error:
        return jsonify({"error": error}), 404

    # Step 2: AI Analysis
    analysis = analyze_with_gemini(repo_data)
    
    return jsonify({
        "repo_data": repo_data,
        "analysis": analysis
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)