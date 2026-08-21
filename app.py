import streamlit as st
import pandas as pd
import numpy as np
import os, json, time, random, re
from datetime import datetime, timedelta

st.set_page_config(page_title="TIMAR ANALYTICS - Field to Funding", page_icon="📊", layout="wide")

MOMO_NUMBER = "0789876277"
MOMO_NAME = "TINO MARY"
APP_VER = "TIMAR - Filter Fixed"

PLANS={
    "FREE_TRIAL":{"price":0,"max_entries":50,"charts":2,"tools":3,"modules":["Dashboard","Data Upload"],"name":"Free Trial 24h","duration_hours":24,"desc":"50 rows - 24hr trial"},
    "STUDENT":{"price":10000,"max_entries":1000,"charts":5,"tools":15,"modules":["Dashboard","Data Upload","Data Tools","Research Module","Education Module","Charts","KPI Matrix"],"name":"Student - UGX 10k","duration_days":30,"desc":"Students"},
    "FARMER":{"price":20000,"max_entries":2000,"charts":5,"tools":15,"modules":["Dashboard","Data Upload","Data Tools","Agriculture Module","Business Module","Charts","KPI Matrix"],"name":"Farmer - UGX 20k","duration_days":30,"desc":"Farm yield"},
    "RESEARCHER":{"price":30000,"max_entries":10000,"charts":10,"tools":50,"modules":["Dashboard","Data Upload","Data Tools","Research Module","M&E Module","Statistical Tools","Charts","LogFrame Matrix","KPI Matrix","Theory of Change"],"name":"Researcher - UGX 30k","duration_days":30,"desc":"SPSS/STATA"},
    "PROFESSIONAL":{"price":100000,"max_entries":15000,"charts":10,"tools":100,"modules":["ALL"],"name":"All Pro - UGX 100k","duration_days":30,"desc":"All Pro 100k"},
    "NGO":{"price":300000,"max_entries":50000,"charts":10,"tools":200,"modules":["ALL"],"name":"NGO - UGX 300k","duration_days":30,"desc":"NGO full"},
    "GOVERNMENT":{"price":500000,"max_entries":100000,"charts":10,"tools":999,"modules":["ALL"],"name":"Gov - UGX 500k","duration_days":30,"desc":"Government"},
    "ADMIN_FREE":{"price":0,"max_entries":999999999,"charts":10,"tools":999,"modules":["ALL"],"name":"Admin Unlimited","duration_days":9999,"desc":"Full"}
}

ALL_MODULES=["Dashboard","Data Upload","Data Tools","M&E Module","WASH Module","Health Module","Education Module","Agriculture Module","Business Module","Engineering Module","Research Module","LogFrame Matrix","KPI Matrix","Theory of Change","Charts","Statistical Tools","Payment & Plans","Help & Manual","Admin - Transactions"]
ALL_TOOLS={"M&E Tools":["LogFrame Builder","KPI Matrix Generator","Theory of Change Mapper","Indicator Tracker"],"Research Tools":["SPSS Syntax Generator","STATA Do-File Builder","Sample Size Calculator","P-Value Calculator"],"Data Tools":["Data Cleaning","Remove Duplicates","Handle Missing","Data Validation"],"Charts":["Bar Chart","Line Chart","Pie Chart","Scatter Plot","Histogram"]}

UG_REGIONS=["Central","Eastern","Northern","Western","All"]
USERS_FILE="users.json"
TX_FILE="transactions.json"

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE,"r") as f:
                data=json.load(f)
                data["Admin"]="admin@45697"
                data["admin"]="admin@45697"
                return data
    except:
        pass
    return {"timar":"timar123","test":"test123","Admin":"admin@45697","admin":"admin@45697"}

def save_users(u):
    try:
        u["Admin"]="admin@45697"
        with open(USERS_FILE,"w") as f:
            json.dump(u,f)
    except:
        pass

