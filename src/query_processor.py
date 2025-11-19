import ast
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st
from gemini_api import call_gemini_auto

class QueryProcessor:
    """Process natural language queries and execute them on data"""
    
    @staticmethod
    def safe_eval(expr, df):
        """Safely evaluate pandas expressions"""
        ALLOWED_NAMES = {"df", "pd", "np"}
        
        try:
            tree = ast.parse(expr, mode="eval")
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id not in ALLOWED_NAMES:
                    raise ValueError(f"Unauthorized name: {node.id}")
            
            return eval(
                compile(tree, "<safe>", "eval"),
                {"__builtins__": {}},
                {"df": df, "pd": pd, "np": np}
            )
        except Exception as e:
            raise ValueError(f"Evaluation error: {str(e)}")
    
    def process_query(self, user_input, df, schema, current_model):
        """Process user query and return response"""
        if df is None:
            return {"type": "text", "content": "Please load data first."}
        
        sample_data = df.head(3).to_string()
        
        system_prompt = f"""You are a data analysis assistant. Analyze the user's query and respond using EXACTLY one of these XML formats:

1) <chat>...</chat> - For general questions, explanations, or when you need clarification
2) <pandas>...</pandas> - For pandas operations that return DataFrames or values
3) <sql>...</sql> - For SQL queries (table name is 'data')

IMPORTANT RULES:
- Always wrap your code in the appropriate XML tags
- For pandas: write valid Python pandas code that works with variable 'df'
- For SQL: write valid SQL for a table named 'data'
- Add <explain>...</explain> after pandas/SQL to explain what the code does
- Keep explanations concise and clear

Dataset Information:
{schema}

Sample Data:
{sample_data}

EXAMPLES:

User: "show me the first 10 rows"
Response: <pandas>df.head(10)</pandas><explain>Displays the first 10 rows of the dataset</explain>

User: "what's the average price?"
Response: <pandas>df['price'].mean()</pandas><explain>Calculates the mean of the price column</explain>

User: "filter rows where sales > 1000"
Response: <pandas>df[df['sales'] > 1000]</pandas><explain>Filters the dataset to show only rows where sales exceed 1000</explain>

User: "group by category and sum revenue"
Response: <pandas>df.groupby('category')['revenue'].sum()</pandas><explain>Groups data by category and sums the revenue for each group</explain>

User: "what columns are available?"
Response: <chat>The dataset has the following columns: {', '.join(df.columns.tolist()[:5])}...</chat>

Now respond to the user's query."""

        model_used, raw_response = call_gemini_auto(system_prompt, user_input)
        
        if model_used:
            st.session_state.current_model = model_used
        
        try:
            # Chat response
            if "<chat>" in raw_response and "</chat>" in raw_response:
                content = raw_response.split("<chat>")[1].split("</chat>")[0].strip()
                return {"type": "text", "content": content}
            
            # Pandas expression
            elif "<pandas>" in raw_response and "</pandas>" in raw_response:
                expr = raw_response.split("<pandas>")[1].split("</pandas>")[0].strip()
                explain = ""
                if "<explain>" in raw_response and "</explain>" in raw_response:
                    explain = raw_response.split("<explain>")[1].split("</explain>")[0].strip()
                
                result = self.safe_eval(expr, df)
                
                if isinstance(result, pd.DataFrame):
                    return {"type": "dataframe", "content": result, "explain": explain, "code": expr}
                elif isinstance(result, pd.Series):
                    return {"type": "dataframe", "content": result.to_frame(), "explain": explain, "code": expr}
                else:
                    return {"type": "text", "content": f"Result: {str(result)}\n\n{explain}" if explain else f"Result: {str(result)}"}
            
            # SQL query
            elif "<sql>" in raw_response and "</sql>" in raw_response:
                query = raw_response.split("<sql>")[1].split("</sql>")[0].strip()
                explain = ""
                if "<explain>" in raw_response and "</explain>" in raw_response:
                    explain = raw_response.split("<explain>")[1].split("</explain>")[0].strip()
                
                conn = sqlite3.connect(":memory:")
                df.to_sql("data", conn, index=False, if_exists="replace")
                result = pd.read_sql_query(query, conn)
                conn.close()
                
                return {"type": "dataframe", "content": result, "explain": explain, "code": query}
            
            else:
                return {"type": "text", "content": raw_response}
        
        except Exception as e:
            return {"type": "error", "content": f"Error: {str(e)}"}
    
    def generate_insights(self, df, schema):
        """Generate AI insights about the dataset"""
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
        return response