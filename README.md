# Tabular-Sense | Agentic AI Data Analyst

**An AI-powered data analyst that turns natural-language questions into actionable insights from tabular data.**

Tabular-Sense is a Streamlit application powered by Google Gemini that combines **five custom-built data analysis tools, automatic tool calling, and persistent memory** to help users explore, clean, analyze, and visualize CSV datasets through a conversational interface.

**Live Demo:** [Tabular-Sense](https://tabular-sense.streamlit.app/)

**[▶ Watch the Tabular-Sense Demo Video](https://youtu.be/E2OXtrIa21k)**

## Core Features

### 1. Five Custom-Built Tools

| Tool | Description |
|---|---|
| **Data Profiler** | Examines dataset structure, column data types, missing values, and sample records. |
| **Data Cleaner** | Handles missing values through row removal or mean imputation. |
| **Pandas Executor** | Performs custom filtering, grouping, aggregation, and calculations using Pandas. |
| **Outlier Detector** | Identifies potential anomalies in numerical columns using the Interquartile Range (IQR) method. |
| **Chart Generator** | Generates bar and line charts from selected dataset columns. |

### 2. Persistent Memory

Tabular-Sense includes a lightweight memory system that saves and retrieves reusable metric definitions and user preferences.

Rather than treating every request independently, the agent can recall previously stored information and use relevant definitions when analyzing data. Users can inspect and delete saved entries through the application's sidebar.

## Agentic Workflow

Tabular-Sense uses Google Gemini's automatic function calling to determine which tools are relevant to a user's request.

1. **Upload** a CSV dataset through the workspace.
2. **Ask** questions in natural language.
3. **Analyze** — the agent selects and executes the appropriate tools.
4. **Visualize** results through generated charts when requested.
5. **Remember** useful definitions and preferences for future analysis.

The goal is to make data analysis more accessible while grounding answers in actual tool-based computation rather than relying solely on model-generated text.

## Technology Stack

- **Python** — Core application and tool logic
- **Streamlit** — Interactive web interface and chat experience
- **Google Gemini API** — Language model and automatic function calling
- **Pandas** — Data manipulation and analysis
- **Matplotlib & Seaborn** — Visualization
- **JSON** — Memory storage

## Tools and Example Use Cases

### a. Data Profiler
Examines dataset structure, data types, missing values, and sample records.

**Example:** "Profile this dataset and identify columns with missing values."

### b. Data Cleaner
Handles missing values through row removal or mean imputation.

**Example:** "Fill missing values in the `price` column with the mean."

### c. Pandas Executor
Performs custom filtering, grouping, aggregation, and calculations using Pandas.

**Example:** "Calculate total revenue for each category using price multiplied by quantity."

### d. Outlier Detector
Identifies potential anomalies in numerical columns using the IQR method.

**Example:** "Find unusually high prices in the dataset."

### e. Chart Generator
Generates bar and line charts from selected dataset columns.

**Example:** "Create a bar chart comparing prices across product categories."

### f. Save Memory
Stores reusable metric definitions and user preferences.

**Example:** "Remember that revenue is calculated as price multiplied by quantity."

### g. Retrieve Memory
Retrieves saved definitions and preferences for use in future analyses.

**Example:** "What definition of revenue have I saved?"

## Deployment

Tabular-Sense is deployed on Streamlit Community Cloud.

- **Live App:** [Launch Tabular-Sense](https://tabular-sense.streamlit.app/)
- **Demo Video:** [▶ Watch the Tabular-Sense Demo](https://youtu.be/E2OXtrIa21k)

## Project Objective

Tabular-Sense explores how LLMs can move beyond conversational assistance by using specialized tools to perform practical data analysis. It combines natural-language interaction, executable analytical operations, visualization, and reusable memory in a single application.

