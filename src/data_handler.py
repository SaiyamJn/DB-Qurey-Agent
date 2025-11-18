import ast
import sqlite3
import pandas as pd
import numpy as np


def load_csv_file(uploaded_file):
    """Try multiple strategies to read CSV file"""
    df = None
    error_messages = []
    
    # Strategy 1: Standard read
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e1:
        error_messages.append(f"Standard: {str(e1)[:50]}")
        
        # Strategy 2: With error handling
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, on_bad_lines='skip', encoding='utf-8')
        except Exception as e2:
            error_messages.append(f"UTF-8: {str(e2)[:50]}")
            
            # Strategy 3: Different encoding
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, on_bad_lines='skip', encoding='latin-1')
            except Exception as e3:
                error_messages.append(f"Latin-1: {str(e3)[:50]}")
                
                # Strategy 4: Python engine
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, engine='python', on_bad_lines='skip', 
                                   encoding='utf-8', sep=None)
                except Exception as e4:
                    error_messages.append(f"Python engine: {str(e4)[:50]}")
    
    return df, error_messages


def generate_schema(df):
    """Generate schema description for the dataframe"""
    rows, cols = df.shape
    schema_lines = [f"{rows:,} rows × {cols} columns"]
    for col in df.columns[:15]:
        schema_lines.append(f"- {col} ({df[col].dtype})")
    if cols > 15:
        schema_lines.append(f"... and {cols - 15} more columns")
    
    return "\n".join(schema_lines)


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


def execute_sql_query(query, df):
    """Execute SQL query on dataframe"""
    conn = sqlite3.connect(":memory:")
    df.to_sql("data", conn, index=False, if_exists="replace")
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result