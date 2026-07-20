# Public QR Survey App for Streamlit Community Cloud - connects to Snowflake via secrets
# Co-authored with CoCo
import snowflake.connector
snowflake.connector.paramstyle = "qmark"
import streamlit as st

st.set_page_config(page_title="AI Readiness Survey", page_icon="🧠", layout="centered")

conn = st.connection("snowflake")

SURVEY_URL = "https://sfworldtour-nqkwvryzwpxpejj2qvesze.streamlit.app"

tab_qr, tab_survey = st.tabs(["📱 Scan QR Code", "📝 Take Survey"])

with tab_qr:
    st.markdown(
        "<h1 style='text-align:center;'>Scan to Take the Survey</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; font-size:1.2em;'>Point your phone camera at the QR code below</p>",
        unsafe_allow_html=True,
    )
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={SURVEY_URL}"
    st.markdown(
        f"<div style='text-align:center;'><img src='{qr_url}' width='400'></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align:center; margin-top:1em; color:gray;'>{SURVEY_URL}</p>",
        unsafe_allow_html=True,
    )

with tab_survey:
    st.title("🧠 AI Readiness Survey")
    st.markdown("Answer these quick questions to discover your AI leadership profile!")
    st.divider()

    # --- SECTION 1: Profile ---
    st.header("About You")

    q1_name = st.text_input("1. What is your name?")

    q2_role = st.selectbox(
        "2. What is your role/designation?",
        ["-- Select --", "Executive", "Manager", "Developer/Engineer", "Analyst", "Data Scientist", "Other"],
    )

    q3_age = st.selectbox(
        "3. What is your age group?",
        ["-- Select --", "20-30", "31-40", "41-50", "51+"],
    )

    st.divider()

    # --- SECTION 2: Scenario-Based Questions ---
    st.header("Scenarios")

    st.subheader("4. Perfectionism vs Pragmatism")
    st.markdown(
        "*Your project is 90% complete but the last 10% will take another 6 months. What do you do?*"
    )
    q4 = st.radio(
        "Choose one:",
        [
            "A) Ship it now, iterate later",
            "B) Wait — deliver it right or not at all",
            "C) Ship the 90% to a subset of users, keep building",
            "D) Renegotiate scope — cut the 10% entirely",
        ],
        key="q4",
        label_visibility="collapsed",
    )

    st.subheader("5. Risk Management")
    st.markdown(
        "*You're offered two projects: one with guaranteed moderate success, another with a 50% chance of massive impact or total failure. Which do you pick?*"
    )
    q5 = st.radio(
        "Choose one:",
        [
            "A) Guaranteed moderate success — stability matters",
            "B) The high-risk, high-reward one — go big",
            "C) Run both in parallel with a smaller team on the risky one",
            "D) Pick the risky one but build a fallback plan first",
        ],
        key="q5",
        label_visibility="collapsed",
    )

    st.subheader("6. Problem-Solving Style")
    st.markdown(
        "*A critical production system breaks at 2 AM. What's your first instinct?*"
    )
    q6 = st.radio(
        "Choose one:",
        [
            "A) Roll back to the last working version immediately",
            "B) Dig into logs to find root cause before touching anything",
            "C) Assemble the team — this needs all hands",
            "D) Apply a quick patch now, investigate properly tomorrow",
        ],
        key="q6",
        label_visibility="collapsed",
    )

    st.subheader("7. Handling Constraints & Priorities")
    st.markdown(
        "*Your boss adds an urgent task but you're already at full capacity. What do you do?*"
    )
    q7 = st.radio(
        "Choose one:",
        [
            "A) Accept it and work extra hours to deliver everything",
            "B) Push back — show what will be dropped if this is added",
            "C) Delegate one of my current tasks to make room",
            "D) Ask which of my current tasks they'd like me to deprioritize",
        ],
        key="q7",
        label_visibility="collapsed",
    )

    st.subheader("8. AI Mindset")
    st.markdown(
        "*AI can now do 60% of your job faster than you. What's your reaction?*"
    )
    q8 = st.radio(
        "Choose one:",
        [
            "A) Great — I'll focus on the 40% that needs human judgment",
            "B) I need to upskill fast so I stay ahead of AI",
            "C) I'll become the person who manages and directs the AI",
            "D) Concerned — what's my value if AI does most of it?",
        ],
        key="q8",
        label_visibility="collapsed",
    )

    st.subheader("9. Leadership Style")
    st.markdown(
        "*Two team members disagree on a technical approach. Both have valid points. How do you resolve it?*"
    )
    q9 = st.radio(
        "Choose one:",
        [
            "A) Let them prototype both — data will decide",
            "B) Make the call myself — someone has to decide",
            "C) Facilitate a discussion until they reach consensus",
            "D) Go with whoever has more experience in this area",
        ],
        key="q9",
        label_visibility="collapsed",
    )

    st.subheader("10. Learning Orientation")
    st.markdown(
        "*You have a free week with no deadlines. How do you spend it?*"
    )
    q10 = st.radio(
        "Choose one:",
        [
            "A) Learn a completely new skill outside my domain",
            "B) Go deep on something I already know — become the expert",
            "C) Build a side project to apply what I've been learning",
            "D) Rest and recharge — sustainability matters",
        ],
        key="q10",
        label_visibility="collapsed",
    )

    st.divider()

    # --- SUBMIT ---
    if st.button("Submit Survey", type="primary", use_container_width=True):
        if not q1_name.strip():
            st.error("Please enter your name.")
        elif q2_role == "-- Select --":
            st.error("Please select your role.")
        elif q3_age == "-- Select --":
            st.error("Please select your age group.")
        else:
            insert_sql = """
                INSERT INTO QR_SURVEY_DEMO.APP.SURVEY_RESPONSES
                (Q1_NAME, Q2_ROLE, Q3_AGE_GROUP,
                 Q4_PERFECTIONISM_VS_PRAGMATISM, Q5_RISK_MANAGEMENT,
                 Q6_PROBLEM_SOLVING, Q7_CONSTRAINTS_PRIORITIES,
                 Q8_AI_MINDSET, Q9_LEADERSHIP_STYLE, Q10_LEARNING_ORIENTATION)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur = conn.raw_connection.cursor()
            cur.execute(
                insert_sql,
                (
                    q1_name.strip(),
                    q2_role,
                    q3_age,
                    q4[0],
                    q5[0],
                    q6[0],
                    q7[0],
                    q8[0],
                    q9[0],
                    q10[0],
                ),
            )
            cur.close()
            st.success("Thank you! Your response has been recorded. 🎉")
            st.balloons()