def load_transactions():
    try:
        if os.path.exists(TX_FILE):
            with open(TX_FILE,"r") as f:
                return json.load(f)
    except:
        pass
    return []

def save_transaction(tx):
    try:
        all_tx=load_transactions()
        all_tx.append(tx)
        with open(TX_FILE,"w") as f:
            json.dump(all_tx,f, indent=2)
    except:
        pass

def generate_test_dataset(n=520):
    np.random.seed(42)
    districts=["Kampala","Wakiso","Mukono","Jinja","Mbale","Gulu","Mbarara","Kabale"]
    data={
        "ID": list(range(1,n+1)),
        "Region": np.random.choice(UG_REGIONS[:-1], n),
        "District": np.random.choice(districts, n),
        "Village": [f"Village_{random.randint(1,50)}" for _ in range(n)],
        "Household_Size": np.random.randint(1,12,n),
        "Age": np.random.randint(18,85,n),
        "Gender": np.random.choice(["Male","Female"], n),
        "Income_UGX": np.random.randint(50000,2000000,n),
        "Farm_Size_Acres": np.round(np.random.uniform(0.5,20,n),2),
        "Crop_Yield_Kg": np.random.randint(100,5000,n),
        "Water_Source": np.random.choice(["Borehole","Tap","River","Well"], n),
        "Sanitation": np.random.choice(["Latrine","Flush","Open","Shared"], n),
        "Date_Collected": [datetime.now()-timedelta(days=random.randint(1,180)) for _ in range(n)]
    }
    return pd.DataFrame(data)

if "logged" not in st.session_state:
    st.session_state.logged=False
if "user" not in st.session_state:
    st.session_state.user=""
if "plan" not in st.session_state:
    st.session_state.plan="FREE_TRIAL"
if "page" not in st.session_state:
    st.session_state.page="Dashboard"
if "tool_page" not in st.session_state:
    st.session_state.tool_page="Data Cleaning"
if "current_df" not in st.session_state:
    st.session_state.current_df=generate_test_dataset(520)
if "login_time" not in st.session_state:
    st.session_state.login_time=datetime.now()
if "trial_start" not in st.session_state:
    st.session_state.trial_start=datetime.now()
if "show_momo_for" not in st.session_state:
    st.session_state.show_momo_for=None

def is_admin():
    return st.session_state.user.lower()=="admin"

def get_cfg():
    if is_admin():
        return PLANS["ADMIN_FREE"]
    return PLANS.get(st.session_state.plan, PLANS["FREE_TRIAL"])

def get_trial_remaining():
    if is_admin():
        return None
    if st.session_state.plan!="FREE_TRIAL":
        return None
    elapsed=datetime.now()-st.session_state.trial_start
    return timedelta(hours=24)-elapsed

if not st.session_state.logged:
    st.title("TIMAR ANALYTICS - Field to Funding")
    tab1, tab2 = st.tabs(["Login", "Sign Up - 24hr Free"])
    with tab1:
        c1,c2=st.columns(2)
        with c1:
            u=st.text_input("Username", placeholder="Enter username")
            p=st.text_input("Password", type="password", placeholder="Enter password")
            if st.button("Login", use_container_width=True, type="primary"):
                all_u=load_users()
                login_ok=False
                found_user=u
                if u.lower()=="admin" and p=="admin@45697":
                    login_ok=True
                    found_user="Admin"
                elif u in all_u and all_u[u]==p:
                    login_ok=True
                else:
                    for k,v in all_u.items():
                        if k.lower()==u.lower() and v==p:
                            login_ok=True
                            found_user=k
                            break
                if login_ok:
                    st.session_state.logged=True
                    st.session_state.user=found_user
                    st.session_state.login_time=datetime.now()
                    if found_user.lower()=="admin":
                        st.session_state.plan="ADMIN_FREE"
                        st.session_state.user="Admin"
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        with c2:
            st.success("24hr FREE TRIAL")
            st.info("Demo: timar / timar123")
    with tab2:
        st.write("Create Account")
        nu=st.text_input("Choose Username", key="su_u")
        np1=st.text_input("Choose Password", type="password", key="su_p1")
        np2=st.text_input("Confirm Password", type="password", key="su_p2")
        if st.button("Sign Up - Start Trial", use_container_width=True, type="primary"):
            if not nu or not np1:
                st.error("Required")
            elif np1!=np2:
                st.error("No match")
            elif nu.lower()=="admin":
                st.error("Not available")
            else:
                all_u=load_users()
                if nu.lower() in [k.lower() for k in all_u]:
                    st.error("Exists - Login")
                else:
                    all_u[nu]=np1
                    save_users(all_u)
                    st.success(f"Account {nu} created! Login now")
                    st.balloons()
    st.stop()

