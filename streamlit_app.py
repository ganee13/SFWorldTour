# Banking AI Readiness Survey - Agentic banking, data residency, and AI trust assessment
# Co-authored with CoCo
import snowflake.connector
snowflake.connector.paramstyle = "qmark"
import streamlit as st
from datetime import datetime, timezone

st.set_page_config(page_title="Agentic Banking Survey", page_icon="🏦", layout="centered")

conn = st.connection("snowflake")

SURVEY_URL = "https://sfworldtour-nqkwvryzwpxpejj2qvesze.streamlit.app"
SURVEY_DIRECT_URL = f"{SURVEY_URL}/?mode=survey"

mode = st.query_params.get("mode", "qr")

if mode == "qr":
    st.markdown(
        "<h1 style='text-align:center;'>🏦 The Agentic Bank</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; font-size:1.2em;'>How do you deploy a reasoning engine inside a bank<br>without violating data residency or triggering an infosec nightmare?</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; font-size:1.1em; color:gray;'>Scan to share your perspective 👇</p>",
        unsafe_allow_html=True,
    )
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={SURVEY_DIRECT_URL}"
    st.markdown(
        f"<div style='text-align:center; margin:1.5em 0;'><img src='{qr_url}' width='350'></div>",
        unsafe_allow_html=True,
    )

    cur = conn.raw_connection.cursor()
    cur.execute("SELECT COUNT(*) FROM QR_SURVEY_DEMO.APP.SURVEY_RESPONSES")
    count = cur.fetchone()[0]
    cur.close()
    st.markdown(
        f"<h2 style='text-align:center;'>📊 {count} responses</h2>",
        unsafe_allow_html=True,
    )

