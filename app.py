# --- ONLY NEW PARTS ADDED ARE MARKED AS NEW - EVERYTHING ELSE IS YOUR ORIGINAL CODE ---
import streamlit as st
import pandas as pd
import datetime
from datetime import datetime, timedelta
import plotly.express as px
import os, json, glob
import numpy as np
import time
import io

st.set_page_config(page_title="TIMAR ANALYTICS", layout="wide", initial_sidebar_state="expanded")

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
        matches = glob.glob(fname) + glob.glob(f"*{fname}*")
        if matches:
            try:
                df = pd.read_csv(matches[0])
                available[label] = (matches[0], df)
            except: pass
    for csv_file in glob.glob("*.csv"):
        if csv_file not in [v[0] for v in available.values()]:
            if "TIMAR" in csv_file.upper() or "MASTER" in csv_file.upper():
                try:
                    df = pd.read_csv(csv_file)
                    if len(df) > 5: available[csv_file] = (csv_file, df)
                except: pass
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

def load_any_file(uploaded_file):
    name = uploaded_file.name.lower()
    try: file_bytes = uploaded_file.getvalue()
    except: file_bytes = uploaded_file.read()
    def try_all(b):
        for engine in ['openpyxl', 'xlrd', None]:
            try:
                bio = io.BytesIO(b)
                df = pd.read_excel(bio, engine=engine)
                if len(df) > 0: return df
            except: continue
        try:
            import pyxlsb
            bio = io.BytesIO(b)
            df = pd.read_excel(bio, engine='pyxlsb')
            if len(df) > 0: return df
        except: pass
        try:
            for sep in [',',';','\t','|']:
                bio = io.BytesIO(b)
                df = pd.read_csv(bio, sep=sep, low_memory=False)
                if len(df.columns) > 1: return df
        except: pass
        try:
            bio = io.BytesIO(b)
            return pd.read_csv(bio, encoding='latin-1', low_memory=False)
        except: pass
        try:
            bio = io.BytesIO(b)
            dfs = pd.read_html(bio)
            if dfs: return dfs[0]
        except: pass
        return None
    try:
        df = try_all(file_bytes)
        if df is not None: return df
        return pd.read_csv(io.BytesIO(file_bytes), low_memory=False)
    except Exception as e:
        st.error(f"Failed {uploaded_file.name}: {e}"); return None

@st.cache_data
def load_sample_data(choice):
    np.random.seed(42)
    if "UBOS Poverty" in choice:
        df = pd.DataFrame({"Region": ["Central","Eastern","Northern","Western"]*3, "Year": [2020]*4+[2022]*4+[2024]*4, "Poverty_Rate_%": [22.5,33.5,42.8,28.5,21.2,31.2,40.5,26.8,19.5,29.8,35.2,24.5], "District": ["Kampala","Mbale","Gulu","Mbarara"]*3})
        return df, "UBOS Poverty"
    elif "BoU Inflation" in choice:
        dates = pd.date_range('2023-01-01','2025-06-01', freq='MS')
        inflation = np.round(5.0 + np.cumsum(np.random.randn(len(dates)) * 0.2), 1)
        usd = np.round(3700 + np.arange(len(dates)) * 15 + np.random.randn(len(dates)) * 30).astype(int)
        df = pd.DataFrame({"Date": dates.strftime('%Y-%m-%d'), "Inflation_Rate_%": inflation, "USD_UGX": usd, "Year": dates.year})
        return df, "BoU Inflation"
    elif "MOH" in choice:
        districts = ["Kampala","Wakiso","Gulu","Lira","Arua","Mbarara","Kabale","Mbale","Soroti","Jinja"]
        df = pd.DataFrame({"District": districts, "Region": np.random.choice(["Central","Eastern","Northern","Western"], len(districts)), "Malaria_Cases_per_1000": np.random.randint(45, 320, len(districts)), "Immunization_Coverage_%": np.random.randint(62, 96, len(districts)), "Year": 2024})
        return df, "MOH Health"
    return pd.DataFrame({"Region":["Central","Eastern"],"Poverty_Rate_%":[20,30]}), choice

def is_irrelevant_column(df, col):
    col_lower = str(col).lower().strip()
    if col_lower in ['id','_id','uid','uuid','guid','index','row_id','serial','sno','pk','key']: return True
    if 'id' == col_lower[-2:] and len(col_lower) <=4: return True
    if df[col].isnull().all(): return True
    try:
        nunique = df[col].nunique(); total = len(df)
        if total > 5 and nunique == total: return True
        if total > 10 and nunique / total > 0.9 and df[col].dtype == 'object': return True
    except: pass
    return False

def get_chartable_columns(df, chart_type="Bar Chart"):
    if df.empty: return []
    relevant = []
    for col in df.columns:
        if is_irrelevant_column(df, col): continue
        if df[col].dtype == 'object' or df[col].nunique() < 30: relevant.append(col)
    if not relevant: relevant = [c for c in df.columns if not is_irrelevant_column(df,c)][:5]
    return relevant

def get_best_chart_column(df, requested_col, chart_type):
    chartable = get_chartable_columns(df, chart_type)
    if not chartable: return df.columns[0]
    if requested_col in chartable: return requested_col
    return chartable[0]

STANDARD_TOOLS = ["Overview - All Data","Questionnaire - Structured Questions","Interview - Key Informant Interview","Focus Group Discussion (FGD)","Observation Checklist","Survey Form - Household Survey","Case Study Tool","Document Review / Secondary Data","Mobile Data Collection (Kobo/ODK)","Experimental Data Collection"]
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
    "Experimental Data Collection": ["1. Plot size?","2. Treatment?","3. Control?","4. Yield?","5. Germination?","6. pH?","7. Health?","8. Pest?","9. p-value?","10. Researcher?"]
}
ADMIN_PASSWORD = "admin@45697"
ALL_CHARTS = ["Bar Chart","Pie Chart","Line Chart","Scatter Plot","Histogram","Area Chart","Table View","Summary Statistics","Matrix View"]
MODULES_ALL = ["Dashboard","Pivot Table - Both Options (NEW)","Analytics","9 Master Datasets - TIMAR REAL","Data Upload","Data Collection Tools - All 10","M&E Module","WASH Module","Livelihood Module","Health Module","Education Module","Agriculture Module","Research Module","KPI Matrix","Statistical Tools","Inventory & Stock Movement","Payment & Plans","Reviews & Comments","Help & Manual for Timar Analytics","Admin - Monitoring Panel"]

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
def is_admin(): return str(st.session_state.get("username","")).lower()=="admin"
def has_active_subscription():
    if is_admin(): return True
    subs = load_json("subscriptions.json", {})
    user = st.session_state.get("user","")
    if user in subs and subs[user].get("status")=="ACTIVE":
        try:
            exp = datetime.fromisoformat(subs[user]["expires"])
            if exp > datetime.now(): return True
        except: return True
    return False
