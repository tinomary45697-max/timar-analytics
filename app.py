import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
import plotly.express as px
import os, json
import numpy as np

st.set_page_config(page_title="TIMAR ANALYTICS", layout="wide", initial_sidebar_state="expanded")

# === 9 MASTER DATASETS - GLOBAL ===
@st.cache_data
def load_9_master_files():
    master_files = {
        "00_MASTER_ALL_9_AUTO (Recommended)": "00_TIMAR_MASTER_AUTO_ALL_9.csv",
        "01_UBOS Agriculture": "01_UBOS_AAS_2018_TIMAR_REAL.csv",
        "02_UNHCR Refugees": "02_UNHCR_Uganda_TIMAR_REAL.csv",
        "03_MoH Health": "03_MoH_DHIS2_TIMAR_REAL.csv",
        "04_WASH MWE": "04_WASH_Uganda_MWE_TIMAR_REAL.csv",
        "05_Livelihood": "05_Livelihood_Uganda_TIMAR_REAL.csv",
        "06_GBV Protection": "06_GBV_Uganda_TIMAR_REAL.csv",
        "07_Inventory Stock": "07_Inventory_Uganda_TIMAR_REAL.csv",
        "08_ME Results": "08_ME_Uganda_TIMAR_REAL.csv",
        "09_Research Thesis (PhD Ready)": "09_Research_Uganda_TIMAR_REAL.csv"
    }
    available = {}
    for label, fname in master_files.items():
        if os.path.exists(fname):
            try:
                df = pd.read_csv(fname)
                available[label] = (fname, df)
            except:
                pass
    # fallback old names
    for fname in ["TIMAR_MASTER_AUTO_ALL_9.csv", "Research_Uganda_TIMAR_REAL.csv"]:
        if os.path.exists(fname) and fname not in [v[0] for v in available.values()]:
            try:
                df = pd.read_csv(fname)
                available[fname] = (fname, df)
            except:
                pass
    return available

NINE_DATASETS = load_9_master_files()

try:
    from research_module import render_research_module
except:
    def render_research_module(df, chart): st.info("Research module not found")
try:
    from admin_module import render_admin_panel
    HAS_EXTERNAL_ADMIN = True
except:
    HAS_EXTERNAL_ADMIN = False

@st.cache_data
def load_sample_data(choice):
    files = {
        "UBOS Poverty by Region (NGO Demo)": "ubos_poverty_sample.csv",
        "BoU Inflation & USD/UGX (Business Demo)": "bou_inflation_sample.csv",
        "MOH Health - Malaria & ANC (Health NGO Demo)": "moh_health_sample.csv",
        "UBOS Population Census 2024 (Research Demo)": "ubos_population_2024_sample.csv",
        "World Bank Uganda GDP & Education": "worldbank_uganda_sample.csv"
    }
    try:
        return pd.read_csv(files[choice]), choice
    except FileNotFoundError:
        dummy = pd.DataFrame({"Region":["Central","Eastern"],"Poverty_Rate_%":[20,30],"Year":[2024,2024],"Poor_Persons":[100,200],"Date":["2024-01-01","2024-02-01"],"Inflation_Rate_%":[5.1,5.2],"USD_UGX":[3800,3850],"District":["Kampala","Gulu"],"Malaria_Cases_per_1000":[100,150],"Immunization_Coverage_%":[80,85],"Population_2024":[1000000,800000],"Female_%":[51,52],"GDP_Billion_USD":[40,45],"Life_Expectancy":[63,64]})
        return dummy, choice + " (Demo Fallback)"

STANDARD_TOOLS = ["Overview - All Data","Questionnaire - Structured Questions","Interview - Key Informant Interview","Focus Group Discussion (FGD)","Observation Checklist","Survey Form - Household Survey","Case Study Tool","Document Review / Secondary Data","Mobile Data Collection (Kobo/ODK)","Experimental Data Collection"]
PLANS = ["FREE","BASIC","STANDARD","PREMIUM","PRO","ENTERPRISE","ADMIN_FREE","ADMIN_BASIC","ADMIN_STANDARD","ADMIN_PREMIUM","ADMIN_PRO","ADMIN_ENTERPRISE","ADMIN_UNLIMITED","STUDENT","RESEARCHER"]
MTN_NUMBER = "0789876277"; MTN_NAME = "Tino Mary"; THEME = "Blue & Gold"
ADMIN_PASSWORD = "admin@45697"

