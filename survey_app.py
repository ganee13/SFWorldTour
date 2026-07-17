# Lightweight survey app - pure Streamlit with no heavy dependencies at import time
# Co-authored with CoCo

import streamlit as st
import uuid
import json
import urllib.parse

st.set_page_config(page_title="Survey", layout="centered")

# --- Session state ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# --- Questions defined directly (no DB call needed at startup) ---
QUESTIONS = [
    {"id": 1, "text": "How familiar are you with Snowflake?", "options": ["Not at all", "Somewhat", "Very familiar", "Expert"]},
    {"id": 2, "text": "What is your primary use case?", "options": ["Data Engineering", "Data Science", "Analytics", "Application Development"]},
    {"id": 3, "text": "Which cloud provider do you primarily use?", "options": ["AWS", "Azure", "GCP", "Multi-cloud"]},
    {"id": 4, "text": "How large is your data team?", "options": ["1-5", "6-20", "21-50", "50+"]},
]


def get_snowflake_session():
    """Lazy-load Snowflake connection only when needed (not at import time)."""
    conn = st.connection("snowflake")
    return conn.session()


def save_responses(session_id, answers):
    """Save responses to Snowflake using raw connector (bypasses Snowpark entirely for DML)."""
    try:
        import snowflake.connector
        raw_conn = snowflake.connector.connect(
            account=st.secrets["connections"]["snowflake"]["account"],
            user=st.secrets["connections"]["snowflake"]["user"],
            password=st.secrets["connections"]["snowflake"]["password"],
            warehouse=st.secrets["connections"]["snowflake"]["warehouse"],
            database=st.secrets["connections"]["snowflake"]["database"],
            schema=st.secrets["connections"]["snowflake"]["schema"],
        )
        cursor = raw_conn.cursor()
        for question_id, selected_option in answers.items():
            cursor.execute(
                "INSERT INTO Smoothies.PUBLIC.RESPONSES (SESSION_ID, QUESTION_ID, SELECTED_OPTION) "
                "VALUES (%s, %s, %s)",
                (session_id, int(question_id), selected_option),
            )
        cursor.close()
        raw_conn.close()
        return True
    except Exception as e:
        st.error(f"Failed to save: {e}")
        return False


def generate_qr_code_url(data):
    encoded = urllib.parse.quote(data)
    return f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={encoded}"


# --- Routing ---
mode = st.query_params.get("mode", "survey")

if mode == "admin":
    st.title("Survey QR Code")
    st.write("Display this QR code on screen. Audience scans to answer questions on their phone.")

    app_url = st.secrets.get("app_url", "https://sfworldtour-atjkg9jtrsapp9nytiqrmpn.streamlit.app")
    survey_url = f"{app_url}?mode=survey"

    qr_url = generate_qr_code_url(survey_url)
    st.image(qr_url, caption="Scan to take the survey", width=400)
    st.code(survey_url, language=None)

    st.divider()
    st.subheader("Live Responses")
    try:
        session = get_snowflake_session()
        count = session.sql("SELECT COUNT(DISTINCT SESSION_ID) AS CNT FROM Smoothies.PUBLIC.RESPONSES").collect()[0]["CNT"]
        st.metric("Total Respondents", count)
    except Exception:
        st.info("Connect to Snowflake to see live count.")

    if st.button("Refresh"):
        st.rerun()

elif st.session_state.submitted:
    st.title("Thank you!")
    st.success("Your responses have been recorded successfully.")
    st.balloons()

else:
    st.title("Quick Survey")
    st.write("Please answer the following questions:")

    answers = {}
    with st.form("survey_form"):
        for q in QUESTIONS:
            answer = st.radio(
                q["text"],
                options=q["options"],
                key=f"q_{q['id']}",
                index=None,
            )
            answers[q["id"]] = answer

        submitted = st.form_submit_button("Submit", type="primary", use_container_width=True)

        if submitted:
            unanswered = [q["text"] for q in QUESTIONS if answers.get(q["id"]) is None]
            if unanswered:
                st.error(f"Please answer all questions ({len(unanswered)} remaining)")
            else:
                if save_responses(st.session_state.session_id, answers):
                    st.session_state.submitted = True
                    st.rerun()
