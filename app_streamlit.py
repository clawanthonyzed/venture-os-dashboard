"""
Venture OS v10.0 — Streamlit HQ Dashboard
🦞 Idea Lobster | Sydney Server | Port 8501

Features:
- 54 project tabs with manager profiles
- OpenAI-powered manager chat per project
- Ollama worker dispatch for bulk drafting
- Asset shelf with download buttons
- Roadblock toggle with filesystem writes
- Dark mode Apple-inspired UI
"""

import streamlit as st
import os
import json
import glob
import requests
from datetime import datetime
from pathlib import Path

# --- Config ---
WORKSPACE = "/home/node/.openclaw/workspace"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://172.17.0.1:11434")

# --- Manager Registry ---
MANAGERS = {
    "venture-os-dashboard": ("Idea Lobster", "🦞", "CEO Architect", "#ff453a"),
    "bloom-and-bub": ("Rosa", "🌹", "Brand Director", "#ff375f"),
    "the-footnote": ("Archie", "📜", "History Producer", "#bf5af2"),
    "boomer-and-roo": ("Bazza", "🦘", "Animation Director", "#ff9f0a"),
    "zara-marin": ("Zara", "💪", "Fitness Brand Lead", "#30d158"),
    "lena-oakes": ("Lena", "🌿", "Doula Content Lead", "#64d2ff"),
    "lofi-engine": ("Vinyl", "🎵", "Music Producer", "#bf5af2"),
    "faceless-channels": ("Ghost", "👻", "Channel Director", "#a1a1a6"),
    "fireplace-videos": ("Ember", "🔥", "Ambience Producer", "#ff9f0a"),
    "fireplace-channel": ("Ember", "🔥", "Ambience Channel", "#ff9f0a"),
    "boring-history-videos": ("Dusty", "📚", "History Scripter", "#8e8e93"),
    "boring-history-channel": ("Dusty", "📚", "History Channel", "#8e8e93"),
    "heartfelt-stories-channel": ("Pearl", "💎", "Stories Producer", "#ff375f"),
    "heartfelt-social": ("Pearl", "💎", "Social Stories", "#ff375f"),
    "bible-history-channel": ("Moses", "⛪", "Faith Content", "#ffd60a"),
    "scroll-and-stone": ("Moses", "⛪", "Bible Lore", "#ffd60a"),
    "mealplan-cart": ("Chef", "👨‍🍳", "Meal Planner", "#30d158"),
    "dva-navigator": ("Sarge", "🎖️", "Veteran Services", "#2997ff"),
    "studymate-ai": ("Tutor", "🎓", "Education Lead", "#2997ff"),
    "prediction-pulse-saas": ("Oracle", "🔮", "Predictions SaaS", "#bf5af2"),
    "polymarket-kalshi-tracker": ("Oracle", "🔮", "Arbitrage Tracker", "#bf5af2"),
    "polymarket-tracker": ("Oracle", "🔮", "Market Signals", "#bf5af2"),
    "plastics-scanner": ("Scout", "🔍", "Product Scanner", "#30d158"),
    "red-pill-ai": ("Neo", "💊", "AI Influencer", "#ff453a"),
    "mens-improvement": ("Titan", "🏛️", "Self-Improvement", "#2997ff"),
    "ai-chat-character": ("Mimic", "🎭", "Character AI", "#ff375f"),
    "ai-characters": ("Mimic", "🎭", "Character Platform", "#ff375f"),
    "ai-mentor": ("Sage", "🧙", "Mentoring AI", "#bf5af2"),
    "ai-mentoring": ("Sage", "🧙", "Mentoring+Products", "#bf5af2"),
    "affiliate-ai-model": ("Cash", "💰", "Affiliate AI", "#30d158"),
    "affiliate-engine": ("Cash", "💰", "Affiliate Engine", "#30d158"),
    "faceless-affiliate-reels": ("Cash", "💰", "Affiliate Reels", "#30d158"),
    "ai-doula-influencer": ("Lena", "🌿", "Doula Influencer", "#64d2ff"),
    "lofi-spotify-engine": ("Vinyl", "🎵", "Spotify Pipeline", "#bf5af2"),
    "lofi-spotify": ("Vinyl", "🎵", "Spotify Distro", "#bf5af2"),
    "domain-ai-flipping": ("Flipper", "🐬", "Domain Trader", "#64d2ff"),
    "domain-flipper": ("Flipper", "🐬", "Domain Hunter", "#64d2ff"),
    "custom-sandals": ("Sole", "👡", "Sandal E-com", "#ff9f0a"),
    "custom-thongs": ("Sole", "👡", "Thong E-com", "#ff9f0a"),
    "maternity-aid-ecom": ("Rosa", "🌹", "Maternity E-com", "#ff375f"),
    "maternity-store": ("Rosa", "🌹", "Maternity Store", "#ff375f"),
    "trending-topic-clothing": ("Drip", "👕", "Trending Apparel", "#2997ff"),
    "trending-apparel": ("Drip", "👕", "Fashion Brand", "#2997ff"),
    "digital-print-shop": ("Pixel", "🖼️", "Print Shop", "#ff9f0a"),
    "digital-prints": ("Pixel", "🖼️", "Print Storefront", "#ff9f0a"),
    "handwritten-books": ("Quill", "✒️", "Custom Books", "#bf5af2"),
    "custom-handwritten-book": ("Quill", "✒️", "Handwriting Books", "#bf5af2"),
    "niche-digital-products": ("Maven", "📦", "Niche Products", "#30d158"),
    "amazon-resell-ops": ("Freight", "📦", "Amazon FBA", "#ff9f0a"),
    "amazon-reseller": ("Freight", "📦", "Amazon Automation", "#ff9f0a"),
    "openclaw-reskins": ("Forge", "🔨", "Agent Reskins", "#a1a1a6"),
    "open-agents": ("Forge", "🔨", "Agent Logic Sales", "#a1a1a6"),
    "security-audit-tool": ("Shield", "🛡️", "Security Ops", "#ff453a"),
    "cudan-studio": ("Idea Lobster", "🦞", "Studio Ops", "#ff453a"),
}

