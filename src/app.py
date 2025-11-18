import streamlit as st
import pandas as pd

# Import custom modules
from config import GEMINI_API_KEY, MODEL_PRIORITY, DARK_THEME_CSS
from data_handler import load_csv_file, generate_schema
from query_processor import process_query
from gemini_api import call_gemini_auto
from ui_components import (
    render_header, render_sidebar, render_chat_tab, 
    render_dashboard_tab, render_analytics_tab
)


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "df" not in st.session_state:
        st.session_state.df = None
    if "schema" not in st.session_state:
        st.session_state.schema = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_model" not in st.session_state:
        st.session_state.current_model = MODEL_PRIORITY[0]


def handle_file_upload(uploaded_file):
    """Handle CSV file upload"""
    df, error_messages = load_csv_file(uploaded_file)
    
    if df is not None and not df.empty:
        st.session_state.df = df
        st.session_state.schema = generate_schema(df)
        rows, cols = df.shape
        st.sidebar.success(f"Loaded {rows:,} rows × {cols} cols")
        
        with st.sidebar.expander("Schema"):
            st.text(st.session_state.schema)
    else:
        st.sidebar.error("Failed to read CSV")
        with st.sidebar.expander("Error Details"):
            for msg in error_messages:
                st.text(msg)


def clear_dataset():
    """Clear current dataset and reset state"""
    st.session_state.df = None
    st.session_state.schema = ""
    st.session_state.messages = []


def main():
    """Main application entry point"""
    # Configuration
    st.set_page_config(page_title="DataSense", layout="wide")
    st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    uploaded_file = render_sidebar(GEMINI_API_KEY, st.session_state.current_model)
    
    # Handle file upload
    if uploaded_file:
        handle_file_upload(uploaded_file)
    
    # Clear dataset button
    if st.session_state.df is not None:
        if st.sidebar.button("Clear Dataset"):
            clear_dataset()
            st.rerun()
    
    # Main content
    if st.session_state.df is None:
        st.info("Please upload a CSV file from the sidebar to get started")
    else:
        tab1, tab2, tab3 = st.tabs(["Chat", "Dashboard", "Analytics"])
        
        with tab1:
            render_chat_tab(
                st.session_state.df, 
                st.session_state.schema,
                st.session_state.messages
            )
        
        with tab2:
            render_dashboard_tab(st.session_state.df)
        
        with tab3:
            render_analytics_tab(
                st.session_state.df, 
                st.session_state.schema,
                GEMINI_API_KEY
            )


if __name__ == "__main__":
    main()