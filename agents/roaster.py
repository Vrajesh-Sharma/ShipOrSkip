# import os
# import json
# import re
# import google.generativeai as genai

# class RoasterAgent:
#     def __init__(self, model_name="gemini-1.5-flash"):
#         genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
#         self.model = genai.GenerativeModel(model_name)

#     def run(self, repo_data: str):
#         """
#         Analyzes the repo data and returns a JSON verdict.
#         """
#         prompt = f"""
#         You are a Senior Staff Software Engineer. You are brutal, funny, but insightful.
#         You are reviewing a GitHub repository.
        
#         Here is the Scout's Report:
#         {repo_data}
        
#         Task:
#         1. Analyze the file structure and code snippets.
#         2. Give a verdict: "Ship It" (Good), "Almost There" (Okay), or "Skip It" (Bad).
#         3. Write a 'Roast': A funny, slightly mean paragraph about the code quality.
#         4. List 'Good Things': 3-4 bullet points of genuine compliments.
#         5. List 'Suggestions': 3-4 bullet points of actionable technical advice.
        
#         OUTPUT FORMAT:
#         You must output strictly Valid JSON.
#         {{
#             "verdict": "Ship It | Almost There | Skip It",
#             "roast": ["Sentence 1", "Sentence 2"],
#             "good_things": ["Point 1", "Point 2"],
#             "suggestions": ["Tip 1", "Tip 2"]
#         }}
#         """

#         try:
#             response = self.model.generate_content(prompt)
#             raw_text = response.text
            
#             # --- Robust JSON Parsing ---
#             # Remove Markdown code blocks
#             clean_text = re.sub(r"```json", "", raw_text, flags=re.IGNORECASE)
#             clean_text = re.sub(r"```", "", clean_text).strip()
            
#             # Extract JSON object between { and }
#             start = clean_text.find('{')
#             end = clean_text.rfind('}') + 1
            
#             if start != -1 and end != -1:
#                 json_str = clean_text[start:end]
#                 return json.loads(json_str)
#             else:
#                 raise ValueError("No JSON found in response")

#         except Exception as e:
#             # Fallback error JSON
#             return {
#                 "verdict": "Skip It",
#                 "roast": [f"I tried to analyze this code, but my brain short-circuited. Error: {str(e)}"],
#                 "good_things": ["You broke the AI. That's an achievement."],
#                 "suggestions": ["Try again later."]
#             }

import os
import json
import re
import google.generativeai as genai

class RoasterAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel(model_name)

    def run(self, scout_data: str):
        prompt = f"""
        You are a Senior Staff Software Engineer. Brutal but funny.
        Review this GitHub repo:
        {scout_data}
        
        OUTPUT JSON ONLY:
        {{
            "verdict": "Ship It | Almost There | Skip It",
            "roast": ["Sentence 1", "Sentence 2"],
            "good_things": ["Point 1", "Point 2"],
            "suggestions": ["Tip 1", "Tip 2"]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            clean_text = re.sub(r"```json|```", "", response.text, flags=re.IGNORECASE).strip()
            
            start = clean_text.find('{')
            end = clean_text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(clean_text[start:end])
            else:
                raise ValueError("No JSON found")
                
        except Exception as e:
            return {"verdict": "Skip It", "roast": [f"AI Error: {str(e)}"], "good_things": [], "suggestions": []}