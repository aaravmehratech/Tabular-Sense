import streamlit as st
import pandas as pd
import json
import os
import google.generativeai as genai
import tools 

# ==========================================
# SETUP GEMINI API
# ==========================================
# PASTE YOUR GOOGLE AI STUDIO API KEY HERE
API_KEY = st.secrets["AARAV_API"]
genai.configure(api_key=API_KEY)

# Bind the python functions to the Gemini model
my_tools = [
    tools.data_profiler, 
    tools.data_cleaner, 
    tools.pandas_executor, 
    tools.outlier_detector, 
    tools.chart_generator,
    tools.save_business_logic,
    tools.retrieve_business_logic
]

model = genai.GenerativeModel(
    model_name='gemini-3.5-flash-lite', 
    tools=my_tools,
    system_instruction="You are TabulaSense, an expert data analyst. You have tools to profile data, clean it, execute pandas code, find outliers, plot charts, and save/retrieve user preferences from memory. Always check memory before applying logic. When rendering a chart, tell the user you have created it."
)

st.set_page_config(page_title="TabulaSense AI", layout="wide")

# 1. Inject Courier New font
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Courier New', Courier, monospace !important;
        }
    </style>
    """, unsafe_allow_html=True)
# 2. Add the Description
st.markdown("### Agentic Data Analyst")
st.markdown(
    "Upload a CSV to instantly chat with your data. This agent interprets natural language "
    "to clean datasets, uncover hidden trends, and generate custom visualizations on the fly."
)

# 3. Add the Function Uses (hidden neatly in an expander)
with st.expander("🛠️ View Agent Capabilities (Functions)"):
    st.markdown("""
    * **Data Profiler:** Instantly summarizes columns, data types, and missing values.
    * **Outlier Detector:** Uses IQR statistical methods to find anomalies in numeric data.
    * **Chart Generator:** Writes and executes Python code to build custom Matplotlib/Seaborn graphs.
    * **Logic Memory:** Learns and remembers your custom business rules across sessions.
    """)

# ==========================================
# UI SIDEBAR: MEMORY MANAGER
# ==========================================
with st.sidebar:
    st.header("🧠 Memory Manager")
    st.markdown("Inspect or delete what the agent has learned.")
    
    if os.path.exists(tools.MEMORY_FILE):
        with open(tools.MEMORY_FILE, "r") as f:
            memory = json.load(f)
            
        for key, data in list(memory.items()):
            with st.expander(f"📌 {key.title()}"):
                st.write(f"**Definition:** {data['value']}")
                st.caption(f"Updated: {data['timestamp']}")
                if st.button(f"Delete '{key}'", key=f"del_{key}"):
                    del memory[key]
                    with open(tools.MEMORY_FILE, "w") as f:
                        json.dump(memory, f)
                    st.rerun()
    else:
        st.info("Memory is empty. Tell the agent a business rule!")

# ==========================================
# MAIN CHAT INTERFACE
# ==========================================
st.title("📊 TabulaSense: Agentic Data Analyst")
st.markdown("Upload a CSV and let the agent analyze it.")

uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])

if uploaded_file:
    # Load dataset and share it with tools.py
    if "df" not in st.session_state:
        st.session_state.df = pd.read_csv(uploaded_file)
        tools.global_df = st.session_state.df 
        st.success(f"Loaded {st.session_state.df.shape[0]} rows.")

    # Initialize API chat and UI messages
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(enable_automatic_function_calling=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display clean UI Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "image" in msg:
                st.image(msg["image"])

    # Handle User Input
    if user_input := st.chat_input("E.g., Clean the data, find outliers, or plot sales by region."):
        
        # 1. Add user message to UI
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. Trigger Agent
        with st.chat_message("assistant"):
            st_placeholder = st.empty()
            st_placeholder.markdown("*(Agent is thinking and analyzing...)*")
            
            try:
                # Gemini handles the recursive tool-calling loop automatically!
                response = st.session_state.chat.send_message(user_input)
                
                ui_msg = {"role": "assistant", "content": response.text}
                
                # Check if the chart generator created a new file
                if tools.latest_chart:
                    st.image(tools.latest_chart)
                    ui_msg["image"] = tools.latest_chart
                    tools.latest_chart = None # Reset for next turn
                
                # Update final answer on screen
                st_placeholder.markdown(response.text)
                
                # Save agent response to UI history
                st.session_state.messages.append(ui_msg)
                
                # Refresh UI to update sidebar if memory was modified
                if "Saved" in response.text or "Updated" in response.text or "memory" in user_input.lower():
                    st.rerun()
                
            except Exception as e:
                st_placeholder.error(f"An error occurred: {e}")