DATA_COLLECTION_SAMPLES = {
    "Overview - All Data": ["Q1: Total records?","Q2: Data quality?","Q3: Missing values?","Q4: Top regions?","Q5: Date range?","Q6: User who collected?"],
    "Questionnaire - Structured Questions": ["1. What is your age? (18-25, 26-35, 36-45, 46+)","2. What is your gender? (Male/Female/Other)","3. What is your highest education level? (None/Primary/Secondary/University)","4. What is your monthly income in UGX?","5. What is your farm size in acres?","6. What is your crop yield in tons per season?","7. What is your main source of water? (Borehole/River/Well/Tap)","8. Which region are you from? (Central/Eastern/Northern/Western)","9. What is your district?","10. How often do you access extension services?"],
    "Interview - Key Informant Interview": ["1. Describe main challenges?","2. Most successful interventions?","3. Climate change effects?","4. Support needed?","5. Opinion on policies?"],
    "Focus Group Discussion (FGD)": ["1. Common farming practices?","2. How share info?","3. Challenges women face?","4. How decide crops?","5. What would help improve yields?"],
    "Observation Checklist": ["1. Farm well maintained? (Yes/No)","2. Crops observed","3. Irrigation present?","4. Storage condition?","5. Use of improved seeds?"],
    "Survey Form - Household Survey": ["1. Household size?","2. Head gender?","3. Income source?","4. Food security months?","5. Asset ownership?"],
    "Case Study Tool": ["1. Case title?","2. Background?","3. Challenge?","4. Intervention?","5. Results?","6. Lessons?"],
    "Document Review / Secondary Data": ["1. Document title?","2. Source?","3. Year?","4. Key findings?","5. Data extracted?","6. Quality?"],
    "Mobile Data Collection (Kobo/ODK)": ["1. Form ID?","2. Enumerator?","3. GPS captured?","4. Photo?","5. Submission status?"],
    "Experimental Data Collection": ["1. What is the experimental plot size?","2. What treatment was applied?","3. What is the control group measurement?","4. What is yield in treatment vs control?","5. What is germination rate?","6. What is soil pH and moisture level?","7. Observations on crop health?","8. Pest/Disease incidence?","9. Statistical significance (p-value)?","10. Researcher name and date?"],
    "WASH Module": ["1. Main water source?","2. Distance?","3. Has latrine?","4. Latrine type?","5. Handwashing?","6. Open defecation?","7. Treatment?","8. Storage?"],
    "Livelihood Module": ["1. Main income source?","2. Monthly income UGX?","3. Other income?","4. Food months /12?","5. Meals?","6. Savings?","7. Coping?","8. Assets?"],
    "Health Module": ["1. Patient name","2. Age","3. Sex","4. Disease","5. Symptoms","6. Tested?","7. Referred?","8. Follow-up"],
    "Education Module": ["1. Pupil name","2. Age","3. Sex","4. Class","5. Status","6. Reason dropout","7. Distance","8. Fees?","9. Materials?"],
    "Agriculture Module": ["1. Farmer name","2. Farm size","3. Crop type","4. Season","5. Seed type","6. Yield","7. Inputs?","8. Training?","9. Challenges?","10. Will plant again?"],
    "Research Module": ["1. Title","2. Objective","3. Methodology","4. Sample size","5. Sampling","6. Tool","7. Data","8. Analysis","9. Findings","10. Recommendations"]
}
ME_TOOLS = ["LogFrame - Logical Framework 4x4","Results Chain / Result Framework","Indicator Tracking Matrix","Risk Matrix - Likelihood x Impact","Stakeholder Matrix - Power/Interest","Data Collection Matrix","Budget Matrix - Activity Based","M&E Plan Matrix","Theory of Change","Problem Tree to Objective Tree"]
ALL_CHARTS = ["Bar Chart","Pie Chart","Line Chart","Scatter Plot","Histogram","Area Chart","Table View","Summary Statistics","Matrix View"]
MODULES = ["Dashboard","Analytics","9 Master Datasets - TIMAR REAL","Data Upload","Data Collection Tools - All 10","M&E Module","WASH Module","Livelihood Module","Health Module","Education Module","Agriculture Module","Research Module","KPI Matrix","Statistical Tools","Inventory & Stock Movement","Payment & Plans","Reviews & Comments","Help & Manual for Timar Analytics","Admin - Monitoring Panel"]

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
    logs=load_json("timar_activity_log.json",[]); logs.append({"Time":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"User":user,"Action":action,"Details":details}); save_json("timar_activity_log.json",logs[-500:])