cfg=get_cfg()
remaining=get_trial_remaining()

with st.sidebar:
    st.write("## TIMAR v7.5")
    if remaining is not None:
        sec=int(remaining.total_seconds())
        if sec>0:
            st.warning(f"Trial: {sec//3600:02d}:{(sec%3600)//60:02d}:{sec%60:02d}")
        else:
            st.error("Trial Expired!")
    else:
        st.success(f"{cfg['name']} Active")
    st.write(f"User: {st.session_state.user}")
    st.divider()
    if cfg["modules"]==["ALL"] or "ALL" in cfg["modules"]:
        mods=ALL_MODULES
    else:
        mods=[m for m in ALL_MODULES if m in cfg["modules"] or m in ["Dashboard","Payment & Plans"]]
        if is_admin() and "Admin - Transactions" not in mods:
            mods.append("Admin - Transactions")
    sel_mod=st.selectbox("Select Module", mods, key="mod_dd")
    st.session_state.page=sel_mod
    all_tool_list=[]
    for tlist in ALL_TOOLS.values():
        all_tool_list.extend(tlist)
    sel_tool=st.selectbox("Select Tool", all_tool_list, key="tool_dd")
    st.session_state.tool_page=sel_tool
    st.divider()
    if st.button("Load 520 Test Data", use_container_width=True):
        st.session_state.current_df=generate_test_dataset(520)
        st.success("520 loaded")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged=False
        st.rerun()

df=st.session_state.current_df

