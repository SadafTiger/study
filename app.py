import streamlit as st
import google.generative_ai as genai
import json
import pandas as pd

# --- ১. মেমোরি সেটআপ (Database) ---
# এটি তোমার সেশনের সব প্রশ্ন এবং রেজাল্ট মনে রাখবে
if 'memory' not in st.session_state:
    st.session_state['memory'] = []
if 'current_quiz' not in st.session_state:
    st.session_state['current_quiz'] = None

# --- ২. AI কনফিগারেশন ---
API_KEY = "AIzaSyDrdvs7jhqVtR5ucFC3D2EPUe0wppCSw2k"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro') # প্রো মডেল ব্যবহার হচ্ছে

st.set_page_config(page_title="HSC AI Steroids", layout="wide", initial_sidebar_state="expanded")

# --- ৩. কাস্টম ডিজাইন (Dark Mode & Mobile Friendly) ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    .q-card { background-color: #1d2129; padding: 20px; border-radius: 12px; border-left: 6px solid #4CAF50; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background: linear-gradient(45deg, #2e7d32, #1b5e20); color: white; border: none; }
</style>
""", unsafe_allow_html=True)

# --- ৪. সাইডবার (প্রগ্রেস ট্র্যাকার) ---
with st.sidebar:
    st.title("📊 My Learning Lab")
    if st.session_state['memory']:
        st.subheader("Proficiency Analysis")
        # AI এখানে তোমার পাস্ট ডাটা এনালাইসিস করবে
        history = str(st.session_state['memory'][-5:]) # লাস্ট ৫টি কুইজ
        analysis_prompt = f"Student Performance Data: {history}. Briefly analyze weak and strong areas in Bangla."
        try:
            analysis = model.generate_content(analysis_prompt)
            st.info(analysis.text)
        except:
            st.write("Keep practicing to see analysis!")
    else:
        st.write("কোনো কুইজ দিলে এখানে তোমার দক্ষতা দেখাবে।")

# --- ৫. মেইন কুইজ ইঞ্জিন ---
st.title("🧠 HSC AI Tutor (Steroids Mode)")

col1, col2 = st.columns(2)
with col1:
    subject = st.selectbox("বিষয় বেছে নাও", ["Physics", "Chemistry", "Math", "Biology", "ICT"])
with col2:
    topic = st.text_input("অধ্যায় বা টপিক", placeholder="যেমন: জৈব রসায়ন")

if st.button("🔥 জেনারেট কাস্টম কুইজ"):
    # AI এখানে প্রম্পট ইঞ্জিনিয়ারিং এর মাধ্যমে তোমার লেভেল বুঝে প্রশ্ন করবে
    prompt = f"""
    Act as a highly experienced HSC Examiner. 
    Topic: {subject} - {topic}.
    Task: Create 10 logical and conceptual MCQs. 
    Memory: The student has done these topics before: {st.session_state['memory']}. 
    Focus: Focus more on conceptual clarity and common mistakes.
    Format: JSON array only. 
    Structure: [{"question": "...", "options": ["A", "B", "C", "D"], "answer_index": 0, "explanation": "Detailed Bangla explanation"}]
    """
    
    with st.spinner("AI তোমার মেমোরি স্ক্যান করে প্রশ্ন বানাচ্ছে..."):
        response = model.generate_content(prompt)
        # JSON ক্লিন করা
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        st.session_state['current_quiz'] = json.loads(clean_text)
        st.session_state['submitted'] = False

# --- ৬. প্রশ্ন প্রদর্শন ও সেভ লজিক ---
if st.session_state['current_quiz']:
    quiz = st.session_state['current_quiz']
    with st.form("exam_form"):
        user_answers = []
        for i, q in enumerate(quiz):
            st.markdown(f"<div class='q-card'><b>{i+1}. {q['question']}</b></div>", unsafe_allow_html=True)
            ans = st.radio(f"অপশনসমূহ {i}", q['options'], key=f"ans_{i}", label_visibility="collapsed")
            user_answers.append(ans)
        
        if st.form_submit_button("খাতা জমা দাও (Submit)"):
            score = 0
            details = []
            for i, q in enumerate(quiz):
                correct_ans = q['options'][q['answer_index']]
                is_correct = user_answers[i] == correct_ans
                if is_correct: score += 1
                details.append({"topic": topic, "question": q['question'], "status": "Correct" if is_correct else "Wrong"})
            
            # মেমোরিতে সেভ করা (Steroids Power)
            st.session_state['memory'].append({"topic": topic, "score": score, "details": details})
            st.session_state['submitted'] = True
            st.balloons()
            st.success(f"তোমার স্কোর: {score} / 10")

    if st.session_state.get('submitted'):
        st.subheader("💡 ব্যাখ্যা ও সমাধান")
        for i, q in enumerate(quiz):
            with st.expander(f"প্রশ্ন {i+1} এর ব্যাখ্যা"):
                st.write(f"সঠিক উত্তর: **{q['options'][q['answer_index']]}**")
                st.info(f"ব্যাখ্যা: {q['explanation']}")