def check_trial(user):
    if not user: return True,"No User"
    if user.lower()=="admin": return True,"Admin Unlimited"
    if st.session_state.get("plan","FREE")!="FREE": return True,"Paid Active"
    trials=load_json("trials.json",{})
    if user not in trials: return True,"24.0h left"
    start=datetime.datetime.fromisoformat(trials[user]["start"]); left=24-(datetime.datetime.now()-start).total_seconds()/3600
    return (False,"Expired") if left<=0 else (True,f"{left:.1f}h left")
def is_admin(): return str(st.session_state.get("username","")).lower()=="admin"

for k,v in [("logged_in",False),("username",""),("user",""),("page","Dashboard"),("tool","Experimental Data Collection"),("standard_tool","Questionnaire - Structured Questions"),("chart","Bar Chart"),("metool","LogFrame - Logical Framework 4x4"),("plan","ADMIN_UNLIMITED"),("show_signup",False),("selected_plan",None),("active_master","00_MASTER_ALL_9_AUTO (Recommended)")]:
    if k not in st.session_state: st.session_state[k]=v
if 'current_df' not in st.session_state:
    if NINE_DATASETS:
        first_key = list(NINE_DATASETS.keys())[0]
        st.session_state.current_df = NINE_DATASETS[first_key][1]
        st.session_state.active_master = first_key
    else:
        @st.cache_data
        def load_data():
            data = {'ID': range(340, 394),'Region': ['Central']*13 + ['Eastern']*12 + ['Northern']*12 + ['Western']*17,'Education': ['Secondary','Primary','University','Primary']*13 + ['Secondary']*2,'Yield': [4.5,7.4,6.7,1.7,3.8,4.1,0.2,0.6]*6 + [4.5,7.4,6.7,1.7,3.8,4.1],'Water_Source': ['River']*54,'Irrigation': ['No','Yes','Yes','Yes']*13 + ['Yes']*2,'Crop': ['Beans','Coffee','Beans','Maize']*13 + ['Beans','Maize'],'Health': ['Healthy','Malnutrition','Malnutrition','Healthy']*13 + ['Healthy']*2,'Status': ['Dropout','Dropout','Enrolled','Dropout']*13 + ['Enrolled']*2,'Age': np.random.randint(18,65,54),'Income': np.random.randint(200000,1500000,54)}
            return pd.DataFrame(data)
        st.session_state.current_df = load_data()