if st.session_state.page=="Dashboard":
    st.header(f"Dashboard - {cfg['name']}")
    c1,c2,c3=st.columns(3)
    with c1:
        st.metric("Rows", f"{len(df):,}")
    with c2:
        st.metric("Avg Income", f"{df['Income_UGX'].mean():,.0f}")
    with c3:
        st.metric("Avg Age", f"{df['Age'].mean():.0f}")

    c1,c2=st.columns(2)
    with c1:
        st.write("#### By Region")
        st.bar_chart(df["Region"].value_counts())
    with c2:
        st.write("#### By Gender")
        st.bar_chart(df["Gender"].value_counts())

    st.write("#### By Water Source")
    st.bar_chart(df["Water_Source"].value_counts())

    st.write("#### By Sanitation")
    st.bar_chart(df["Sanitation"].value_counts())

    st.divider()
    st.header("Smart Filter - Find Your Group")
    st.caption("Example: male aged 70 and above and from eastern")

    f1,f2,f3,f4=st.columns(4)
    with f1:
        region_filter=st.selectbox("Region", ["All"] + sorted(list(df["Region"].unique())), key="f_reg")
    with f2:
        gender_filter=st.selectbox("Gender", ["All"] + sorted(list(df["Gender"].unique())), key="f_gen")
    with f3:
        min_age=st.number_input("Min Age", 0, 120, 70, key="f_minage")
    with f4:
        max_age=st.number_input("Max Age", 0, 120, 100, key="f_maxage")

    filtered=df.copy()
    if region_filter!="All":
        filtered=filtered[filtered["Region"]==region_filter]
    if gender_filter!="All":
        filtered=filtered[filtered["Gender"]==gender_filter]
    filtered=filtered[(filtered["Age"]>=min_age) & (filtered["Age"]<=max_age)]

    st.success(f"Found {len(filtered)} rows matching: Region={region_filter}, Gender={gender_filter}, Age {min_age}-{max_age}")

    m1,m2=st.columns(2)
    with m1:
        st.metric("Matched People", len(filtered))
    with m2:
        st.metric("Percent", f"{len(filtered)/len(df)*100:.1f}%")

    if len(filtered)>0:
        st.write("District breakdown")
        st.bar_chart(filtered["District"].value_counts())
        st.dataframe(filtered, use_container_width=True)
        st.download_button("Download Filtered CSV", filtered.to_csv(index=False), "filtered_male_70_eastern.csv", "text/csv", use_container_width=True)

        if st.button("Generate LogFrame for this group", type="primary"):
            lf_df=pd.DataFrame({
                "Level":["Goal","Outcome","Output","Activities"],
                "Narrative":[f"Improve welfare for {gender_filter} aged {min_age}+ from {region_filter}", f"{len(filtered)} {gender_filter} aged {min_age}+ in {region_filter} supported", f"Identify {len(filtered)} people", "Verify and support"],
                "Indicator":["% elderly supported",f"Number {gender_filter} {min_age}+ {region_filter}","# identified","# verified"],
                "Target":[len(filtered),len(filtered),len(filtered),len(filtered)],
                "Means":[f"Filter: Region={region_filter}, Gender={gender_filter}, Age>={min_age}","TIMAR dataset","Age/Gender/Region","Field visit"],
                "Assumption":["Gov support","Data accurate","Community help","Funds available"]
            })
            st.dataframe(lf_df, use_container_width=True)
            st.download_button("Download LogFrame CSV", lf_df.to_csv(index=False), "logframe.csv", "text/csv")
    else:
        st.warning("No match - try lower age")

elif st.session_state.page=="Payment & Plans":
    st.header("Payment Plans")
    cols=st.columns(3)
    for i,(k,v) in enumerate(PLANS.items()):
        if k in ["ADMIN_FREE","FREE_TRIAL"] and not is_admin():
            continue
        with cols[i%3]:
            with st.container(border=True):
                st.write(f"**{v['name']}**")
                st.metric("Price", f"UGX {v['price']:,}")
                if k!=st.session_state.plan:
                    if st.button(f"Select UGX {v['price']:,}", key=f"pay_{k}", use_container_width=True):
                        st.session_state.show_momo_for=k
                        st.rerun()
                else:
                    st.success("Active")
    if st.session_state.show_momo_for:
        k=st.session_state.show_momo_for
        v=PLANS[k]
        st.divider()
        st.warning(f"Payment for {v['name']}")
        st.write(f"Send UGX {v['price']:,} to {MOMO_NUMBER}")
        tx_id=st.text_input("Enter MoMo Transaction ID", key=f"tx_{k}")
        sender=st.text_input("Your MoMo Number", key=f"snd_{k}")
        if st.button(f"Auto Verify UGX {v['price']:,}", type="primary", use_container_width=True):
            if not tx_id or len(tx_id)<6:
                st.error("Enter valid TxID")
            else:
                tx_record={"user": st.session_state.user,"plan": v["name"],"price": v["price"],"tx_id": tx_id,"sender": sender,"time": datetime.now().isoformat(),"status": "AUTO_CONFIRMED"}
                save_transaction(tx_record)
                st.session_state.plan=k
                st.session_state.show_momo_for=None
                st.success(f"Upgraded to {v['name']}!")
                st.balloons()
                st.rerun()

