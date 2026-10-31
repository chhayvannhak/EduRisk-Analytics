import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# Page Configuration
st.set_page_config(
    page_title="EduRisk Analytics - Lab 04",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Enhanced Native Pandas Styling
def style_risk_level(val):
    if val == "High Risk":
        return "background-color: #ff4b4b33; color: #ff4b4b; font-weight: bold;"
    elif val == "Medium Risk":
        return "background-color: #ffa42133; color: #ffa421; font-weight: bold;"
    elif val == "Low Risk":
        return "background-color: #21c35433; color: #21c354; font-weight: bold;"
    return ""


def style_dataframe(df):
    grad_cols = [c for c in ["Score", "Attendance", "Study Hours"] if c in df.columns]
    styler = df.style
    if grad_cols:
        styler = styler.background_gradient(subset=grad_cols, cmap="Blues", vmin=0, vmax=100)
    if "Risk Level" in df.columns:
        styler = styler.map(style_risk_level, subset=["Risk Level"])
    return styler


# Load Dataset from CSV
def load_student_data():
    try:
        data = pd.read_csv("students.csv")
        return data
    except FileNotFoundError:
        st.error(
            "students.csv was not found. Please place it in the same folder as appp.py."
        )
        st.stop()


student_df = load_student_data()


# Risk Calculation Logic
def get_risk_level(score, attendance):
    if score < 60 or attendance < 60:
        return "High Risk"
    elif score < 75 or attendance < 75:
        return "Medium Risk"
    else:
        return "Low Risk"


student_df["Risk Level"] = student_df.apply(
    lambda row: get_risk_level(row["Score"], row["Attendance"]),
    axis=1
)

# Initialize Session State for Lab 04
if "risk_history" not in st.session_state:
    st.session_state["risk_history"] = []

# ---------------------------------------------------------
# Modern "Option Menu" Sidebar
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎓 EduRisk Menu")
    selected_page = option_menu(
        menu_title=None,
        options=["Home", "Dashboard", "Student Data", "Risk Checker", "About"],
        icons=["house", "bar-chart-fill", "table", "shield-check", "info-circle"],
        menu_icon="menu-button-wide",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "white", "font-size": "16px"},
            "nav-link": {
                "font-size": "15px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#262730"
            },
            "nav-link-selected": {"background-color": "#ff4b4b"},
        }
    )

# ---------------------------------------------------------
# Page Implementations
# ---------------------------------------------------------
if selected_page == "Home":
    st.title("🎓 EduRisk Analytics")
    st.markdown("#### *Reliable Risk Checker with Forms and Session State*")
    st.divider()

    col1, col2 = st.columns([2, 1.2])
    with col1:
        st.write("Welcome to **Lab 04**.")
        st.write(
            "In this lab, the app improves the Risk Checker page using "
            "Streamlit forms, input validation, and session state."
        )
        st.success("✨ Lab 04 app is running successfully!")

    with col2:
        with st.container(border=True):
            st.info(
                "💡 **Quick Tip:** \n\nNavigate to the **Risk Checker** via the "
                "sidebar menu to test form validation and session history."
            )
            st.metric("Total Enrolled Students", len(student_df))

