import streamlit as st
import google.generative_ai as genai
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# --- SETUP: Google Sheet & AI ---
def connect_to_sheet():
    # Streamlit Secrets theke login info nibe
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # Tomar Sheet ID (Change korar dorkar nai jodi ager sheet use koro)
    SHEET_ID = "1ZqD3LOchLCL1Wt11qX7LznfIsFFqWNvgTkw-nbzTePg"
    return client.open_by_key(SHEET_ID).sheet1

# AI API Key Setup
genai.configure(api_key=st.secrets["general"]["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-pro')

st.set_page_config(page_title="HSC AI Tutor", layout="wide")

# --- UI Design ---
st.title("🧠 HSC AI Tutor (Final Pro Ver.)")
st.markdown("---")

# --- SIDEBAR: Database & Memory ---
with st.sidebar:
    st.header("📂 Memory Status")
    try:
        sheet = connect_to_sheet()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        st.success(f"✅ Database Connected! Total Qs: {len(df)}")
        
        # Weakness Tracker
        if not df.empty:
            mistakes = df[df['Status'] == 'Wrong']
            if not mistakes.empty:
                st.error(f"⚠️ Focus on: {len(mistakes)} mistakes found.")
    except Exception as e:
        st.error("❌ Connection Failed! Check Step 4.")
        st.write(e)
        df = pd.DataFrame()

# --- MAIN APP: Exam Generator ---
col1, col2 = st.columns(2)
subject = col1.selectbox("Subject", ["Physics", "Chemistry", "Math", "Biology", "ICT"])
topic = col2.text_input("Topic Name", placeholder="Example: Vector")

if st.button("🔥 Create Exam"):
    # AI Memory Check
    memory_context = ""
    if not df.empty and topic:
        # Filter mistakes for this specific topic
        topic_mistakes = df[
            (df['Topic'].astype(str).str.contains(topic, case=False)) & 
            (df['Status'] == 'Wrong')
        ]
        if not topic_mistakes.empty:
            bad_questions = topic_mistakes['Question'].tolist()[-3:] # Last 3 mistakes
            memory_context = f"Student previously failed these: {bad_questions}. Make similar tricky questions."

    prompt = f"""
    Act as HSC Teacher. Subject: {subject}, Topic: {topic}.
    Memory Context: {memory_context}
    Task: Create 5 MCQ Questions.
    Format: JSON Array ONLY. 
    Structure: [{{"q": "Question", "o": ["A", "B", "C", "D"], "a": 0, "e": "Explanation (Bangla)"}}]
    """
    
    with st.spinner("AI is thinking..."):
        try:
            res = model.generate_content(prompt)
            clean_json = res.text.replace('```json', '').replace('```', '').strip()
            st.session_state['quiz'] = json.loads(clean_json)
            st.session_state['submitted'] = False
        except:
            st.error("AI Error. Try again.")

# --- QUIZ DISPLAY ---
if 'quiz' in st.session_state:
    with st.form("exam_form"):
        user_picks = {}
        for i, item in enumerate(st.session_state['quiz']):
            st.write(f"**Q{i+1}: {item['q']}**")
            user_picks[i] = st.radio("Select:", item['o'], key=f"q{i}", label_visibility="collapsed")
            st.divider()
        
        # Submit Logic
        if st.form_submit_button("Submit & Save"):
            score = 0
            rows_to_add = []
            
            for i, item in enumerate(st.session_state['quiz']):
                correct = item['o'][item['a']]
                status = "Correct" if user_picks[i] == correct else "Wrong"
                if status == "Correct": score += 1
                
                # Sheet e ja jabe
                rows_to_add.append([subject, topic, item['q'], status, item['e']])
            
            # Save to Google Sheet
            try:
                sheet.append_rows(rows_to_add)
                st.toast("✅ Saved to Google Sheet!")
            except:
                st.error("Save failed. Check permissions.")
                
            st.session_state['score'] = score
            st.session_state['submitted'] = True
            st.rerun()

# --- RESULT & ANKI ---
if st.session_state.get('submitted'):
    st.balloons()
    st.header(f"Score: {st.session_state['score']} / 5")
    
    st.subheader("📋 Copy for Anki")
    st.code("\n".join([
        f"{q['q']} <br> {q['o']} ; ✅ {q['o'][q['a']]} <br> 💡 {q['e']}" 
        for q in st.session_state['quiz']
    ]))
    
    with st.expander("Show Explanations"):
        for q in st.session_state['quiz']:
            st.info(f"{q['q']} \n\n ✅ Answer: {q['o'][q['a']]} \n\n 💡 {q['e']}")
