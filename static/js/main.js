const loadingMessages = [
    "🔍 Agent 1: Scouting Repository Metadata...",
    "📂 Agent 1: analyzing folder structure...",
    "📜 Agent 2: Reading README (judging your grammar)...",
    "🐍 Agent 2: Checking language distribution...",
    "🧠 Senior Dev Agent: Formulating roasting strategy...",
    "⚖️ Senior Dev Agent: Writing final verdict..."
];

async function analyzeRepo() {
    const url = document.getElementById('repoUrl').value;
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    const loadingText = document.getElementById('loadingText');
    const scanLine = document.getElementById('scanLine');

    if (!url) {
        alert("Paste a URL first, rookie.");
        return;
    }

    // Reset UI
    resultsDiv.classList.add('hidden');
    loadingDiv.classList.remove('hidden');
    scanLine.style.display = 'block';
    
    // Simulate Agent Progress
    let msgIndex = 0;
    loadingText.innerText = loadingMessages[0];
    const interval = setInterval(() => {
        msgIndex = (msgIndex + 1) % loadingMessages.length;
        loadingText.innerText = loadingMessages[msgIndex];
    }, 1200);

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ repo_url: url })
        });

        const data = await response.json();
        
        clearInterval(interval);
        loadingDiv.classList.add('hidden');
        scanLine.style.display = 'none';

        if (response.ok) {
            renderResults(data);
        } else {
            alert(data.error || "Something broke. Probably your code.");
        }

    } catch (error) {
        clearInterval(interval);
        loadingDiv.classList.add('hidden');
        alert("Server error. Check console.");
    }
}

function renderResults(data) {
    const analysis = data.analysis;
    const resultsDiv = document.getElementById('results');
    
    // 1. Verdict Styling
    const verdictBanner = document.getElementById('verdictBanner');
    const verdictText = document.getElementById('verdictText');
    
    verdictText.innerText = analysis.verdict.toUpperCase();
    
    verdictBanner.className = "p-6 rounded-xl text-center border-2 shadow-lg transform transition hover:scale-105 ";
    
    if (analysis.verdict.includes("Ship")) {
        verdictBanner.classList.add("bg-green-900/30", "border-green-500", "text-green-400");
    } else if (analysis.verdict.includes("Almost")) {
        verdictBanner.classList.add("bg-yellow-900/30", "border-yellow-500", "text-yellow-400");
    } else {
        verdictBanner.classList.add("bg-red-900/30", "border-red-500", "text-red-400");
    }

    // 2. Populate Lists
    populateList('roastList', analysis.roast);
    populateList('goodList', analysis.good_things);
    populateList('fixList', analysis.suggestions); // Merging suggestions + issues for simplicity

    resultsDiv.classList.remove('hidden');
}

function populateList(elementId, items) {
    const list = document.getElementById(elementId);
    list.innerHTML = "";
    items.forEach(item => {
        const li = document.createElement('li');
        li.innerText = item;
        list.appendChild(li);
    });
}