def get_manager(repo):
    return MANAGERS.get(repo, ("Recruit", "🆕", "Unassigned", "#8e8e93"))


def get_projects():
    """Scan workspace for project directories."""
    projects = []
    for d in sorted(os.listdir(WORKSPACE)):
        full = os.path.join(WORKSPACE, d)
        if os.path.isdir(full) and not d.startswith('.') and d not in ('node_modules', 'skills', 'memory'):
            files = [f for f in os.listdir(full) if not f.startswith('.') and f != 'node_modules' and f != '.git']
            has_v1 = 'VERSION-1.md' in files
            has_v2 = any(f.startswith('VERSION-2') for f in files)
            mgr = get_manager(d)
            projects.append({
                'name': d,
                'path': full,
                'files': files,
                'has_v1': has_v1,
                'has_v2': has_v2,
                'manager': mgr,
                'status': 'v2-ready' if has_v2 else 'v1-ready' if has_v1 else 'pending',
            })
    return projects


def chat_openai(message, project_name, history):
    """Send chat to OpenAI with project context."""
    if not OPENAI_API_KEY:
        return "⚠️ OPENAI_API_KEY not set. Add it to your environment."
    
    mgr = get_manager(project_name)
    system = f"""You are {mgr[0]} {mgr[1]}, the {mgr[2]} for the project '{project_name}' in Anthony's $0 startup conglomerate.
You are managed by Idea Lobster 🦞 (the CEO Architect).
Be concise, actionable, and direct. No fluff. Reference specific files in the project when relevant.
"""
    # Add project file context
    proj_path = os.path.join(WORKSPACE, project_name)
    for fname in ['VERSION-1.md', 'README.md', 'GOALS.md']:
        fpath = os.path.join(proj_path, fname)
        if os.path.exists(fpath):
            content = open(fpath).read()[:2000]
            system += f"\n[{fname}]:\n{content}\n"

    messages = [{"role": "system", "content": system}]
    for h in history[-10:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})

    try:
        import openai
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
        )
        reply = resp.choices[0].message.content
        # Log to project
        log_path = os.path.join(proj_path, "CHAT-LOG.md")
        with open(log_path, "a") as f:
            f.write(f"\n## {datetime.now().isoformat()}\n**You:** {message}\n**{mgr[0]}:** {reply}\n")
        return reply
    except Exception as e:
        return f"❌ OpenAI error: {str(e)}"