if not st.session_state.logged_in:
    st.markdown("""<style>[data-testid="stSidebar"]{display:none;}header{visibility:hidden;}.stApp{background:linear-gradient(135deg,#0F2C5C 0%,#1E3A8A 50%,#1E40AF 100%)!important;}.login-card{background:white;padding:35px 30px;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,0.3);text-align:center;margin-top:30px;}.login-card h1{color:#1E3A8A;font-size:28px;font-weight:800;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""<div class="login-card"><h1>🌾 TIMAR ANALYTICS</h1><p>Uganda's Smart Data Platform | Secure Login</p><p style="font-size:12px;color:#1E3A8A;font-weight:bold;">⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p></div>""", unsafe_allow_html=True)
        st.write("")
        users = load_users()
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter username", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="login_pass")
            c1,c2 = st.columns(2)
            with c1: submit_login = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            with c2: submit_signup_toggle = st.form_submit_button("Sign Up 24h Trial", use_container_width=True)
            if submit_login:
                if username.lower()=="admin" and password==ADMIN_PASSWORD:
                    st.session_state.logged_in=True; st.session_state.username="Admin"; st.session_state.user="Admin"; st.session_state.plan="ADMIN_FREE"; log_activity("Admin","LOGIN"); st.rerun()
                elif username in users and users[username]==password:
                    st.session_state.logged_in=True; st.session_state.username=username; st.session_state.user=username
                    trials=load_json("trials.json",{})
                    if username not in trials: trials[username]={"start":datetime.datetime.now().isoformat()}; save_json("trials.json",trials)
                    log_activity(username,"LOGIN"); st.rerun()
                else: st.error("Invalid username or password")
            if submit_signup_toggle: st.session_state.show_signup = True
        if st.session_state.get("show_signup", False):
            with st.container(border=True):
                st.markdown("### Create Account - 24h FREE TRIAL")
                nu=st.text_input("Choose Username",key="s_u"); npw=st.text_input("Choose Password",type="password",key="s_p"); cpw=st.text_input("Confirm Password",type="password",key="s_c"); phone=st.text_input("Phone Number", placeholder="07XXXXXXXX"); agree=st.checkbox("I agree to start 24hr free trial")
                if st.button("Create & Start Trial",type="primary",use_container_width=True, key="btn_create"):
                    users=load_users()
                    if not nu or not npw: st.error("Username & password required")
                    elif npw!=cpw: st.error("Passwords don't match")
                    elif nu in users: st.error("Username exists")
                    elif not agree: st.error("Please agree to trial")
                    else:
                        users[nu]=npw; save_json("users.json",{k:v for k,v in users.items() if k!="Admin"}); trials=load_json("trials.json",{}); trials[nu]={"start":datetime.datetime.now().isoformat(),"phone":phone}; save_json("trials.json",trials); log_activity(nu,"SIGNUP"); st.success(f"Account {nu} created! Now Sign In above."); st.balloons()
    st.stop()

df = st.session_state.current_df
now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ok,msg=check_trial(st.session_state.username)

with st.sidebar:
    st.title("🌾 TIMAR ANALYTICS")
    st.markdown(f"""<div style="background:white;padding:10px;border-radius:10px;text-align:center;"><p style="color:#1E3A8A!important;font-weight:900;margin:0;">👤 USER ID: {st.session_state.username}</p><p style="color:#D4AF37!important;font-weight:bold;margin:0;">⏰ {now_str}</p><p style="color:#1E3A8A!important;font-size:11px;margin:0;">Plan: {st.session_state.plan} | Rows: {len(df)}</p></div>""", unsafe_allow_html=True)
    st.caption(f"MTN {MTN_NUMBER} - {MTN_NAME}")

    # === GLOBAL DROPDOWN FOR 9 DATASETS ===
    st.divider()
    st.markdown("### 🚀 9 Master Data (Dropdown)")
    if NINE_DATASETS:
        st.success(f"✅ {len(NINE_DATASETS)} auto-found")
        master_choice = st.selectbox("Select Dataset:", list(NINE_DATASETS.keys()), index=list(NINE_DATASETS.keys()).index(st.session_state.active_master) if st.session_state.active_master in NINE_DATASETS else 0, key="master_select_sidebar")
        if st.button("🔵 Load Dataset", key="load_master_btn_sidebar", use_container_width=True):
            fname, fdf = NINE_DATASETS[master_choice]
            st.session_state.current_df = fdf
            st.session_state.active_master = master_choice
            log_activity(st.session_state.username, "LOAD_MASTER_SIDEBAR", fname)
            st.rerun()
        st.caption(f"Active: {st.session_state.active_master}")
    else:
        st.warning("No CSVs found. Add 00_ to 09_ files.")

    st.divider()
    sel_mod = st.selectbox("📦 Modules - 19 Total", MODULES, index=MODULES.index(st.session_state.page) if st.session_state.page in MODULES else 0, key="mod_select")
    st.session_state.page = sel_mod
    st.markdown(f"<div style='background:#D4AF37;color:white;padding:6px;border-radius:8px;text-align:center;font-weight:bold;'>✅ {sel_mod}</div>", unsafe_allow_html=True)
    sel_standard = st.selectbox("📋 STANDARD_TOOLS - 10 Tools", STANDARD_TOOLS, index=STANDARD_TOOLS.index(st.session_state.standard_tool) if st.session_state.standard_tool in STANDARD_TOOLS else 0, key="standard_tool_select")
    st.session_state.standard_tool = sel_standard
    sel_chart = st.selectbox("📈 Chart Type", ALL_CHARTS, index=ALL_CHARTS.index(st.session_state.chart) if st.session_state.chart in ALL_CHARTS else 0, key="chart_select")
    st.session_state.chart = sel_chart
    st.divider()
    if st.button("🚪 Logout", width='stretch', key="logout_btn"):
        log_activity(st.session_state.username,"LOGOUT"); st.session_state.logged_in=False; st.session_state.username=""; st.session_state.user=""; st.rerun()

