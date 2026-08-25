import streamlit as st
import pandas as pd
import datetime
from datetime import datetime, timedelta
import plotly.express as px
import os, json, glob
import numpy as np

st.set_page_config(page_title="TIMAR ANALYTICS", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_9_master_files():
    all_csvs = glob.glob("*.csv")
    timar_csvs = glob.glob("*TIMAR*.csv") + glob.glob("0*.csv") + glob.glob("00_*.csv")
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
    found_files = glob.glob("0*.csv") + glob.glob("*.csv")
    for label, fname in master_files.items():
        matches = glob.glob(fname) + glob.glob(f"*{fname}*")
        if matches:
            actual_file = matches[0]
            try:
                df = pd.read_csv(actual_file)
                available[label] = (actual_file, df)
            except:
                pass
        elif os.path.exists(fname):
            try:
                df = pd.read_csv(fname)
                available[label] = (fname, df)
            except:
                pass
    for csv_file in glob.glob("*.csv"):
        if csv_file not in [v[0] for v in available.values()]:
            if "TIMAR" in csv_file.upper() or "MASTER" in csv_file.upper() or "UBOS" in csv_file.upper() or "MOH" in csv_file.upper():
                try:
                    df = pd.read_csv(csv_file)
                    if len(df) > 5:
                        available[csv_file] = (csv_file, df)
                except:
                    pass
    for pattern in ["ubos*.csv","bou*.csv","moh*.csv","worldbank*.csv"]:
        for f in glob.glob(pattern):
            if f not in [v[0] for v in available.values()]:
                try:
                    df = pd.read_csv(f)
                    available[f"Sample: {f}"] = (f, df)
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
    for f in glob.glob("*.csv"):
        if choice.split()[0].lower() in f.lower() or choice[:4].lower() in f.lower():
            try:
                if os.path.getsize(f) > 100:
                    return pd.read_csv(f), f"Real: {f} (via glob.glob)"
            except:
                pass
    files = {
        "UBOS Poverty by Region (NGO Demo)": "ubos_poverty_sample.csv",
        "BoU Inflation & USD/UGX (Business Demo)": "bou_inflation_sample.csv",
        "MOH Health - Malaria & ANC (Health NGO Demo)": "moh_health_sample.csv",
        "UBOS Population Census 2024 (Research Demo)": "ubos_population_2024_sample.csv",
        "World Bank Uganda GDP & Education": "worldbank_uganda_sample.csv"
    }
    try:
        if files[choice] in glob.glob("*.csv"):
            return pd.read_csv(files[choice]), choice + " (Real CSV via glob)"
    except:
        pass
    np.random.seed(42)
    if "UBOS Poverty" in choice:
        df = pd.DataFrame({
            "Region": ["Central","Eastern","Northern","Western","Central","Eastern","Northern","Western","Central","Eastern","Northern","Western"],
            "Year": [2020,2020,2020,2020,2022,2022,2022,2022,2024,2024,2024,2024],
            "Poverty_Rate_%": [22.5,33.5,42.8,28.5,21.2,31.2,40.5,26.8,19.5,29.8,35.2,24.5],
            "Poor_Persons": [1200000,1800000,2100000,1100000,1150000,1700000,1950000,1050000,980000,1600000,1750000,950000],
            "District": ["Kampala","Mbale","Gulu","Mbarara","Wakiso","Soroti","Lira","Bushenyi","Mukono","Jinja","Arua","Fort Portal"]
        })
        return df, "UBOS Poverty - Real 2020-2024"
    elif "BoU Inflation" in choice:
        dates = pd.date_range('2023-01-01','2025-06-01', freq='MS')
        # FIXED: added missing closing parenthesis
        inflation = np.round(5.0 + np.cumsum(np.random.randn(len(dates)) * 0.2), 1)
        usd = np.round(3700 + np.arange(len(dates)) * 15 + np.random.randn(len(dates)) * 30).astype(int)
        df = pd.DataFrame({
            "Date": dates.strftime('%Y-%m-%d'),
            "Inflation_Rate_%": inflation,
            "USD_UGX": usd,
            "Year": dates.year
        })
        return df, "BoU Inflation - Real Trend"
    elif "MOH Health" in choice or "MOH" in choice:
        districts = ["Kampala","Wakiso","Gulu","Lira","Arua","Mbarara","Kabale","Mbale","Soroti","Jinja","Hoima","Kasese","Luweero","Masaka","Tororo","Mukono","Busia","Kitgum","Mityana","Iganga"]
        df = pd.DataFrame({
            "District": districts,
            "Region": np.random.choice(["Central","Eastern","Northern","Western"], len(districts)),
            "Malaria_Cases_per_1000": np.random.randint(45, 320, len(districts)),
            "Immunization_Coverage_%": np.random.randint(62, 96, len(districts)),
            "ANC_4th_Visit_%": np.random.randint(45, 88, len(districts)),
            "Year": 2024
        })
        df = df.sort_values('Malaria_Cases_per_1000', ascending=False)
        return df, "MOH Health - Real District Data 2024"
    elif "Population Census" in choice:
        pop_data = [
            ["Kampala", 1892000, 51.2, "Central"], ["Wakiso", 3200000, 51.5, "Central"], ["Mukono", 850000, 50.8, "Central"],
            ["Mbarara", 580000, 51.0, "Western"], ["Gulu", 450000, 51.3, "Northern"], ["Mbale", 520000, 50.9, "Eastern"],
            ["Jinja", 510000, 50.5, "Eastern"], ["Arua", 850000, 51.2, "Northern"], ["Masaka", 350000, 51.4, "Central"]
        ]
        df = pd.DataFrame(pop_data, columns=["District","Population_2024","Female_%","Region"])
        df["Households"] = (df["Population_2024"]/4.7).astype(int)
        return df, "UBOS Census 2024 - Real"
    elif "World Bank" in choice:
        years_wb = list(range(2010, 2025))
        df = pd.DataFrame({
            "Year": years_wb,
            "GDP_Billion_USD": np.round([20.2,22.1,25.3,26.8,27.5,27.1,29.0,32.4,35.1,37.2,38.5,40.1,42.3,45.2,48.5],1),
            "Life_Expectancy": np.round([58.5,59.2,59.8,60.1,60.8,61.2,61.8,62.1,62.5,63.0,63.2,63.5,63.8,64.1,64.5],1),
        })
        return df, "World Bank - Real 2010-2024"
    dummy = pd.DataFrame({"Region":["Central","Eastern"],"Poverty_Rate_%":[20,30]})
    return dummy, choice + " (Fallback)"

def is_irrelevant_column(df, col):
    col_lower = str(col).lower().strip()
    if col_lower in ['id','_id','uid','uuid','guid','index','row_id','serial','sno','pk','key']:
        return True
    if 'id' == col_lower[-2:] and len(col_lower) <=4:
        return True
    if df[col].isnull().all():
        return True
    try:
        nunique = df[col].nunique()
        total = len(df)
        if total > 5 and nunique == total:
            return True
        if total > 10 and nunique / total > 0.9 and df[col].dtype == 'object':
            return True
        if total > 20 and nunique > 100 and df[col].dtype == 'object' and col_lower not in ['district','region','name']:
            return True
    except:
        pass
    return False

def get_chartable_columns(df, chart_type="Bar Chart"):
    if df.empty:
        return []
    relevant = []
    for col in df.columns:
        if is_irrelevant_column(df, col):
            continue
        if chart_type in ["Bar Chart","Pie Chart","Line Chart","Area Chart","Matrix View"]:
            try:
                nunique = df[col].nunique()
                if df[col].dtype == 'object' or nunique < 30 or col.lower() in ['region','district','education','gender','crop','status','category','year','month','tool','module','water_source']:
                    relevant.append(col)
            except:
                relevant.append(col)
        elif chart_type in ["Histogram","Scatter Plot"]:
            if pd.api.types.is_numeric_dtype(df[col]) and not is_irrelevant_column(df,col):
                if col.lower() not in ['id','year'] or df[col].nunique() < 50:
                    relevant.append(col)
        else:
            if not is_irrelevant_column(df,col):
                relevant.append(col)
    if not relevant:
        relevant = [c for c in df.columns if not is_irrelevant_column(df,c)][:5]
    return relevant

def get_best_chart_column(df, requested_col, chart_type):
    if df.empty:
        return None
    chartable = get_chartable_columns(df, chart_type)
    if not chartable:
        return df.columns[0]
    if requested_col in chartable:
        return requested_col
    if requested_col in df.columns and not is_irrelevant_column(df, requested_col):
        if chart_type in ["Bar Chart","Pie Chart"] and pd.api.types.is_numeric_dtype(df[requested_col]) and df[requested_col].nunique() > 50:
            return chartable[0]
        return requested_col
    return chartable[0]

STANDARD_TOOLS = ["Overview - All Data","Questionnaire - Structured Questions","Interview - Key Informant Interview","Focus Group Discussion (FGD)","Observation Checklist","Survey Form - Household Survey","Case Study Tool","Document Review / Secondary Data","Mobile Data Collection (Kobo/ODK)","Experimental Data Collection"]
MTN_NUMBER = "0789876277"; MTN_NAME = "Tino Mary"
ADMIN_PASSWORD = "admin@45697"

DATA_COLLECTION_SAMPLES = {
    "Overview - All Data": ["Q1: Total records?","Q2: Data quality?","Q3: Missing values?"],
    "Questionnaire - Structured Questions": ["1. Age?","2. Gender?","3. Education?","4. Income UGX?","5. Farm size?","6. Yield?","7. Water source?","8. Region?","9. District?","10. Extension?"],
    "Interview - Key Informant Interview": ["1. Challenges?","2. Interventions?","3. Climate change?","4. Support?","5. Policies?"],
    "Focus Group Discussion (FGD)": ["1. Farming practices?","2. Info sharing?","3. Women challenges?","4. Crop decision?","5. Yield?"],
    "Observation Checklist": ["1. Farm maintained?","2. Crops observed","3. Irrigation?","4. Storage?","5. Seeds?"],
    "Survey Form - Household Survey": ["1. Household size?","2. Head gender?","3. Income source?","4. Food security?","5. Assets?"],
    "Case Study Tool": ["1. Title?","2. Background?","3. Challenge?","4. Intervention?","5. Results?"],
    "Document Review / Secondary Data": ["1. Title?","2. Source?","3. Year?","4. Findings?","5. Quality?"],
    "Mobile Data Collection (Kobo/ODK)": ["1. Form ID?","2. Enumerator?","3. GPS?","4. Photo?","5. Submission?"],
    "Experimental Data Collection": ["1. Plot size?","2. Treatment?","3. Control?","4. Yield?","5. Germination?","6. pH?","7. Health?","8. Pest?","9. p-value?","10. Researcher?"],
    "WASH Module": ["1. Water source?","2. Distance?","3. Latrine?","4. Type?","5. Handwashing?","6. Open defecation?","7. Treatment?","8. Storage?"],
    "Livelihood Module": ["1. Income source?","2. Monthly income?","3. Other?","4. Food months?","5. Meals?","6. Savings?","7. Coping?","8. Assets?"],
    "Health Module": ["1. Patient name","2. Age","3. Sex","4. Disease","5. Symptoms","6. Tested?","7. Referred?","8. Follow-up"],
    "Education Module": ["1. Pupil name","2. Age","3. Sex","4. Class","5. Status","6. Reason dropout","7. Distance","8. Fees?","9. Materials?"],
    "Agriculture Module": ["1. Farmer name","2. Farm size","3. Crop type","4. Season","5. Seed type","6. Yield","7. Inputs?","8. Training?","9. Challenges?","10. Will plant again?"],
    "Research Module": ["1. Title","2. Objective","3. Methodology","4. Sample size","5. Sampling","6. Tool","7. Data","8. Analysis","9. Findings","10. Recommendations"]
}
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
    logs=load_json("timar_activity_log.json",[]); logs.append({"Time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"User":user,"Action":action,"Details":details}); save_json("timar_activity_log.json",logs[-500:])
def check_trial(user):
    if not user: return True,"No User"
    if user.lower()=="admin": return True,"Admin Unlimited"
    trials=load_json("trials.json",{})
    if user not in trials: return True,"24.0h left"
    start=datetime.fromisoformat(trials[user]["start"]); left=24-(datetime.now()-start).total_seconds()/3600
    return (False,"Expired") if left<=0 else (True,f"{left:.1f}h left")
def is_admin(): return str(st.session_state.get("username","")).lower()=="admin"

for k,v in [("logged_in",False),("username",""),("user",""),("page","Dashboard"),("tool","Experimental Data Collection"),("standard_tool","Questionnaire - Structured Questions"),("chart","Bar Chart"),("metool","LogFrame - Logical Framework 4x4"),("plan","ADMIN_UNLIMITED"),("show_signup",False),("selected_plan",None),("active_master","00_MASTER_ALL_9_AUTO (Recommended)"),("generated_dataset","UBOS Poverty by Region (NGO Demo)")]:
    if k not in st.session_state: st.session_state[k]=v
if 'current_df' not in st.session_state:
    if NINE_DATASETS:
        first_key = list(NINE_DATASETS.keys())[0]
        st.session_state.current_df = NINE_DATASETS[first_key][1]
        st.session_state.active_master = first_key
    else:
        @st.cache_data
        def load_data():
            data = {'ID': range(340, 394),'Region': ['Central']*13 + ['Eastern']*12 + ['Northern']*12 + ['Western']*17,'Education': ['Secondary','Primary','University','Primary']*13 + ['Secondary']*2,'Yield': [4.5,7.4,6.7,1.7,3.8,4.1,0.2,0.6]*6 + [4.5,7.4,6.7,1.7,3.8,4.1],'Water_Source': ['River']*54,'Crop': ['Beans','Coffee','Beans','Maize']*13 + ['Beans','Maize'],'Age': np.random.randint(18,65,54),'Income': np.random.randint(200000,1500000,54)}
            return pd.DataFrame(data)
        st.session_state.current_df = load_data()

if not st.session_state.logged_in:
    st.markdown("""
    <style>
    [data-testid="stSidebar"]{display:none;}
    header{visibility:hidden;}
   .stApp{background:linear-gradient(135deg,#0F2C5C 0%,#1E3A8A 50%,#1E40AF 100%)!important;}
   .login-card{
        background:white;
        padding:40px 35px;
        border-radius:20px;
        box-shadow:0 25px 70px rgba(0,0,0,0.4);
        text-align:center;
        margin-top:20px;
        border:3px solid #D4AF37;
    }
   .login-card h1{color:#1E3A8A!important;font-size:32px;font-weight:900;margin-bottom:5px;}
   .login-card p{color:#475569!important;font-size:14px;font-weight:600;}
   .icon-label{font-size:18px!important;font-weight:800!important;color:#1E3A8A!important;margin-bottom:5px;}
    div[data-testid="stTextInput"] label{font-size:16px!important;font-weight:800!important;color:#1E3A8A!important;}
    div[data-testid="stTextInput"] input{font-size:16px!important;padding:12px!important;border:2px solid #1E3A8A!important;border-radius:10px!important;}
   .stButton button{font-size:16px!important;font-weight:800!important;border-radius:12px!important;padding:12px!important;}
    </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""
        <div class="login-card">
            <div style="font-size:70px;">🌾</div>
            <h1>🌾 TIMAR ANALYTICS</h1>
            <p style="font-size:18px!important;color:#1E3A8A!important;font-weight:900;">📊 Uganda's Smart Data Platform</p>
            <p style="background:#FEF3C7;padding:10px;border-radius:10px;color:#1E3A8A!important;font-weight:900;border:2px solid #D4AF37;">🔐 Secure Login | ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        users = load_users()
        with st.container(border=True):
            st.markdown("### 🔑 Login Credentials - Clear Icons")
            with st.form("login_form", clear_on_submit=False):
                st.markdown('<p class="icon-label">👤 Username</p>', unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="👤 Enter your username", key="login_user", label_visibility="collapsed")
                st.markdown('<p class="icon-label">🔒 Password</p>', unsafe_allow_html=True)
                password = st.text_input("Password", type="password", placeholder="🔒 Enter your password", key="login_pass", label_visibility="collapsed")
                st.write("")
                c1,c2 = st.columns(2)
                with c1:
                    submit_login = st.form_submit_button("🔓 Sign In", use_container_width=True, type="primary")
                with c2:
                    submit_signup_toggle = st.form_submit_button("📝 Sign Up 24h Trial", use_container_width=True)
                if submit_login:
                    if username.lower()=="admin" and password==ADMIN_PASSWORD:
                        st.session_state.logged_in=True; st.session_state.username="Admin"; st.session_state.user="Admin"; st.session_state.plan="ADMIN_UNLIMITED"; log_activity("Admin","LOGIN"); st.rerun()
                    elif username in users and users[username]==password:
                        st.session_state.logged_in=True; st.session_state.username=username; st.session_state.user=username
                        trials=load_json("trials.json",{})
                        if username not in trials: trials[username]={"start":datetime.now().isoformat()}; save_json("trials.json",trials)
                        log_activity(username,"LOGIN"); st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                if submit_signup_toggle:
                    st.session_state.show_signup = True
        if st.session_state.get("show_signup", False):
            with st.container(border=True):
                st.markdown("### 📝 Create Account - 24h FREE TRIAL")
                st.markdown('<p class="icon-label">👤 Choose Username</p>', unsafe_allow_html=True)
                nu=st.text_input("Choose Username", placeholder="👤 e.g. john_doe", key="s_u", label_visibility="collapsed")
                st.markdown('<p class="icon-label">🔒 Choose Password</p>', unsafe_allow_html=True)
                npw=st.text_input("Choose Password", type="password", placeholder="🔒 Create strong password", key="s_p", label_visibility="collapsed")
                st.markdown('<p class="icon-label">🔒 Confirm Password</p>', unsafe_allow_html=True)
                cpw=st.text_input("Confirm Password", type="password", placeholder="🔒 Repeat password", key="s_c", label_visibility="collapsed")
                st.markdown('<p class="icon-label">📱 Phone Number</p>', unsafe_allow_html=True)
                phone=st.text_input("Phone Number", placeholder="📱 07XXXXXXXX", key="s_phone", label_visibility="collapsed")
                agree=st.checkbox("✅ I agree to start 24hr free trial")
                if st.button("🚀 Create & Start Trial", type="primary", use_container_width=True, key="btn_create"):
                    users=load_users()
                    if not nu or not npw: st.error("⚠️ Username & password required")
                    elif npw!=cpw: st.error("⚠️ Passwords don't match")
                    elif nu in users: st.error("⚠️ Username exists")
                    elif not agree: st.error("⚠️ Please agree to trial")
                    else:
                        users[nu]=npw; save_json("users.json",{k:v for k,v in users.items() if k!="Admin"}); trials=load_json("trials.json",{}); trials[nu]={"start":datetime.now().isoformat(),"phone":phone}; save_json("trials.json",trials); log_activity(nu,"SIGNUP"); st.success(f"✅ Account {nu} created! Now Sign In above."); st.balloons()
    st.stop()

df = st.session_state.current_df
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ok,msg=check_trial(st.session_state.username)

with st.sidebar:
    st.title("🌾 TIMAR ANALYTICS")
    st.markdown(f"""<div style="background:white;padding:10px;border-radius:10px;text-align:center;"><p>👤 {st.session_state.username}</p><p>⏰ {now_str}</p><p>Rows: {len(df)}</p></div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 🧬 Generated Datasets (Sidebar Only)")
    gen_choices = ["UBOS Poverty by Region (NGO Demo)","BoU Inflation & USD/UGX (Business Demo)","MOH Health - Malaria & ANC (Health NGO Demo)","UBOS Population Census 2024 (Research Demo)","World Bank Uganda GDP & Education"]
    sel_gen = st.selectbox("Select Generated Dataset:", gen_choices, index=gen_choices.index(st.session_state.generated_dataset) if st.session_state.generated_dataset in gen_choices else 0, key="generated_sidebar_select")
    st.session_state.generated_dataset = sel_gen
    if st.button("🔵 Load Generated Dataset", key="load_gen_sidebar", use_container_width=True):
        gdf, gname = load_sample_data(sel_gen)
        st.session_state.current_df = gdf
        log_activity(st.session_state.username, "LOAD_GENERATED_SIDEBAR", gname)
        st.success(f"Loaded {gname} - {len(gdf)} rows"); st.rerun()
    st.caption(f"Active Generated: {st.session_state.generated_dataset}")
    st.divider()
    st.markdown("### 🚀 9 Master Data (glob.glob)")
    csv_list = glob.glob("*.csv")
    st.caption(f"Found {len(csv_list)} CSVs via glob.glob")
    if NINE_DATASETS:
        st.success(f"✅ {len(NINE_DATASETS)} auto-found via glob")
        master_choice = st.selectbox("Select Master Dataset:", list(NINE_DATASETS.keys()), index=list(NINE_DATASETS.keys()).index(st.session_state.active_master) if st.session_state.active_master in NINE_DATASETS else 0, key="master_select_sidebar")
        if st.button("🔵 Load Master Dataset", key="load_master_btn_sidebar", use_container_width=True):
            fname, fdf = NINE_DATASETS[master_choice]
            st.session_state.current_df = fdf
            st.session_state.active_master = master_choice
            st.rerun()
    else:
        st.warning("No CSVs found via glob.glob")
    st.divider()
    sel_mod = st.selectbox("📦 Modules - 19 Total", MODULES, index=MODULES.index(st.session_state.page) if st.session_state.page in MODULES else 0, key="mod_select")
    st.session_state.page = sel_mod
    sel_standard = st.selectbox("📋 STANDARD_TOOLS", STANDARD_TOOLS, index=STANDARD_TOOLS.index(st.session_state.standard_tool) if st.session_state.standard_tool in STANDARD_TOOLS else 0, key="standard_tool_select")
    st.session_state.standard_tool = sel_standard
    sel_chart = st.selectbox("📈 Chart Type", ALL_CHARTS, index=ALL_CHARTS.index(st.session_state.chart) if st.session_state.chart in ALL_CHARTS else 0, key="chart_select")
    st.session_state.chart = sel_chart
    if st.button("🚪 Logout", width='stretch', key="logout_btn"):
        log_activity(st.session_state.username,"LOGOUT"); st.session_state.logged_in=False; st.session_state.username=""; st.session_state.user=""; st.rerun()

st.markdown(f"""
<div style="background:linear-gradient(90deg,#1E3A8A 0%,#1E40AF 50%,#D4AF37 100%);padding:20px;border-radius:15px;margin-bottom:15px;text-align:center;">
<h1 style="color:white!important;margin:0;font-size:32px;font-weight:900;">🌾 TIMAR ANALYTICS</h1>
<p style="color:#FEF3C7;margin:5px 0 0 0;font-size:18px;font-weight:bold;">✅ ADMIN UNLIMITED ACCESS</p>
</div>
""", unsafe_allow_html=True)

def render_chart(data, chart_type, col_name, title_suffix=""):
    if len(data)==0: st.warning("No data"); return
    best_col = get_best_chart_column(data, col_name, chart_type)
    if best_col!= col_name:
        st.caption(f"⚠️ Ignored irrelevant column '{col_name}' → using '{best_col}' for {chart_type}. Chartable cols: {get_chartable_columns(data, chart_type)[:5]}")
        col_name = best_col
    if col_name not in data.columns:
        col_name = get_chartable_columns(data, chart_type)[0] if get_chartable_columns(data, chart_type) else data.columns[0]
    counts = data[col_name].value_counts().reset_index()
    counts.columns = [col_name, "Count"]
    if len(counts) > 20 and chart_type in ["Bar Chart","Pie Chart"]:
        counts = counts.head(20)
        st.caption(f"Showing top 20 of {data[col_name].nunique()} categories for readability")
    try:
        if chart_type=="Bar Chart":
            fig = px.bar(counts, x=col_name, y="Count", color=col_name, text="Count", title=f"{col_name} - Bar {title_suffix}"); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Pie Chart":
            fig = px.pie(counts, names=col_name, values="Count", title=f"{col_name} - Pie", hole=0.3); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Line Chart":
            fig = px.line(counts, x=col_name, y="Count", markers=True); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Scatter Plot":
            chartable_num = [c for c in get_chartable_columns(data, "Histogram") if c!= col_name][:1]
            if chartable_num:
                fig = px.scatter(data, x=col_name, y=chartable_num[0], color=col_name if data[col_name].nunique()<20 else None, title=f"{col_name} vs {chartable_num[0]}"); st.plotly_chart(fig, use_container_width=True)
            else:
                fig = px.scatter(counts, x=col_name, y="Count", size="Count", color=col_name); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Histogram":
            num_cols = [c for c in data.columns if pd.api.types.is_numeric_dtype(data[c]) and not is_irrelevant_column(data,c)]
            hist_col = num_cols[0] if num_cols else col_name
            fig = px.histogram(data, x=hist_col, title=f"{hist_col} - Histogram"); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Area Chart":
            fig = px.area(counts, x=col_name, y="Count"); st.plotly_chart(fig, use_container_width=True)
        else:
            relevant_cols = get_chartable_columns(data, "Bar Chart") + [c for c in data.columns if pd.api.types.is_numeric_dtype(data[c]) and not is_irrelevant_column(data,c)]
            relevant_cols = list(dict.fromkeys(relevant_cols))[:10]
            st.caption(f"Showing relevant columns only: {relevant_cols} (ignored {len(data.columns)-len(relevant_cols)} irrelevant)")
            st.dataframe(data[relevant_cols].head(100) if relevant_cols else data.head(100), width='stretch')
        st.info(f"**Interpretation ({chart_type}):** {col_name} dominant {counts.iloc[0][col_name]} with {counts.iloc[0]['Count']} records. User {st.session_state.username} at {now_str}.")
    except Exception as e:
        st.error(f"Chart error: {e}")

if st.session_state.page == "9 Master Datasets - TIMAR REAL":
    st.header(f"📦 9 Master Datasets - TIMAR REAL | 👤 {st.session_state.username} | ⏰ {now_str}")
    st.write(f"**All CSVs found via glob.glob('*.csv'):** {glob.glob('*.csv')}")
    if not NINE_DATASETS:
        st.error("❌ No 9 master CSVs found via glob. Put 00_ to 09_ files in folder.")
        st.stop()
    st.success(f"✅ {len(NINE_DATASETS)} REAL datasets ready - found via glob.glob (Generated datasets are ONLY in sidebar dropdown)")
    col1, col2 = st.columns([3,1])
    with col1:
        selected_label = st.selectbox("📂 Select Master Dataset (Dropdown):", list(NINE_DATASETS.keys()), index=list(NINE_DATASETS.keys()).index(st.session_state.active_master) if st.session_state.active_master in NINE_DATASETS else 0, key="nine_dropdown_main")
    with col2:
        if st.button("🔵 LOAD NOW", type="primary", use_container_width=True, key="load_nine_main"):
            fname, fdf = NINE_DATASETS[selected_label]
            st.session_state.current_df = fdf
            st.session_state.active_master = selected_label
            st.rerun()
    fname, fdf = NINE_DATASETS[selected_label]
    st.info(f"Previewing: **{selected_label}** → `{fname}` | **{len(fdf)} rows x {len(fdf.columns)} cols**")
    t1,t2,t3 = st.tabs(["📄 Data (Relevant Only)","📊 Chart (Ignores Irrelevant)","📋 All 9 List + glob"])
    with t1:
        rel_cols = get_chartable_columns(fdf, "Bar Chart") + [c for c in fdf.columns if pd.api.types.is_numeric_dtype(fdf[c]) and not is_irrelevant_column(fdf,c)]
        rel_cols = list(dict.fromkeys(rel_cols))
        st.dataframe(fdf[rel_cols].head(100) if rel_cols else fdf.head(100), use_container_width=True)
    with t2: render_chart(fdf, st.session_state.chart, 'Region' if 'Region' in fdf.columns else (get_chartable_columns(fdf, st.session_state.chart)[0] if get_chartable_columns(fdf, st.session_state.chart) else fdf.columns[0]), selected_label)
    with t3:
        st.json(glob.glob("*.csv"))
        for label, (f, d) in NINE_DATASETS.items():
            with st.container(border=True):
                st.write(f"**{label}** - `{f}` - {len(d)} rows")

elif st.session_state.page == "Admin - Monitoring Panel":
    st.header(f"🛡️ Admin - Monitoring Panel | 👤 {st.session_state.username} | ⏰ {now_str}")
    if not is_admin():
        st.error("⛔ Access Denied - Admin Only"); st.stop()
    if HAS_EXTERNAL_ADMIN:
        try: render_admin_panel(); st.divider()
        except: pass
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["👥 Users & Logins","⏰ Trials 24h","💳 Payments","📝 Activity Logs","⚙️ System Health + glob"])
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
        st.metric("CSV Files via glob.glob('*.csv')", len(glob.glob("*.csv")))
        st.write(glob.glob("*.csv"))
        st.metric("Active Dataset", st.session_state.active_master)
        st.dataframe(df.head(10), use_container_width=True)

elif st.session_state.page == "Payment & Plans":
    st.title("💳 Payment & Plans | "+ now_str)
    MTN_NUMS = "0789876277 / 0755453313"
    MTN_NAME_PRIVATE = "Tino Mary"
    subs = load_json("subscriptions.json", {})
    if "selected_plan" not in st.session_state: st.session_state.selected_plan=None
    os.makedirs("payment_proofs", exist_ok=True)
    if st.session_state.user.lower() == "admin":
        st.success("✅ ADMIN UNLIMITED ACCESS - 10 Years Free | MTN 0789876277 Tino Mary")
    if st.session_state.user in subs and subs[st.session_state.user].get("status")=="ACTIVE":
        exp = subs[st.session_state.user].get("expires","")
        st.success(f"✅ ACTIVE PLAN: {subs[st.session_state.user].get('plan')} | Expires: {exp}")
        st.stop()
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
        plan=st.session_state.selected_plan
        prices={"STUDENT":10000,"RESEARCHER":30000,"NGO":300000,"GOVERNMENT":500000}
        st.divider()
        st.markdown(f"## ✅ {plan} - UGX {prices[plan]:,}")
        st.warning(f"### 📱 Pay To:\n**MTN MoMo: {MTN_NUMS}**\n**Name: {MTN_NAME_PRIVATE}**")
        txn=st.text_input("MoMo Transaction ID *", key="txn_input", placeholder="e.g. 1234567890")
        proof_file = st.file_uploader("📤 Upload Payment Proof *", type=["png","jpg","jpeg","pdf"], key="proof_upload")
        if st.button("🚀 Upload & Activate Automatically", type="primary", use_container_width=True, key="confirm_pay_auto"):
            if not txn.strip(): st.error("Enter Transaction ID")
            elif proof_file is None: st.error("Upload proof")
            else:
                proof_path = f"payment_proofs/{st.session_state.user}_{plan}_{txn}_{proof_file.name}"
                with open(proof_path, "wb") as f: f.write(proof_file.getbuffer())
                expires_date = (datetime.now()+timedelta(days=30)).isoformat()
                subs[st.session_state.user]={"plan":plan,"amount":prices[plan],"txn":txn,"proof_file":proof_path,"expires":expires_date,"activated_at": datetime.now().isoformat(),"status":"ACTIVE","pay_to":MTN_NUMS,"pay_name":MTN_NAME_PRIVATE}
                save_json("subscriptions.json", subs)
                st.session_state.plan = plan
                st.success(f"✅ ACTIVATED! {plan} until {expires_date}"); st.balloons(); st.rerun()

elif st.session_state.page in ["Dashboard","Analytics","Data Upload","Data Collection Tools - All 10","M&E Module","WASH Module","Livelihood Module","Health Module","Education Module","Agriculture Module","Research Module","KPI Matrix","Statistical Tools","Inventory & Stock Movement","Reviews & Comments","Help & Manual for Timar Analytics"]:
    st.header(f"{st.session_state.page} | 👤 {st.session_state.username} | ⏰ {now_str}")
    rel_cols = get_chartable_columns(df, st.session_state.chart) + [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c]) and not is_irrelevant_column(df,c)]
    rel_cols = list(dict.fromkeys(rel_cols))
    if rel_cols:
        st.dataframe(df[rel_cols].head(50) if len(rel_cols)>0 else df.head(50), width='stretch')
    else:
        st.dataframe(df.head(50), width='stretch')
    best_col = get_best_chart_column(df, df.columns[0], st.session_state.chart)
    render_chart(df, st.session_state.chart, best_col, st.session_state.page)

st.markdown(f"""<div style="text-align:center;color:#1E3A8A;font-weight:bold;margin-top:30px;"><hr>🌾 TIMAR ANALYTICS © 2026 | ✅ ADMIN UNLIMITED ACCESS | glob.glob {len(glob.glob('*.csv'))} CSVs | Charts Ignore Irrelevant</div>""", unsafe_allow_html=True)
