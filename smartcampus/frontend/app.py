import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from smart_campus import SmartCampusSystem, InvalidDirectoryError, EmptyDirectoryError

# Configure page visual boundaries
st.set_page_layout = "wide"
st.set_page_config(page_title="Smart Campus System", page_icon="🏛️", layout="wide")

# Persistent State Initialization
if "system" not in st.session_state:
    st.session_state.system = SmartCampusSystem()

sys = st.session_state.system

# Custom Dark Theme Styling Override 
st.markdown("""
    <style>
        stApp { background-color: #0e1117; color: #ffffff; }
        div[data-testid="stMetricValue"] { color: #2ecc71; font-weight: bold; }
        .stButton>button { background-color: #3498db; color: white; border-radius: 6px; width: 100%; }
        .stButton>button:hover { background-color: #2980b9; color: white; }
    </style>
""", unsafe_allow_html=True)

# Navigation Menu Sidebar
st.sidebar.title("🏛️ Smart Campus")
st.sidebar.caption("DSEC Mini Project Dashboard")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "NAVIGATION",
    ["Dashboard & Records", "Registration", "Enrollment", "Sort & Search", "Fee Calculator", "File Handling", "Dir Scanner", "Analytics"]
)

# =====================================================================
# MODULE COMPONENT VIEWS
# =====================================================================

if menu == "Dashboard & Records":
    st.title("🗃️ Active Student Registry Dashboard")
    if not sys.student_records:
        st.info("The live memory database is currently empty. Use the Registration tab to add profiles.")
    else:
        # Reformat dictionary layout directly into a clean display DataFrame
        table_rows = []
        for sid, info in sys.student_records.items():
            table_rows.append({
                "Student ID": sid,
                "Name": info["name"],
                "Age": info["age"],
                "Exam Score": info["grades"]["Exam Score"],
                "Grade": info["grades"]["Grade"],
                "Remark": info["grades"]["Remark"]
            })
        df_display = pd.DataFrame(table_rows)
        
        # Display high-level metrics widgets
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Profiles Enrolled", len(df_display))
        m2.metric("Cohort Class Average Marks", f"{df_display['Exam Score'].mean():.2f}")
        m3.metric("Top Achieving Marks", f"{df_display['Exam Score'].max():.1f}")
        
        st.markdown("### Active Student Database Records")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

elif menu == "Registration":
    st.title("📝 Student Registration Portal")
    with st.form("reg_form"):
        sid = st.number_input("Unique Student ID (Integer)", min_value=1, step=1, value=101)
        name = st.text_input("Full Student Name", placeholder="e.g. Rahul Sharma")
        age = st.number_input("Student Age", min_value=16, max_value=100, value=20)
        score = st.slider("Initial Exam Score Outcome", min_value=0.0, max_value=100.0, value=75.0)
        submitted = st.form_submit_button("Register & Evaluate Grade")
        
        if submitted:
            if not name.strip():
                st.error("Name field cannot remain empty.")
            else:
                success, msg = sys.register_student_backend(int(sid), name, int(age), score)
                if success: st.success(msg)
                else: st.error(msg)

elif menu == "Enrollment":
    st.title("📚 Course Enrollment Management")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("#### Add Course Profile")
        c_name = st.text_input("Course Module Name", placeholder="e.g. Mathematics")
        c_credits = st.number_input("Academic Credit Value", min_value=1, max_value=5, value=3)
        if st.button("Add Course to System"):
            if c_name:
                sys.add_course_backend(c_name.strip(), c_credits)
                st.success(f"Added module '{c_name}' successfully.")
    with col2:
        st.markdown("#### Current System Course Manifest")
        if not sys.courses:
            st.info("No courses currently configured in system state.")
        else:
            df_c = pd.DataFrame(list(sys.courses.items()), columns=["Course Name", "Credits"])
            st.dataframe(df_c, use_container_width=True, hide_index=True)

elif menu == "Sort & Search":
    st.title("🔍 Binary Search Engine Verification")
    if not sys.student_ids:
        st.warning("Database contains no registered tracking records.")
    else:
        st.write(f"**Live Unsorted ID Array Array:** {sys.student_ids}")
        sorted_ids = sorted(sys.student_ids)
        st.write(f"**Sorted Reference Search Array:** {sorted_ids}")
        
        target = st.number_input("Enter exact Student ID to search", min_value=1, step=1, value=int(sorted_ids[0]))
        if st.button("Execute High-Speed Binary Search"):
            idx = sys.binary_search(sorted_ids, target)
            st.info(f"Binary Search closed execution loops at sorted array index point: {idx}")
            if idx != -1:
                st.success(f"🎉 Student Found! Records: {sys.student_records[target]}")
            else:
                st.error("❌ The queried tracking key index is missing from system logs.")

