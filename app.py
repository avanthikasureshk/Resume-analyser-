import os
import streamlit as st
import PyPDF2
import docx
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Streamlit Page Setup
st.set_page_config(page_title="Resume Analyzer & Job Matcher", page_icon="🧠", layout="wide")

# 💅 Custom Styling
st.markdown("""
<style>
body {
    background-color: #f5f8fa;
}
.main-title {
    font-size: 40px;
    font-weight: bold;
    color: #2c3e50;
    text-align: center;
    margin-top: 10px;
}
.sub-title {
    font-size: 18px;
    color: #7f8c8d;
    text-align: center;
    margin-bottom: 30px;
}
.section-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    margin-top: 20px;
}
.success-banner {
    background: linear-gradient(to right, #27ae60, #2ecc71);
    color: white;
    font-size: 16px;
    padding: 12px;
    text-align: center;
    border-radius: 8px;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# 🧠 Titles
st.markdown('<h1 class="main-title">🧠 Resume Analyzer & Job Matcher</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">AI-Powered Career Insights from Your Resume</p>', unsafe_allow_html=True)

# 📂 Upload Section
uploaded_file = st.file_uploader("📄 Upload your Resume (.pdf or .docx)", type=["pdf", "docx"])

# 📄 Resume Text Extraction
def extract_resume_text(file_path, file_type):
    text = ""
    if file_type == "pdf":
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    elif file_type == "docx":
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text.strip()

# 🤖 Analyze Resume
def analyze_resume(text):
    prompt = f"""
    You are an AI Resume Consultant. Based on the following resume details:
    {text}
    
    Respond in this format:
    [Job Roles]
    - Job Role 1
    - Job Role 2
    
    [Missing Skills]
    - Skill: Suggestion
    
    [Resume Tips]
    - Tip 1
    - Tip 2
    """
    model = genai.GenerativeModel("gemini-1.5-pro-latest")
    response = model.generate_content(prompt)
    return response.text.strip()

# 🧠 Main Logic
if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1]
    file_path = f"temp_resume.{file_type}"

    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ Resume uploaded successfully!")

    with st.spinner("🔍 Extracting and analyzing your resume..."):
        resume_text = extract_resume_text(file_path, file_type)
        if not resume_text:
            st.error("❌ No text could be extracted. Try uploading a different file.")
        else:
            result = analyze_resume(resume_text)

    os.remove(file_path)

    # ✅ Parsed Output
    if result:
        st.markdown("### 📌 Results")
        st.markdown('<div class="section-card">', unsafe_allow_html=True)

        # Tabs for categorized output
        tab1, tab2, tab3 = st.tabs(["💼 Job Matches", "🔍 Missing Skills", "📝 Resume Tips"])
        job_roles, skills, tips = "", "", ""
        if "[Job Roles]" in result:
            sections = result.split("[")
            for section in sections:
                if section.startswith("Job Roles]"):
                    job_roles = section.replace("Job Roles]", "").strip()
                elif section.startswith("Missing Skills]"):
                    skills = section.replace("Missing Skills]", "").strip()
                elif section.startswith("Resume Tips]"):
                    tips = section.replace("Resume Tips]", "").strip()

        with tab1:
            st.markdown("#### 💼 Suitable Job Roles")
            st.markdown(job_roles or "No job roles found.")

        with tab2:
            st.markdown("#### 🔍 Missing Skills & Recommendations")
            st.markdown(skills or "No missing skills found.")

        with tab3:
            st.markdown("#### 📝 Resume Improvement Tips")
            st.markdown(tips or "No resume tips provided.")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('<div class="success-banner">🎯 Resume analyzed! Take the next step in your career. 🚀</div>', unsafe_allow_html=True)
        st.balloons()
    else:
        st.error("⚠ Failed to analyze resume.")