st.markdown(f"""<div style="background:linear-gradient(90deg,#1E3A8A 0%,#1E40AF 50%,#D4AF37 100%);padding:15px;border-radius:15px;margin-bottom:15px;"><div style="display:flex;justify-content:space-between;flex-wrap:wrap;"><div><h1 style="color:white!important;margin:0;">🌾 TIMAR ANALYTICS 📊</h1><p style="color:#FEF3C7;margin:0;font-weight:bold;">Tool: {st.session_state.standard_tool} | User: {st.session_state.username} | Active: {st.session_state.active_master}</p></div><div style="background:white;padding:10px 15px;border-radius:10px;min-width:280px;"><p style="color:#1E3A8A!important;font-weight:900;margin:0;">👤 {st.session_state.username}</p><p style="color:#D4AF37!important;font-weight:bold;margin:0;">⏰ {now_str}</p><p style="color:#1E3A8A!important;margin:0;font-size:11px;">Module: {st.session_state.page}</p></div></div></div>""", unsafe_allow_html=True)

def auto_interpret(data, chart_type, col_name):
    if len(data)==0: return "No data."
    try:
        if col_name not in data.columns: col_name = data.columns[0]
        vc = data[col_name].value_counts(); top = vc.idxmax(); top_c = vc.max()
        return f"**Interpretation ({chart_type}):** {col_name} shows {top} dominant with {top_c} records ({top_c/len(data)*100:.1f}%). User {st.session_state.username} at {now_str}."
    except: return f"**Interpretation:** {len(data)} records for {st.session_state.username}."

def render_chart(data, chart_type, col_name, title_suffix=""):
    if len(data)==0: st.warning("No data"); return
    if col_name not in data.columns: col_name = data.columns[0]
    counts = data[col_name].value_counts().reset_index()
    counts.columns = [col_name, "Count"]
    try:
        if chart_type=="Bar Chart":
            fig = px.bar(counts, x=col_name, y="Count", color=col_name, text="Count", title=f"{col_name} - Bar {title_suffix}")
            fig.update_layout(showlegend=False); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Pie Chart":
            fig = px.pie(counts, names=col_name, values="Count", title=f"{col_name} - Pie {title_suffix}", hole=0.3); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Line Chart":
            fig = px.line(counts, x=col_name, y="Count", markers=True, title=f"{col_name} - Line"); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Scatter Plot":
            fig = px.scatter(counts, x=col_name, y="Count", size="Count", color=col_name, title=f"{col_name} - Scatter"); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Histogram":
            fig = px.histogram(data, x=col_name, title=f"{col_name} - Histogram"); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Area Chart":
            fig = px.area(counts, x=col_name, y="Count", title=f"{col_name} - Area"); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Summary Statistics": st.dataframe(data.describe(include='all'), width='stretch')
        elif chart_type=="Matrix View":
            if len(data.columns)>=2: st.dataframe(pd.crosstab(data[data.columns[0]], data[data.columns[1]]), width='stretch')
            else: st.dataframe(data.head(20), width='stretch')
        else: st.dataframe(data.head(100), width='stretch')
        st.info(auto_interpret(data, chart_type, col_name))
    except Exception as e:
        st.error(f"Chart error: {e}"); st.dataframe(counts, width='stretch')

