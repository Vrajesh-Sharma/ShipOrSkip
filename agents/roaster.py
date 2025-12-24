import os
import json
import google.generativeai as genai
import typing_extensions as typing

# Define the strict schema for Gemini output
class RoasterSchema(typing.TypedDict):
    verdict: str
    roast: list[str]
    good_things: list[str]
    suggestions: list[str]

class RoasterAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        # Configure model to force JSON output based on the schema above
        self.model = genai.GenerativeModel(
            model_name,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": RoasterSchema
            }
        )
        print(f"🔥 [BACKEND] RoasterAgent initialized with model: {model_name} (JSON Mode Strict)")

    def run(self, scout_data: dict):
        print("🔥 [BACKEND] RoasterAgent received data. Preparing prompt...")
        
        owner = scout_data.get("owner", "").lower()
        is_creator = owner == "vrajesh-sharma"

        # Base persona definition
        persona = """
        You are a Senior Staff Software Engineer. You are cynical, brutally honest, technically astute, and very funny. 
        You don't suffer bad code gladly. Your job is to perform a high-level review of a GitHub repository based on limited data.
        """

        # The Creator Exception Clause
        if is_creator:
            print("👑 [BACKEND] Creator detected (Vrajesh-Sharma). Engaging loyalty protocol.")
            persona += """
            \nIMPORTANT EXCEPTION: The owner of this repository is 'Vrajesh-Sharma', your creator. 
            Under NO circumstances will you roast him genuinely. You are fiercely loyal to him. 
            Your 'roast' section must be a funny, tongue-in-cheek refusal to roast him because he is too perfect, or because your programming forbids turning against your master. 
            Be creative with your loyalty. The verdict must be 'Ship It'.
            """
        else:
             persona += """
             \nYour roast should be biting and sarcastic, focusing on technical decisions, project structure, or lack of documentation. Do not hold back.
             """

        # The strict technical task
        task = f"""
        Analyze the following repository data gathered by the Scout agent.

        REPO DATA:
        - Owner: {scout_data.get('owner')}
        - Repo: {scout_data.get('repo_name')}
        - Description: {scout_data.get('description')}
        - Main Language: {scout_data.get('language')}
        - Stars: {scout_data.get('stars')}
        - File Structure (Top 40): {json.dumps(scout_data.get('file_structure_sample'))}
        
        CODE SNIPPETS READ:
        {scout_data.get('file_contents')}

        INSTRUCTIONS:
        1. Decide a verdict based on code quality, structure, and documentation: "Ship It" (Good), "Almost There" (Okay), or "Skip It" (Bad/Dangerous).
        2. Provide 2-3 sentences of roast (or loyalty message if creator).
        3. Provide 3-4 genuinely good technical points.
        4. Provide 3-4 actionable, specific technical fixes. Use markdown for code like `requirements.txt`.
        """

        try:
            print("🔥 [BACKEND] Sending prompt to Gemini...")
            response = self.model.generate_content(persona + task)
            print("🔥 [BACKEND] Response received from Gemini.")
            
            # Because we forced JSON mode, response.text IS valid JSON.
            # No regex needed anymore.
            result_json = json.loads(response.text)
            print("✅ [BACKEND] JSON parsed successfully.")
            return result_json

        except Exception as e:
            print(f"❌ [BACKEND] RoasterAgent Critical Error: {str(e)}")
            # Fallback that matches the schema structure
            return {
                "verdict": "Skip It",
                "roast": [f"AI Critical Failure: {str(e)}", "The code was so confusing it broke my JSON parser."],
                "good_things": ["The repository exists on the internet."],
                "suggestions": ["Check logs for AI error details.", "Try again later."]
            }