elif selected_page == "Dashboard":
    st.title("Dashboard Prototype")
    st.write(
        "This dashboard gives a quick overview of student performance "
        "using data loaded from `students.csv`."
    )
    st.write("")

    with st.container(border=True):
        st.markdown("### ⚙️ Filter Controls")
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

        with filter_col1:
            courses = ["All"] + list(student_df["Course"].unique()) if "Course" in student_df.columns else ["All"]
            selected_course = st.selectbox("Select Course", courses)
        with filter_col2:
            selected_risk = st.selectbox("Select Risk Level", ["All", "Low Risk", "Medium Risk", "High Risk"])
        with filter_col3:
            min_attendance = st.slider("Minimum Attendance", 0, 100, 0)
        with filter_col4:
            min_score = st.slider("Minimum Score", 0, 100, 0)

    filtered_df = student_df.copy()
    if selected_course != "All" and "Course" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["Course"] == selected_course]
    if selected_risk != "All":
        filtered_df = filtered_df[filtered_df["Risk Level"] == selected_risk]
    filtered_df = filtered_df[filtered_df["Attendance"] >= min_attendance]
    filtered_df = filtered_df[filtered_df["Score"] >= min_score]

    st.divider()

    total_students = len(filtered_df)
    average_score = filtered_df["Score"].mean() if not filtered_df.empty else 0
    average_attendance = filtered_df["Attendance"].mean() if not filtered_df.empty else 0
    high_risk_students = filtered_df[filtered_df["Risk Level"] == "High Risk"].shape[0]

    st.markdown("### Dashboard Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.metric("Students", total_students)
    with col2:
        with st.container(border=True):
            st.metric("Average Score", round(average_score, 2))
    with col3:
        with st.container(border=True):
            st.metric("Average Attendance", f"{round(average_attendance, 2)}%")
    with col4:
        with st.container(border=True):
            st.metric("High Risk", high_risk_students)

    st.write("")
    st.markdown("### Student Records")
    show_data = st.checkbox("Show Student Dataset", value=True)

    if show_data:
        st.dataframe(style_dataframe(filtered_df), use_container_width=True, hide_index=True)
        st.download_button(
            label="Download Filtered Data",
            data=filtered_df.to_csv(index=False),
            file_name="filtered_student_data.csv",
            mime="text/csv",
            type="primary"
        )

    st.divider()
    st.markdown("### Charts")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        with st.container(border=True):
            st.markdown("**Student Score Chart**")
            if not filtered_df.empty:
                score_chart = filtered_df.set_index("Student Name")["Score"]
                st.bar_chart(score_chart, color="#ff4b4b")
            else:
                st.warning("No data available.")

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Course Count**")
            if not filtered_df.empty and "Course" in filtered_df.columns:
                course_count = filtered_df["Course"].value_counts()
                st.bar_chart(course_count, color="#1f77b4")
            else:
                st.warning("No data available.")

    st.info(
        "Ethics Reminder: Academic monitoring should support students, "
        "not label or punish them."
    )

elif selected_page == "Student Data":
    st.title("Student Data")
    st.write("This page displays and inspects the dataset loaded from `students.csv`.")
    st.divider()

    st.markdown("### 🔍 Data Inspection")
    insp_col1, insp_col2, insp_col3 = st.columns([1, 1, 2])

    with insp_col1:
        with st.container(border=True):
            st.metric("Total Rows", student_df.shape[0])
    with insp_col2:
        with st.container(border=True):
            st.metric("Total Columns", student_df.shape[1])
    with insp_col3:
        with st.container(border=True):
            st.write("**Column Names:**")
            st.code(", ".join(student_df.columns.tolist()), language="text")

    st.markdown("#### First 5 Rows")
    st.dataframe(style_dataframe(student_df.head()), use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### 📋 Full Student Dataset")
    st.dataframe(style_dataframe(student_df), use_container_width=True, hide_index=True)

elif selected_page == "Risk Checker":
    st.title("Single Student Risk Checker")
    st.write(
        "Enter student information to check risk level. "
        "The result is based on score and attendance."
    )
    st.info(
        "This tool is for academic support. Risk results should help students, "
        "not label or punish them."
    )
    st.divider()

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        with st.container(border=True):
            st.markdown("### 📝 Student Input")
            with st.form("risk_checker_form"):
                input_name = st.text_input("Student Name")
                input_score = st.number_input("Score", 0, 100, 50, step=1)
                input_attendance = st.number_input("Attendance", 0, 100, 50, step=1)

                submitted = st.form_submit_button(
                    "Check Risk",
                    type="primary",
                    use_container_width=True
                )

    with col2:
        if submitted:
            if input_name.strip() == "":
                st.warning("Please enter the student name.")
            else:
                clean_name = input_name.strip()
                risk_result = get_risk_level(input_score, input_attendance)

                result = {
                    "Student Name": clean_name,
                    "Score": input_score,
                    "Attendance": input_attendance,
                    "Risk Level": risk_result
                }
                st.session_state["risk_history"].append(result)

                with st.container(border=True):
                    st.markdown(f"### 📊 Results: {clean_name}")

                    st.write("**Course Score:**")
                    st.progress(input_score / 100, text=f"{input_score}/100")

                    st.write("**Attendance:**")
                    st.progress(input_attendance / 100, text=f"{input_attendance}%")

                    st.write("")

                    if risk_result == "Low Risk":
                        st.success("Risk Level: Low Risk")
                        st.write("Student appears on track.")
                    elif risk_result == "Medium Risk":
                        st.warning("Risk Level: Medium Risk")
                        st.write("Monitor progress and provide guidance.")
                    else:
                        st.error("Risk Level: High Risk")
                        st.write("Student may need additional support.")

    st.divider()
    st.subheader("🕒 Recent Risk Checks")

    if len(st.session_state["risk_history"]) > 0:
        history_df = pd.DataFrame(st.session_state["risk_history"])
        st.dataframe(style_dataframe(history_df), use_container_width=True, hide_index=True)

        if st.button("Clear History", type="primary"):
            st.session_state["risk_history"] = []
            st.success("Risk check history cleared.")
            st.rerun()
    else:
        st.info("No risk checks yet.")

    st.warning(
        "Ethics Reminder: Risk results should be used as guidance for support, "
        "not as final judgment about a student."
    )

elif selected_page == "About":
    st.title("About")
    st.divider()

    with st.container(border=True):
        st.markdown("### 🎓 Project Details")
        st.write("**Lab:** This app is part of Lab 04.")
        st.write("**Course:** Web App Development for Data Science")
        st.write("**Project Theme:** EduRisk Analytics")
        st.write("**Topic:** Forms, Validation, and Session State")

    st.info(
        "This version improves the Risk Checker page using Streamlit forms, "
        "input validation, and session state."
    )

    st.warning(
        "Ethics Reminder: Student risk information should be used responsibly "
        "to support learning and student success."
    )