# ============ 9 MASTER DATASETS PAGE WITH DROPDOWN ============
if st.session_state.page == "9 Master Datasets - TIMAR REAL":
    st.header(f"📦 9 Master Datasets - TIMAR REAL | 👤 {st.session_state.username} | ⏰ {now_str}")
    if not NINE_DATASETS:
        st.error("❌ No 9 master CSVs found. Put 00_ to 09_ files in folder.")
        st.stop()
    st.success(f"✅ {len(NINE_DATASETS)} REAL datasets ready - with dropdown selector")
    col1, col2 = st.columns([3,1])
    with col1:
        selected_label = st.selectbox("📂 Select Dataset (Dropdown):", list(NINE_DATASETS.keys()), index=list(NINE_DATASETS.keys()).index(st.session_state.active_master) if st.session_state.active_master in NINE_DATASETS else 0, key="nine_dropdown_main")
    with col2:
        if st.button("🔵 LOAD NOW", type="primary", use_container_width=True, key="load_nine_main"):
            fname, fdf = NINE_DATASETS[selected_label]
            st.session_state.current_df = fdf
            st.session_state.active_master = selected_label
            log_activity(st.session_state.username, "LOAD_9_PAGE", fname)
            st.rerun()
    fname, fdf = NINE_DATASETS[selected_label]
    st.info(f"Previewing: **{selected_label}** → `{fname}` | **{len(fdf)} rows x {len(fdf.columns)} cols**")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Rows", len(fdf)); c2.metric("Cols", len(fdf.columns)); c3.metric("Avg Yield", f"{fdf['Yield'].mean():.2f}" if 'Yield' in fdf.columns else "N/A"); c4.metric("Regions", fdf['Region'].nunique() if 'Region' in fdf.columns else "N/A")
    if 'Education' in fdf.columns and 'Yield' in fdf.columns:
        edu_yield = fdf.groupby('Education')['Yield'].mean().round(2)
        st.write("**Education → Yield:**", edu_yield.to_dict())
    t1,t2,t3 = st.tabs(["📄 Data","📊 Chart","📋 All 9 List"])
    with t1: st.dataframe(fdf.head(100), use_container_width=True)
    with t2: render_chart(fdf, st.session_state.chart, 'Region' if 'Region' in fdf.columns else fdf.columns[0], selected_label)
    with t3:
        for label, (f, d) in NINE_DATASETS.items():
            with st.container(border=True):
                st.write(f"**{label}** - `{f}` - {len(d)} rows")
                st.dataframe(d.head(3), use_container_width=True)

# ============ ADMIN PANEL - OWN TABS ONLY ============
elif st.session_state.page == "Admin - Monitoring Panel":
    st.header(f"🛡️ Admin - Monitoring Panel | 👤 {st.session_state.username} | ⏰ {now_str}")
    if not is_admin():
        st.error("⛔ Access Denied - Admin Only"); st.stop()
    if HAS_EXTERNAL_ADMIN:
        try: render_admin_panel(); st.divider()
        except: pass
    st.subheader("🔒 Internal Admin Monitor - Own Tabs")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 Users & Logins","⏰ Trials 24h","💳 Payments","📝 Activity Logs","⚙️ System Health"])
    with tab1:
        users = load_users(); st.metric("Total Users", len(users))
        st.dataframe(pd.DataFrame([{"Username":k} for k in users.keys()]), use_container_width=True)
    with tab2:
        trials = load_json("trials.json", {}); st.metric("Trials", len(trials))
        if trials: st.dataframe(pd.DataFrame([{"User":k, "Start":v.get("start","")} for k,v in trials.items()]), use_container_width=True)
    with tab3:
        subs = load_json("subscriptions.json", {}); st.metric("Subscriptions", len(subs))
        if subs: st.dataframe(pd.DataFrame([{"User":k, "Plan":v.get("plan"), "Txn":v.get("txn")} for k,v in subs.items()]), use_container_width=True)
    with tab4:
        logs = load_json("timar_activity_log.json", []); st.metric("Logs", len(logs))
        if logs: st.dataframe(pd.DataFrame(logs[-100:][::-1]), use_container_width=True)
    with tab5:
        st.metric("CSV Files", len([f for f in os.listdir(".") if f.endswith(".csv")]))
        st.write([f for f in os.listdir(".") if f.endswith(".csv")][:20])
        st.metric("Active Dataset", st.session_state.active_master)
        st.dataframe(df.head(10), use_container_width=True)

