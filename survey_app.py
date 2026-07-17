# External Streamlit survey app with QR code generation and Snowflake backend
# Co-authored with CoCo

import streamlit as st
import snowflake.connector
import uuid
import json
import urllib.parse


def get_snowflake_connection():
    return snowflake.connector.connect(
        account=st.secrets["snowflake"]["account"],
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
    )


def load_questions(conn):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT QUESTION_ID, QUESTION_TEXT, OPTIONS FROM QUESTIONS WHERE IS_ACTIVE = TRUE ORDER BY QUESTION_ID"
    )
    questions = []
    for row in cursor:
        questions.append({
            "id": row[0],
            "text": row[1],
            "options": json.loads(row[2]) if isinstance(row[2], str) else row[2],
        })
    cursor.close()
    return questions


def submit_responses(conn, session_id, answers):
    cursor = conn.cursor()
    for question_id, selected_option in answers.items():
        cursor.execute(
            "INSERT INTO RESPONSES (SESSION_ID, QUESTION_ID, SELECTED_OPTION) VALUES (%s, %s, %s)",
            (session_id, question_id, selected_option),
        )
    conn.commit()
    cursor.close()


def generate_qr_code(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


# --- App Configuration ---
st.set_page_config(page_title="Survey", layout="centered")

# Unique session per respondent
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]

if "submitted" not in st.session_state:
    st.session_state.submitted = False

# Switch between admin (QR display) and survey mode via query param
mode = st.query_params.get("mode", "survey")

conn = get_snowflake_connection()

if mode == "admin":
    # --- ADMIN VIEW: Display QR code on projector ---
    st.title("Survey QR Code")
    st.write("Display this on screen. Audience scans to open the survey.")

    app_url = st.secrets.get("app_url", "https://your-app-name.streamlit.app")
    survey_url = f"{app_url}?mode=survey"

    qr_image = generate_qr_code(survey_url)
    st.image(qr_image, caption="Scan to take the survey", width=400)
    st.code(survey_url, language=None)

    # Live response counter
    st.subheader("Live Responses")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT SESSION_ID) FROM RESPONSES")
    count = cursor.fetchone()[0]
    cursor.close()
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

    questions = load_questions(conn)

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
                    submit_responses(conn, st.session_state.session_id, answers)
                    st.session_state.submitted = True
                    st.rerun()

conn.close()
