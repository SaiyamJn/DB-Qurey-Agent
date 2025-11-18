import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_PRIORITY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
]

# Theme Configuration
DARK_THEME_CSS = """
    <style>
    :root {
        --bg: #1a1a1a;
        --card: #2d2d2d;
        --muted: #a0a0a0;
        --accent: #ff6b35;
        --border: rgba(255,255,255,0.1);
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg);
        color: #e0e0e0;
    }
    
    .stApp {
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    .main-title {
        font-size: 64px;
        font-weight: 600;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #ffffff;
        margin-bottom: 4px;
        text-align: center;
        letter-spacing: 0.5px;
    }
    
    .subtitle {
        color: var(--muted);
        font-size: 20px;
        margin-bottom: 32px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-align: center;
    }
    
    .user-message {
        background: var(--card);
        color: #ffffff;
        padding: 10px 14px;
        border-radius: 6px;
        margin: 6px 0;
        text-align: right;
        border-left: 3px solid var(--accent);
    }
    
    .bot-message {
        background: var(--card);
        color: #e0e0e0;
        padding: 10px 14px;
        border-radius: 6px;
        margin: 6px 0;
        border: 1px solid var(--border);
    }
    
    .stButton>button {
        background: var(--accent);
        border: none;
        color: #ffffff;
        padding: 6px 14px;
        border-radius: 4px;
        transition: all 0.2s;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background: #ff8555;
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
    }
    
    .stTextInput>div>div>input {
        background: var(--card);
        border: 1px solid var(--border);
        color: #e0e0e0;
        border-radius: 4px;
    }
    
    .stDataFrame {
        background: var(--card);
        border-radius: 4px;
    }
    
    [data-testid="stSidebar"] {
        background: var(--card);
        border-right: 1px solid var(--border);
    }
    
    .metric-card {
        background: var(--card);
        padding: 12px;
        border-radius: 4px;
        border: 1px solid var(--border);
    }
    
    .delete-btn {
        background: transparent;
        border: 1px solid #666;
        color: #999;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 11px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .delete-btn:hover {
        border-color: #ff4444;
        color: #ff4444;
    }
    
    .chat-message-container {
        position: relative;
        margin: 6px 0;
    }
    
    .message-actions {
        display: inline-block;
        margin-left: 8px;
        opacity: 0.6;
    }
    
    .message-actions:hover {
        opacity: 1;
    }
    </style>
"""