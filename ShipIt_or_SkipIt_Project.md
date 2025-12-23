# 🚀 Project Prompt: ShipIt or SkipIt  
## An AI Project Reviewer for Builders (7-Day Challenge)

You are a **senior full-stack engineer, AI agent architect, and product designer**.

Your task is to design and implement a complete, production-ready project called **“ShipIt or SkipIt”** — an AI-powered GitHub project reviewer that evaluates repositories honestly, constructively, and with light humor.

This project should feel like feedback from a **strict but caring senior / big-brother developer**.

The goal is:
- NOT to insult  
- NOT to demotivate  
- BUT to **tell the truth, roast bad practices lightly, and help builders improve**

---

## 🧠 CORE IDEA

User pastes a **GitHub repository URL**.

The system:
1. Fetches repository metadata using GitHub API  
2. Analyzes README, description, codebase, and language distribution  
3. Uses an AI agent (**Gemini-2.5-Flash**) to:
   - Review project quality  
   - Roast missing or misleading practices (light + funny)  
   - Suggest concrete improvements  
4. Produces a final verdict:
   - 🚀 Ship It  
   - 🛠 Almost There  
   - 🛑 Skip It  

---

## ⚙️ TECH STACK (STRICT – DO NOT CHANGE)

### Backend
- Python  
- Flask  
- GitHub REST API  
- Gemini-2.5-Flash (Google Generative AI)  

### Frontend
- HTML  
- TailwindCSS  
- Vanilla JavaScript (NO React, NO frameworks)

---

## 🧩 BACKEND ARCHITECTURE (FLASK)

### API Endpoint
POST /analyze

### Request Body
```json
{
  "repo_url": "https://github.com/username/repository"
}
```

---

## 🔧 Backend Responsibilities

### 1️⃣ GitHub Data Extraction
Fetch:
- Repository name  
- Description  
- README content  
- Primary language  
- Language distribution  
- Folder structure  
- Commit count  

Missing README or description should trigger **ROAST MODE**.

---

### 2️⃣ Pre-AI Analysis
Compute signals:
- README present or not  
- Description quality  
- Project claim vs actual stack  
- AI project with <20% Python → suspicious  
- Messy folder structure  

---

## 🤖 AGENT DESIGN

### Model
Gemini-2.5-Flash

### Agent Role
“You are a brutally honest but caring senior software engineer reviewing a junior developer’s GitHub project.”

### Output Format (STRICT JSON)
```json
{
  "roast": [],
  "good_things": [],
  "issues": [],
  "suggestions": [],
  "verdict": "Ship It | Almost There | Skip It"
}
```

---

## 🎨 FRONTEND (HTML + Tailwind)

### Pages
1. Landing Page – Extraordinary UI/UX
2. Analyze Repo Page - repo input  
2. Loading State – progress messages  (using agent1, completed agent1, agent2, completed agent2, ...)
3. Result View – verdict, roast, feedback  

---

## 🎯 GOAL
Encourage builders to ship better projects, learn best practices, and grow — with honesty and humor.