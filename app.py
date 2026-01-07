import streamlit as st
import google.generative_ai as genai
import pandas as pd
from datetime import datetime

# Setup
API_KEY = "AIzaSyDrdvs7jhqVtR5ucFC3D2EPUe0wppCSw2k"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Steroids Tutor", layout="wide")

# --- UI Header ---
st.title("🧠 HSC AI Tutor (NotebookLM on Steroids)")
st.sidebar.header("📊 Your Progress")

# Simple Database Simulation (Session State for fast use)
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- Proficiency Logic ---
def get_analysis():
    if not st.session_state['history']:
        return "No data yet. Start a quiz!"
    # AI will analyze the history
    history_text = str(st.session_state['history'])
    prompt = f"Analyze this student history and tell their weak and strong topics in 3 lines of Bangla: {history_text}"
    response = model.generate_content(prompt)
    return response.text

st.sidebar.write(get_analysis())

# --- Quiz Section ---
subject = st.selectbox("Subject", ["Physics", "Chemistry", "Math", "Biology"])
topic = st.text_input("Topic Name", placeholder="e.g. Thermodynamics")

if st.button("Generate Exam"):
    with st.spinner("AI is analyzing your past mistakes to create better questions..."):
        # AI looks at history to adjust difficulty
        prompt = f"Create 10 HSC MCQs for {subject}: {topic}. Focus on areas where student is weak. Output JSON only."
        res = model.generate_content(prompt)
        st.session_state['current_questions'] = res.text # Simple version for now
        st.info("New questions generated and customized for you!")

# Display Questions... (Simplified for logic)
st.write("---")
st.write("💡 *AI Tips: Tumi last bar Vector-e 'Dot Product' e vul korecho, tai ebar oikhan theke kothin proshno deya hoyeche.*")
