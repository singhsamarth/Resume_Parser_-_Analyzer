import streamlit as st
import sqlite3
import pandas as pd
from pyresparser import ResumeParser
import base64
import datetime
import tempfile
import os

from courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos

# Set page config FIRST
st.set_page_config(page_title="Resume_Parser_&_Analyser", layout='wide')

# Custom CSS
st.markdown("""
    <style>
        body {
            background-color: #f0f2f6;
        }
        .main {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        h1, h2, h3, h4 {
            color: #004080;
        }
        .stButton>button {
            background-color: #004080;
            color: white;
            border-radius: 8px;
        }
        .stDownloadButton>button {
            background-color: #008CBA;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Connect to SQLite
conn = sqlite3.connect('sra.db', check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        Email TEXT,
        Contact TEXT,
        Resume_score INTEGER,
        Date TEXT
    )
''')
conn.commit()

# Insert Data
def insert_data(name, email, contact, score, date):
    name = name[:100] if name else ''
    email = email[:100] if email else ''
    contact = contact[:20] if contact else ''
    cursor.execute('INSERT INTO user_data (Name, Email, Contact, Resume_score, Date) VALUES (?, ?, ?, ?, ?)',
                   (name, email, contact, score, date))
    conn.commit()

# Fetch Data
def fetch_all_users():
    cursor.execute('SELECT * FROM user_data')
    return cursor.fetchall()

# Download link for CSV
def get_csv_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download CSV</a>'

# Resume Score
def calculate_resume_score(parsed_data):
    score = 0
    if parsed_data.get('skills'):
        score += len(parsed_data['skills']) * 2
    if parsed_data.get('education'):
        score += len(parsed_data['education']) * 2
    if parsed_data.get('experience'):
        score += len(parsed_data['experience']) * 3
    return min(score, 100)

# App Title
st.title("🚀 Resume Parser & Analyser")

# Upload
pdf_file = st.file_uploader("📋 Upload Your Resume", type=['pdf', 'docx'])

if pdf_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(pdf_file.name)[1]) as tmp_file:
        tmp_file.write(pdf_file.getbuffer())
        tmp_path = tmp_file.name

    try:
        data = ResumeParser(tmp_path).get_extracted_data()
        os.remove(tmp_path)

        if data:
            st.subheader("📋 Extracted Resume Info:")

            st.markdown("""
                <style>
                .info-card {
                    background-color: #f9f9f9;
                    padding: 15px 25px;
                    margin-bottom: 12px;
                    border-radius: 10px;
                    border-left: 5px solid #004080;
                    font-family: 'Segoe UI', sans-serif;
                }
                .info-label {
                    font-weight: 700;
                    color: #003366;
                    font-size: 16px;
                }
                .info-value {
                    font-weight: 500;
                    color: #222;
                    font-size: 15px;
                }
                </style>
            """, unsafe_allow_html=True)

            if data:
                def show_info(label, value):
                    if value:
                        st.markdown(f"""
                        <div class="info-card">
                            <span class="info-label">{label}:</span><br>
                            <span class="info-value">{value}</span>
                        </div>
                        """, unsafe_allow_html=True)

                show_info("Name", data.get('name', 'N/A'))
                show_info("Email", data.get('email', 'N/A'))
                show_info("Mobile", data.get('mobile_number', 'N/A'))
                show_info("Degree", ', '.join(data.get('degree')) if data.get('degree') else 'N/A')
                show_info("College", data.get('college_name', 'N/A'))
                show_info("Experience", data.get('experience', 'N/A'))
                show_info("Skills", ', '.join(data.get('skills')) if data.get('skills') else 'N/A')
                show_info("Companies", ', '.join(data.get('company_names')) if data.get('company_names') else 'N/A')
                show_info("Designation", data.get('designation', 'N/A'))
                show_info("Total Experience", data.get('total_experience', 'N/A'))


            # Score
            resume_score = calculate_resume_score(data)
            st.success(f"✅ Resume Score: {resume_score}/100")

            # DB insert
            insert_data(
                data.get('name', 'N/A'),
                data.get('email', 'N/A'),
                data.get('mobile_number', 'N/A'),
                resume_score,
                str(datetime.datetime.now().date())
            )

            # Recommendations
            st.subheader("🎓 Recommended Courses:")
            if data.get('skills'):
                skill_set = [s.lower() for s in data['skills']]
                if any(s in skill_set for s in ['ml', 'machine learning', 'ai', 'data science']):
                    for course in ds_course[:3]:
                        st.markdown(f"- [{course[0]}]({course[1]})")
                elif any(s in skill_set for s in ['html', 'css', 'js', 'react', 'django', 'flask']):
                    for course in web_course[:3]:
                        st.markdown(f"- [{course[0]}]({course[1]})")
                elif any(s in skill_set for s in ['android', 'kotlin', 'flutter']):
                    for course in android_course[:3]:
                        st.markdown(f"- [{course[0]}]({course[1]})")
                elif any(s in skill_set for s in ['ios', 'swift']):
                    for course in ios_course[:3]:
                        st.markdown(f"- [{course[0]}]({course[1]})")
                elif any(s in skill_set for s in ['ui', 'ux', 'adobe xd', 'figma']):
                    for course in uiux_course[:3]:
                        st.markdown(f"- [{course[0]}]({course[1]})")

            # Videos
            st.subheader("📽️ Resume Building Videos:")
            for vid in resume_videos[:2]:
                st.video(vid)

            st.subheader("🎤 Interview Prep Videos:")
            for vid in interview_videos[:2]:
                st.video(vid)

        else:
            st.error("❌ Could not extract data from the resume. Please try another file.")

    except Exception as e:
        st.error(f"❌ Error processing resume: {e}")
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# Admin Panel
st.sidebar.title("Admin Panel")
if st.sidebar.checkbox("📁 View User Data"):
    user_records = fetch_all_users()
    if user_records:
        df_users = pd.DataFrame(user_records, columns=["ID", "Name", "Email", "Contact", "Score", "Date"])
        st.sidebar.subheader("📊 User Records")
        st.sidebar.dataframe(df_users)

        st.sidebar.markdown(get_csv_download_link(df_users, "user_data.csv"), unsafe_allow_html=True)
    else:
        st.sidebar.info("No user data found.")
