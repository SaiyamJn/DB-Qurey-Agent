import streamlit as st
import pandas as pd
from query_processor import process_query
from gemini_api import call_gemini_auto
from visualization import (
    create_chart, create_missing_values_chart, 
    create_correlation_heatmap, create_distribution_plots,
    get_column_statistics, get_top_correlations
)


def render_header():
    """Render application header"""
    st.markdown('<div class="main-title">DataSense</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI-powered database query agent with analytics & dashboards</div>', 
                unsafe_allow_html=True)


def render_sidebar(api_key, current_model):
    """Render sidebar with API status and file upload"""
    if api_key:
        st.sidebar.success("API key loaded")
    else:
        st.sidebar.error("GEMINI_API_KEY not found in .env file")
    
    st.sidebar.markdown(f"**Model:** {current_model}")
    st.sidebar.markdown("---")
    
    st.sidebar.header("Data Source")
    return st.sidebar.file_uploader("Upload CSV", type=["csv"])


def render_chat_message(msg, idx):
    """Render a single chat message"""
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


def render_chat_tab(df, schema, messages):
    """Render chat interface tab"""
    # Display chat history
    chat_container = st.container()
    with chat_container:
        if messages:
            for idx, msg in enumerate(messages):
                render_chat_message(msg, idx)
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
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Process query
        with st.spinner("Thinking..."):
            model_used, response = process_query(user_input, df, schema)
            if model_used:
                st.session_state.current_model = model_used
        
        # Add bot response
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Clear chat button
    if messages:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()


def render_dashboard_tab(df):
    """Render dashboard tab with overview and charts"""
    st.markdown("### Data Overview")
    
    # Quick stats
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
    
    # Data preview
    st.markdown("### Data Preview")
    preview_rows = st.slider("Rows to display", 5, 100, 10)
    st.dataframe(df.head(preview_rows), use_container_width=True)
    
    st.markdown("---")
    
    # Chart builder
    st.markdown("### Chart Builder")
    
    cols = df.columns.tolist()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        chart_type = st.selectbox("Chart Type", ["Scatter", "Line", "Bar", "Histogram", "Box Plot"])
    with col2:
        x_col = st.selectbox("X-axis", cols, index=0)
    with col3:
        y_col = st.selectbox("Y-axis", cols, index=1 if len(cols) > 1 else 0)
    
    if st.button("Generate Chart"):
        try:
            fig = create_chart(df, chart_type, x_col, y_col)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error creating chart: {str(e)}")
    
    st.markdown("---")
    
    # Download data
    st.markdown("### Export Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="datasense_export.csv",
        mime="text/csv"
    )


def render_analytics_tab(df, schema, api_key):
    """Render analytics tab with statistical analysis"""
    st.markdown("### Statistical Summary")
    st.dataframe(df.describe(), use_container_width=True)
    
    st.markdown("---")
    
    # Missing values analysis
    st.markdown("### Missing Values Analysis")
    missing_df = pd.DataFrame({
        'Column': df.columns,
        'Missing Count': df.isnull().sum().values,
        'Missing %': (df.isnull().sum().values / len(df) * 100).round(2)
    })
    missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)
    
    if len(missing_df) > 0:
        st.dataframe(missing_df, use_container_width=True)
        fig = create_missing_values_chart(missing_df)
        st.pyplot(fig)
    else:
        st.success("No missing values found")
    
    st.markdown("---")
    
    # Correlation analysis
    numeric_df = df.select_dtypes(include=['number'])
    if len(numeric_df.columns) > 1:
        st.markdown("### Correlation Analysis")
        
        fig, corr_matrix = create_correlation_heatmap(numeric_df)
        st.pyplot(fig)
        
        st.markdown("#### Strongest Correlations")
        corr_df = get_top_correlations(corr_matrix)
        st.dataframe(corr_df, use_container_width=True)
    
    st.markdown("---")
    
    # Distribution analysis
    st.markdown("### Distribution Analysis")
    
    if len(numeric_df.columns) > 0:
        selected_col = st.selectbox("Select column to analyze", numeric_df.columns)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist, fig_box = create_distribution_plots(numeric_df, selected_col)
            st.pyplot(fig_hist)
        
        with col2:
            st.pyplot(fig_box)
        
        # Statistics
        st.markdown("#### Statistics")
        stats_df = get_column_statistics(numeric_df, selected_col)
        st.dataframe(stats_df, use_container_width=True)
    
    st.markdown("---")
    
    # AI Insights
    st.markdown("### AI-Generated Insights")
    if st.button("Generate Insights"):
        if not api_key:
            st.error("API key not configured")
        else:
            with st.spinner("Analyzing data..."):
                insights_prompt = f"""Analyze this dataset and provide 5-7 key insights in bullet points.

Dataset Info:
{schema}

Summary Statistics:
{df.describe().to_string()}

Provide insights about:
- Data quality and completeness
- Key patterns or trends
- Interesting findings
- Potential issues or outliers
- Recommendations for further analysis

Keep each insight concise (1-2 sentences)."""
                
                _, response = call_gemini_auto("You are a data analyst providing insights.", insights_prompt)
                st.markdown(f'<div class="bot-message">{response}</div>', unsafe_allow_html=True)