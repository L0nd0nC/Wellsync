import streamlit as st
from datetime import date, timedelta
from urllib.request import urlopen
from urllib.parse import urlencode
import xml.etree.ElementTree as ET
# ---------------- PAGE SETUP ----------------
st.set_page_config(
    page_title="WellSync",
    page_icon="💚",
    layout="wide"
)

st.title("WellSync")
st.caption("Your health, organized in one place.")
st.info(
    "WellSync is a student prototype for general health education, "
    "not a substitute for professional medical care."
)

# ---------------- SESSION DATA ----------------
if "profile" not in st.session_state:
    st.session_state.profile = None

if "symptom_logs" not in st.session_state:
    st.session_state.symptom_logs = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- NAVIGATION ----------------
profile_tab, symptoms_tab, chatbot_tab = st.tabs(
    ["Patient Profile", "Symptom Tracker", "AI Health Assistant"]
)

# ---------------- PATIENT PROFILE ----------------
with profile_tab:
    st.header("Your Patient Profile")
    st.write("Enter your information to create a profile.")

    with st.form("profile_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=1, max_value=120, value=18)
        sex = st.selectbox(
            "Sex (optional)",
            ["Prefer not to say", "Female", "Male", "Other"]
        )
        height = st.text_input("Height (e.g., 5 ft 4 in)")
        weight = st.text_input("Weight (e.g., 130 lb)")
        medical_info = st.text_area(
            "Relevant medical information (optional)",
            help="For this prototype, use fictional information."
        )

        save_profile = st.form_submit_button("Save Profile")

    if save_profile:
        if not name.strip():
            st.error("Please enter a name.")
        else:
            st.session_state.profile = {
                "name": name.strip(),
                "age": age,
                "sex": sex,
                "height": height,
                "weight": weight,
                "medical_info": medical_info
            }
            st.success("Profile saved for this session!")

    if st.session_state.profile:
        profile = st.session_state.profile
        st.subheader("Profile Summary")
        st.write(f"**Name:** {profile['name']}")
        st.write(f"**Age:** {profile['age']}")
        st.write(f"**Sex:** {profile['sex']}")
        st.write(f"**Height:** {profile['height'] or 'Not provided'}")
        st.write(f"**Weight:** {profile['weight'] or 'Not provided'}")
        st.write(
            f"**Relevant medical information:** "
            f"{profile['medical_info'] or 'Not provided'}"
        )

# ---------------- SYMPTOM TRACKER ----------------
with symptoms_tab:
    st.header("Symptom Tracker")
    st.write("Record symptoms and monitor them over time.")

    with st.form("symptom_form"):
        symptom = st.text_input("What symptom are you experiencing?")
        symptom_date = st.date_input("Date of symptom", value=date.today())
        severity = st.slider("Severity (1 = mild, 10 = severe)", 1, 10, 5)
        notes = st.text_area("Additional notes (optional)")

        log_symptom = st.form_submit_button("Log Symptom")

    if log_symptom:
        if not symptom.strip():
            st.error("Please enter a symptom.")
        else:
            entry = {
                "symptom": symptom.strip(),
                "date": symptom_date,
                "severity": severity,
                "notes": notes.strip()
            }
            st.session_state.symptom_logs.append(entry)
            st.success("Symptom logged successfully!")

    logs = st.session_state.symptom_logs

    if logs:
        st.subheader("Your Symptom History")

        # Show the most recent entries first
        for entry in reversed(logs):
            with st.container(border=True):
                st.write(f"**{entry['symptom']}**")
                st.write(f"Date: {entry['date']}")
                st.write(f"Severity: {entry['severity']}/10")
                if entry["notes"]:
                    st.write(f"Notes: {entry['notes']}")

        # Summarize entries from the past 7 calendar days
        today = date.today()
        week_start = today - timedelta(days=6)

        weekly_logs = [
            entry for entry in logs
            if week_start <= entry["date"] <= today
        ]

        st.subheader("Past 7 Days Summary")
        st.write(f"Period: {week_start} through {today}")

        if weekly_logs:
            st.write(f"Symptoms logged: {len(weekly_logs)}")

            average_severity = sum(
                entry["severity"] for entry in weekly_logs
            ) / len(weekly_logs)

            st.metric("Average reported severity",
                      f"{average_severity:.1f}/10")

            for entry in weekly_logs:
                st.write(
                    f"- {entry['date']}: {entry['symptom']} "
                    f"({entry['severity']}/10)"
                )
        else:
            st.write("No symptoms logged during the past 7 days.")

    else:
        st.info("Your symptom history will appear here.")

# ---------------- AI HEALTH CHATBOT ----------------
with chatbot_tab:
    st.header("WellSync Health Assistant")
    st.write(
        "Search trusted health resources to learn more "
        "about symptoms and health topics."
    )

    question = st.text_input(
        "What health topic would you like to learn about?",
        placeholder="Try headaches, allergies, or sleep"
    )

    if st.button("Search Health Articles"):

        if question.strip() == "":
            st.warning("Please enter a health topic.")

        else:
            search_url = (
                "https://wsearch.nlm.nih.gov/ws/query?"
                + urlencode({
                    "db": "healthTopics",
                    "term": question.strip()
                })
            )

            try:
                with st.spinner("Searching trusted health resources..."):
                    response = urlopen(search_url, timeout=15)
                    xml_data = response.read()

                root = ET.fromstring(xml_data)
                articles = root.findall(".//document")

                if articles:
                    st.subheader("Search Results")

                    shown = 0

                    for article in articles:
                        if shown >= 5:
                            break

                        title = ""
                        link = article.get("url", "")
                        summary = ""

                        for item in article.findall("content"):
                            name = item.get("name", "")
                            text = "".join(item.itertext())

                            if name == "title":
                                title = text

                            elif name == "snippet":
                                summary = text

                        if title and link:
                            st.markdown(f"### [{title}]({link})")

                            if summary:
                                st.write(summary)

                            st.divider()
                            shown += 1

                    if shown == 0:
                        st.info(
                            "No articles found. Try another health topic."
                        )

                    st.caption("Articles provided by MedlinePlus.")

                else:
                    st.info(
                        "No articles found. Try a different keyword."
                    )

            except Exception as error:
                st.error(
                    "We couldn't load the articles. "
                    "Check your internet connection and try again."
                )

    st.divider()

    st.subheader("Trusted Health Websites")

    st.markdown(
        "- [MedlinePlus](https://medlineplus.gov/)\n"
        "- [CDC](https://www.cdc.gov/)\n"
        "- [NHS](https://www.nhs.uk/)"
    )

    st.caption(
        "WellSync provides general health education, "
        "not medical diagnoses. For urgent symptoms, "
        "seek help from a trusted adult or medical professional."
    )