def draft_with_ollama(prompt, project_name):
    """Use local Ollama for free drafting."""
    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={"model": "llama3.2:3b", "prompt": prompt, "stream": False},
            timeout=120,
        )
        if resp.status_code == 200:
            result = resp.json().get("response", "")
            # Save draft
            draft_path = os.path.join(WORKSPACE, project_name, f"DRAFT-{datetime.now().strftime('%H%M')}.md")
            with open(draft_path, "w") as f:
                f.write(f"# Draft — {project_name}\n_Generated by Ollama llama3.2:3b at {datetime.now().isoformat()}_\n\n{result}")
            return result, draft_path
        return f"Ollama error: {resp.status_code}", None
    except Exception as e:
        return f"Ollama error: {str(e)}", None


# --- Page Config ---
st.set_page_config(
    page_title="Venture OS v10.0 — HQ",
    page_icon="🦞",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Dark Theme CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp { background-color: #000000; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #080808; border-right: 1px solid #1a1a1a; }
    [data-testid="stSidebar"] .stMarkdown h1, 
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 { color: #f5f5f7; }
    
    .stMarkdown h1 { color: #f5f5f7; font-weight: 700; letter-spacing: -0.5px; }
    .stMarkdown h2 { color: #f5f5f7; font-weight: 600; }
    .stMarkdown h3 { color: #a1a1a6; font-weight: 500; }
    .stMarkdown p, .stMarkdown li { color: #d1d1d6; }
    
    .stat-card {
        background: #0f0f0f;
        border: 1px solid #1a1a1a;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
    }
    .stat-value { font-size: 32px; font-weight: 700; color: #f5f5f7; }
    .stat-label { font-size: 11px; color: #6e6e73; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 4px; }
    
    .manager-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
    }
    
    .status-active { background: rgba(48,209,88,0.15); color: #30d158; }
    .status-init { background: rgba(41,151,255,0.15); color: #2997ff; }
    .status-pending { background: rgba(142,142,147,0.15); color: #8e8e93; }
    
    div[data-testid="stChatMessage"] { background: #0f0f0f; border-radius: 12px; }
    .stDownloadButton button { 
        background: #1c1c1e !important; 
        border: 1px solid #2a2a2a !important; 
        color: #2997ff !important;
        border-radius: 8px !important;
    }
    .stDownloadButton button:hover { border-color: #2997ff !important; }
    
    .stCheckbox label { color: #d1d1d6 !important; }
    
    div[data-testid="stMetric"] { background: #0f0f0f; border: 1px solid #1a1a1a; border-radius: 12px; padding: 16px; }
    div[data-testid="stMetric"] label { color: #6e6e73 !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #f5f5f7 !important; }
</style>
""", unsafe_allow_html=True)

# --- State Init ---
if "chat_histories" not in st.session_state:
    st.session_state.chat_histories = {}

# --- Load Projects ---
projects = get_projects()
project_names = [p['name'] for p in projects]
project_map = {p['name']: p for p in projects}

# --- Sidebar ---
with st.sidebar:
    st.markdown("# 🦞 Venture OS v10.0")
    st.markdown(f"<span style='color:#30d158;font-size:12px'>● Sydney Bridge Online</span> | <span style='color:#6e6e73;font-size:12px'>{len(projects)} projects</span>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Navigation
    nav = st.radio(
        "Navigation",
        ["🏠 HQ Overview", "🏛️ Manager Atrium", "🚨 Roadblocks", "⚡ Ollama Worker"] + [f"{get_manager(n)[1]} {n}" for n in project_names],
        label_visibility="collapsed",
    )

# --- Main Content ---
if nav == "🏠 HQ Overview":
    st.markdown("# 🦞 HQ Overview")
    
    # Stats row
    c1, c2, c3, c4 = st.columns(4)
    v2_count = sum(1 for p in projects if p['has_v2'])
    v1_count = sum(1 for p in projects if p['has_v1'])
    total_files = sum(len(p['files']) for p in projects)
    
    c1.metric("Total Projects", len(projects))
    c2.metric("V2 Assets Ready", v2_count)
    c3.metric("V1 Specs Done", v1_count)
    c4.metric("Total Files", total_files)
    
    st.markdown("---")
    
    # Project grid
    st.markdown("### All Projects")
    cols = st.columns(3)
    for i, proj in enumerate(projects):
        mgr = proj['manager']
        status_class = "status-active" if proj['has_v2'] else "status-init" if proj['has_v1'] else "status-pending"
        status_text = "V2 Ready" if proj['has_v2'] else "V1 Ready" if proj['has_v1'] else "Pending"
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#0f0f0f;border:1px solid #1a1a1a;border-radius:14px;padding:16px;margin-bottom:10px">
                <div style="font-size:24px;margin-bottom:4px">{mgr[1]}</div>
                <div style="font-size:14px;font-weight:600;color:#f5f5f7">{proj['name']}</div>
                <div style="font-size:11px;color:#6e6e73">{mgr[0]} — {mgr[2]}</div>
                <div style="margin-top:8px">
                    <span class="manager-badge {status_class}">{status_text}</span>
                    <span style="font-size:10px;color:#6e6e73;margin-left:8px">{len(proj['files'])} files</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

elif nav == "🏛️ Manager Atrium":
    st.markdown("# 🏛️ Manager Atrium")
    st.markdown("Live feed from all 54 project managers.")
    
    # Show recent chat logs across all projects
    logs = []
    for proj in projects:
        log_path = os.path.join(proj['path'], 'CHAT-LOG.md')
        if os.path.exists(log_path):
            content = open(log_path).read()
            mgr = proj['manager']
            logs.append((proj['name'], mgr, content[-500:]))
    
    if logs:
        for name, mgr, content in logs:
            st.markdown(f"**{mgr[1]} {mgr[0]}** ({name})")
            st.markdown(content)
            st.markdown("---")
    else:
        st.info("No manager activity yet. Chat with a project to see updates here.")

elif nav == "🚨 Roadblocks":
    st.markdown("# 🚨 Active Roadblocks")
    
    roadblocks = [
        ("bloom-and-bub", "Paste Gumroad product copy", True),
        ("venture-os-dashboard", "Enable Google Generative AI API", True),
        ("faceless-channels", "Fix ElevenLabs API key", True),
        ("bloom-and-bub", "Create Instagram @bloomandbubbaby", False),
        ("the-footnote", "Create YouTube channel", False),
        ("fireplace-channel", "Create Ambient Escapes YouTube channel", False),
        ("red-pill-ai", "Create X/Twitter @redpillai_agent + API keys", False),
    ]
    
    for i, (project, task, urgent) in enumerate(roadblocks):
        col1, col2 = st.columns([0.05, 0.95])
        with col1:
            done = st.checkbox("", key=f"rb_{i}")
        with col2:
            prefix = "🔥 " if urgent else ""
            style = "text-decoration:line-through;color:#6e6e73" if done else "color:#f5f5f7" if urgent else "color:#d1d1d6"
            st.markdown(f"<span style='{style}'>{prefix}{task}</span> <span style='font-size:10px;color:#6e6e73'>({project})</span>", unsafe_allow_html=True)
        
        if done:
            # Write to ROADBLOCKS.md
            rb_path = os.path.join(WORKSPACE, project, "ROADBLOCKS.md")
            if not os.path.exists(rb_path):
                with open(rb_path, "w") as f:
                    f.write(f"# {project} — Roadblocks\n\n")
            content = open(rb_path).read()
            if f"- [ ] {task}" in content:
                content = content.replace(f"- [ ] {task}", f"- [x] {task} ✅ (completed {datetime.now().strftime('%Y-%m-%d')})")
                with open(rb_path, "w") as f:
                    f.write(content)
            elif f"[x] {task}" not in content:
                with open(rb_path, "a") as f:
                    f.write(f"\n- [x] {task} ✅ (completed {datetime.now().strftime('%Y-%m-%d')})\n")

elif nav == "⚡ Ollama Worker":
    st.markdown("# ⚡ Ollama Worker — Free Drafting")
    st.markdown(f"Connected to `{OLLAMA_HOST}` (llama3.2:3b)")
    
    # Check Ollama status
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        models = r.json().get("models", [])
        st.success(f"✅ Ollama online — {len(models)} model(s): {', '.join(m['name'] for m in models)}")
    except:
        st.error("❌ Ollama not responding")
    
    st.markdown("---")
    
    target_project = st.selectbox("Target Project", project_names)
    prompt = st.text_area("Draft Prompt", placeholder="e.g., Write a product description for the Birth Plan PDF...")
    
    if st.button("🚀 Generate Draft ($0)", type="primary"):
        if prompt:
            with st.spinner(f"Ollama drafting for {target_project}..."):
                result, draft_path = draft_with_ollama(prompt, target_project)
                st.markdown("### Draft Output")
                st.markdown(result)
                if draft_path:
                    st.success(f"Saved to: {draft_path}")

else:
    # Project detail view
    project_name = nav.split(" ", 1)[1] if " " in nav else nav
    if project_name in project_map:
        proj = project_map[project_name]
        mgr = proj['manager']
        
        st.markdown(f"# {mgr[1]} {project_name}")
        st.markdown(f"**Manager:** {mgr[0]} — {mgr[2]}")
        
        # Status metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Status", proj['status'].upper())
        c2.metric("Files", len(proj['files']))
        c3.metric("Manager", mgr[0])
        
        # Tabs: Chat | Assets | Worker
        tab_chat, tab_assets, tab_worker = st.tabs(["💬 Manager Chat", "📁 Asset Shelf", "⚡ Ollama Worker"])
        
        with tab_chat:
            st.markdown(f"### Chat with {mgr[0]} {mgr[1]}")
            st.markdown(f"<span style='font-size:11px;color:#6e6e73'>Powered by OpenAI gpt-4o-mini | Logged to {project_name}/CHAT-LOG.md</span>", unsafe_allow_html=True)
            
            # Chat history
            if project_name not in st.session_state.chat_histories:
                st.session_state.chat_histories[project_name] = []
            
            history = st.session_state.chat_histories[project_name]
            
            for msg in history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            if prompt := st.chat_input(f"Talk to {mgr[0]}..."):
                history.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                with st.chat_message("assistant"):
                    with st.spinner(f"{mgr[0]} is thinking..."):
                        reply = chat_openai(prompt, project_name, history)
                        st.markdown(reply)
                        history.append({"role": "assistant", "content": reply})
        
        with tab_assets:
            st.markdown("### 📁 Asset Shelf")
            st.markdown(f"<span style='font-size:11px;color:#6e6e73'>Files in {WORKSPACE}/{project_name}/</span>", unsafe_allow_html=True)
            
            if not proj['files']:
                st.info("No files yet. Use the chat or Ollama worker to generate assets.")
            else:
                for fname in sorted(proj['files']):
                    fpath = os.path.join(proj['path'], fname)
                    if os.path.isfile(fpath):
                        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
                        with col1:
                            icon = "📄" if fname.endswith('.md') else "📦" if fname.endswith('.json') else "🔧" if fname.endswith('.py') else "📎"
                            st.markdown(f"{icon} **{fname}**")
                        with col2:
                            size = os.path.getsize(fpath)
                            st.markdown(f"<span style='color:#6e6e73;font-size:11px'>{size/1024:.1f} KB</span>", unsafe_allow_html=True)
                        with col3:
                            with open(fpath, "r", errors="replace") as f:
                                content = f.read()
                            st.download_button(
                                "⬇️ Download",
                                content,
                                file_name=fname,
                                key=f"dl_{project_name}_{fname}",
                            )
                        
                        # Preview on click
                        if fname.endswith('.md'):
                            with st.expander(f"Preview {fname}"):
                                st.markdown(content[:3000])
        
        with tab_worker:
            st.markdown(f"### ⚡ Draft with Ollama for {project_name}")
            st.markdown("<span style='font-size:11px;color:#6e6e73'>Free generation via llama3.2:3b — $0 cost</span>", unsafe_allow_html=True)
            
            worker_prompt = st.text_area("Prompt", placeholder=f"e.g., Draft a product description for {project_name}...", key=f"worker_{project_name}")
            if st.button("Generate Draft", key=f"gen_{project_name}", type="primary"):
                if worker_prompt:
                    with st.spinner("Ollama working..."):
                        result, draft_path = draft_with_ollama(worker_prompt, project_name)
                        st.markdown(result)
                        if draft_path:
                            st.success(f"Saved: {draft_path}")
                            st.rerun()