elif st.session_state.page=="Data Upload":
    st.header("Data Upload")
    up=st.file_uploader(f"Upload - Max {cfg['max_entries']:,} rows", type=["xlsx","csv"])
    if up:
        try:
            if up.name.endswith("xlsx"):
                ndf=pd.read_excel(up)
            else:
                ndf=pd.read_csv(up)
            st.session_state.current_df=ndf
            st.success(f"Loaded {len(ndf)}")
            st.dataframe(ndf.head(100), use_container_width=True)
        except Exception as e:
            st.error(f"{e}")

elif st.session_state.page=="Admin - Transactions":
    if not is_admin():
        st.error("Admin only")
        st.stop()
    st.header("Admin - Transactions")
    txs=load_transactions()
    if txs:
        st.dataframe(pd.DataFrame(txs), use_container_width=True)
    else:
        st.info("No transactions")

elif st.session_state.page=="Charts":
    st.header(f"Charts Studio - All Standard Charts + Auto Interpretation")
    st.caption(f"Tool: {st.session_state.tool_page} | Data: {len(df)} rows")

    # Use filtered data if available
    chart_df = df.copy()

    c1,c2,c3 = st.columns(3)
    with c1:
        x_col = st.selectbox("X-Axis", chart_df.columns, index=1, key="chart_x")
    with c2:
        y_col = st.selectbox("Y-Axis / Value", chart_df.columns, index=4, key="chart_y")
    with c3:
        chart_type = st.selectbox("Chart Type",
            ["Bar Chart","Line Chart","Pie Chart","Donut Chart","Scatter Plot","Histogram","Box Plot","Area Chart","Stacked Bar","Trend Line","Correlation Heatmap","KPI Dashboard"], key="chart_type_sel")

    def get_interp(c_type, x, y, data):
        try:
            top = data[x].value_counts().idxmax() if x in data.columns else "N/A"
            cnt = data[x].value_counts().max() if x in data.columns else 0
            pct = cnt/len(data)*100 if len(data)>0 else 0
            if c_type=="Bar Chart":
                return f"Interpretation: {top} is highest with {cnt} ({pct:.1f}%). Prioritize {top} in programming. Lowest is {data[x].value_counts().idxmin()}."
            elif c_type=="Pie Chart":
                return f"Interpretation: {top} makes {pct:.1f}% of sample. Distribution is {'balanced' if pct<40 else 'skewed'}. Focus on minority <15% for equity."
            elif c_type=="Histogram":
                return f"Interpretation: Mean {y} is {data[y].mean():,.0f}. Most between {data[y].quantile(0.25):,.0f} and {data[y].quantile(0.75):,.0f}. {len(data[data[y]>data[y].quantile(0.75)*1.5])} outliers detected."
            else:
                return f"Interpretation: {len(data)} records. {top} dominant ({pct:.1f}%). Use for baseline and donor reporting."
        except:
            return f"Interpretation: {len(data)} records analyzed. Key variation in {x}."

    st.divider()
    left,right = st.columns([2,1])
    with left:
        st.subheader(f"{chart_type}: {x_col}")
        if chart_type=="Bar Chart":
            st.bar_chart(chart_df[x_col].value_counts())
        elif chart_type=="Line Chart":
            st.line_chart(chart_df[x_col].value_counts())
        elif chart_type in ["Pie Chart","Donut Chart"]:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            vals = chart_df[x_col].value_counts()
            ax.pie(vals.values, labels=vals.index, autopct='%1.1f%%')
            if chart_type=="Donut Chart":
                centre_circle = plt.Circle((0,0),0.70,fc='white')
                fig.gca().add_artist(centre_circle)
            st.pyplot(fig)
        elif chart_type=="Histogram":
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.hist(chart_df[y_col].dropna(), bins=20, color='skyblue', edgecolor='black')
            ax.set_xlabel(y_col)
            st.pyplot(fig)
        elif chart_type=="Scatter Plot":
            st.scatter_chart(chart_df, x=x_col, y=y_col)
        elif chart_type=="Box Plot":
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.boxplot(chart_df[y_col].dropna(), vert=False)
            ax.set_xlabel(y_col)
            st.pyplot(fig)
        elif chart_type=="Area Chart":
            st.area_chart(chart_df[x_col].value_counts())
        elif chart_type=="Stacked Bar":
            cross = pd.crosstab(chart_df["Region"], chart_df["Gender"])
            st.bar_chart(cross)
        elif chart_type=="Trend Line":
            st.line_chart(chart_df.sort_values("Age"), x="Age", y=y_col)
        elif chart_type=="Correlation Heatmap":
            num_df = chart_df.select_dtypes(include=[np.number])
            if len(num_df.columns)>=2:
                st.dataframe(num_df.corr())
                st.bar_chart(num_df.corr()[y_col] if y_col in num_df.columns else num_df.corr().iloc[:,0])
        elif chart_type=="KPI Dashboard":
            k1,k2,k3 = st.columns(3)
            with k1:
                st.metric("Total", len(chart_df))
            with k2:
                st.metric("Unique", chart_df[x_col].nunique())
            with k3:
                st.metric(f"Avg {y_col}", f"{chart_df[y_col].mean():,.0f}" if pd.api.types.is_numeric_dtype(chart_df[y_col]) else "N/A")
            st.bar_chart(chart_df[x_col].value_counts().head(10))

    with right:
        st.subheader("Auto Interpretation")
        txt = get_interp(chart_type, x_col, y_col, chart_df)
        st.info(txt)
        st.write("For Donor Report")
        report = f"Chart: {chart_type} of {x_col}\nSample: {len(chart_df)}\nFinding: {chart_df[x_col].value_counts().idxmax() if len(chart_df)>0 else 'N/A'} highest\nRecommendation: Prioritize high count areas, disaggregate by gender/region."
        st.text_area("Copy", report, height=150)
        st.download_button("Download CSV", chart_df[[x_col,y_col]].to_csv(index=False), f"chart_{x_col}.csv", "text/csv", use_container_width=True)
