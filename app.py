import streamlit as st
from groq import Groq
import json

st.set_page_config(
    page_title="CareerIQ — AI Career Advisor",
    page_icon="🎯",
    layout="centered"
)

st.markdown("""
<style>
    .chip-green {
        display: inline-block;
        background: #d1fae5; color: #065f46;
        border-radius: 999px; padding: 3px 12px;
        font-size: 13px; margin: 3px;
    }
    .chip-amber {
        display: inline-block;
        background: #fef3c7; color: #92400e;
        border-radius: 999px; padding: 3px 12px;
        font-size: 13px; margin: 3px;
    }
    .project-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 CareerIQ — AI Career Advisor")
st.caption("Fill in your profile and get a personalized career roadmap powered by AI")

st.divider()

with st.form("career_form"):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your Name", placeholder="e.g. Ritika Sharma")
    with col2:
        degree = st.text_input("Degree / Branch", placeholder="e.g. B.Tech CSE (2027)")

    skills = st.text_input("Your Current Skills", placeholder="e.g. Python, React, SQL, Machine Learning")
    interests = st.text_input("Your Interests", placeholder="e.g. AI/ML, building web apps, competitive programming")
    goal = st.text_input("Career Goal", placeholder="e.g. SDE at a product company or AI startup")

    submitted = st.form_submit_button("✨ Generate My Career Roadmap", use_container_width=True, type="primary")

if submitted:
    if not all([name, degree, skills, interests, goal]):
        st.error("Please fill in all fields.")
        st.stop()

    prompt = f"""You are a career advisor for college students in India. Analyze this student profile and return career guidance.

Student Profile:
- Name: {name}
- Degree/Branch: {degree}
- Current Skills: {skills}
- Interests: {interests}
- Career Goal: {goal}

Return ONLY a valid JSON object (no markdown, no extra text) with this exact structure:
{{
  "careerPath": "Best career path title",
  "careerEmoji": "single relevant emoji",
  "careerReason": "2-3 sentence explanation of why this path suits them",
  "skillsHave": ["skill1", "skill2", "skill3", "skill4"],
  "skillsNeed": ["skill1", "skill2", "skill3", "skill4"],
  "roadmap": [
    {{ "month": "Month 1", "focus": "Focus area", "tasks": "3-4 concrete tasks to do this month" }},
    {{ "month": "Month 2", "focus": "Focus area", "tasks": "3-4 concrete tasks to do this month" }},
    {{ "month": "Month 3", "focus": "Focus area", "tasks": "3-4 concrete tasks to do this month" }}
  ],
  "projects": [
    {{ "name": "Project name", "description": "One line description of what to build and what it demonstrates" }},
    {{ "name": "Project name", "description": "One line description" }},
    {{ "name": "Project name", "description": "One line description" }}
  ],
  "interviewTips": [
    "Specific actionable tip 1",
    "Specific actionable tip 2",
    "Specific actionable tip 3",
    "Specific actionable tip 4",
    "Specific actionable tip 5"
  ]
}}"""

    with st.spinner("Analyzing your profile..."):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(raw)
        except json.JSONDecodeError:
            st.error("Could not parse AI response. Please try again.")
            st.stop()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            st.stop()

    st.divider()

    st.markdown(f"## {result.get('careerEmoji', '🎯')} {result.get('careerPath', '')}")
    st.info(result.get("careerReason", ""))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ Skills You Have")
        chips = "".join(f'<span class="chip-green">{s}</span>' for s in result.get("skillsHave", []))
        st.markdown(chips, unsafe_allow_html=True)
    with col2:
        st.markdown("#### 📚 Skills to Build")
        chips = "".join(f'<span class="chip-amber">{s}</span>' for s in result.get("skillsNeed", []))
        st.markdown(chips, unsafe_allow_html=True)

    st.divider()

    st.markdown("#### 🗓️ 3-Month Learning Roadmap")
    month_colors = ["#7c6ef5", "#3dd68c", "#f5a623"]
    for i, month in enumerate(result.get("roadmap", [])):
        color = month_colors[i % len(month_colors)]
        st.markdown(f"""
        <div style="border-left: 3px solid {color}; padding-left: 16px; margin-bottom: 16px;">
            <strong style="color:{color}">{month['month']} — {month['focus']}</strong><br>
            <span style="color:#444; font-size:14px">{month['tasks']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("#### 🛠️ Project Ideas to Build")
    for i, proj in enumerate(result.get("projects", []), 1):
        st.markdown(f"""
        <div class="project-card">
            <strong>P{i}: {proj['name']}</strong><br>
            <span style="color:#64748b; font-size:13px">{proj['description']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown("#### 💡 Interview Preparation Tips")
    for tip in result.get("interviewTips", []):
        st.markdown(f"- {tip}")
