
import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้า Dashboard
st.set_page_config(
    page_title="FACTORY PRODUCTION DASHBOARD ",
    page_icon="🏭",
    layout="wide"
)

# อ่านข้อมูลจาก Excel
@st.cache_data
def load_data():
    production_df = pd.read_excel(
        "Factory_Data.xlsx",
        sheet_name="Production Data"
    )

    downtime_df = pd.read_excel(
        "Factory_Data.xlsx",
        sheet_name="Downtime Log"
    )

    return production_df, downtime_df


# เรียกใช้ข้อมูล
df, downtime_df = load_data()

# =================================
# SIDEBAR FILTER
# =================================

st.sidebar.markdown(
    """
    <h2 style="color:#166534;">
        ⚙️ SIDEBAR FILTER
    </h2>
    <p style="color:#64748B; font-size:13px;">
        Select production conditions
    </p>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

# เลือกวันที่
selected_date = st.sidebar.date_input(
    "Select Date",
    value=pd.to_datetime(df["Date"]).max()
)

# เลือกกะการทำงาน
shift_list = ["All"] + sorted(df["Shift"].dropna().unique().tolist())

selected_shift = st.sidebar.selectbox(
    "Select Shift",
    shift_list
)

# เลือกไลน์การผลิต
line_list = ["All"] + sorted(df["Line"].dropna().unique().tolist())

selected_line = st.sidebar.selectbox(
    "Select Production Line",
    line_list
)

# กรองข้อมูล
filtered_df = df.copy()

filtered_df["Date"] = pd.to_datetime(filtered_df["Date"]).dt.date

filtered_df = filtered_df[
    filtered_df["Date"] == selected_date
]

if selected_shift != "All":
    filtered_df = filtered_df[
        filtered_df["Shift"] == selected_shift
    ]

if selected_line != "All":
    filtered_df = filtered_df[
        filtered_df["Line"] == selected_line
    ]

# =================================
# FILTER DOWNTIME DATA
# =================================

filtered_downtime_df = downtime_df.copy()

filtered_downtime_df["Date"] = pd.to_datetime(
    filtered_downtime_df["Date"]
).dt.date

filtered_downtime_df = filtered_downtime_df[
    filtered_downtime_df["Date"] == selected_date
]

if selected_shift != "All":
    filtered_downtime_df = filtered_downtime_df[
        filtered_downtime_df["Shift"] == selected_shift
    ]

if selected_line != "All":
    filtered_downtime_df = filtered_downtime_df[
        filtered_downtime_df["Line"] == selected_line
    ]

# =================================
# KPI CALCULATION
# =================================

total_target = filtered_df["Target"].sum()
total_produced = filtered_df["Produced"].sum()
total_defect = filtered_df["Defect"].sum()

achievement = (
    total_produced / total_target * 100
    if total_target > 0 else 0
)

# =================================
# DASHBOARD HEADER
# =================================

st.markdown(
    """
    <div style="
        background-color: #166534;
        padding: 22px 28px;
        border-radius: 12px;
        margin-bottom: 20px;
    ">
        <h1 style="
            color: white;
            margin: 0;
            font-size: 30px;
        ">
            🏭 FACTORY PRODUCTION DASHBOARD
        </h1>
        <p style="
            color: #DCFCE7;
            margin: 6px 0 0 0;
            font-size: 15px;
        ">
            Production Performance & Quality Monitoring
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("Production Overview")

# =================================
# KPI CARDS
# =================================

# =================================
# KPI CARDS
# =================================

st.subheader("Production Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("🎯 **TOTAL TARGET**")
    st.metric(
        label="Production Goal",
        value=f"{total_target:,.0f}"
    )

with col2:
    st.markdown("🏭 **TOTAL PRODUCED**")
    st.metric(
        label="Actual Production",
        value=f"{total_produced:,.0f}"
    )

with col3:
    st.markdown("📈 **ACHIEVEMENT**")
    st.metric(
        label="Target Achievement",
        value=f"{achievement:.2f}%"
    )

with col4:
    st.markdown("⚠️ **DEFECT QTY**")
    st.metric(
        label="Defect Quantity",
        value=f"{total_defect:,.0f}"
    )

# =================================
# PRODUCTION VS TARGET CHART
# =================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("Production vs Target")

    chart_data = filtered_df.groupby("Line")[
        ["Target", "Produced"]
    ].sum().reset_index()

    fig = px.bar(
    chart_data,
    x="Line",
    y=["Target", "Produced"],
    barmode="group",
    title="Production Comparison by Line",
    color_discrete_map={
        "Target": "#1565C0",
        "Produced": "#F97316"
    }
)

    st.plotly_chart(
    fig,
    use_container_width=True,
    height=250
)

# =================================
# DOWNTIME ANALYSIS
# =================================

with col2:
    st.subheader("Downtime Analysis")

    downtime_chart = filtered_downtime_df.groupby(
        "Reason"
    )["Downtime_Minutes"].sum().reset_index()

    fig_downtime = px.bar(
    downtime_chart,
    x="Reason",
    y="Downtime_Minutes",
    title="Downtime by Reason",
    labels={
        "Reason": "Downtime Reason",
        "Downtime_Minutes": "Downtime (Minutes)"
    },
    text_auto=True,
    color_discrete_sequence=["#1565C0"]
)
    st.plotly_chart(
        fig_downtime,
        use_container_width=True,
        height=250
    )

# =================================
# DEFECT ANALYSIS & PRODUCTION TABLE
# =================================

col3, col4 = st.columns(2)

# ฝั่งซ้าย: Defect Analysis
with col3:

    st.subheader("Defect Analysis")

    defect_chart = filtered_df.groupby(
        "Machine"
    )["Defect"].sum().reset_index()

    fig_defect = px.bar(
        defect_chart,
        x="Machine",
        y="Defect",
        title="Defect by Machine",
        text_auto=True
    )

    st.plotly_chart(
        fig_defect,
        use_container_width=True,
        height=250
    )


# ฝั่งขวา: Production Data Details
with col4:

    st.subheader("📋 Production Data Details")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=250,
        column_config={
            "Date": st.column_config.DateColumn(
                "Production Date",
                format="DD/MM/YYYY"
            ),
            "Target": st.column_config.NumberColumn(
                "Target",
                format="%d"
            ),
            "Produced": st.column_config.NumberColumn(
                "Produced",
                format="%d"
            ),
            "Defect": st.column_config.NumberColumn(
                "Defect",
                format="%d"
            )
        }
    )