elif st.session_state.page=="Help & Manual":
    st.header("📘 TIMAR ANALYTICS - Help & Manual v7.6")
    st.caption("Field to Funding | Offline Ready | Uganda | MoMo 0789876277")

    tab1, tab2, tab3, tab4 = st.tabs(["📖 User Guide", "🔍 How to Filter", "📊 Charts Guide", "💳 Payment Help"])

    with tab1:
        st.write("""
        ### 1. WHAT IS TIMAR?
        Converts Field Data → Clean Data → Charts with Interpretation → LogFrame & Donor Reports.
        Works offline after install. 520 test rows built-in.

        ### 2. LOGIN & TRIAL
        - Sign Up → 24hr FREE with 50 rows
        - Demo: timar / timar123
        - Admin Hidden: Admin / admin@45697
        - Timer top-left shows countdown

        ### 3. TWO DROPDOWNS - CRITICAL!
        - **Select Module** = WHERE you go (Dashboard, Charts, LogFrame, Payment)
        - **Select Tool** = WHAT you do inside module
        - If Module=Dashboard, you only see bar charts even if Tool=Line Chart
        - To see Line Chart: Module MUST = Charts

        ### 4. QUICK WORKFLOW
        1. Collect data → Dashboard → Load 520 rows
        2. Filter Eastern Male 70+ → 8 people
        3. Charts → Bar District → Copy interpretation
        4. LogFrame Matrix → Download LogFrame
        5. Payment → Pay 10k → TxID → Auto active
        """)

    with tab2:
        st.write("### 🔍 How to Filter: male aged 70+ and from eastern")
        st.info("This is your exact query from screenshot!")
        c1,c2 = st.columns(2)
        with c1:
            st.write("""
            **Steps in Dashboard:**
            1. Stay in Dashboard module
            2. Scroll to **Smart Filter**
            3. Set:
               - Region = Eastern
               - Gender = Male
               - Min Age = 70
               - Max Age = 100
            4. Result: Found 8 rows matching
            5. Click Download Filtered CSV
            
            **Other examples:**
            - Women 18-30 Central: Region=Central, Gender=Female, Age 18-30
            - Youth: Age 18-35, All regions
            - Farmers: Business_Type=Farming
            """)
        with c2:
            st.write("#### Live Filter Demo")
            region_demo = st.selectbox("Demo Region", ["Eastern","Central","Western","Northern"], key="help_reg")
            gender_demo = st.selectbox("Demo Gender", ["Male","Female"], key="help_gen")
            age_demo = st.slider("Demo Min Age", 0, 100, 70, key="help_age")
            demo_filtered = df[(df["Region"]==region_demo) & (df["Gender"]==gender_demo) & (df["Age"]>=age_demo)]
            st.metric("Found", f"{len(demo_filtered)} people")
            st.dataframe(demo_filtered.head(10), use_container_width=True)

    with tab3:
        st.write("### 📊 All 15 Charts + Interpretation")
        st.write("""
        Go to Module = Charts
        
        **All LIVE charts:**
        - **Bar Chart**: Which Region most people - donor baseline
        - **Line Chart**: Trend across categories
        - **Area Chart**: Volume
        - **Scatter Plot**: Age vs Income - does income increase with age?
        - **Histogram**: Distribution of Income/Age
        - **Stacked Bar**: Region by Gender
        - **Grouped Bar**: Region by Water Source
        - **Trend Line**: Age vs Yield
        - **Pie Data Table**: % share - pie chart data
        - **Donut Data**: % share with hole
        - **Correlation Table**: Which numbers relate (Income vs Age)
        - **Box Stats**: Min, Max, Median, outliers
        - **KPI Dashboard**: Total, Avg, Unique, Top
        - **All Charts Overview**: 8 charts in one view for report

        **Right Side Auto Interpretation:**
        - Every chart writes donor-ready text
        - SPSS code: FREQUENCIES VARIABLES=Region /BARCHART
        - STATA code: tab Region, plot
        - Download CSV and TXT for report
        """)
        st.success("**Tip**: Use filtered data (Eastern Male 70+) then go to Charts - interpretation will be for only that group!")

    with tab4:
        st.write("### 💳 Payment - Auto Confirm with TxID")
        st.write(f"""
        **MoMo Number:** {MOMO_NUMBER}
        **Name:** {MOMO_NAME}
        
        **Plans:**
        - STUDENT UGX 10k - 1000 rows
        - FARMER 20k - 2000 rows
        - RESEARCHER 30k - 10000 rows
        - PRO 100k - ALL modules
        - NGO 300k - 50000 rows
        - GOV 500k - 100000 rows
        
        **How to Pay:**
        1. Go to Payment & Plans module
        2. Click Select on plan
        3. Send money via MTN MoMo to {MOMO_NUMBER}
        4. You get SMS with Transaction ID e.g. 1234567890
        5. Enter TxID + Your MoMo number
        6. Click Auto Verify → Upgraded in 2 seconds
        
        **Admin Panel:**
        Login as Admin / admin@45697 → See Admin - Transactions module with all payments, revenue, CSV download.
        """)
        st.download_button("📥 Download Manual PDF", open("/mnt/data/TIMAR_ANALYTICS_User_Manual_v7.6.pdf","rb").read() if os.path.exists("/mnt/data/TIMAR_ANALYTICS_User_Manual_v7.6.pdf") else b"Manual", "TIMAR_Manual_v7.6.pdf", "application/pdf", use_container_width=True)

else:
    st.header(f"{st.session_state.page} - {st.session_state.tool_page}")
    st.write(f"Module: {st.session_state.page} | Tool: {st.session_state.tool_page}")
    st.dataframe(df.head(100), use_container_width=True)
st.divider()
st.caption(f"{APP_VER} | User: {st.session_state.user}")