elif st.session_state.page == "Payment & Plans":
    st.title("💳 Payment & Plans | "+ now_str)
    if st.session_state.user == "Admin": st.success("✅ ADMIN_UNLIMITED")
    if "selected_plan" not in st.session_state: st.session_state.selected_plan=None
    subs = load_json("subscriptions.json", {})
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.markdown("### 🎓 STUDENT\n## UGX 10,000")
            if st.button("Select STUDENT", key="s1", use_container_width=True): st.session_state.selected_plan="STUDENT"; st.rerun()
    with c2:
        with st.container(border=True):
            st.markdown("### 🔬 RESEARCHER\n## UGX 30,000")
            if st.button("Select RESEARCHER", type="primary", key="s2", use_container_width=True): st.session_state.selected_plan="RESEARCHER"; st.rerun()
    with c3:
        with st.container(border=True):
            st.markdown("### 🏢 NGO\n## UGX 300,000")
            if st.button("Select NGO", key="s3", use_container_width=True): st.session_state.selected_plan="NGO"; st.rerun()
    with c4:
        with st.container(border=True):
            st.markdown("### 🏛️ GOVERNMENT\n## UGX 500,000")
            if st.button("Select GOVERNMENT", key="s4", use_container_width=True): st.session_state.selected_plan="GOVERNMENT"; st.rerun()
    if st.session_state.selected_plan:
        plan=st.session_state.selected_plan; prices={"STUDENT":10000,"RESEARCHER":30000,"NGO":300000,"GOVERNMENT":500000}
        st.markdown(f"## ✅ {plan} - UGX {prices[plan]:,}")
        txn=st.text_input("MoMo Transaction ID *", key="txn_input")
        if st.button("Confirm Payment", type="primary", use_container_width=True, key="confirm_pay"):
            if txn:
                subs[st.session_state.user]={"plan":plan,"amount":prices[plan],"txn":txn,"expires":(datetime.datetime.now()+timedelta(days=30)).isoformat(),"status":"PENDING"}
                save_json("subscriptions.json", subs); st.success("Submitted"); st.balloons()

elif st.session_state.page=="Data Collection Tools - All 10":
    st.header(f"📋 Data Collection Tools | 👤 {st.session_state.username} | ⏰ {now_str}")
    t_overview, t_current = st.tabs(["📦 Overview - All 10 Tools", f"🔧 Current: {st.session_state.standard_tool}"])
    with t_overview:
        st.info("Questions hidden - click Show to reveal")
        for tool in STANDARD_TOOLS:
            with st.expander(f"📋 {tool} ({len(DATA_COLLECTION_SAMPLES.get(tool,[]))} Qs)", expanded=False):
                if st.button(f"👁️ Show Questions for {tool}", key=f"show_q_{tool}"):
                    for q in DATA_COLLECTION_SAMPLES.get(tool, []): st.write(f"- {q}")
                st.dataframe(df.head(5), width='stretch')
        render_chart(df, st.session_state.chart, df.columns[0], "Overview")
    with t_current:
        tool_name = st.session_state.standard_tool
        q_tab, form_tab, chart_tab, data_tab = st.tabs(["📋 Questions (Hidden)","📝 Form","📊 Chart","📄 Data"])
        with q_tab:
            if f"reveal_{tool_name}" not in st.session_state: st.session_state[f"reveal_{tool_name}"]=False
            if st.button(f"👁️ Reveal Questions for {tool_name}", key=f"reveal_btn_{tool_name}", type="primary"):
                st.session_state[f"reveal_{tool_name}"]=True
            if st.session_state[f"reveal_{tool_name}"]:
                for i, q in enumerate(DATA_COLLECTION_SAMPLES.get(tool_name, []), 1): st.write(f"**{i}.** {q}")
                if st.button(f"🙈 Hide", key=f"hide_btn_{tool_name}"): st.session_state[f"reveal_{tool_name}"]=False; st.rerun()
            else:
                st.info(f"🔒 {len(DATA_COLLECTION_SAMPLES.get(tool_name,[]))} questions hidden.")
        with form_tab:
            if st.button(f"💾 Save {tool_name}", type="primary", width='stretch', key=f"save_{tool_name}"):
                responses=load_json(f"responses_{tool_name}_{st.session_state.username}.json", []); responses.append({"Time":now_str,"User":st.session_state.username}); save_json(f"responses_{tool_name}_{st.session_state.username}.json", responses); st.success("Saved!")
        with chart_tab: render_chart(df, st.session_state.chart, df.columns[0], f"{tool_name}")
        with data_tab: st.dataframe(df.head(100), width='stretch')

