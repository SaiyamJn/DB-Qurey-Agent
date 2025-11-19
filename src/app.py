import streamlit as st
import pandas as pd
from config import PAGE_TITLE, PAGE_LAYOUT, GEMINI_API_KEY
from data_handler import DataHandler
from ui_components import (
    apply_dark_theme, 
    render_header, 
    render_data_source_selector,
    render_csv_uploader,
    render_database_form,
    render_table_selector,
    render_data_source_info
)
from query_processor import QueryProcessor
from visualization import Visualizer

# -------------------------
# Configuration
# -------------------------
st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)
apply_dark_theme()

# -------------------------
# Session State Initialization
# -------------------------
if "df" not in st.session_state:
    st.session_state.df = None
if "schema" not in st.session_state:
    st.session_state.schema = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_model" not in st.session_state:
    from config import MODEL_PRIORITY
    st.session_state.current_model = MODEL_PRIORITY[0]
if "data_source_type" not in st.session_state:
    st.session_state.data_source_type = None
if "db_connection" not in st.session_state:
    st.session_state.db_connection = None
if "db_type" not in st.session_state:
    st.session_state.db_type = None
if "current_table" not in st.session_state:
    st.session_state.current_table = None
if "available_tables" not in st.session_state:
    st.session_state.available_tables = []

# -------------------------
# Initialize Processor
# -------------------------
query_processor = QueryProcessor()

# -------------------------
# UI: Header
# -------------------------
render_header()

# API Key Status
if GEMINI_API_KEY:
    st.sidebar.success("✓ API key loaded")
else:
    st.sidebar.error("✗ GEMINI_API_KEY not found in .env file")

st.sidebar.markdown(f"**Model:** {st.session_state.current_model}")
st.sidebar.markdown("---")

# -------------------------
# Data Source Selection
# -------------------------
source_type = render_data_source_selector()

# Handle CSV Upload
if source_type == "CSV File":
    uploaded_file = render_csv_uploader()
    
    if uploaded_file:
        df, error_messages = DataHandler.load_csv(uploaded_file)
        
        if df is not None and not df.empty:
            st.session_state.df = df
            st.session_state.data_source_type = "csv"
            st.session_state.current_table = uploaded_file.name
            st.session_state.schema = DataHandler.generate_schema(df, "csv", uploaded_file.name)
            
            rows, cols = df.shape
            st.sidebar.success(f"✓ Loaded {rows:,} rows × {cols} cols")
            
            with st.sidebar.expander("Schema"):
                st.text(st.session_state.schema)
        else:
            st.sidebar.error("Failed to read CSV")
            with st.sidebar.expander("Error Details"):
                for msg in error_messages:
                    st.text(msg)

# Handle Database Connection
elif source_type == "Database Connection":
    db_type, connection_params, test_btn, connect_btn = render_database_form()
    
    # Test Connection
    if test_btn:
        with st.spinner("Testing connection..."):
            success, message = DataHandler.test_connection(db_type, connection_params)
            if success:
                st.sidebar.success(message)
            else:
                st.sidebar.error(message)
    
    # Connect to Database
    if connect_btn:
        with st.spinner("Connecting to database..."):
            conn, _, error = DataHandler.load_from_database(db_type, connection_params)
            
            if error:
                st.sidebar.error(error)
            else:
                st.session_state.db_connection = conn
                st.session_state.db_type = db_type
                st.session_state.data_source_type = "database"
                
                # Get available tables
                tables = DataHandler.get_tables(conn, db_type)
                st.session_state.available_tables = tables
                
                if tables:
                    st.sidebar.success(f"✓ Connected! Found {len(tables)} tables")
                else:
                    st.sidebar.warning("Connected but no tables found")
    
    # Table Selection
    if st.session_state.db_connection and st.session_state.available_tables:
        result = render_table_selector(st.session_state.available_tables, st.session_state.db_type)
        
        if result and result[0]:
            selected_table, limit = result
            with st.spinner(f"Loading {selected_table}..."):
                df, error = DataHandler.load_table(
                    st.session_state.db_connection, 
                    selected_table, 
                    st.session_state.db_type,
                    limit
                )
                
                if error:
                    st.sidebar.error(error)
                else:
                    st.session_state.df = df
                    st.session_state.current_table = selected_table
                    st.session_state.schema = DataHandler.generate_schema(
                        df, 
                        st.session_state.db_type, 
                        selected_table
                    )
                    
                    rows, cols = df.shape
                    st.sidebar.success(f"✓ Loaded {rows:,} rows × {cols} cols")
                    
                    with st.sidebar.expander("Schema"):
                        st.text(st.session_state.schema)

# Display Data Source Info
if st.session_state.df is not None:
    render_data_source_info(
        st.session_state.data_source_type,
        st.session_state.current_table,
        {"db_type": st.session_state.db_type} if st.session_state.data_source_type == "database" else None
    )

# Clear Data Button
if st.session_state.df is not None:
    if st.sidebar.button("Clear Data & Reset"):
        st.session_state.df = None
        st.session_state.schema = ""
        st.session_state.messages = []
        st.session_state.data_source_type = None
        st.session_state.current_table = None
        
        # Close database connections properly
        if st.session_state.db_connection:
            try:
                if st.session_state.db_type == "MongoDB":
                    st.session_state.db_connection['client'].close()
                elif st.session_state.db_type == "Redis":
                    st.session_state.db_connection['client'].close()
                elif st.session_state.db_type == "Cassandra":
                    st.session_state.db_connection['cluster'].shutdown()
                elif st.session_state.db_type in ["PostgreSQL", "MySQL", "SQLite", "SQL Server"]:
                    st.session_state.db_connection.close()
            except:
                pass
        
        st.session_state.db_connection = None
        st.session_state.db_type = None
        st.session_state.available_tables = []
        st.rerun()