else:
    # --- BEHAVIORAL TRACKING ---
    if "survey_start_time" not in st.session_state:
        st.session_state.survey_start_time = datetime.now(timezone.utc)
        st.session_state.num_interactions = 0
        st.session_state.submitted = False

    st.session_state.num_interactions += 1

    if st.session_state.submitted:
        st.title("🏦 The Agentic Bank")
        st.success("You've submitted your response. Thank you!")
        cur = conn.raw_connection.cursor()
        cur.execute("SELECT COUNT(*) FROM QR_SURVEY_DEMO.APP.SURVEY_RESPONSES")
        count = cur.fetchone()[0]
        cur.close()
        st.metric("Total Responses", count)
        st.stop()

    st.title("🏦 The Agentic Bank")
    st.markdown("*How ready is your organization to deploy AI reasoning engines in regulated environments?*")

    cur = conn.raw_connection.cursor()
    cur.execute("SELECT COUNT(*) FROM QR_SURVEY_DEMO.APP.SURVEY_RESPONSES")
    count = cur.fetchone()[0]
    cur.close()
    st.info(f"📊 **{count}** responses so far")

    st.divider()

    # --- SECTION 1: Profile ---
    st.header("About You")

    q1_name = st.text_input("1. What is your name?")

    q2_role = st.selectbox(
        "2. What is your role?",
        ["-- Select --", "CTO/CIO", "CISO/InfoSec", "Data/AI Lead", "Developer/Engineer", "Risk/Compliance", "Business/Product"],
    )

    q3_inst = st.selectbox(
        "3. What type of institution?",
        ["-- Select --", "Global Bank", "Regional Bank", "Fintech", "Insurance", "Payment Provider", "Regulator/Consultant"],
    )

    st.divider()

    # --- SECTION 2: Banking AI Scenarios ---
    st.header("Scenarios")

    st.subheader("4. Data Residency vs AI Capability")
    st.markdown("*Your AI vendor offers a 10x better model, but data must leave your jurisdiction for inference. What do you do?*")
    q4 = st.radio(
        "q4", label_visibility="collapsed",
        options=[
            "A) Reject — data residency is non-negotiable, full stop",
            "B) Explore — if we can anonymize/tokenize the data first",
            "C) Accept — with contractual safeguards and encryption in transit",
            "D) Build our own — train in-house to avoid the problem",
        ],
        key="q4",
    )

    st.subheader("5. InfoSec vs Speed of Deployment")
    st.markdown("*Your team has a working AI prototype that saves $10M/year, but InfoSec needs 6 months to approve. What's your move?*")
    q5 = st.radio(
        "q5", label_visibility="collapsed",
        options=[
            "A) Wait — no shortcuts on security in banking",
            "B) Sandbox it — run in isolated environment while approval pending",
            "C) Escalate to the board — ROI justifies fast-tracking",
            "D) Redesign — fit within already-approved security boundaries",
        ],
        key="q5",
    )

    st.subheader("6. Trust in AI-Generated Code")
    st.markdown("*An AI assistant generates SQL that touches your production customer data. How do you feel?*")
    q6 = st.radio(
        "q6", label_visibility="collapsed",
        options=[
            "A) Uncomfortable — humans must write all production queries",
            "B) Fine — if there's a review step before execution",
            "C) Great — AI is faster and makes fewer errors than humans",
            "D) Depends — read-only fine, writes need human approval",
        ],
        key="q6",
    )

    st.subheader("7. Agentic AI in Banking")
    st.markdown("*An AI agent autonomously detects fraud, freezes accounts, and notifies customers — no human in the loop. Your reaction?*")
    q7 = st.radio(
        "q7", label_visibility="collapsed",
        options=[
            "A) Never — every customer action needs human approval",
            "B) Detection and alerting only — not taking action",
            "C) Yes for clear-cut cases (>99% confidence), humans for edge cases",
            "D) Absolutely — speed is everything in fraud",
        ],
        key="q7",
    )

    st.subheader("8. Where Should AI Live?")
    st.markdown("*Where should your bank's AI reasoning engine physically run?*")
    q8 = st.radio(
        "q8", label_visibility="collapsed",
        options=[
            "A) On-premises only — nothing leaves our data center",
            "B) Sovereign cloud — same compliance as on-prem",
            "C) Any major cloud — as long as it's contractually compliant",
            "D) Hybrid — sensitive on-prem, everything else in cloud",
        ],
        key="q8",
    )

    st.subheader("9. Biggest Blocker")
    st.markdown("*What's the #1 thing stopping your bank from deploying AI faster?*")
    q9 = st.radio(
        "q9", label_visibility="collapsed",
        options=[
            "A) Regulatory uncertainty — don't know what's allowed",
            "B) Data quality — our data isn't ready for AI",
            "C) Talent — can't hire fast enough",
            "D) Culture — leadership doesn't trust AI yet",
        ],
        key="q9",
    )

    st.subheader("10. The Agentic Bank in 3 Years")
    st.markdown("*In 3 years, what % of banking operations will be handled by AI agents?*")
    q10 = st.radio(
        "q10", label_visibility="collapsed",
        options=[
            "A) <10% — banking is too regulated for agents",
            "B) 10-30% — back-office and analytics only",
            "C) 30-60% — most routine operations, humans for exceptions",
            "D) >60% — AI agents will be the default",
        ],
        key="q10",
    )

    st.divider()

    # --- SECTION 3: AML Simulation ---
    st.header("🔍 AML Simulation")
    st.markdown("*You're now a fictional bank customer. Help us simulate money laundering detection.*")

    st.subheader("11. Your Transaction Profile")
    st.markdown("*Pick the transaction pattern that best describes your fictional customer:*")
    q11 = st.radio(
        "q11", label_visibility="collapsed",
        options=[
            "A) 5 transfers/month, avg $2,000, domestic only",
            "B) 15 transfers/month, avg $8,000, 3 countries",
            "C) 50+ transfers/month, avg $500, 10+ countries",
            "D) 2 transfers/month, avg $95,000, offshore jurisdictions",
        ],
        key="q11",
    )

    st.subheader("12. Sudden Behavior Change")
    st.markdown("*Your fictional customer suddenly changes behavior. What happened?*")
    q12 = st.radio(
        "q12", label_visibility="collapsed",
        options=[
            "A) Salary increase — transfers went from $2K to $5K monthly",
            "B) New business — 30 new payees added in one week",
            "C) Round-tripping — money sent to Country X, returned from Country Y same day",
            "D) Dormant account — no activity 11 months, then $200K outbound",
        ],
        key="q12",
    )

    st.subheader("13. AI Flags This — What Do You Do?")
    st.markdown("*AI flags this customer as suspicious (85% confidence). Your call:*")
    q13 = st.radio(
        "q13", label_visibility="collapsed",
        options=[
            "A) Auto-file SAR — 85% is good enough",
            "B) Escalate to human analyst for review",
            "C) Request more data — 85% isn't enough for action",
            "D) Ignore — too many false positives already",
        ],
        key="q13",
    )

    st.divider()

    # --- SUBMIT ---
    if st.button("Submit", type="primary", use_container_width=True):
        if not q1_name.strip():
            st.error("Please enter your name.")
        elif q2_role == "-- Select --":
            st.error("Please select your role.")
        elif q3_inst == "-- Select --":
            st.error("Please select your institution type.")
        else:
            submit_time = datetime.now(timezone.utc)
            duration_seconds = (submit_time - st.session_state.survey_start_time).total_seconds()
            num_interactions = st.session_state.num_interactions
            name_length = len(q1_name.strip())
            started_at = st.session_state.survey_start_time.strftime("%Y-%m-%d %H:%M:%S")

            insert_sql = """
                INSERT INTO QR_SURVEY_DEMO.APP.SURVEY_RESPONSES
                (Q1_NAME, Q2_ROLE, Q3_INSTITUTION,
                 Q4_DATA_RESIDENCY, Q5_SECURITY_VS_INNOVATION,
                 Q6_AI_CODE_TRUST, Q7_AGENTIC_AUTONOMY,
                 Q8_INFRASTRUCTURE, Q9_BIGGEST_BLOCKER, Q10_FUTURE_VISION,
                 Q11_TRANSACTION_PROFILE, Q12_BEHAVIOR_CHANGE, Q13_AML_DECISION,
                 STARTED_AT, DURATION_SECONDS, NUM_INTERACTIONS, NAME_LENGTH)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur = conn.raw_connection.cursor()
            cur.execute(
                insert_sql,
                (
                    q1_name.strip(),
                    q2_role,
                    q3_inst,
                    q4[0],
                    q5[0],
                    q6[0],
                    q7[0],
                    q8[0],
                    q9[0],
                    q10[0],
                    q11[0],
                    q12[0],
                    q13[0],
                    started_at,
                    duration_seconds,
                    num_interactions,
                    name_length,
                ),
            )
            cur.close()
            st.session_state.submitted = True
            st.success("Thank you! Your response has been recorded. 🎉")
            st.balloons()
