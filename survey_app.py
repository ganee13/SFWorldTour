# External Streamlit survey app with QR code generation and Snowflake backend
# Co-authored with CoCo

import streamlit as st
import uuid
import json
import urllib.parse


def load_questions(session):
    result = session.sql(
        "SELECT QUESTION_ID, QUESTION_TEXT, OPTIONS FROM QUESTIONS WHERE IS_ACTIVE = TRUE ORDER BY QUESTION_ID"
    ).collect()
    questions = []
    for row in result:
        options = row["OPTIONS"]
        if isinstance(options, str):
            options = json.loads(options)
        questions.append({
            "id": row["QUESTION_ID"],
            "text": row["QUESTION_TEXT"],
            "options": options,
        })
    return questions


def submit_responses(session, session_id, answers):
    for question_id, selected_option in answers.items():
        session.sql(
            f"INSERT INTO RESPONSES (SESSION_ID, QUESTION_ID, SELECTED_OPTION) "
            f"VALUES ('{session_id}', {question_id}, '{selected_option}')"
        ).collect()


def generate_qr_code_url(data):
    encoded = urllib.parse.quote(data)
    return f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={encoded}"


# --- App Configuration ---
st.set_page_config(page_title="Survey", layout="centered")

# Unique session per respondent
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Switch between admin (QR display) and survey mode via query param
mode = st.query_params.get("mode", "survey")

# Connect to Snowflake using Streamlit's built-in connection
conn = st.connection("snowflake")
session = conn.session()

if mode == "admin":
    # --- ADMIN VIEW: Display QR code on projector ---
    st.title("Survey QR Code")
    st.write("Display this on screen. Audience scans to open the survey.")

    app_url = st.secrets.get("app_url", "https://your-app-name.streamlit.app")
    survey_url = f"{app_url}?mode=survey"

    qr_url = generate_qr_code_url(survey_url)
    st.image(qr_url, caption="Scan to take the survey", width=400)
    st.code(survey_url, language=None)

    # Live response counter
    st.subheader("Live Responses")
    count = session.sql("SELECT COUNT(DISTINCT SESSION_ID) AS CNT FROM RESPONSES").collect()[0]["CNT"]
    st.metric("Total Respondents", count)

    if st.button("Refresh"):
        st.rerun()

elif st.session_state.submitted:
    # --- THANK YOU SCREEN ---
    st.title("Thank you!")
    st.success("Your responses have been recorded.")

else:
    # --- SURVEY FORM (what audience sees on their phone) ---
    st.title("Quick Survey")
    st.write("Please answer the following questions:")

    questions = load_questions(session)

    if not questions:
        st.warning("No questions available.")
    else:
        answers = {}
        with st.form("survey_form"):
            for q in questions:
                answer = st.radio(
                    q["text"],
                    options=q["options"],
                    key=f"q_{q['id']}",
                    index=None,
                )
                answers[q["id"]] = answer

            submitted = st.form_submit_button("Submit", type="primary")

            if submitted:
                unanswered = [q["text"] for q in questions if answers.get(q["id"]) is None]
                if unanswered:
                    st.error(f"Please answer all questions. Missing: {len(unanswered)}")
                else:
                    submit_responses(session, st.session_state.session_id, answers)
                    st.session_state.submitted = True
                    st.rerun()