elif menu == "Fee Calculator":
    st.title("🧮 Dynamic Student Fee Calculator")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Fee Calculator Parameters")
        tuition = st.number_input("Core Academic Tuition Fee (₹) *", min_value=0.0, value=85000.0, step=1000.0)
        
        opt_hostel = st.checkbox("Include Optional Hostel Accommodations")
        hostel = st.number_input("Hostel Fee (₹)", min_value=0.0, value=48000.0) if opt_hostel else 0.0
        
        opt_trans = st.checkbox("Include Optional Fleet Transportation Logistics")
        transport = st.number_input("Transportation Fee (₹)", min_value=0.0, value=12000.0) if opt_trans else 0.0
        
        calc_trigger = st.button("Calculate Aggregated Total Fee Invoice")
    
    with c2:
        st.markdown("#### Invoice Fee Breakdown Settlement Summary")
        if calc_trigger:
            total = sys.calculate_total_fees(tuition, hostel, transport)
            st.metric("Total Aggregated Invoice", f"₹ {total:,.2f}")
            
            # Simple Matplotlib pie chart breakdown
            labels, values = ["Tuition"], [tuition]
            if hostel > 0: labels.append("Hostel"); values.append(hostel)
            if transport > 0: labels.append("Transport"); values.append(transport)
            
            fig, ax = plt.subplots(figsize=(4, 4))
            fig.patch.set_facecolor('#0e1117')
            ax.set_facecolor('#0e1117')
            ax.pie(values, labels=labels, autopct='%1.1f%%', textprops={'color':"w"}, colors=["#3498db", "#2ecc71", "#f1c40f"])
            st.pyplot(fig)
        else:
            st.caption("Change metric variables or toggle checkbox modifiers to generate visualization breakdowns.")

elif menu == "File Handling":
    st.title("💾 File Records Serialization & Storage Engine")
    if st.button("Commit Local Context Data Matrices out to Disc Archive File"):
        sys.save_records_to_file()
        st.success(f"Data state flushed out smoothly to local storage file asset: '{sys.records_file}'")
    
    if os.path.exists(sys.records_file):
        st.markdown("#### Structured Raw File View Representation (`academic_records.txt`)")
        with open(sys.records_file, "r") as f:
            st.code(f.read(), language="json")

elif menu == "Dir Scanner":
    st.title("📂 Security Shell OS Directory File Tree Scanner")
    path_to_scan = st.text_input("Enter localized file directory string pathway to index", value=".")
    if st.button("Initiate System OS Scan Thread Pipeline"):
        try:
            contents = sys.scan_directory_backend(path_to_scan)
            st.success(f"Discovery phase resolved successfully. Found {len(contents)} active tracking element assets:")
            for item in contents:
                full_element_path = os.path.join(path_to_scan, item)
                prefix = "📁 [Folder]" if os.path.isdir(full_element_path) else "📄 [File]"
                st.text(f" └── {prefix} {item}")
        except InvalidDirectoryError as ide: st.error(f"Custom Directory Error: {ide}")
        except EmptyDirectoryError as ede: st.warning(f"Custom Directory Warning: {ede}")
        except PermissionError: st.error("Security System Exception: Insufficient processing access privileges.")
        except Exception as e: st.error(f"Unexpected structural breakdown error: {e}")

elif menu == "Analytics":
    st.title("📊 Data Analytics Performance Engineering Suite")
    if not os.path.exists(sys.analytics_file):
        st.error("Historical dataset data core metrics asset sheet missing.")
    else:
        df = pd.read_csv(sys.analytics_file)
        
        # Matrix calculations
        math_arr, sci_arr = df["Math_Score"].to_numpy(), df["Science_Score"].to_numpy()
        df["STEM_Average"] = np.mean([math_arr, sci_arr], axis=0)
        
        # Display metric data layout
        col_a, col_b = st.columns(2)
        col_a.metric("Global Cohort Attendance Average", f"{np.mean(df['Attendance_Rate']):.2f} %")
        col_b.dataframe(df.nlargest(3, 'STEM_Average')[['StudentID', 'STEM_Average']].rename(columns={'STEM_Average':'Top STEM Average'}), hide_index=True)
        
        st.markdown("#### Advanced Descriptive Aggregations Summary Matrix")
        st.dataframe(df[["Math_Score", "Science_Score", "English_Score", "Attendance_Rate"]].describe(), use_container_width=True)
        
        # Matplotlib Multi-Panel Pipeline Charts Rendering
        st.markdown("#### System Analytics Performance Distribution Profiling Graphs")
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
        fig.patch.set_facecolor('#1e2430')
        
        for ax in [ax1, ax2]:
            ax.set_facecolor('#1e2430')
            ax.tick_params(colors='white')
            ax.xaxis.label.set_color('white')
            ax.yaxis.label.set_color('white')
            ax.title.set_color('white')
            
        # Left graph setup
        ax1.hist(df['Attendance_Rate'], bins=10, color='#3498db', edgecolor='black')
        ax1.set_title('Distribution of Student Attendance Rates')
        ax1.set_xlabel('Attendance Percentage (%)')
        ax1.set_ylabel('Student Head Count')
        
        # Right graph setup
        ax2.scatter(df['Attendance_Rate'], df['Math_Score'], color='#e74c3c', alpha=0.8)
        ax2.set_title('Attendance vs. Mathematics Score Matrix')
        ax2.set_xlabel('Attendance Rate (%)')
        ax2.set_ylabel('Final Math Grade Score')
        ax2.grid(True, linestyle='--', alpha=0.3)
        
        st.pyplot(fig)
