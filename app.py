# import os
# import json
# import time
# import re
# from flask import Flask, render_template, request, Response, stream_with_context
# from flask_cors import CORS
# from dotenv import load_dotenv

# # CrewAI Imports
# from crewai import Task, Crew, Process

# # Custom Agent Imports
# from agents.scout import get_scout_agent
# from agents.roaster import get_roaster_agent

# load_dotenv()

# app = Flask(__name__)
# CORS(app)

# # Model Definition
# llm = "gemini/gemini-2.5-flash"

# @app.route('/')
# def landing():
#     return render_template('landing.html')

# @app.route('/analyze_page')
# def analyze_page():
#     return render_template('analyze.html')

# @app.route('/stream_analyze')
# def stream_analyze():
#     repo_url = request.args.get('repo_url')
    
#     def generate():
#         # --- STEP 1: INIT ---
#         yield f"data: {json.dumps({'status': '[1/4] 🚀 Initializing CrewAI Agents...'})}\n\n"
#         time.sleep(0.5)

#         try:
#             # Instantiate Agents
#             scout = get_scout_agent(llm)
#             roaster = get_roaster_agent(llm)

#             # --- STEP 2: SCOUT ---
#             yield f"data: {json.dumps({'status': '[2/4] 🕵️ Agent [Scout]: Reading repo files...'})}\n\n"

#             task_extract = Task(
#                 description=f"Analyze the repository at {repo_url}. Get the file structure, languages, and read key code files.",
#                 expected_output="A detailed technical summary.",
#                 agent=scout
#             )

#             task_review = Task(
#                 description="Based on the Scout's summary, create a final review. Output strictly Valid JSON.",
#                 expected_output='''JSON with keys: "verdict" (Ship It/Skip It), "roast" (list), "good_things" (list), "suggestions" (list).''',
#                 agent=roaster,
#                 context=[task_extract]
#             )

#             # --- STEP 3: ROASTER & KICKOFF ---
#             yield f"data: {json.dumps({'status': '[3/4] 🔥 Agent [Roaster]: Analyzing code & generating verdict...'})}\n\n"
            
#             crew = Crew(
#                 agents=[scout, roaster],
#                 tasks=[task_extract, task_review],
#                 process=Process.sequential,
#                 verbose=True
#             )

#             # KICKOFF (This takes time)
#             result = crew.kickoff()
            
#             # --- STEP 4: PARSING ---
#             yield f"data: {json.dumps({'status': '[4/4] ⚙️ Finalizing: Parsing Output...'})}\n\n"
            
#             # --- ROBUST PARSING LOGIC ---
#             # Handle different CrewAI result types
#             if hasattr(result, 'raw'):
#                 raw_output = result.raw
#             else:
#                 raw_output = str(result)

#             # DEBUG LOG: Print to VS Code Terminal so we can see what happened
#             print(f"\n\n============= DEBUG: RAW AGENT OUTPUT =============\n{raw_output}\n===================================================\n\n")

#             # 1. Clean Markdown Code Blocks
#             # Removes ```json and ``` to get pure text
#             clean_text = re.sub(r"```json", "", raw_output, flags=re.IGNORECASE)
#             clean_text = re.sub(r"```", "", clean_text)
            
#             # 2. Extract JSON Object using substring search
#             # Finds the first '{' and last '}'
#             start_index = clean_text.find('{')
#             end_index = clean_text.rfind('}') + 1

#             if start_index != -1 and end_index != -1:
#                 json_str = clean_text[start_index:end_index]
#             else:
#                 raise ValueError("Could not find { } brackets in the output.")

#             # 3. Parse
#             final_data = json.loads(json_str)
            
#             yield f"data: {json.dumps({'status': '✅ Analysis Complete!', 'final_data': final_data})}\n\n"
            
#         except Exception as e:
#             print(f"ERROR IN STREAM: {str(e)}") # Print error to terminal
#             yield f"data: {json.dumps({'error': f'Server Error: {str(e)}'})}\n\n"

#     return Response(stream_with_context(generate()), mimetype='text/event-stream')

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)



from flask import Flask, render_template, request, Response, stream_with_context
from flask_cors import CORS
from dotenv import load_dotenv

# Import ONLY the Orchestrator
from agents.orchestrator import OrchestratorAgent

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/analyze_page')
def analyze_page():
    return render_template('analyze.html')

@app.route('/stream_analyze')
def stream_analyze():
    repo_url = request.args.get('repo_url')
    
    # Instantiate the Orchestrator
    orchestrator = OrchestratorAgent()
    
    # Stream the generator
    return Response(
        stream_with_context(orchestrator.work(repo_url)), 
        mimetype='text/event-stream'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)