import streamlit as st
import pandas as pd
import numpy as np
import os, json
from datetime import datetime

st.set_page_config(page_title="TIMAR ANALYTICS", page_icon="📊", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #FFF8E1 0%, #E8F5E9 50%, #E3F2FD 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1B5E20 0%, #2E7D32 50%, #388E3C 100%); }
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p { color: white!important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] { background-color: white!important; border-radius: 10px!important; border: 2px solid #FFA000!important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] > div { background-color: white!important; color: #1B5E20!important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] span, section[data-testid="stSidebar"] div[data-baseweb="select"] div, section[data-testid="stSidebar"] div[data-baseweb="select"] input, section[data-testid="stSidebar"] div[data-baseweb="select"] svg { color: #1B5E20!important; fill: #1B5E20!important; font-weight: 900!important; opacity: 1!important; }
div[data-baseweb="popover"] div { background: white!important; color: #1B5E20!important; }
h1 { background: linear-gradient(90deg, #1B5E20, #FFA000); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900!important; }
h2, h3 { color: #1B5E20!important; font-weight: 700!important; }
h2 { border-left: 6px solid #FFA000; padding-left: 12px; }
[data-testid="stMetric"] { background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-top: 4px solid #FFA000; }
[data-testid="stVerticalBlockBorderWrapper"] { background: rgba(255,255,255,0.95); border-radius: 15px; box-shadow: 0 8px 25px rgba(0,0,0,0.08); }
.stButton > button { background: linear-gradient(90deg, #FFA000 0%, #2E7D32 100%); color: white!important; border-radius: 25px; font-weight: bold; border: none; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(90deg, #1B5E20 0%, #2E7D32 50%, #FFA000 100%); padding:15px; border-radius:15px; margin-bottom:15px; text-align:center;">
    <h1 style="color:white!important; -webkit-text-fill-color:white; margin:0; border:none; padding:0;">🌾 TIMAR ANALYTICS 📊</h1>
    <p style="color:#FFEB3B; margin:0; font-weight:bold;">Uganda's Smart Data Platform | All 15 Modules | Analytics Restored</p>
</div>
""", unsafe_allow_html=True)

MTN_NUMBER = "0789876277"; AIRTEL_NUMBER = "0755453313"; MTN_NAME = "Tino Mary"; AIRTEL_NAME = "Tino Mary"; ADMIN_PASSWORD = "admin@45697"
LANGUAGES = {"English":"en","Luganda":"lg","Lunyankole":"nyn","Swahili":"sw","Kinyarwanda":"rw","French":"fr","Spanish":"es","Portuguese":"pt","Arabic":"ar","Chinese":"zh","German":"de","Ateso":"teo","Acholi":"ach","Langi":"laj","Karamojong":"akj"}
MODULES_ADMIN = ["Dashboard","Analytics","Data Upload","M&E Module","WASH Module","Livelihood Module","Health Module","Education Module","Agriculture Module","Research Module","KPI Matrix","Statistical Tools","Payment & Plans","Reviews & Comments","Help & Manual for Timar Analytics","Admin - Monitoring Panel"]
MODULES_USER = ["Dashboard","Analytics","Data Upload","M&E Module","WASH Module","Livelihood Module","Health Module","Education Module","Agriculture Module","Research Module","KPI Matrix","Statistical Tools","Payment & Plans","Reviews & Comments","Help & Manual for Timar Analytics"]
STANDARD_TOOLS = ["Overview - All Data","Questionnaire - Structured Questions","Interview - Key Informant Interview","Focus Group Discussion (FGD)","Observation Checklist","Survey Form - Household Survey","Case Study Tool","Document Review / Secondary Data","Mobile Data Collection (Kobo/ODK)","Experimental Data Collection"]
ME_TOOLS = ["LogFrame - Logical Framework 4x4","Results Chain / Result Framework","Indicator Tracking Matrix","Risk Matrix - Likelihood x Impact","Stakeholder Matrix - Power/Interest","Data Collection Matrix","Budget Matrix - Activity Based","M&E Plan Matrix","Theory of Change","Problem Tree to Objective Tree"]
ALL_CHARTS = ["Bar Chart","Pie Chart","Line Chart","Scatter Plot","Histogram","Area Chart","Table View","Summary Statistics","Matrix View"]
PLANS = {"FREE_TRIAL":{"price":0,"name":"Free Trial 24h","days":"24 Hours"},"STUDENT":{"price":10000,"name":"STUDENT","days":"30 Days"},"FARMER":{"price":20000,"name":"FARMER","days":"30 Days"},"RESEARCHER":{"price":30000,"name":"RESEARCHER","days":"30 Days"},"PROFESSIONAL":{"price":100000,"name":"ALL PRO","days":"30 Days"},"NGO":{"price":300000,"name":"NGO","days":"90 Days"},"GOVERNMENT":{"price":500000,"name":"GOVERNMENT","days":"365 Days"},"ADMIN_FREE":{"price":0,"name":"ADMIN","days":"Unlimited"}}

def generate_sample_data(n=520):
    np.random.seed(42)
    return pd.DataFrame({"Region": np.random.choice(["Central","Eastern","Northern","Western"], n),"Gender": np.random.choice(["Male","Female"], n),"Age": np.random.randint(18,85,n),"Income": np.random.randint(200000,2000000,n),"District": np.random.choice(["Kampala","Gulu","Mbarara","Mbale","Arua","Jinja","Lira","Kabale"], n),"Collection_Tool": np.random.choice(STANDARD_TOOLS[1:], n),"Education": np.random.choice(["Primary","Secondary","University","None"], n),"Farm_Size_Acres": np.round(np.random.uniform(0.5,10,n),1),"Yield_Tons": np.round(np.random.uniform(0.2,5,n),1),"Water_Source": np.random.choice(["Borehole","Tap","River","Well"], n),"Has_Latrine": np.random.choice(["Yes","No"], n),"Crop_Type": np.random.choice(["Maize","Beans","Coffee","Matooke"], n),"Health_Status": np.random.choice(["Healthy","Malaria","Malnutrition"], n),"School_Status": np.random.choice(["Enrolled","Dropout"], n)})

SAMPLE_LOGFRAME = [{"Level":"Goal","Narrative Summary":"Improve livelihoods 2027","Indicators (OVI)":"% income +30%","Means of Verification":"Household survey","Assumptions":"Stable market"},{"Level":"Purpose","Narrative Summary":"Increase income and yield","Indicators (OVI)":"Avg income 300k to 800k","Means of Verification":"HH survey","Assumptions":"Good rains"}]
SAMPLE_BUDGET = [{"Activity":"Training 520 farmers","Quantity":10,"Unit":"Session","Unit Cost UGX":200000,"Total UGX":2000000},{"Activity":"Seed kits","Quantity":520,"Unit":"Kit","Unit Cost UGX":5000,"Total UGX":2600000}]

def load_users():
    if os.path.exists("users.json"):
        try:
            with open("users.json") as f: d=json.load(f); d["Admin"]=ADMIN_PASSWORD; return d
        except: pass
    return {"timar":"timar123","Admin":ADMIN_PASSWORD}
def load_json(file, default):
    if os.path.exists(file):
        try:
            with open(file) as f: return json.load(f)
        except: return default
    return default
def save_json(file, data):
    with open(file,"w") as f: json.dump(data,f,indent=2)
def log_activity(user, action, details=""):
    logs=load_json("timar_activity_log.json",[]); logs.append({"Time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"User":user,"Action":action,"Details":details}); save_json("timar_activity_log.json",logs[-500:])
def check_trial(user):
    if user.lower()=="admin": return True,"Admin Unlimited"
    if st.session_state.plan!="FREE_TRIAL": return True,"Paid Active"
    trials=load_json("trials.json",{})
    if user not in trials:
        trials[user]={"start":datetime.now().isoformat()}; save_json("trials.json",trials); return True,"24.0h left"
    start=datetime.fromisoformat(trials[user]["start"]); left=24-(datetime.now()-start).total_seconds()/3600
    if left<=0: return False,"Expired"
    return True,f"{left:.1f}h left"

for k in ["logged","user","plan","page","tool","metool","chart","current_df","lang_name","selected_plan","selected_plan_key"]:
    if k not in st.session_state:
        if k=="logged": st.session_state[k]=False
        elif k=="user": st.session_state[k]=""
        elif k=="plan": st.session_state[k]="FREE_TRIAL"
        elif k=="page": st.session_state[k]="Dashboard"
        elif k=="tool": st.session_state[k]="Overview - All Data"
        elif k=="metool": st.session_state[k]="LogFrame - Logical Framework 4x4"
        elif k=="chart": st.session_state[k]="Bar Chart"
        elif k=="current_df": st.session_state[k]=generate_sample_data()
        elif k=="lang_name": st.session_state[k]="English"
        else: st.session_state[k]=None
def is_admin(): return st.session_state.user.lower()=="admin"

if not st.session_state.logged:
    left, right = st.columns([1.2,1])
    with left:
        st.title("TIMAR ANALYTICS")
        st.subheader("Uganda's Smart Data Platform - 520 Sample Ready")
        with st.container(border=True):
            st.markdown("### 15 Modules | Analytics Restored | 9 Statistical Tools")
            st.success("✅ Dashboard, Analytics, Data Upload, M&E, WASH, Livelihood, Health, Education, Agriculture, Research, KPI, Statistical Tools, Payment, Reviews, Help, Admin")
    with right:
        t1,t2=st.tabs(["LOGIN","SIGN UP + TRIAL"])
        with t1:
            u=st.text_input("Username",key="l_u"); p=st.text_input("Password",type="password",key="l_p")
            if st.button("Login",type="primary",width='stretch'):
                users=load_users()
                if u.lower()=="admin" and p==ADMIN_PASSWORD:
                    st.session_state.logged=True; st.session_state.user="Admin"; st.session_state.plan="ADMIN_FREE"; log_activity("Admin","LOGIN"); st.rerun()
                elif u in users and users[u]==p:
                    st.session_state.logged=True; st.session_state.user=u; trials=load_json("trials.json",{});
                    if u not in trials: trials[u]={"start":datetime.now().isoformat()}; save_json("trials.json",trials)
                    log_activity(u,"LOGIN"); st.rerun()
                else: st.error("Invalid")
        with t2:
            nu=st.text_input("Choose Username",key="s_u"); npw=st.text_input("Choose Password",type="password",key="s_p"); cpw=st.text_input("Confirm",type="password",key="s_c"); phone=st.text_input("Phone"); agree=st.checkbox("I agree to start 24hr trial")
            if st.button("Create & Start Trial",type="primary",width='stretch'):
                users=load_users()
                if not nu or not npw: st.error("Required")
                elif npw!=cpw: st.error("No match")
                elif nu in users: st.error("Exists")
                elif not agree: st.error("Agree")
                else:
                    users[nu]=npw; save_json("users.json",users); trials=load_json("trials.json",{}); trials[nu]={"start":datetime.now().isoformat(),"phone":phone}; save_json("trials.json",trials); log_activity(nu,"SIGNUP"); st.success(f"{nu} created! Go to LOGIN"); st.balloons()
    st.stop()

ok,msg=check_trial(st.session_state.user)

with st.sidebar:
    st.markdown("""<div style="background:white; padding:10px; border-radius:10px; text-align:center; margin-bottom:10px;"><h2 style="color:#1B5E20!important; margin:0; border:none; padding:0;">🌾 TIMAR</h2><p style="color:#FF6F00!important; font-weight:bold; margin:0; font-size:12px;">Tino Mary</p></div>""", unsafe_allow_html=True)
    st.caption(f"👤 {st.session_state.user} | ⏰ {msg}"); st.divider()
    st.markdown("### 📦 Modules - 15 Total")
    mods = MODULES_ADMIN if is_admin() else MODULES_USER
    sel_mod = st.selectbox("Select Module", mods, index=mods.index(st.session_state.page) if st.session_state.page in mods else 0, label_visibility="collapsed", key="sb_mod")
    st.session_state.page = sel_mod
    st.markdown(f"<div style='background:#FFEB3B; color:#1B5E20!important; padding:6px; border-radius:8px; font-weight:bold; font-size:13px; text-align:center; margin-bottom:15px;'>✅ {sel_mod}</div>", unsafe_allow_html=True)
    st.markdown("### 📋 Data Collection Tools")
    sel_tool = st.selectbox("Select Collection Tool", STANDARD_TOOLS, index=STANDARD_TOOLS.index(st.session_state.tool) if st.session_state.tool in STANDARD_TOOLS else 0, label_visibility="collapsed", key="sb_tool")
    st.session_state.tool = sel_tool
    st.markdown(f"<div style='background:#FFEB3B; color:#1B5E20!important; padding:6px; border-radius:8px; font-weight:bold; font-size:13px; text-align:center; margin-bottom:15px;'>🔧 {sel_tool[:32]}</div>", unsafe_allow_html=True)
    st.markdown("### 📊 M&E Tools")
    sel_me = st.selectbox("Select M&E Tool", ME_TOOLS, index=ME_TOOLS.index(st.session_state.metool) if st.session_state.metool in ME_TOOLS else 0, label_visibility="collapsed", key="sb_me")
    st.session_state.metool = sel_me
    st.markdown(f"<div style='background:#FFEB3B; color:#1B5E20!important; padding:6px; border-radius:8px; font-weight:bold; font-size:13px; text-align:center; margin-bottom:15px;'>📈 {sel_me}</div>", unsafe_allow_html=True)
    st.markdown("### 📈 Charts")
    sel_chart = st.selectbox("Select Chart", ALL_CHARTS, index=ALL_CHARTS.index(st.session_state.chart) if st.session_state.chart in ALL_CHARTS else 0, label_visibility="collapsed", key="sb_chart")
    st.session_state.chart = sel_chart
    st.markdown(f"<div style='background:#FFEB3B; color:#1B5E20!important; padding:6px; border-radius:8px; font-weight:bold; font-size:13px; text-align:center; margin-bottom:15px;'>📉 {sel_chart}</div>", unsafe_allow_html=True)
    st.markdown("### 🌍 Languages")
    sel_lang = st.selectbox("Select Language", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(st.session_state.lang_name), label_visibility="collapsed", key="sb_lang")
    st.session_state.lang_name = sel_lang
    st.markdown(f"<div style='background:#FFEB3B; color:#1B5E20!important; padding:6px; border-radius:8px; font-weight:bold; font-size:13px; text-align:center; margin-bottom:10px;'>🌐 {sel_lang}</div>", unsafe_allow_html=True)
    st.divider()
    if st.button("🔄 Load 520 Sample Data", width='stretch', key="sb_load"):
        st.session_state.current_df = generate_sample_data(); log_activity(st.session_state.user, "LOAD 520 SAMPLE"); st.success("520 sample loaded")
    st.markdown(f"""<div style="background:white; padding:10px; border-radius:10px; text-align:center; border:2px solid #FFA000; margin-bottom:10px;"><p style="color:#1B5E20!important; font-weight:bold; margin:0; font-size:12px;">Rows Active</p><p style="color:#FF6F00!important; font-weight:900; margin:0; font-size:22px;">{len(st.session_state.current_df)}</p></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div style="background:white; border-radius:10px; padding:10px; margin-top:10px; border:2px solid #FFA000;"><p style="color:#1B5E20!important; font-weight:900!important; font-size:12px; margin:2px;">📌 YOU ARE VIEWING:</p><p style="color:#000000!important; font-weight:bold!important; font-size:12px; margin:3px;">📦 Module: {sel_mod}</p><p style="color:#000000!important; font-weight:bold!important; font-size:12px; margin:3px;">🔧 Tool: {sel_tool[:24]}</p><p style="color:#000000!important; font-weight:bold!important; font-size:12px; margin:3px;">📊 M&E: {sel_me[:24]}</p><p style="color:#000000!important; font-weight:bold!important; font-size:12px; margin:3px;">📈 Chart: {sel_chart}</p><p style="color:#000000!important; font-weight:bold!important; font-size:12px; margin:3px;">🌐 Lang: {sel_lang}</p></div>""", unsafe_allow_html=True)
    if st.button("🚪 Logout", width='stretch', key="sb_logout"):
        log_activity(st.session_state.user, "LOGOUT"); st.session_state.logged=False; st.rerun()

df=st.session_state.current_df
if not ok and not is_admin() and st.session_state.page!="Payment & Plans":
    st.error("Trial Expired - Pay to continue"); st.session_state.page="Payment & Plans"

if st.session_state.page=="Dashboard":
    st.header(f"Dashboard | {st.session_state.tool} | {st.session_state.chart}")
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Records",len(df)); c2.metric("Regions",df["Region"].nunique()); c3.metric("Avg Age",f"{df['Age'].mean():.1f}"); c4.metric("Avg Income",f"UGX {df['Income'].mean():,.0f}"); c5.metric("Avg Yield",f"{df['Yield_Tons'].mean():.1f}")
    filt=df.copy()
    if st.session_state.tool!="Overview - All Data" and "Collection_Tool" in df.columns and st.session_state.tool in df["Collection_Tool"].unique().tolist():
        filt=df[df["Collection_Tool"]==st.session_state.tool]
    st.success(f"Found {len(filt)} sample records via {st.session_state.tool}")
    st.dataframe(filt.head(100), width='stretch')
    if st.session_state.chart=="Bar Chart": st.bar_chart(filt["Region"].value_counts())
    elif st.session_state.chart=="Pie Chart": st.bar_chart(filt["Region"].value_counts())
    elif st.session_state.chart=="Line Chart": st.line_chart(filt["Age"].value_counts().sort_index())
    elif st.session_state.chart=="Scatter Plot": st.scatter_chart(filt,x="Age",y="Income",color="Region")
    elif st.session_state.chart=="Histogram": st.bar_chart(filt["Age"].value_counts(bins=10,sort=False))
    elif st.session_state.chart=="Area Chart": st.area_chart(filt["Region"].value_counts())
    elif st.session_state.chart=="Summary Statistics": st.dataframe(filt.describe(),width='stretch')
    elif st.session_state.chart=="Matrix View": st.dataframe(pd.crosstab(filt["Region"],filt["Gender"]),width='stretch')
    else: st.dataframe(filt.head(100),width='stretch')

elif st.session_state.page=="Analytics":
    st.header(f"📊 Analytics Module RESTORED | {st.session_state.tool} | {st.session_state.chart}")
    filt = df.copy()
    if st.session_state.tool!="Overview - All Data" and "Collection_Tool" in df.columns and st.session_state.tool in df["Collection_Tool"].unique().tolist():
        filt = df[df["Collection_Tool"]==st.session_state.tool]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Records", len(filt)); c2.metric("Avg Income", f"UGX {filt['Income'].mean():,.0f}"); c3.metric("Avg Yield", f"{filt['Yield_Tons'].mean():.2f} tons"); c4.metric("Progress", f"{filt['Yield_Tons'].mean()/3.0*100:.0f}%")
    with st.container(border=True):
        st.subheader("Smart Analytics - Filtered by Data Collection Tool")
        st.success(f"Found {len(filt)} records via {st.session_state.tool}")
        col_left, col_right = st.columns([2,1])
        with col_left:
            if st.session_state.chart=="Bar Chart": st.bar_chart(filt["Region"].value_counts())
            elif st.session_state.chart=="Pie Chart": st.bar_chart(filt["Region"].value_counts())
            elif st.session_state.chart=="Line Chart": st.line_chart(filt["Age"].value_counts().sort_index())
            elif st.session_state.chart=="Scatter Plot": st.scatter_chart(filt,x="Age",y="Income",color="Region")
            elif st.session_state.chart=="Histogram": st.bar_chart(filt["Age"].value_counts(bins=10,sort=False))
            elif st.session_state.chart=="Area Chart": st.area_chart(filt["Region"].value_counts())
            elif st.session_state.chart=="Summary Statistics": st.dataframe(filt.describe(),width='stretch')
            elif st.session_state.chart=="Matrix View": st.dataframe(pd.crosstab(filt["Region"],filt["Gender"]),width='stretch')
            else: st.dataframe(filt.head(100),width='stretch')
        with col_right:
            st.subheader("Auto Insights")
            st.info(f"Tool: {st.session_state.tool}\nRecords: {len(filt)}\nTop Region: {filt['Region'].mode()[0]}\nGender: {filt['Gender'].value_counts().to_dict()}\nAvg Age {filt['Age'].mean():.1f}\nIncome UGX {filt['Income'].mean():,.0f}")
            st.dataframe(filt["Region"].value_counts(), width='stretch')
    st.dataframe(filt.head(100), width='stretch')

elif st.session_state.page=="Data Upload":
    st.header("Data Upload - ALL Users - Active")
    up=st.file_uploader("Upload CSV/Excel",type=["csv","xlsx","xls"])
    if up:
        try:
            ndf=pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
            st.session_state.current_df=ndf; os.makedirs("uploads",exist_ok=True)
            with open(f"uploads/{st.session_state.user}_{up.name}","wb") as f: f.write(up.getbuffer())
            log_activity(st.session_state.user,"UPLOAD",f"{len(ndf)}"); st.success(f"{len(ndf)} rows ACTIVE!"); st.dataframe(ndf.head(100),width='stretch'); st.balloons()
        except Exception as e: st.error(str(e))
    else: st.dataframe(df.head(50),width='stretch')

elif st.session_state.page=="M&E Module":
    st.header(f"M&E Module | {st.session_state.metool}")
    if st.session_state.metool=="LogFrame - Logical Framework 4x4":
        log_data=load_json(f"logframe_{st.session_state.user}.json",SAMPLE_LOGFRAME)
        edited=st.data_editor(pd.DataFrame(log_data),width='stretch',num_rows="dynamic")
        if st.button("Save LogFrame",type="primary"): save_json(f"logframe_{st.session_state.user}.json",edited.to_dict(orient="records")); st.success("Saved!")
    elif st.session_state.metool=="Budget Matrix - Activity Based":
        budg=load_json(f"budget_{st.session_state.user}.json",SAMPLE_BUDGET)
        edited=st.data_editor(pd.DataFrame(budg),width='stretch',num_rows="dynamic")
        edited["Total UGX"]=edited["Quantity"]*edited["Unit Cost UGX"]
        st.metric("Total",f"UGX {edited['Total UGX'].sum():,}")
        st.bar_chart(edited.set_index("Activity")["Total UGX"])
        if st.button("Save Budget",type="primary"): save_json(f"budget_{st.session_state.user}.json",edited.to_dict(orient="records")); st.success("Saved!")
    else:
        st.write(f"{st.session_state.metool} - Edit")
        df_me=load_json(f"{st.session_state.metool}_{st.session_state.user}.json",[{"Item":"Sample - Edit"}])
        edited=st.data_editor(pd.DataFrame(df_me),width='stretch',num_rows="dynamic")
        if st.button(f"Save {st.session_state.metool}",type="primary"): save_json(f"{st.session_state.metool}_{st.session_state.user}.json",edited.to_dict(orient="records")); st.success("Saved!")

elif st.session_state.page=="WASH Module":
    st.header("🚰 WASH Module - Water Sanitation Hygiene")
    c1,c2=st.columns(2); c1.metric("Has Latrine %", f"{(df['Has_Latrine']=='Yes').mean()*100:.1f}%"); c2.metric("Water Source Top", df["Water_Source"].mode()[0] if "Water_Source" in df.columns else "Borehole")
    with st.container(border=True):
        st.subheader("WASH Survey - Questions One Per Line")
        st.write("Q1 Water source: [Borehole/Tap/River/Well]"); st.write("Q2 Distance to water mins: ___"); st.write("Q3 Has latrine: [Yes/No]"); st.write("Q4 Latrine type: [VIP/Traditional/Flush]"); st.write("Q5 Handwashing facility: [Yes/No]"); st.write("Q6 Open defecation: [Yes/No]"); st.write("Q7 Water treatment: [Boil/Chlorine/None]"); st.write("Q8 HH water storage covered: [Yes/No]")
        st.dataframe(df[["District","Water_Source","Has_Latrine"]].head(50), width='stretch'); st.bar_chart(df["Water_Source"].value_counts() if "Water_Source" in df.columns else df["Region"].value_counts())

elif st.session_state.page=="Livelihood Module":
    st.header("💼 Livelihood Module")
    c1,c2,c3=st.columns(3); c1.metric("Avg Income", f"UGX {df['Income'].mean():,.0f}"); c2.metric("Food Months Avg", "8.5/12"); c3.metric("Employment %", "68%")
    with st.container(border=True):
        st.subheader("Livelihood Questions One Per Line")
        st.write("Q1 Main income source: [Farming/Casual/Business/Salary]"); st.write("Q2 Monthly income UGX: ___ Baseline 300k Target 800k"); st.write("Q3 Other income UGX: ___"); st.write("Q4 Food months /12: ___"); st.write("Q5 Meals per day: ___"); st.write("Q6 Savings group member: [Yes/No]"); st.write("Q7 Coping strategy: [Reduce meals/Borrow/Sell asset]"); st.write("Q8 Asset index: [Radio/Bike/Phone/None]")
        st.bar_chart(df["Income"] if "Income" in df.columns else df["Age"])

elif st.session_state.page=="Health Module":
    st.header("🏥 Health Module - VHT Screening")
    c1,c2=st.columns(2); c1.metric("Healthy %", f"{(df['Health_Status']=='Healthy').mean()*100:.1f}%" if "Health_Status" in df.columns else "75%"); c2.metric("Top Disease", df["Health_Status"].mode()[0] if "Health_Status" in df.columns else "Malaria")
    with st.container(border=True):
        st.subheader("Health Screening - Questions One Per Line")
        st.write("Q1 Patient name: ___"); st.write("Q2 Age: ___"); st.write("Q3 Sex: [Male/Female]"); st.write("Q4 Disease: [Malaria/TB/Malnutrition/Diarrhea/Pregnancy]"); st.write("Q5 Symptoms: [Fever/Cough/Vomiting/Weight Loss]"); st.write("Q6 Tested: [Yes/No]"); st.write("Q7 Referred: [Yes/No]"); st.write("Q8 Follow-up date: ___")
        st.dataframe(df[["District","Gender","Health_Status"]].head(50) if "Health_Status" in df.columns else df.head(50), width='stretch')

elif st.session_state.page=="Education Module":
    st.header("🎓 Education Module - School Enrollment")
    c1,c2=st.columns(2); c1.metric("Enrolled %", f"{(df['School_Status']=='Enrolled').mean()*100:.1f}%" if "School_Status" in df.columns else "82%"); c2.metric("Dropout Top Reason", "Fees")
    with st.container(border=True):
        st.subheader("Education Questions One Per Line")
        st.write("Q1 Pupil name: ___"); st.write("Q2 Age: ___"); st.write("Q3 Sex: [Male/Female]"); st.write("Q4 Class: [P1-P7/S1-S6]"); st.write("Q5 Enrolled: [Yes/No - Dropout]"); st.write("Q6 Reason dropout: [Fees/Pregnancy/Distance/Orphan]"); st.write("Q7 Distance to school km: ___"); st.write("Q8 Fees paid: [Yes/No]"); st.write("Q9 Materials: [Yes/No]")
        st.dataframe(df[["District","Gender","Education","School_Status"]].head(50) if "School_Status" in df.columns else df.head(50), width='stretch')

elif st.session_state.page=="Agriculture Module":
    st.header("🌱 Agriculture Module - Farmer Registry")
    c1,c2,c3=st.columns(3); c1.metric("Avg Farm Size", f"{df['Farm_Size_Acres'].mean():.1f} acres"); c2.metric("Avg Yield", f"{df['Yield_Tons'].mean():.1f} tons"); c3.metric("Top Crop", df["Crop_Type"].mode()[0] if "Crop_Type" in df.columns else "Maize")
    with st.container(border=True):
        st.subheader("Agriculture Questions One Per Line")
        st.write("Q1 Farmer name: ___"); st.write("Q2 Farm size acres: ___"); st.write("Q3 Crop type: [Maize/Beans/Coffee/Matooke/Rice]"); st.write("Q4 Season: [Season A/Season B]"); st.write("Q5 Seed type: [Local/Improved]"); st.write("Q6 Yield tons/acre: ___ Baseline 1.0 Target 3.0"); st.write("Q7 Inputs received: [Yes/No]"); st.write("Q8 Training attended: [Yes/No]"); st.write("Q9 Challenges: [Drought/Pests/Market/No Inputs]"); st.write("Q10 Will plant again: [Yes/No]")
        st.dataframe(df[["District","Crop_Type","Farm_Size_Acres","Yield_Tons"]].head(50) if "Crop_Type" in df.columns else df.head(50), width='stretch'); st.scatter_chart(df, x="Farm_Size_Acres", y="Yield_Tons", color="Region")

elif st.session_state.page=="Research Module":
    st.header("🔬 Research Module - Custom Studies")
    with st.container(border=True):
        st.subheader("Research Tool - 10 Questions One Per Line")
        st.write("Q1 Research title: ___"); st.write("Q2 Objective: ___"); st.write("Q3 Methodology: [Qualitative/Quantitative/Mixed]"); st.write("Q4 Sample size: ___"); st.write("Q5 Sampling method: [Random/Purposive/Snowball]"); st.write("Q6 Tool used: [Questionnaire/Interview/FGD]"); st.write("Q7 Data collected: ___"); st.write("Q8 Analysis method: [Thematic/Statistical]"); st.write("Q9 Findings summary: ___"); st.write("Q10 Recommendations: ___")
        st.dataframe(df.head(50), width='stretch')

elif st.session_state.page=="KPI Matrix":
    st.header("📊 KPI Matrix - Key Performance Indicators")
    kpi_data = [{"KPI":"Farmers Trained","Baseline":0,"Target":520,"Achieved":480,"Progress %":92,"Status":"On Track"},{"KPI":"Kits Distributed","Baseline":0,"Target":520,"Achieved":520,"Progress %":100,"Status":"Achieved"},{"KPI":"Avg Yield tons","Baseline":1.0,"Target":3.0,"Achieved":2.8,"Progress %":90,"Status":"On Track"},{"KPI":"Avg Income UGX","Baseline":300000,"Target":800000,"Achieved":750000,"Progress %":90,"Status":"On Track"},{"KPI":"Demo Plots","Baseline":0,"Target":20,"Achieved":18,"Progress %":90,"Status":"On Track"}]
    df_kpi = pd.DataFrame(load_json(f"kpi_{st.session_state.user}.json", kpi_data))
    edited = st.data_editor(df_kpi, width='stretch', num_rows="dynamic")
    st.bar_chart(edited.set_index("KPI")["Progress %"])
    if st.button("Save KPI Matrix", type="primary"): save_json(f"kpi_{st.session_state.user}.json", edited.to_dict(orient="records")); st.success("Saved!")
    st.metric("Overall Progress", f"{edited['Progress %'].mean():.1f}%")

elif st.session_state.page=="Statistical Tools":
    st.header("📈 Statistical Tools - All 9 Tools at Once")
    filt = df.copy()
    if st.session_state.tool!="Overview - All Data" and "Collection_Tool" in df.columns and st.session_state.tool in df["Collection_Tool"].unique().tolist():
        filt = df[df["Collection_Tool"]==st.session_state.tool]
    t1, t2, t3, t4, t5 = st.tabs(["📊 Summary + Bar", "🥧 Pie + Line", "⚪ Scatter + Hist", "📈 Area + Matrix", "🧮 Full Stats"])
    with t1:
        col1, col2 = st.columns(2)
        with col1: st.subheader("📊 Summary Statistics"); st.dataframe(filt.describe(), width='stretch')
        with col2: st.subheader("📊 Bar Chart - Region"); st.bar_chart(filt["Region"].value_counts()); st.metric("Top Region", filt["Region"].mode()[0], f"{filt['Region'].value_counts().iloc[0]} records")
    with t2:
        col1, col2 = st.columns(2)
        with col1: st.subheader("🥧 Pie (as Bar) - Gender"); st.bar_chart(filt["Gender"].value_counts()); st.write(filt["Gender"].value_counts().to_dict())
        with col2: st.subheader("📈 Line Chart - Age Distribution"); st.line_chart(filt["Age"].value_counts().sort_index()); st.metric("Avg Age", f"{filt['Age'].mean():.1f}", f"Min {filt['Age'].min()} Max {filt['Age'].max()}")
    with t3:
        col1, col2 = st.columns(2)
        with col1: st.subheader("⚪ Scatter - Age vs Income by Region"); st.scatter_chart(filt, x="Age", y="Income", color="Region"); st.caption("Each dot = 1 farmer")
        with col2: st.subheader("📊 Histogram - Age Groups"); st.bar_chart(filt["Age"].value_counts(bins=10, sort=False)); st.metric("Farm-Yield Correlation", f"{filt['Farm_Size_Acres'].corr(filt['Yield_Tons']):.2f}")
    with t4:
        col1, col2 = st.columns(2)
        with col1: st.subheader("📈 Area Chart - Region"); st.area_chart(filt["Region"].value_counts())
        with col2: st.subheader("🔢 Matrix View - Region x Gender"); st.dataframe(pd.crosstab(filt["Region"], filt["Gender"]), width='stretch'); st.dataframe(pd.crosstab(filt["Region"], filt["Education"]), width='stretch')
    with t5:
        st.subheader("🧮 Complete Analysis - All in One")
        c1,c2,c3,c4 = st.columns(4); c1.metric("Total Records", len(filt)); c2.metric("Avg Income", f"UGX {filt['Income'].mean():,.0f}"); c3.metric("Avg Yield", f"{filt['Yield_Tons'].mean():.2f} tons"); c4.metric("Avg Farm", f"{filt['Farm_Size_Acres'].mean():.1f} acres")
        st.dataframe(filt.head(100), width='stretch')
        st.info(f"ANALYSIS FOR {st.session_state.tool}: Found {len(filt)} records across {filt['Region'].nunique()} regions. Dominant {filt['Region'].mode()[0]}. Gender {filt['Gender'].value_counts().to_dict()}. Avg age {filt['Age'].mean():.1f}. Income UGX {filt['Income'].mean():,.0f}. Yield {filt['Yield_Tons'].mean():.2f} vs Target 3.0. Progress {filt['Yield_Tons'].mean()/3.0*100:.0f}%.")

elif st.session_state.page=="Payment & Plans":
    st.header("💳 Choose Your Plan - Pay Securely")
    st.warning("🔒 Payment numbers hidden for security. They appear ONLY after you click a plan below.")
    cols=st.columns(3)
    for i,(key,plan) in enumerate(PLANS.items()):
        if key=="ADMIN_FREE": continue
        with cols[i%3]:
            with st.container(border=True):
                st.subheader(plan["name"]); st.metric("Price",f"UGX {plan['price']:,}" if plan["price"]>0 else "FREE"); st.caption(plan["days"])
                if st.button(f"Pay {plan['name']}",key=f"pay_{key}",width='stretch'):
                    st.session_state.selected_plan=plan; st.session_state.selected_plan_key=key
    if st.session_state.selected_plan:
        plan=st.session_state.selected_plan; pkey=st.session_state.selected_plan_key
        st.divider()
        st.markdown(f"""<div style="background:linear-gradient(90deg,#1B5E20,#FFA000); padding:15px; border-radius:15px; text-align:center;"><h3 style="color:white!important; border:none;">✅ You Selected {plan['name']} - UGX {plan['price']:,}</h3><p style="color:#FFEB3B; font-weight:bold; font-size:18px;">MTN MoMo: {MTN_NUMBER} - Names: {MTN_NAME}</p><p style="color:white; font-weight:bold; font-size:18px;">Airtel Money: {AIRTEL_NUMBER} - Names: {AIRTEL_NAME}</p><p style="color:white;">Send UGX {plan['price']:,} now then upload receipt below</p></div>""", unsafe_allow_html=True)
        receipt=st.file_uploader("Upload Payment Document",type=["png","jpg","jpeg","pdf"]); txn=st.text_input("Txn ID")
        if receipt is not None:
            os.makedirs("payments",exist_ok=True); path=f"payments/{st.session_state.user}_{pkey}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{receipt.name}"
            with open(path,"wb") as f: f.write(receipt.getbuffer())
            tr=load_json("timar_transactions.json",[]); tr.append({"Time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"User":st.session_state.user,"Plan":plan["name"],"Key":pkey,"Amount":plan["price"],"Txn":txn,"Receipt":path,"Status":"AUTO CONFIRMED"}); save_json("timar_transactions.json",tr); st.session_state.plan=pkey; log_activity(st.session_state.user,"PAYMENT AUTO",plan["name"]); st.success(f"AUTO CONFIRMED! {plan['name']} ACTIVE!"); st.balloons(); st.rerun()

elif st.session_state.page=="Reviews & Comments":
    st.header("⭐ Reviews & Comments - TIMAR ANALYTICS")
    tab_write, tab_view = st.tabs(["✍️ Write Review", "👁️ View All Reviews"])
    with tab_write:
        with st.container(border=True):
            st.subheader("Write Your Review")
            st.write(f"Logged in as: **{st.session_state.user}**")
            rating = st.selectbox("⭐ Rating", [5,4,3,2,1], index=0, format_func=lambda x: f"{x} Stars {'⭐'*x}")
            comment = st.text_area("💬 Your Review", placeholder="Type your feedback here...", height=150)
            if st.button("📤 Submit Review", type="primary", width='stretch', key="submit_rev"):
                if not comment.strip(): st.error("Write something")
                else:
                    reviews = load_json("reviews.json", [])
                    reviews.append({"Time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"User":st.session_state.user,"Rating":rating,"Comment":comment,"Lang":st.session_state.lang_name})
                    save_json("reviews.json", reviews); log_activity(st.session_state.user, "REVIEW", f"{rating} stars"); st.success("Saved! Go to View tab"); st.balloons(); st.rerun()
    with tab_view:
        reviews = load_json("reviews.json", [])
        st.subheader(f"👁️ All User Reviews ({len(reviews)})")
        if not reviews: st.warning("No reviews yet. Go to Write Review tab and be first!")
        else:
            avg = sum([r['Rating'] for r in reviews])/len(reviews) if reviews else 0
            c1,c2,c3 = st.columns(3); c1.metric("Total Reviews", len(reviews)); c2.metric("Average Rating", f"{avg:.1f} ⭐"); c3.metric("5-Star", len([r for r in reviews if r['Rating']==5]))
            st.divider()
            search = st.text_input("🔍 Search reviews by user or comment")
            filtered = reviews
            if search: filtered = [r for r in reviews if search.lower() in r['User'].lower() or search.lower() in r['Comment'].lower()]
            for r in reversed(filtered[-50:]):
                with st.container(border=True):
                    stars = "⭐" * r.get("Rating",5)
                    st.markdown(f"**👤 {r['User']}** | {stars} ({r['Rating']}/5) | 🕒 {r['Time']}")
                    st.info(f"💬 {r['Comment']}"); st.caption(f"Lang: {r.get('Lang','English')}")
            if st.button("🗑️ Clear All Reviews (Admin Only)", key="clear_rev"):
                if is_admin(): save_json("reviews.json", []); st.success("Cleared"); st.rerun()
                else: st.error("Admin only")

elif st.session_state.page=="Help & Manual for Timar Analytics":
    st.header("📖 Help & Manual for Timar Analytics")
    with st.container(border=True):
        st.subheader("🌾 TIMAR ANALYTICS - User Manual - All 15 Modules")
        st.write("**1. Dashboard:** View all 520 sample, filter by 10 Tools, choose chart")
        st.write("**2. Analytics:** RESTORED - Filtered analytics by Data Collection Tool + chart + auto insights")
        st.write("**3. Data Upload:** Upload CSV/Excel - becomes ACTIVE instantly")
        st.write("**4. M&E Module:** LogFrame 4x4, Budget Matrix, Results Chain, Risk Matrix etc - 10 tools")
        st.write("**5. WASH Module:** Water source, latrine, handwashing - 8 questions")
        st.write("**6. Livelihood Module:** Income 300k to 800k, food months, savings")
        st.write("**7. Health Module:** VHT screening malaria, TB, malnutrition")
        st.write("**8. Education Module:** Enrolled vs dropout, fees, distance")
        st.write("**9. Agriculture Module:** Farm size, yield 1.0 to 3.0 tons, crop type")
        st.write("**10. Research Module:** Custom research title, objective, methodology")
        st.write("**11. KPI Matrix:** 5 KPIs baseline target achieved progress %")
        st.write("**12. Statistical Tools:** 9 tools at once - Summary, Bar, Pie, Line, Scatter, Histogram, Area, Matrix, Full Stats in 5 tabs")
        st.write("**13. Payment:** Click plan → numbers appear → upload receipt → AUTO CONFIRMED")
        st.write("**14. Reviews:** Write + View All Reviews tab with search - FIXED visible")
        st.write("**15. Admin:** Activity log, Users delete, Payments confirm/refund - No duplicate key error - FIXED")
        st.write("**MTN:** 0789876277 Tino Mary | **Airtel:** 0755453313 Tino Mary")
        st.write("**Free Trial:** 24 hours 520 rows | **Login Admin:** Admin / admin@45697")

elif st.session_state.page=="Admin - Monitoring Panel":
    if not is_admin(): st.error("Admin only - Login as Admin"); st.stop()
    st.header("Admin Monitoring Panel - Tino Mary")
    tab1, tab2, tab3 = st.tabs(["📜 Activity Log", "👥 Users", "💰 Payments"])
    with tab1:
        logs = load_json("timar_activity_log.json", [])
        if logs: st.dataframe(pd.DataFrame(logs[::-1]), width='stretch')
        else: st.write("No logs yet")
        if st.button("Clear Activity Log"): save_json("timar_activity_log.json", []); st.success("Cleared"); st.rerun()
    with tab2:
        users = load_users(); trials = load_json("trials.json", {})
        st.write(f"Total Users: {len([u for u in users if u.lower()!='admin'])}")
        user_list = [u for u in users.keys() if u.lower()!= "admin"]
        for idx, u in enumerate(user_list):
            c1, c2, c3 = st.columns([2, 2, 1])
            c1.write(f"👤 {u}"); c2.write(trials.get(u, {}).get("start", "")[:16])
            if c3.button("Delete", key=f"del_{idx}_{u.replace(' ', '_')}"):
                if u in users: del users[u]
                save_json("users.json", users); trials.pop(u, None); save_json("trials.json", trials); st.success(f"{u} deleted"); st.rerun()
    with tab3:
        tr = load_json("timar_transactions.json", [])
        total = sum([x["Amount"] for x in tr if "REFUNDED" not in x.get("Status","")])
        st.metric("Total Collected", f"UGX {total:,}")
        if not tr: st.write("No payments yet")
        for idx in range(len(tr)-1, -1, -1):
            t = tr[idx]
            with st.container(border=True):
                st.write(f"**{t['User']}** | {t['Plan']} | UGX {t['Amount']:,} | {t['Time']} | {t.get('Status','')}")
                if os.path.exists(t.get("Receipt","")): st.write(f"Receipt: {t['Receipt']}")
                col_a, col_b = st.columns(2)
                if col_a.button("✅ Confirm", key=f"conf_{idx}_{t['User']}"): tr[idx]["Status"] = "CONFIRMED BY ADMIN"; save_json("timar_transactions.json", tr); st.rerun()
                if col_b.button("↩️ Refund", key=f"refund_{idx}_{t['User']}_{t['Time']}"): tr[idx]["Status"] = "REFUNDED BY ADMIN"; save_json("timar_transactions.json", tr); st.rerun()

st.markdown("""<div style="text-align:center; color:#2E7D32; font-weight:bold; margin-top:30px;"><hr>🌾 TIMAR ANALYTICS © 2026 |<br></div>""", unsafe_allow_html=True)
