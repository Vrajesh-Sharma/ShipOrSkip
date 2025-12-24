import json
import time
from .scout import ScoutAgent
from .roaster import RoasterAgent

class OrchestratorAgent:
    def __init__(self):
        print("🧠 [BACKEND] Orchestrator initializing agents...")
        self.scout = ScoutAgent()
        # Using 1.5 Flash for speed and cost-effectiveness
        self.roaster = RoasterAgent(model_name="gemini-2.5-flash")
        print("🧠 [BACKEND] Agents ready.")

    def work(self, repo_url):
        """
        Generator function that streams status updates and the final result.
        """
        print(f"\n--- [BACKEND] New Analysis Request: {repo_url} ---")
        
        # --- Step 1: Initialization ---
        yield self._msg("[1/4] 🚀 Orchestrator: Initializing workflow...")
        time.sleep(0.5) # Small UI pause

        # --- Step 2: Scouting ---
        print("🧠 [BACKEND] Starting Step 2: Scout")
        yield self._msg("[2/4] 🕵️ Agent [Scout]: Infiltrating GitHub API...")
        
        scout_result = self.scout.run(repo_url)
        
        if "error" in scout_result:
             print(f"🧠 [BACKEND] Scout failed: {scout_result['error']}")
             yield self._error(scout_result["error"])
             return

        # --- Step 3: Roasting ---
        print("🧠 [BACKEND] Starting Step 3: Roaster")
        yield self._msg("[3/4] 🔥 Agent [Roaster]: Analyzing architecture & Judging code...")
        
        # Pass the structured data dictionary to the roaster
        final_verdict = self.roaster.run(scout_result["data"])

        # --- Step 4: Finalizing ---
        print("🧠 [BACKEND] Starting Step 4: Finalizing")
        yield self._msg("[4/4] ⚙️ Orchestrator: Formatting JSON response...")
        
        # Success Event
        print("--- [BACKEND] Analysis Request Complete ---\n")
        yield f"data: {json.dumps({'status': '✅ Analysis Complete!', 'final_data': final_verdict})}\n\n"

    def _msg(self, text):
        # Helper for status updates
        return f"data: {json.dumps({'status': text})}\n\n"

    def _error(self, text):
        # Helper for error messages
        return f"data: {json.dumps({'error': text})}\n\n"