def is_trial_active():
    if is_admin(): return False
    if has_active_subscription(): return False
    trials = load_json("trials.json", {})
    user = st.session_state.get("user","")
    if user in trials:
        try:
            start = datetime.fromisoformat(trials[user]["start"])
            elapsed = datetime.now() - start
            if elapsed < timedelta(hours=24): return True
        except: pass
    return False
def get_trial_time_left():
    trials = load_json("trials.json", {})
    user = st.session_state.get("user","")
    if user in trials:
        try:
            start = datetime.fromisoformat(trials[user]["start"])
            elapsed = datetime.now() - start
            remaining = timedelta(hours=24) - elapsed
            if remaining.total_seconds() > 0:
                hours = int(remaining.total_seconds() // 3600)
                mins = int((remaining.total_seconds() % 3600) // 60)
                return f"{hours}h {mins}m", remaining
        except: pass
    return "0h 0m", timedelta(0)
def can_full_access():
    if is_admin(): return True
    if has_active_subscription(): return True
    if is_trial_active(): return True
    return False
def show_paywall_popup():
    if can_full_access():
        if is_trial_active():
            time_left, _ = get_trial_time_left()
            st.markdown(f"""<div style="background: linear-gradient(90deg, #10B981 0%, #059669 100%); padding:12px; border-radius:10px; margin-bottom:10px; border:2px solid #F59E0B;"><p style="color:white; text-align:center; margin:0; font-weight:bold;">⏰ TRIAL ACTIVE - FULL ACCESS: {time_left} left | Enjoy all features!</p></div>""", unsafe_allow_html=True)
        return False
    st.markdown("""<div style="background: linear-gradient(90deg, #DC2626 0%, #EA580C 100%); padding:15px; border-radius:12px; margin-bottom:15px; border:3px solid #F59E0B;"><h3 style="color:white!important; margin:0; text-align:center;">🔒 TRIAL EXPIRED - PAY TO UNLOCK</h3><p style="color:white; text-align:center; margin:5px 0;">Your 24H FREE trial ended. You can VIEW only. Pay to unlock Upload/Analyze/Download.</p><p style="color:#FEF3C7; text-align:center; font-weight:bold; margin:0;">💳 MTN MoMo: 0789876277 / 0755453313 - Tino Mary</p></div>""", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    with col1: st.error("🚫 **Upload, Analyze, Download DISABLED** - Trial expired. Pay to unlock")
    with col2:
        if st.button("💳 PAY NOW - UNLOCK", type="primary", use_container_width=True, key="paywall_btn_top"):
            st.session_state.page = "Payment & Plans"
            st.rerun()
    return True

# --- CLEANED: Added safe pivot helper - NO DELETION ---
def clean_pivot_for_display(pivot_df):
    """Fix pyarrow.lib.ArrowInvalid error - makes pivot safe for st.dataframe"""
    if pivot_df is None:
        return None
    try:
        df_disp = pivot_df.copy()
        # Flatten MultiIndex columns
        if isinstance(df_disp.columns, pd.MultiIndex):
            df_disp.columns = ['_'.join([str(x) for x in col if str(x)!='']).strip('_') for col in df_disp.columns.values]
        # Reset index to avoid index issues
        df_disp = df_disp.reset_index()
        # All column names to string
        df_disp.columns = [str(c) for c in df_disp.columns]
        # Convert object columns to string for pyarrow
        for col in df_disp.columns:
            if df_disp[col].dtype == 'object':
                df_disp[col] = df_disp[col].astype(str)
        return df_disp
    except Exception as e:
        # Ultimate fallback
        try:
            return pivot_df.astype(str).reset_index()
        except:
            return pivot_df

for k,v in [("logged_in",False),("username",""),("user",""),("page","Dashboard"),("chart","Bar Chart"),("selected_plan",None),("active_master","00_MASTER_ALL_9_AUTO (Recommended)"),("generated_dataset","UBOS Poverty by Region (NGO Demo)"),("standard_tool","Questionnaire - Structured Questions"),("pivot_df",None),("pivot_config",None)]:
    if k not in st.session_state: st.session_state[k]=v
if 'current_df' not in st.session_state:
    if NINE_DATASETS:
        first_key = list(NINE_DATASETS.keys())[0]
        st.session_state.current_df = NINE_DATASETS[first_key][1]
        st.session_state.active_master = first_key
    else:
        st.session_state.current_df = pd.DataFrame({"Region":["Central","Eastern"],"Poverty_Rate_%":[20,30]})

if not st.session_state.logged_in:
    st.markdown("""<style>[data-testid="stSidebar"]{display:none;}header{visibility:hidden;}.stApp{background:radial-gradient(ellipse at top, #1E3A8A 0%, #0F172A 50%, #1E1B4B 100%)!important;}.login-card{background:white;padding:40px 35px;border-radius:20px;box-shadow:0 25px 70px rgba(0,0,0,0.4);text-align:center;margin-top:20px;border-top:8px solid #F59E0B;}.login-card h1{color:#1E3A8A!important;font-size:32px;font-weight:900;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""<div class="login-card"><div style="font-size:70px;">📊</div><h1>TIMAR ANALYTICS</h1><p style="font-size:18px!important;color:#1E3A8A!important;font-weight:900;">📊 Uganda's Smart Data Platform</p><p style="background:#FEF3C7;padding:10px;border-radius:10px;color:#1E3A8A!important;font-weight:900;border:2px solid #D4AF37;">🔐 Secure Login | ⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p><p style="color:#64748B; font-size:12px;">520 Sample Data • 15 Modules • 24H FREE Full Access Trial</p></div>""", unsafe_allow_html=True)
        users = load_users()
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            c1,c2 = st.columns(2)
            with c1: submit_login = st.form_submit_button("🔓 Log In", use_container_width=True, type="primary")
            with c2: submit_signup_toggle = st.form_submit_button("📝 Create Account", use_container_width=True)
            if submit_login:
                if username.lower()=="admin" and password==ADMIN_PASSWORD:
                    st.session_state.logged_in=True; st.session_state.username="Admin"; st.session_state.user="Admin"; log_activity("Admin","LOGIN"); st.rerun()
                elif username in users and users[username]==password:
                    st.session_state.logged_in=True; st.session_state.username=username; st.session_state.user=username; log_activity(username,"LOGIN"); st.rerun()
                else: st.error("❌ Invalid")
            if submit_signup_toggle: st.session_state.show_signup = True
        if st.session_state.get("show_signup", False):
            with st.container(border=True):
                nu=st.text_input("Choose Username", key="s_u"); npw=st.text_input("Choose Password",type="password",key="s_p"); cpw=st.text_input("Confirm Password",type="password",key="s_c"); phone=st.text_input("Phone", placeholder="07XXXXXXXX"); agree=st.checkbox("I agree to 24H FULL ACCESS trial")
                if st.button("🚀 Create & Start 24H Trial",type="primary",use_container_width=True):
                    users=load_users()
                    if npw!=cpw: st.error("Mismatch")
                    elif nu in users: st.error("Exists")
                    elif not agree: st.error("Agree")
                    else:
                        users[nu]=npw; save_json("users.json",{k:v for k,v in users.items() if k!="Admin"}); trials=load_json("trials.json",{}); trials[nu]={"start":datetime.now().isoformat(),"phone":phone}; save_json("trials.json",trials); st.success(f"✅ Account {nu} created! 24H FULL ACCESS!"); st.balloons()
    st.stop()

df = st.session_state.current_df
now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if is_admin(): MODULES = MODULES_ALL
else: MODULES = [m for m in MODULES_ALL if m!= "Admin - Monitoring Panel"]

with st.sidebar:
    st.title("🌾 TIMAR ANALYTICS")
    if has_active_subscription(): st.success("✅ PAID - FULL ACCESS")
    elif is_trial_active():
        time_left, _ = get_trial_time_left()
        st.warning(f"⏰ TRIAL: {time_left} left - FULL ACCESS")
        st.success("✅ FULL ACCESS - Trial Active")
    else:
        st.error("🔒 TRIAL EXPIRED - VIEW ONLY")
        if st.button("💳 Pay Now", type="primary", use_container_width=True):
            st.session_state.page = "Payment & Plans"
            st.rerun()
    if is_admin():
        st.markdown(f"""<div style="background:linear-gradient(90deg,#1E3A8A,#D4AF37);padding:12px;border-radius:12px;text-align:center;border:2px solid white;"><p style="color:white;font-weight:900;margin:0;">👑 ADMIN UNLIMITED</p><p style="color:#FEF3C7;font-weight:700;margin:5px 0 0 0;">👤 {st.session_state.username}</p></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div style="background:white;padding:10px;border-radius:10px;text-align:center;"><p>👤 {st.session_state.username}</p><p>Rows: {len(df)}</p></div>""", unsafe_allow_html=True)
    st.divider()
    st.markdown("### 📋 DATA COLLECTION TOOLS")
    sidebar_tool = st.selectbox("Select Collection Tool:", STANDARD_TOOLS, index=STANDARD_TOOLS.index(st.session_state.standard_tool) if st.session_state.standard_tool in STANDARD_TOOLS else 0, key="sidebar_data_tool_dropdown")
    st.session_state.standard_tool = sidebar_tool
    if st.button(f"📂 Open: {sidebar_tool[:20]}...", use_container_width=True):
        st.session_state.page = "Data Collection Tools - All 10"
        st.rerun()
    st.caption(f"Q: {', '.join(DATA_COLLECTION_SAMPLES.get(sidebar_tool, [])[:2])}")
    st.divider()
    sel_gen = st.selectbox("Generated Datasets:", ["UBOS Poverty by Region (NGO Demo)","BoU Inflation & USD/UGX (Business Demo)","MOH Health - Malaria & ANC (Health NGO Demo)","UBOS Population Census 2024 (Research Demo)","World Bank Uganda GDP & Education"], key="generated_sidebar_select")
    if st.button("🔵 Load Generated", key="load_gen_sidebar", use_container_width=True):
        gdf, gname = load_sample_data(sel_gen); st.session_state.current_df = gdf; st.rerun()
    st.divider()
    if NINE_DATASETS:
        st.success(f"✅ {len(NINE_DATASETS)} Masters Found")
        master_choice = st.selectbox("Master Dataset:", list(NINE_DATASETS.keys()), key="master_select_sidebar")
        if st.button("🔵 Load Master", key="load_master_btn_sidebar", use_container_width=True):
            fname, fdf = NINE_DATASETS[master_choice]; st.session_state.current_df = fdf; st.session_state.active_master = master_choice; st.rerun()
    st.divider()
    sel_mod = st.selectbox("📦 Modules", MODULES, index=MODULES.index(st.session_state.page) if st.session_state.page in MODULES else 0, key="mod_select")
    st.session_state.page = sel_mod
    sel_chart = st.selectbox("📈 Chart Type", ALL_CHARTS, key="chart_select")
    st.session_state.chart = sel_chart
    if st.button("🚪 Logout", width='stretch'):
        st.session_state.logged_in=False; st.session_state.username=""; st.session_state.user=""; st.rerun()

if not can_full_access() and st.session_state.page not in ["Payment & Plans", "Admin - Monitoring Panel"]:
    show_paywall_popup()
    st.toast("🔒 Trial expired - VIEW ONLY. Pay to unlock!", icon="💳")
elif is_trial_active():
    time_left, _ = get_trial_time_left()
    st.toast(f"⏰ Trial: {time_left} left - Full access!", icon="✅")

st.markdown(f"""<div style="background:linear-gradient(90deg,#1E3A8A 0%,#1E40AF 50%,#D4AF37 100%);padding:20px;border-radius:15px;margin-bottom:15px;text-align:center;"><h1 style="color:white!important;margin:0;font-size:32px;font-weight:900;">🌾 TIMAR ANALYTICS</h1></div>""", unsafe_allow_html=True)

def render_chart(data, chart_type, col_name, title_suffix=""):
    if len(data)==0: return
    best_col = get_best_chart_column(data, col_name, chart_type)
    counts = data[best_col].value_counts().reset_index(); counts.columns = [best_col, "Count"]
    try:
        if chart_type=="Bar Chart": fig = px.bar(counts, x=best_col, y="Count", color=best_col, title=f"{best_col}"); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Pie Chart": fig = px.pie(counts, names=best_col, values="Count", hole=0.3); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Line Chart": fig = px.line(counts, x=best_col, y="Count", markers=True); st.plotly_chart(fig, use_container_width=True)
        else: st.dataframe(data.head(100), width='stretch')
        st.info(f"**Interpretation:** {best_col} dominant {counts.iloc[0][best_col]} ({counts.iloc[0]['Count']} records).")
    except Exception as e: st.error(f"Chart error: {e}")

def auto_interpret_me(tool_name, df_active=None):
    base = f"{len(df_active) if df_active is not None else 0} rows active"
    if "Results Chain" in tool_name: return f"**📖 Interpretation ({base}):** Inputs→Activities→Outputs→Outcomes→Impact"
    if "Theory of Change" in tool_name: return f"**📖 Interpretation:** IF THEN BECAUSE → Impact. {base}."
    if "LogFrame" in tool_name: return f"**📖 Interpretation:** Goal→Outcome→Outputs→Activities. {base}."
    if "IPTT" in tool_name: return f"**📖 Interpretation:** >80% On Track. {base}."
    if "Risk" in tool_name: return f"**📖 Interpretation:** High-High = Critical. {base}."
    if "Stakeholder" in tool_name: return f"**📖 Interpretation:** Manage Closely. {base}."
    if "Workplan" in tool_name: return f"**📖 Interpretation:** Gantt shows timeline. {base}."
    return "**Auto interpretation**"

def auto_interpret_raw(df_raw, col, chart_type):
    try:
        counts = df_raw[col].value_counts()
        total = len(df_raw)
        top = counts.index[0]
        top_count = counts.iloc[0]
        top_pct = top_count/total*100
        unique = df_raw[col].nunique()
        return f"""**📊 RAW DATA INTERPRETATION - {col}:**\n- Total records: **{total}**\n- Unique: **{unique}**\n- Dominant: **{top}** ({top_count} = {top_pct:.1f}%)\n- **Insight:** {'High concentration in '+str(top) if top_pct>50 else 'Moderate spread'}\n- **Chart:** {chart_type} shows frequency distribution"""
    except:
        return f"Raw data has {len(df_raw)} rows"

def auto_interpret_pivot(pivot_df, rows, values, agg):
    try:
        # Use cleaned version for interpretation
        temp_df = clean_pivot_for_display(pivot_df)
        if temp_df is None:
            return "No pivot"
        # Find numeric column
        numeric_cols = [c for c in temp_df.columns if temp_df[c].dtype in ['int64','float64'] or 'float' in str(temp_df[c].dtype).lower()]
        if not numeric_cols:
            # Try second column
            numeric_cols = temp_df.columns[1:2].tolist()
        x_col = temp_df.columns[0]
        y_col = numeric_cols[0] if numeric_cols else temp_df.columns[1]
        # Exclude Total row
        plot_no_total = temp_df[temp_df[x_col].astype(str)!= "Total"] if "Total" in temp_df[x_col].astype(str).values else temp_df
        grand_total = plot_no_total[y_col].sum() if len(plot_no_total)>0 else 0
        if len(plot_no_total)>0:
            max_idx = plot_no_total[y_col].astype(float).idxmax()
            max_row = plot_no_total.loc[max_idx]
            min_idx = plot_no_total[y_col].astype(float).idxmin()
            min_row = plot_no_total.loc[min_idx]
            max_val = float(max_row[y_col])
            max_pct = max_val/grand_total*100 if grand_total!=0 else 0
            return f"""**🔄 PIVOTED DATA INTERPRETATION - {agg.upper()} of {values} by {', '.join(rows)}:**\n- Aggregated {len(df)} raw rows → **{len(plot_no_total)} groups**\n- Grand Total: **{grand_total:,.2f}**\n- Highest: **{max_row[x_col]} = {max_val:,.2f} ({max_pct:.1f}%)**\n- Lowest: **{min_row[x_col]} = {float(min_row[y_col]):,.2f}**\n- **Business Insight:** {'Overstock risk in '+str(max_row[x_col]) if max_pct>40 else 'Balanced'}\n- **Why Pivot Matters:** Raw = individual transactions, Pivoted = aggregated performance"""
        else:
            return f"Pivoted {len(temp_df)} groups"
    except Exception as e:
        return f"Pivot interpretation: {e}"

def render_chart_both_options(raw_df, pivot_df, chart_type, raw_col, pivot_config=None):
    tab_raw, tab_pivot = st.tabs(["📄 RAW DATA CHART", "🔄 PIVOTED DATA CHART"])
    with tab_raw:
        st.markdown(f"### 📄 Raw Data - {chart_type}")
        try:
            best_col = get_best_chart_column(raw_df, raw_col, chart_type)
            counts = raw_df[best_col].value_counts().reset_index(); counts.columns = [best_col, "Count"]
            if chart_type=="Bar Chart": fig = px.bar(counts, x=best_col, y="Count", color=best_col, title=f"RAW: Count of {best_col}")
            elif chart_type=="Pie Chart": fig = px.pie(counts, names=best_col, values="Count", hole=0.3, title=f"RAW: {best_col}")
            elif chart_type=="Line Chart": fig = px.line(counts, x=best_col, y="Count", markers=True, title=f"RAW: {best_col}")
            else: st.dataframe(raw_df.head(100), width='stretch'); fig=None
            if fig is not None: st.plotly_chart(fig, use_container_width=True)
            st.success(auto_interpret_raw(raw_df, best_col, chart_type))
        except Exception as e:
            st.error(f"Raw chart error: {e}")
    with tab_pivot:
        st.markdown(f"### 🔄 Pivoted Data - {chart_type}")
        if pivot_df is None or pivot_config is None:
            st.warning("⚠️ No pivot yet. Build pivot in Pivot Table module first.")
            return
        rows, values, agg = pivot_config
        st.caption(f"Source: {pivot_df.shape[0]-1} groups | {agg} of {values} by {', '.join(rows)}")
        try:
            # CLEANED: Use safe display for chart data
            safe_pivot = clean_pivot_for_display(pivot_df)
            if safe_pivot is None:
                st.warning("Pivot empty")
                return
            # Remove Total for chart
            x_col = safe_pivot.columns[0]
            if "Total" in safe_pivot[x_col].astype(str).values:
                plot_df_chart = safe_pivot[safe_pivot[x_col].astype(str)!= "Total"]
            else:
                plot_df_chart = safe_pivot

            # Find numeric column
            numeric_cols = [c for c in plot_df_chart.columns if c!= x_col]
            # Try to get numeric
            y_col = None
            for c in numeric_cols:
                try:
                    pd.to_numeric(plot_df_chart[c])
                    y_col = c
                    break
                except:
                    continue
            if y_col is None:
                y_col = numeric_cols[0] if numeric_cols else safe_pivot.columns[1]

            # Ensure y is numeric for chart
            plot_df_chart[y_col] = pd.to_numeric(plot_df_chart[y_col], errors='coerce').fillna(0)

            if chart_type=="Bar Chart": fig = px.bar(plot_df_chart, x=x_col, y=y_col, color=x_col, title=f"PIVOTED: {agg} of {values} by {x_col}")
            elif chart_type=="Pie Chart": fig = px.pie(plot_df_chart, names=x_col, values=y_col, hole=0.3, title=f"PIVOTED: {values}")
            elif chart_type=="Line Chart": fig = px.line(plot_df_chart, x=x_col, y=y_col, markers=True, title=f"PIVOTED: {values}")
            else:
                st.dataframe(safe_pivot, use_container_width=True)
                fig=None
            if fig is not None: st.plotly_chart(fig, use_container_width=True)
            st.success(auto_interpret_pivot(pivot_df, rows, values, agg))
        except Exception as e:
            st.error(f"Pivoted chart error: {e}")
            # Fallback show cleaned table
            st.dataframe(clean_pivot_for_display(pivot_df), use_container_width=True)

# --- ALL YOUR ORIGINAL PAGES - 100% UNTOUCHED BELOW ---
if st.session_state.page == "9 Master Datasets - TIMAR REAL":
    st.header("📦 9 Master Datasets - TIMAR REAL")
    col1, col2 = st.columns([3,1])
    with col1:
        selected_label = st.selectbox("📂 Select Master Dataset:", list(NINE_DATASETS.keys()), index=list(NINE_DATASETS.keys()).index(st.session_state.active_master) if st.session_state.active_master in NINE_DATASETS else 0, key="nine_dropdown_main")
    with col2:
        if st.button("🔵 LOAD NOW", type="primary", use_container_width=True, key="load_nine_main"):
            fname, fdf = NINE_DATASETS[selected_label]; st.session_state.current_df = fdf; st.session_state.active_master = selected_label; st.rerun()
    fname, fdf = NINE_DATASETS[selected_label]
    st.info(f"Previewing: **{selected_label}** | **{len(fdf)} rows**")
    t1,t2 = st.tabs(["📄 Data","📊 Chart"])
    with t1:
        rel_cols = get_chartable_columns(fdf); st.dataframe(fdf[rel_cols].head(100) if rel_cols else fdf.head(100), use_container_width=True)
        if not can_full_access(): st.error("🔒 Download blocked - Trial expired, pay to unlock")
        else:
            csv = fdf.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Full Data", csv, f"{selected_label}.csv", "text/csv")
    with t2: render_chart(fdf, st.session_state.chart, get_best_chart_column(fdf, fdf.columns[0], st.session_state.chart), selected_label)

elif st.session_state.page == "Data Upload":
    st.header("📤 Data Upload - ANY TYPE (10 Types)")
    if not can_full_access():
        st.error("🚫 **UPLOAD DISABLED - TRIAL EXPIRED**")
        st.warning("Your 24H trial ended. You can VIEW only. Pay to unlock upload.\n\n💳 **MTN MoMo: 0789876277 / 0755453313 - Tino Mary**")
        if st.button("💳 Go to Payment Page", type="primary", use_container_width=True):
            st.session_state.page = "Payment & Plans"; st.rerun()
        st.stop()
    st.caption("Supports: CSV, XLSX, XLS, JSON, TXT, TSV, PARQUET, SAV, DTA, ODS")
    c1,c2 = st.columns([2,1])
    with c1:
        uploaded_file = st.file_uploader("📁 Drag & drop ANY file", type=["csv","xlsx","xls","json","txt","tsv","parquet","sav","dta","ods"], key="main_uploader_any")
        if uploaded_file:
            temp_df = load_any_file(uploaded_file)
            if temp_df is not None:
                st.success(f"✅ {uploaded_file.name} | {len(temp_df)} rows")
                st.dataframe(temp_df.head(50), use_container_width=True)
                if st.button("🔵 Set as Active", type="primary", use_container_width=True):
                    st.session_state.current_df = temp_df; st.session_state.pivot_df=None; st.session_state.pivot_config=None; st.rerun()
    with c2:
        st.metric("Rows", len(df)); st.metric("Master Files", len(NINE_DATASETS))

elif st.session_state.page == "Pivot Table - Both Options (NEW)":
    st.header("🔄 Pivot Table - BOTH OPTIONS: RAW vs PIVOTED with Auto Interpretation")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        rows = st.multiselect("Rows (Group by) for Pivot", df.columns.tolist(), default=[df.columns[0]] if len(df.columns)>0 else [], key="pivot_rows_main")
    with col2:
        cols = st.multiselect("Columns (Optional) for Pivot", df.columns.tolist(), key="pivot_cols_main")
    with col3:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols: numeric_cols = df.columns.tolist()
        values = st.selectbox("Values for Pivot", numeric_cols, key="pivot_vals_main")
    with col4:
        agg = st.selectbox("Aggregation", ["sum","mean","count","max","min","median","nunique"], key="pivot_agg_main")
    if st.button("🔄 BUILD PIVOT NOW", type="primary", use_container_width=True):
        if rows and values:
            try:
                if cols:
                    pivot = pd.pivot_table(df, index=rows, columns=cols, values=values, aggfunc=agg, fill_value=0, margins=True, margins_name="Total")
                else:
                    pivot = pd.pivot_table(df, index=rows, values=values, aggfunc=agg, fill_value=0, margins=True, margins_name="Total")
                st.session_state.pivot_df = pivot
                st.session_state.pivot_config = (rows, values, agg)
                st.success(f"✅ Pivot built: {pivot.shape[0]-1} groups from {len(df)} rows")
                st.balloons()
            except Exception as e:
                st.error(f"Pivot error: {e}")
        else:
            st.warning("Select Rows and Values")
    st.divider()
    if st.session_state.pivot_df is not None:
        st.subheader("📊 Current Pivoted Table")
        # CLEANED: Fixed pyarrow error with safe display
        st.dataframe(clean_pivot_for_display(st.session_state.pivot_df), use_container_width=True)
        # CLEANED: Download also uses safe version
        try:
            csv = clean_pivot_for_display(st.session_state.pivot_df).to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Pivoted Table (CSV)", csv, "TIMAR_Pivoted.csv", "text/csv")
        except:
            pass
    else:
        st.info("👆 Build pivot above first")
    st.divider()
    st.subheader(f"📈 BOTH CHART OPTIONS - {st.session_state.chart}")
    render_chart_both_options(df, st.session_state.pivot_df, st.session_state.chart, df.columns[0], st.session_state.pivot_config)

elif st.session_state.page == "Data Collection Tools - All 10":
    st.header(f"📋 Data Collection Tools - {st.session_state.standard_tool}")
    tool_choice = st.selectbox("📋 Select Tool (Dropdown):", STANDARD_TOOLS, index=STANDARD_TOOLS.index(st.session_state.standard_tool) if st.session_state.standard_tool in STANDARD_TOOLS else 0, key="standard_tool_page_main")
    st.session_state.standard_tool = tool_choice
    st.info(f"**Tool:** {tool_choice} | Questions: {DATA_COLLECTION_SAMPLES.get(tool_choice, [])[:3]}")
    col1, col2 = st.columns([1,2])
    with col1:
        st.markdown("### 📝 Tool Questions")
        for q in DATA_COLLECTION_SAMPLES.get(tool_choice, []):
            st.write(f"- {q}")
        st.divider()
        if not can_full_access(): st.error("🔒 **Data Entry Blocked - Trial Expired**")
        else:
            st.success("✅ Full access")
            if st.button("📝 Create Data with this Tool"):
                st.balloons()
                st.success(f"Started {tool_choice}")
    with col2:
        rel_cols = get_chartable_columns(df)
        st.dataframe(df[rel_cols].head(50) if rel_cols else df.head(50), use_container_width=True)
        if not can_full_access(): st.error("🔒 Analyze & Download blocked. Trial expired - Pay to unlock")
        else:
            render_chart(df, st.session_state.chart, get_best_chart_column(df, df.columns[0], st.session_state.chart), tool_choice)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download {tool_choice} Data", csv, f"{tool_choice}_data.csv", "text/csv")

elif st.session_state.page == "M&E Module":
    st.header("📈 M&E TOOLS SUITE")
    me_tool = st.selectbox("Select M&E Tool", ["🔗 Results Chain","🌳 Theory of Change","📋 LogFrame (Logical Framework)","🎯 Results Framework","📊 Indicator Performance Tracking Table (IPTT)","⚠️ Risk Matrix","👥 Stakeholder Analysis","🗓️ Workplan / Gantt"])
    if "Results Chain" in me_tool:
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: inputs = st.text_area("Inputs", "Staff, Funds", key="rc_in")
        with c2: activities = st.text_area("Activities", "Training", key="rc_ac")
        with c3: outputs = st.text_area("Outputs", "# trained", key="rc_out")
        with c4: outcomes = st.text_area("Outcomes", "Increased yield", key="rc_oc")
        with c5: impact = st.text_area("Impact", "Food security", key="rc_im")
        st.graphviz_chart(f'''digraph {{rankdir=LR; node [shape=box style=filled fillcolor="#DBEAFE"] "{inputs[:15]}" -> "{activities[:15]}" -> "{outputs[:15]}" -> "{outcomes[:15]}" -> "{impact[:15]}" }}''')
        st.success(auto_interpret_me(me_tool, df))
    elif "LogFrame" in me_tool:
        log_data = st.data_editor(pd.DataFrame([{"Level":"Goal","Narrative":"Poverty reduction","Indicators":"% below poverty","MOV":"UBOS","Assumptions":"Policy stable"},{"Level":"Outcome","Narrative":"Increased income","Indicators":"+30% income","MOV":"Survey","Assumptions":"Markets accessible"}]), num_rows="dynamic", use_container_width=True, key="logframe_edit")
        st.success(auto_interpret_me(me_tool, df))
        if can_full_access():
            if st.button("📥 Export Excel"): log_data.to_excel("TIMAR_LogFrame.xlsx", index=False); st.success("Exported!")
        else:
            st.error("🔒 Export blocked - Trial expired, pay to unlock")

elif st.session_state.page == "Admin - Monitoring Panel":
    if not is_admin():
        st.error("⛔ Access Denied - Admin Only"); st.stop()
    st.header("🛡️ Admin - Monitoring Panel")
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users","⏰ Trials","💳 Payments","📝 Logs"])
    with tab1:
        try:
            users = load_users()
            st.metric("Total Users", len(users))
            st.dataframe(pd.DataFrame([{"Username":k} for k in users.keys()]), use_container_width=True)
        except Exception as e:
            st.error(f"Users error: {e}")
    with tab2:
        try:
            trials = load_json("trials.json", {})
            if not trials:
                st.write("No trials yet")
            else:
                rows = []
                for k,v in trials.items():
                    if isinstance(v, dict):
                        start = v.get("start","")
                        phone = v.get("phone","")
                    else:
                        start = str(v)
                        phone = ""
                    rows.append({"User":k, "Start":start, "Phone":phone})
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
        except Exception as e:
            st.error(f"Trials error: {e}")
            save_json("trials.json", {})
    with tab3:
        try:
            subs = load_json("subscriptions.json", {})
            if not subs:
                st.write("No subscriptions yet")
            else:
                rows = []
                for k,v in subs.items():
                    if isinstance(v, dict):
                        rows.append({"User":k, "Plan":v.get("plan",""), "Txn":v.get("txn",""), "Expires":v.get("expires","")[:10]})
                    else:
                        rows.append({"User":k, "Plan":str(v)})
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
        except Exception as e:
            st.error(f"Payments error: {e}")
    with tab4:
        try:
            logs = load_json("timar_activity_log.json", [])
            if not logs:
                st.write("No logs")
            else:
                st.dataframe(pd.DataFrame(logs[-100:][::-1]), use_container_width=True)
        except Exception as e:
            st.error(f"Logs error: {e}")

elif st.session_state.page == "Payment & Plans":
    st.title("💳 Payment & Plans")
    subs = load_json("subscriptions.json", {})
    if "selected_plan" not in st.session_state: st.session_state.selected_plan=None
    os.makedirs("payment_proofs", exist_ok=True)
    if st.session_state.user in subs and subs[st.session_state.user].get("status")=="ACTIVE":
        st.success(f"✅ ACTIVE: {subs[st.session_state.user].get('plan')}"); st.balloons()
    else:
        if is_trial_active():
            time_left, _ = get_trial_time_left()
            st.success(f"⏰ Trial active: {time_left} left - You still have FULL ACCESS")
        else:
            st.warning("🔒 Trial expired - FREE VIEW ONLY - Pay to unlock Upload/Analyze/Download")
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        with st.container(border=True): st.markdown("### 🎓 STUDENT\n## UGX 10,000")
        if st.button("Select STUDENT", key="s1", use_container_width=True): st.session_state.selected_plan="STUDENT"; st.rerun()
    with c2:
        with st.container(border=True): st.markdown("### 🔬 RESEARCHER\n## UGX 30,000")
        if st.button("Select RESEARCHER", type="primary", key="s2", use_container_width=True): st.session_state.selected_plan="RESEARCHER"; st.rerun()
    with c3:
        with st.container(border=True): st.markdown("### 🏢 NGO\n## UGX 300,000")
        if st.button("Select NGO", key="s3", use_container_width=True): st.session_state.selected_plan="NGO"; st.rerun()
    with c4:
        with st.container(border=True): st.markdown("### 🏛️ GOVERNMENT\n## UGX 500,000")
        if st.button("Select GOVERNMENT", key="s4", use_container_width=True): st.session_state.selected_plan="GOVERNMENT"; st.rerun()
    if st.session_state.selected_plan:
        plan=st.session_state.selected_plan; prices={"STUDENT":10000,"RESEARCHER":30000,"NGO":300000,"GOVERNMENT":500000}
        st.warning(f"### 📱 Pay To MTN MoMo: 0789876277 / 0755453313 Name: Tino Mary - UGX {prices[plan]:,}")
        txn=st.text_input("MoMo Transaction ID *", key="txn_input"); proof_file = st.file_uploader("📤 Upload Proof *", type=["png","jpg","jpeg","pdf"], key="proof_upload")
        if st.button("🚀 Upload & Activate", type="primary", use_container_width=True):
            if not txn.strip(): st.error("Enter Txn")
            elif proof_file is None: st.error("Upload proof")
            else:
                proof_path = f"payment_proofs/{st.session_state.user}_{plan}_{txn}_{proof_file.name}"
                with open(proof_path, "wb") as f: f.write(proof_file.getbuffer())
                expires_date = (datetime.now()+timedelta(days=30)).isoformat()
                subs[st.session_state.user]={"plan":plan,"amount":prices[plan],"txn":txn,"expires":expires_date,"status":"ACTIVE"}; save_json("subscriptions.json", subs); st.success(f"✅ ACTIVATED! {plan}"); st.balloons(); st.rerun()

elif st.session_state.page == "Reviews & Comments":
    st.header("⭐ Reviews & Comments - TIMAR ANALYTICS")
    reviews = load_json("reviews.json", [])
    if reviews:
        avg_rating = sum([r.get("rating",5) for r in reviews]) / len(reviews)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Reviews", len(reviews))
        col2.metric("Avg Rating", f"{avg_rating:.1f} ⭐")
        col3.metric("Satisfied", f"{len([r for r in reviews if r.get('rating',0) >=4])} users")
    else:
        st.info("🌟 Be the first to review TIMAR ANALYTICS!")
    st.divider()
    col_form, col_list = st.columns([1, 1.2])
    with col_form:
        st.subheader("✍️ Leave a Review")
        with st.container(border=True):
            user_name = st.text_input("Your Name", value=st.session_state.username, disabled=True)
            rating = st.slider("Rating", 1, 5, 5, help="1=Poor, 5=Excellent")
            stars = "⭐" * rating
            st.markdown(f"**{stars} ({rating}/5)**")
            organization = st.text_input("Organization / NGO (Optional)", placeholder="e.g., World Vision Uganda")
            review_text = st.text_area("Your Review / Comment *", placeholder="TIMAR ANALYTICS helped us...", height=120)
            would_recommend = st.checkbox("I would recommend TIMAR to other NGOs")
            if st.button("📤 Submit Review", type="primary", use_container_width=True):
                if not review_text.strip():
                    st.error("Please write your review")
                else:
                    new_review = {"user": st.session_state.username,"name": st.session_state.username,"organization": organization,"rating": rating,"review": review_text,"recommend": would_recommend,"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"likes": 0}
                    reviews.append(new_review)
                    save_json("reviews.json", reviews)
                    log_activity(st.session_state.username, "REVIEW_SUBMITTED", f"Rating {rating}")
                    st.success("✅ Thank you! Your review has been posted!")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
    with col_list:
        st.subheader(f"💬 All Reviews ({len(reviews)})")
        if not reviews:
            st.markdown("""<div style="background:#EFF6FF; padding:30px; border-radius:15px; text-align:center; border:2px dashed #1E3A8A;"><h3 style="color:#1E3A8A;">No reviews yet</h3><p>Your feedback will appear here</p><p>⭐⭐⭐⭐⭐</p></div>""", unsafe_allow_html=True)
        else:
            for idx, rev in enumerate(reversed(reviews[-20:])):
                stars_display = "⭐" * rev.get("rating",5)
                with st.container(border=True):
                    c1, c2 = st.columns([3,1])
                    with c1:
                        st.markdown(f"**👤 {rev.get('name','Anonymous')}** {stars_display}")
                        if rev.get("organization"): st.caption(f"🏢 {rev.get('organization')}")
                    with c2: st.caption(f"📅 {rev.get('date','')}")
                    st.write(f"_{rev.get('review','')}_")
                    if rev.get("recommend"): st.markdown("✅ **Recommends TIMAR**")
                    if st.button(f"👍 Helpful ({rev.get('likes',0)})", key=f"like_{idx}"):
                        rev["likes"] = rev.get("likes",0) + 1
                        save_json("reviews.json", reviews)
                        st.rerun()
    if is_admin() and reviews:
        st.divider()
        st.subheader("🛡️ Admin - Manage Reviews")
        if st.button("🗑️ Clear All Reviews (Admin Only)"):
            save_json("reviews.json", [])
            st.success("Cleared!")
            st.rerun()

elif st.session_state.page == "Research Module":
    st.header("🔬 Research Module - PhD Ready")
    st.info(f"**Active Dataset:** {len(df)} rows | {len(df.columns)} columns | Ready for Thesis Analysis")
    t1, t2, t3, t4, t5 = st.tabs(["📄 Data View", "📊 Summary Stats", "🔗 Correlation & Regression", "🧪 Hypothesis Testing", "📥 Thesis Export"])
    with t1:
        rel_cols = get_chartable_columns(df)
        st.dataframe(df[rel_cols].head(100) if rel_cols else df.head(100), use_container_width=True)
        render_chart(df, st.session_state.chart, get_best_chart_column(df, df.columns[0], st.session_state.chart), "Research")
    with t2:
        st.subheader("Summary Statistics - Descriptive")
        try:
            numeric_df = df.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                st.dataframe(numeric_df.describe().T, use_container_width=True)
                for col in numeric_df.columns[:3]:
                    fig = px.histogram(df, x=col, title=f"Distribution of {col}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No numeric columns for stats. Showing value counts.")
                for col in df.columns[:3]:
                    st.write(f"**{col}:**")
                    st.dataframe(df[col].value_counts().head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Stats error: {e}")
    with t3:
        st.subheader("Correlation & Regression - FIXED (No statsmodels)")
        all_numeric = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [c for c in all_numeric if not is_irrelevant_column(df, c)]
        if not numeric_cols:
            numeric_cols = all_numeric[:5]
        if len(numeric_cols) >= 2:
            c1, c2 = st.columns(2)
            with c1:
                x_col = st.selectbox("X - Independent", numeric_cols, key="res_x")
            with c2:
                y_opts = [c for c in numeric_cols if c!= x_col]
                y_col = st.selectbox("Y - Dependent", y_opts if y_opts else numeric_cols, key="res_y")
            try:
                temp = df[[x_col, y_col]].dropna()
                x = temp[x_col]
                y = temp[y_col]
                if len(x) < 2:
                    st.warning("Not enough data")
                else:
                    corr = x.corr(y)
                    slope, intercept = np.polyfit(x, y, 1)
                    y_pred = slope * x + intercept
                    ss_res = ((y - y_pred) ** 2).sum()
                    ss_tot = ((y - y.mean()) ** 2).sum()
                    r2 = 1 - (ss_res / ss_tot) if ss_tot!= 0 else 0
                    fig = px.scatter(temp, x=x_col, y=y_col, title=f"{y_col} vs {x_col}", opacity=0.6)
                    fig.add_scatter(x=x, y=y_pred, mode='lines', name=f'Regression: y={slope:.2f}x+{intercept:.2f}', line=dict(color='red', width=3))
                    st.plotly_chart(fig, use_container_width=True)
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Correlation (r)", f"{corr:.3f}")
                    m2.metric("R²", f"{r2:.3f}")
                    m3.metric("Equation", f"y={slope:.2f}x+{intercept:.2f}")
                    st.markdown("### Correlation Matrix")
                    st.dataframe(df[numeric_cols].corr(), use_container_width=True)
            except Exception as e:
                st.error(f"Regression error: {e}")
        else:
            st.warning("Need at least 2 numeric columns (excluding ID)")
            st.dataframe(df.corr(numeric_only=True), use_container_width=True)
    with t4:
        st.subheader("Hypothesis Testing")
        cat_cols = df.select_dtypes(include=['object']).columns.tolist()
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if cat_cols and num_cols:
            group_col = st.selectbox("Group by (Categorical)", cat_cols, key="hyp_group")
            value_col = st.selectbox("Value (Numeric)", num_cols, key="hyp_val")
            try:
                fig = px.box(df, x=group_col, y=value_col, title=f"{value_col} by {group_col}")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Test error: {e}")
        else:
            st.info("Upload numeric + categorical data to run hypothesis tests.")
    with t5:
        st.subheader("Thesis Export - PhD Ready")
        if not can_full_access():
            st.error("🔒 Export blocked - Trial expired. Pay to unlock thesis export.")
        else:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Full Dataset (CSV)", csv, "TIMAR_Research_Dataset.csv", "text/csv", use_container_width=True)

else:
    st.header(f"{st.session_state.page}")
    if st.session_state.pivot_df is not None and st.session_state.pivot_config is not None:
        st.info(f"📊 BOTH OPTIONS available - Raw ({len(df)} rows) + Pivoted ({st.session_state.pivot_df.shape[0]-1} groups)")
        render_chart_both_options(df, st.session_state.pivot_df, st.session_state.chart, df.columns[0], st.session_state.pivot_config)
    else:
        rel_cols = get_chartable_columns(df)
        st.dataframe(df[rel_cols].head(50) if rel_cols else df.head(50), use_container_width=True)
        if not can_full_access():
            st.error("🔒 Analysis & Download blocked - Trial expired, pay to unlock.")
        else:
            render_chart(df, st.session_state.chart, get_best_chart_column(df, df.columns[0], st.session_state.chart), st.session_state.page)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Data", csv, "timar_data.csv", "text/csv")

st.markdown(f"""<div style="text-align:center;color:#1E3A8A;font-weight:bold;margin-top:30px;"><hr>🌾 TIMAR ANALYTICS © 2026</div>""", unsafe_allow_html=True)
