from flask import Flask, render_template, request, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Import ONLY the Orchestrator
from agents.orchestrator import OrchestratorAgent

# Load environment variables
load_dotenv()
if not os.getenv("GOOGLE_API_KEY"):
    print("⚠️ [WARNING] GOOGLE_API_KEY not found in .env file.")

app = Flask(__name__)
CORS(app)

print("🚀 [BACKEND] Flask Application Starting...")

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/analyze_page')
def analyze_page():
    return render_template('analyze.html')

@app.route('/stream_analyze')
def stream_analyze():
    repo_url = request.args.get('repo_url')
    
    # Instantiate the Orchestrator for this request
    orchestrator = OrchestratorAgent()
    
    # Stream the generator response back to the client
    return Response(
        stream_with_context(orchestrator.work(repo_url)), 
        mimetype='text/event-stream'
    )

if __name__ == '__main__':
    # Debug mode enables hot-reloading during development
    app.run(debug=True, port=5000)