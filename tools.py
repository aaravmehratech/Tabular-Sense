import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import time
from datetime import datetime

MEMORY_FILE = "memory_store.json"

# Global variables so the Gemini API can access state
global_df = None 
latest_chart = None

# ==========================================
# 1. CORE ANALYTICAL FUNCTIONS
# ==========================================

def data_profiler() -> str:
    """Explores the dataset schema. Call this FIRST when a new dataset is uploaded."""
    global global_df
    if global_df is None:
        return "No dataset loaded."
    info = pd.DataFrame({
        'Data Type': global_df.dtypes,
        'Missing Values': global_df.isnull().sum()
    })
    return f"Schema:\n{info.to_string()}\n\nSample (3 rows):\n{global_df.head(3).to_string()}"

def data_cleaner(column_name: str, strategy: str) -> str:
    """
    Handles missing data by dropping rows or filling with the average.
    Args:
        column_name: The name of the column to clean.
        strategy: Either 'drop' or 'fill_mean'.
    """
    global global_df
    if column_name not in global_df.columns:
        return f"Error: Column '{column_name}' not found."
    
    if strategy == 'drop':
        global_df.dropna(subset=[column_name], inplace=True)
        return f"Cleaned: Dropped all missing rows in '{column_name}'."
    else:
        mean_val = global_df[column_name].mean()
        global_df[column_name].fillna(mean_val, inplace=True)
        return f"Cleaned: Filled missing values in '{column_name}' with {mean_val:.2f}."

def pandas_executor(code_string: str) -> str:
    """
    Executes pandas code to filter, group, or calculate metrics. 
    Assume the dataframe is named 'df'.
    Args:
        code_string: A valid python expression, e.g., df.groupby('col')['val'].sum()
    """
    global global_df
    local_vars = {'df': global_df, 'pd': pd}
    try:
        # Restricted execution environment
        exec(f"result = {code_string}", {"__builtins__": {}}, local_vars)
        return str(local_vars.get('result', 'Execution finished with no return.'))
    except Exception as e:
        return f"Execution Error: {str(e)}"

def outlier_detector(column_name: str) -> str:
    """
    Finds extreme anomalies in a numeric column.
    Args:
        column_name: The name of the numeric column to check.
    """
    global global_df
    if column_name not in global_df.columns or not pd.api.types.is_numeric_dtype(global_df[column_name]):
        return f"Error: '{column_name}' must be a numeric column."
        
    Q1 = global_df[column_name].quantile(0.25)
    Q3 = global_df[column_name].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = global_df[(global_df[column_name] < lower_bound) | (global_df[column_name] > upper_bound)]
    return f"Found {len(outliers)} anomalies in '{column_name}'.\n\nOutliers:\n{outliers.head(5).to_string()}"

def chart_generator(x_col: str, y_col: str, chart_type: str) -> str:
    """
    Generates a visualization and saves it as a PNG.
    Args:
        x_col: The x-axis column.
        y_col: The y-axis column.
        chart_type: Either 'bar' or 'line'.
    """
    global global_df, latest_chart
    if x_col not in global_df.columns or y_col not in global_df.columns:
        return f"Error: Columns not found."
        
    plt.figure(figsize=(8, 5))
    if chart_type == 'bar':
        sns.barplot(data=global_df, x=x_col, y=y_col)
    else:
        sns.lineplot(data=global_df, x=x_col, y=y_col)
        
    timestamp = int(time.time())
    filepath = f"chart_{timestamp}.png"
    plt.tight_layout()
    plt.savefig(filepath)
    plt.close()
    
    latest_chart = filepath
    return f"Chart saved to {filepath}"

# ==========================================
# 2. MEMORY FUNCTIONS
# ==========================================

def save_business_logic(key: str, memory_type: str, value: str) -> str:
    """
    Saves user preferences or metric definitions to persistent memory.
    Args:
        key: The concept name (e.g. 'Active Users')
        memory_type: Either 'metric_definition' or 'user_preference'
        value: The rule or SQL/Pandas logic
    """
    memory = {}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
            
    key = key.lower().strip()
    action = "Updated" if key in memory else "Saved"
    
    memory[key] = {
        "type": memory_type,
        "value": value,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)
    return f"{action} {memory_type} for '{key}'."

def retrieve_business_logic(search_term: str) -> str:
    """
    Retrieves saved logic. Call this BEFORE writing pandas code to check for custom definitions.
    Args:
        search_term: The noun or concept to search for in memory.
    """
    if not os.path.exists(MEMORY_FILE):
        return "No memory found."
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
        
    term = search_term.lower().strip()
    results = {k: v['value'] for k, v in memory.items() if term in k or term in v['value'].lower()}
    
    if results:
        return f"Found logic: {json.dumps(results)}"
    return f"No memory found relating to '{search_term}'."