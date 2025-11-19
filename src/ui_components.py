import streamlit as st

def apply_dark_theme():
    """Apply minimal dark theme to Streamlit app"""
    st.markdown("""
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
        
        .data-source-indicator {
            background: var(--card);
            padding: 8px 12px;
            border-radius: 4px;
            border-left: 3px solid var(--accent);
            margin: 10px 0;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render application header"""
    st.markdown('<div class="main-title">DataSense</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI-powered database query agent with analytics & dashboards</div>', unsafe_allow_html=True)

def render_data_source_selector():
    """Render data source selection interface"""
    st.sidebar.header("Data Source")
    
    source_type = st.sidebar.radio(
        "Select data source type:",
        ["CSV File", "Database Connection"],
        help="Choose between uploading a CSV file or connecting to a database"
    )
    
    return source_type

def render_csv_uploader():
    """Render CSV file uploader"""
    return st.sidebar.file_uploader("Upload CSV", type=["csv"])

def render_database_form():
    """Render database connection form"""
    from config import SUPPORTED_DB_TYPES, DEFAULT_DB_TYPE, SUPPORTED_SQL_DB_TYPES, SUPPORTED_NOSQL_DB_TYPES
    
    with st.sidebar.expander("Database Connection", expanded=True):
        # Organize by SQL and NoSQL
        db_category = st.radio("Database Category", ["SQL", "NoSQL"])
        
        if db_category == "SQL":
            db_type = st.selectbox("Database Type", SUPPORTED_SQL_DB_TYPES, 
                                  index=SUPPORTED_SQL_DB_TYPES.index(DEFAULT_DB_TYPE))
        else:
            db_type = st.selectbox("Database Type", SUPPORTED_NOSQL_DB_TYPES)
        
        connection_params = {}
        
        if db_type == "SQLite":
            connection_params['database'] = st.text_input("Database Path", value="database.db")
        
        elif db_type == "MongoDB":
            connection_params['host'] = st.text_input("Host", value="localhost")
            connection_params['port'] = st.number_input("Port", value=27017, step=1)
            connection_params['database'] = st.text_input("Database Name")
            connection_params['user'] = st.text_input("Username (optional)")
            connection_params['password'] = st.text_input("Password (optional)", type="password")
        
        elif db_type == "Redis":
            connection_params['host'] = st.text_input("Host", value="localhost")
            connection_params['port'] = st.number_input("Port", value=6379, step=1)
            connection_params['database'] = st.number_input("Database Number", value=0, step=1, min_value=0)
            connection_params['password'] = st.text_input("Password (optional)", type="password")
        
        elif db_type == "Cassandra":
            connection_params['host'] = st.text_input("Host", value="localhost")
            connection_params['port'] = st.number_input("Port", value=9042, step=1)
            connection_params['keyspace'] = st.text_input("Keyspace (optional)")
            connection_params['user'] = st.text_input("Username (optional)")
            connection_params['password'] = st.text_input("Password (optional)", type="password")
        
        else:
            # SQL databases (PostgreSQL, MySQL, SQL Server)
            connection_params['host'] = st.text_input("Host", value="localhost")
            connection_params['port'] = st.number_input("Port", 
                value=5432 if db_type == "PostgreSQL" else 3306 if db_type == "MySQL" else 1433,
                step=1)
            connection_params['database'] = st.text_input("Database Name")
            connection_params['user'] = st.text_input("Username")
            connection_params['password'] = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            test_btn = st.button("Test Connection", use_container_width=True)
        with col2:
            connect_btn = st.button("Connect", use_container_width=True, type="primary")
        
        return db_type, connection_params, test_btn, connect_btn

def render_table_selector(tables, db_type):
    """Render table selector for database connections"""
    if not tables:
        st.sidebar.warning("No tables/collections found in database")
        return None
    
    with st.sidebar.expander("Select Table/Collection", expanded=True):
        label = "Available Collections" if db_type == "MongoDB" else \
                "Available Keys" if db_type == "Redis" else \
                "Available Tables"
        
        selected_table = st.selectbox(label, tables)
        
        # For Redis and large datasets, add limit option
        if db_type in ["Redis", "MongoDB", "Cassandra"]:
            limit = st.number_input("Max rows to load", value=1000, min_value=100, max_value=50000, step=100)
        else:
            limit = 10000
        
        load_table_btn = st.button("Load Data", use_container_width=True, type="primary")
        
        return (selected_table, limit) if load_table_btn else (None, limit)

def render_data_source_info(source_type, table_name=None, connection_info=None):
    """Render current data source information"""
    if source_type == "csv":
        info_text = f"**Data Source:** CSV File"
    else:
        info_text = f"**Data Source:** {connection_info.get('db_type', 'Database')}"
        if table_name:
            info_text += f" - Table: `{table_name}`"
    
    st.sidebar.markdown(f'<div class="data-source-indicator">{info_text}</div>', unsafe_allow_html=True)