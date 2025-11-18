import pandas as pd
from gemini_api import call_gemini_auto
from data_handler import safe_eval, execute_sql_query


def build_system_prompt(schema, sample_data, df_columns):
    """Build the system prompt for Gemini"""
    return f"""You are a data analysis assistant. Analyze the user's query and respond using EXACTLY one of these XML formats:

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
Response: <chat>The dataset has the following columns: {', '.join(df_columns[:5])}...</chat>

Now respond to the user's query."""


def parse_response(raw_response, df):
    """Parse Gemini response and execute appropriate action"""
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
            
            result = safe_eval(expr, df)
            
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
            
            result = execute_sql_query(query, df)
            return {"type": "dataframe", "content": result, "explain": explain, "code": query}
        
        else:
            # Fallback - treat as chat
            return {"type": "text", "content": raw_response}
    
    except Exception as e:
        return {"type": "error", "content": f"Error: {str(e)}"}


def process_query(user_input, df, schema):
    """Process user query and return response"""
    if df is None:
        return {"type": "text", "content": "Please upload a CSV file first."}
    
    # Get sample data for context
    sample_data = df.head(3).to_string()
    
    # Build system prompt
    system_prompt = build_system_prompt(schema, sample_data, df.columns.tolist())
    
    # Call Gemini API
    model_used, raw_response = call_gemini_auto(system_prompt, user_input)
    
    # Parse and execute response
    result = parse_response(raw_response, df)
    
    return model_used, result