elif st.session_state.page=="Dashboard":
    st.header(f"Dashboard | 👤 {st.session_state.username} | ⏰ {now_str}")
    st.caption(f"Active: {st.session_state.active_master}")
    with st.expander(f"📋 {st.session_state.standard_tool} - Hidden", expanded=False):
        if st.button("Reveal questions", key="dash_reveal"):
            for q in DATA_COLLECTION_SAMPLES.get(st.session_state.standard_tool, []): st.write(f"- {q}")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Records", len(df)); c2.metric("Cols", len(df.columns)); c3.metric("Regions", df['Region'].nunique() if 'Region' in df.columns else 0); c4.metric("Avg Yield", f"{df['Yield'].mean():.2f}" if 'Yield' in df.columns else "N/A")
    st.dataframe(df.head(50), width='stretch')
    render_chart(df, st.session_state.chart, 'Region' if 'Region' in df.columns else df.columns[0], "")

elif st.session_state.page=="Analytics":
    st.header(f"📊 Analytics | {st.session_state.username}")
    render_chart(df, st.session_state.chart, df.columns[0], "")

elif st.session_state.page=="Data Upload":
    st.header(f"Data Upload | 👤 {st.session_state.username} | ⏰ {now_str}")
    if NINE_DATASETS:
        with st.expander("🚀 Quick Load 9 Master Datasets (Dropdown)", expanded=True):
            sel = st.selectbox("Choose:", list(NINE_DATASETS.keys()), key="upload_master_sel")
            if st.button("Load Master", key="upload_load_master"): st.session_state.current_df=NINE_DATASETS[sel][1]; st.session_state.active_master=sel; st.rerun()
    up=st.file_uploader("Upload ANY File", type=["csv","xlsx","xls"], key="file_uploader")
    if up:
        try:
            if up.name.endswith(".csv"):
                try: ndf=pd.read_csv(up)
                except: up.seek(0); ndf=pd.read_csv(up, encoding='latin1')
            else: ndf=pd.read_excel(up)
            ndf.columns=[str(c).strip() for c in ndf.columns]; ndf=ndf.dropna(how='all')
            st.session_state.current_df=ndf; st.success(f"✅ {len(ndf)} rows"); st.balloons()
        except Exception as e: st.error(str(e))
    st.dataframe(df.head(50), width='stretch')

elif st.session_state.page in ["M&E Module","WASH Module","Livelihood Module","Health Module","Education Module","Agriculture Module","Research Module","KPI Matrix","Statistical Tools","Inventory & Stock Movement","Reviews & Comments","Help & Manual for Timar Analytics"]:
    st.header(f"{st.session_state.page} | 👤 {st.session_state.username} | ⏰ {now_str}")
    st.dataframe(df.head(50), width='stretch')
    render_chart(df, st.session_state.chart, df.columns[0], st.session_state.page)

st.markdown(f"""<div style="text-align:center;color:#1E3A8A;font-weight:bold;margin-top:30px;"><hr>🌾 TIMAR © 2026 | User: {st.session_state.username} | Active: {st.session_state.active_master} | Admin Own Tabs</div>""", unsafe_allow_html=True)