# -------------------------
# Main Content
# -------------------------
if st.session_state.df is None:
    st.info("Please select a data source from the sidebar to get started")
else:
    tab1, tab2, tab3 = st.tabs(["Chat", "Dashboard", "Analytics"])
    
    # -------------------------
    # TAB 1: CHAT
    # -------------------------
    with tab1:
        # Display chat history
        chat_container = st.container()
        with chat_container:
            if st.session_state.messages:
                for idx, msg in enumerate(st.session_state.messages):
                    if msg["role"] == "user":
                        col1, col2 = st.columns([6, 1])
                        with col1:
                            st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
                        with col2:
                            if st.button("Delete", key=f"del_user_{idx}", help="Delete this message"):
                                if idx + 1 < len(st.session_state.messages):
                                    del st.session_state.messages[idx:idx+2]
                                else:
                                    del st.session_state.messages[idx]
                                st.rerun()
                    else:
                        content = msg["content"]
                        if isinstance(content, dict):
                            if content.get("type") == "dataframe":
                                st.markdown('<div class="bot-message">Query Result:</div>', unsafe_allow_html=True)
                                st.dataframe(content["content"], use_container_width=True)
                                if content.get("explain"):
                                    st.markdown(f'<div class="bot-message">{content["explain"]}</div>', unsafe_allow_html=True)
                                if content.get("code"):
                                    with st.expander("View Code"):
                                        st.code(content["code"])
                            elif content.get("type") == "error":
                                st.markdown(f'<div class="bot-message">Error: {content["content"]}</div>', unsafe_allow_html=True)
                            elif content.get("type") == "text":
                                st.markdown(f'<div class="bot-message">{content["content"]}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="bot-message">{content}</div>', unsafe_allow_html=True)
            else:
                st.info("""**Ask questions about your data:**
                
Examples:
- Show me the first 10 rows
- What's the average of column X?
- Filter rows where sales > 1000
- Group by category and count items
- Show unique values in the status column
                """)

        # Chat input
        st.markdown("---")
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input("Ask a question...", key="user_input", label_visibility="collapsed", 
                                      placeholder="e.g., Show top 5 rows sorted by revenue")
        with col2:
            send_button = st.button("Send", use_container_width=True, type="primary")

        if send_button and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            with st.spinner("Thinking..."):
                response = query_processor.process_query(
                    user_input,
                    st.session_state.df,
                    st.session_state.schema,
                    st.session_state.current_model
                )
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
        
        if st.session_state.messages:
            if st.button("Clear Chat"):
                st.session_state.messages = []
                st.rerun()
    
    # -------------------------
    # TAB 2: DASHBOARD
    # -------------------------
    with tab2:
        df = st.session_state.df
        visualizer = Visualizer(df)
        
        st.markdown("### Data Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{len(df):,}")
        with col2:
            st.metric("Total Columns", len(df.columns))
        with col3:
            missing = df.isnull().sum().sum()
            st.metric("Missing Values", f"{missing:,}")
        with col4:
            duplicates = df.duplicated().sum()
            st.metric("Duplicate Rows", f"{duplicates:,}")
        
        st.markdown("---")
        
        st.markdown("### Data Preview")
        from config import PREVIEW_ROWS_DEFAULT, PREVIEW_ROWS_MIN, PREVIEW_ROWS_MAX
        preview_rows = st.slider("Rows to display", PREVIEW_ROWS_MIN, PREVIEW_ROWS_MAX, PREVIEW_ROWS_DEFAULT)
        st.dataframe(df.head(preview_rows), use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("### Chart Builder")
        visualizer.render_chart_builder()
        
        st.markdown("---")
        
        st.markdown("### Export Data")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download as CSV",
            data=csv,
            file_name=f"datasense_export_{st.session_state.current_table or 'data'}.csv",
            mime="text/csv"
        )
    
    # -------------------------
    # TAB 3: ANALYTICS
    # -------------------------
    with tab3:
        df = st.session_state.df
        visualizer = Visualizer(df)
        
        st.markdown("### Statistical Summary")
        st.dataframe(df.describe(), use_container_width=True)
        
        st.markdown("---")
        
        st.markdown("### Missing Values Analysis")
        visualizer.render_missing_values_analysis()
        
        st.markdown("---")
        
        st.markdown("### Correlation Analysis")
        visualizer.render_correlation_analysis()
        
        st.markdown("---")
        
        st.markdown("### Distribution Analysis")
        visualizer.render_distribution_analysis()
        
        st.markdown("---")
        
        st.markdown("### AI-Generated Insights")
        if st.button("Generate Insights"):
            if not GEMINI_API_KEY:
                st.error("API key not configured")
            else:
                with st.spinner(" Analyzing data..."):
                    insights = query_processor.generate_insights(df, st.session_state.schema)
                    st.markdown(f'<div class="bot-message">{insights}</div>', unsafe_allow_html=True)