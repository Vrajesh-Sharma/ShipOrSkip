import json
import time
from .scout import ScoutAgent
from .roaster import RoasterAgent

class OrchestratorAgent:
    def __init__(self):
        self.scout = ScoutAgent()
        # Using 1.5 Flash for stability on free tier
        self.roaster = RoasterAgent(model_name="gemini-2.5-flash")

    def work(self, repo_url):
        """
        Generator function that streams status updates and the final result.
        """
        # --- Step 1: Initialization ---
        yield self._msg("[1/4] 🚀 Orchestrator: Initializing Agents...")
        time.sleep(0.5)

        # --- Step 2: Scouting ---
        yield self._msg("[2/4] 🕵️ Agent [Scout]: Infiltrating GitHub...")
        
        scout_result = self.scout.run(repo_url)
        
        if "error" in scout_result:
            yield self._error(scout_result["error"])
            return

        # --- Step 3: Roasting ---
        yield self._msg("[3/4] 🔥 Agent [Roaster]: Analyzing code & Judging you...")
        
        final_verdict = self.roaster.run(scout_result["data"])

        # --- Step 4: Finalizing ---
        yield self._msg("[4/4] ⚙️ Orchestrator: Formatting Results...")
        
        # Success Event
        yield f"data: {json.dumps({'status': '✅ Analysis Complete!', 'final_data': final_verdict})}\n\n"

    def _msg(self, text):
        return f"data: {json.dumps({'status': text})}\n\n"

    def _error(self, text):
        return f"data: {json.dumps({'error': text})}\n\n"