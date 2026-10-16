import streamlit as st
import pandas as pd
import json
import os
import google.generativeai as genai
import tools 

st.set_page_config(page_title="TabulaSense AI", page_icon="📊", layout="wide")

st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Courier New', Courier, monospace !important;
        }
        .stChatMessage {
            border-radius: 8px;
            padding: 10px;
            background-color: #0e0e0e;
            border-left: 3px solid #00D2BE;
        }
        .stButton>button {
            border-radius: 4px;
            border: 1px solid #00D2BE;
            color: #00D2BE;
            transition: all 0.3s ease-in-out;
            background-color: transparent;
        }
        .stButton>button:hover {
            background-color: #00D2BE;
            color: #000000;
            box-shadow: 0 0 10px #00D2BE;
        }
    </style>
""", unsafe_allow_html=True)
API_KEY = st.secrets["AARAV_API"]
genai.configure(api_key=API_KEY)

my_tools = [
    tools.data_profiler, tools.data_cleaner, tools.pandas_executor, 
    tools.outlier_detector, tools.chart_generator,
    tools.save_business_logic, tools.retrieve_business_logic
]

model = genai.GenerativeModel(
    model_name='gemini-3.5-flash-lite', 
    tools=my_tools,
    system_instruction="You are TabulaSense, an expert data analyst. You have tools to profile data, clean it, execute pandas code, find outliers, plot charts, and save/retrieve user preferences from memory. Always check memory before applying logic. When rendering a chart, tell the user you have created it."
)

with st.sidebar:
    st.header("⚙️ TabulaSense OS")
    st.caption("Aarav Mehra, MAIT")
    st.divider()
    
    st.subheader("📂 Workspace")
    uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])
    
    if uploaded_file:
        if "df" not in st.session_state or st.session_state.df is None:
            uploaded_file.seek(0)
            st.session_state.df = pd.read_csv(uploaded_file)
            
        tools.global_df = st.session_state.df 
        st.success(f"Dataset loaded into active memory. ({st.session_state.df.shape[0]} rows)", icon="✅")
    else:
        st.session_state.df = None
        tools.global_df = None
        
    st.divider()
    st.subheader("🧠 Memory Manager")
    
    memory_file = getattr(tools, "MEMORY_FILE", "memory_store.json")
    if os.path.exists(memory_file):
        with open(memory_file, "r") as f:
            memory = json.load(f)
        for key, data in list(memory.items()):
            with st.expander(f"📌 {key.title()}"):
                st.write(f"**Definition:** {data['value']}")
                if st.button(f"Delete '{key}'", key=f"del_{key}"):
                    del memory[key]
                    with open(memory_file, "w") as f:
                        json.dump(memory, f)
                    st.rerun()
    else:
        st.info("Memory is empty.")

st.title("TabulaSense: Agentic Data Analyst")

with st.expander("🛠️ View Agent Capabilities (Functions)"):
    st.markdown("""
    * **Data Profiler:** Instantly summarizes columns, data types, and missing values.
    * **Data Cleaner:** Automatically handles null values and drops duplicate rows.
    * **Pandas Executor:** Runs complex, custom Pandas queries for advanced filtering.
    * **Outlier Detector:** Uses IQR statistical methods to find anomalies.
    * **Chart Generator:** Writes and executes Python code to build custom graphs.
    * **Logic Memory:** Learns and remembers your custom business rules.
    """)

if uploaded_file:
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(enable_automatic_function_calling=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg.get("avatar", "🤖" if msg["role"] == "assistant" else "👤")):
            st.markdown(msg["content"])
            if "image" in msg and msg["image"]:
                st.image(msg["image"])

    if user_input := st.chat_input("E.g., Clean the data, find outliers, or plot sales by region."):
        
        st.session_state.messages.append({"role": "user", "content": user_input, "avatar": "👤"})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        prompt_lower = user_input.lower()
        if "plot" in prompt_lower or "chart" in prompt_lower or "graph" in prompt_lower:
            agent_name, agent_icon = "Visualization Agent", "🎨"
        elif "remember" in prompt_lower or "rule" in prompt_lower or "logic" in prompt_lower:
            agent_name, agent_icon = "Memory Agent", "🧠"
        else:
            agent_name, agent_icon = "Data Analyst Agent", "📊"

        with st.chat_message("assistant", avatar=agent_icon):
            try:
              
                with st.status(f"**{agent_name}** is analyzing request...", expanded=True) as status:
                    st.write("Interpreting intent and executing background functions...")
                    response = st.session_state.chat.send_message(user_input)
                    status.update(label=f"Task completed by {agent_name}!", state="complete", expanded=False)
                
              
                try:
                    final_text = response.text
                except ValueError:
                    final_text = "I executed the tool, but didn't generate a text summary. (Make sure to specify a column name next time!)"
                
                st.markdown(final_text)
                ui_msg = {"role": "assistant", "content": final_text, "avatar": agent_icon}
                
                if "latest_chart" in st.session_state and st.session_state.latest_chart:
                    st.image(st.session_state.latest_chart)
                    ui_msg["image"] = st.session_state.latest_chart
                    st.session_state.latest_chart = None
                    
                st.session_state.messages.append(ui_msg)

                st.rerun()
                
                if "Saved" in final_text or "Updated" in final_text:
                    st.rerun()
                    
            except Exception as e:
                st.error(f"An error occurred during execution: {e}")
else:
    st.info("👈 Please upload a CSV file in the sidebar to begin analysis.")
