import streamlit as st
import pandas as pd
import datetime
from datetime import datetime, timedelta
import plotly.express as px
import os, json, glob
import numpy as np
import time

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
            except:
                pass
    return available

NINE_DATASETS = load_9_master_files()

# --- HELPER FUNCTIONS (Must be first) ---
def is_irrelevant_column(df, col):
    try:
        col_lower = str(col).lower().strip()
        if col_lower in ['id','_id','uid','uuid','guid','index','row_id','serial','sno','pk','key']:
            return True
        if df[col].isnull().all():
            return True
        nunique = df[col].nunique()
        total = len(df)
        if total > 5 and nunique == total:
            return True
        if total > 10 and nunique / total > 0.9 and df[col].dtype == 'object':
            return True
    except:
        return False
    return False

def get_chartable_columns(df, chart_type="Bar Chart"):
    if df.empty:
        return []
    relevant = []
    for col in df.columns:
        if is_irrelevant_column(df, col):
            continue
        if df[col].dtype == 'object' or df[col].nunique() < 30:
            relevant.append(col)
    if not relevant:
        relevant = [c for c in df.columns if not is_irrelevant_column(df, c)][:5]
    if not relevant:
        relevant = list(df.columns[:3])
    return relevant

def get_best_chart_column(df, requested_col, chart_type):
    chartable = get_chartable_columns(df, chart_type)
    if not chartable:
        return df.columns[0]
    if requested_col in chartable:
        return requested_col
    return chartable[0]

def load_any_file(uploaded_file):
    name = uploaded_file.name.lower()
    try:
        if name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif name.endswith('.xlsx'):
            return pd.read_excel(uploaded_file, engine='openpyxl')
        elif name.endswith('.xls'):
            return pd.read_excel(uploaded_file, engine='xlrd')
        elif name.endswith('.json'):
            return pd.read_json(uploaded_file)
        elif name.endswith('.txt'):
            try:
                return pd.read_csv(uploaded_file, sep='\t')
            except:
                return pd.read_csv(uploaded_file)
        elif name.endswith('.tsv'):
            return pd.read_csv(uploaded_file, sep='\t')
        elif name.endswith('.parquet'):
            return pd.read_parquet(uploaded_file)
        elif name.endswith('.dta'):
            return pd.read_stata(uploaded_file)
        elif name.endswith('.ods'):
            return pd.read_excel(uploaded_file, engine='odf')
        elif name.endswith('.sav'):
            import pyreadstat
            df,_ = pyreadstat.read_sav(uploaded_file)
            return df
        else:
            return pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"Failed {uploaded_file.name}: {e}")
        st.info("Tip: If Excel fails, save as CSV and upload CSV - always works")
        return None

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
    else:
        districts = ["Kampala","Wakiso","Gulu","Lira","Arua","Mbarara","Kabale","Mbale","Soroti","Jinja"]
        df = pd.DataFrame({"District": districts, "Region": np.random.choice(["Central","Eastern","Northern","Western"], len(districts)), "Malaria_Cases_per_1000": np.random.randint(45, 320, len(districts)), "Immunization_Coverage_%": np.random.randint(62, 96, len(districts)), "Year": 2024})
        return df, "MOH Health"

STANDARD_TOOLS = ["Overview - All Data","Questionnaire - Structured Questions","Interview - Key Informant Interview","Focus Group Discussion (FGD)","Observation Checklist","Survey Form - Household Survey","Case Study Tool","Document Review / Secondary Data","Mobile Data Collection (Kobo/ODK)","Experimental Data Collection"]
DATA_COLLECTION_SAMPLES = {
    "Overview - All Data": ["Q1: Total records?","Q2: Data quality?"],
    "Questionnaire - Structured Questions": ["1. Age?","2. Gender?","3. Education?","4. Income?"],
    "Interview - Key Informant Interview": ["1. Challenges?","2. Interventions?"],
    "Focus Group Discussion (FGD)": ["1. Farming practices?","2. Info sharing?"],
    "Observation Checklist": ["1. Farm maintained?","2. Crops observed"],
    "Survey Form - Household Survey": ["1. Household size?","2. Head gender?"],
    "Case Study Tool": ["1. Title?","2. Background?"],
    "Document Review / Secondary Data": ["1. Title?","2. Source?"],
    "Mobile Data Collection (Kobo/ODK)": ["1. Form ID?","2. Enumerator?"],
    "Experimental Data Collection": ["1. Plot size?","2. Treatment?"]
}
ADMIN_PASSWORD = "admin@45697"
ALL_CHARTS = ["Bar Chart","Pie Chart","Line Chart","Scatter Plot","Histogram","Area Chart","Table View","Summary Statistics","Matrix View"]
MODULES_ALL = ["Dashboard","Analytics","9 Master Datasets - TIMAR REAL","Data Upload","Data Collection Tools - All 10","M&E Module","WASH Module","Livelihood Module","Health Module","Education Module","Agriculture Module","Research Module","KPI Matrix","Statistical Tools","Inventory & Stock Movement","Payment & Plans","Reviews & Comments","Help & Manual for Timar Analytics","Admin - Monitoring Panel"]

def load_users():
    if os.path.exists("users.json"):
        try:
            with open("users.json") as f:
                d=json.load(f); d["Admin"]=ADMIN_PASSWORD; return d
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
            if datetime.now() - start < timedelta(hours=24): return True
        except: pass
    return False
def get_trial_time_left():
    trials = load_json("trials.json", {})
    user = st.session_state.get("user","")
    if user in trials:
        try:
            start = datetime.fromisoformat(trials[user]["start"])
            remaining = timedelta(hours=24) - (datetime.now() - start)
            if remaining.total_seconds() > 0:
                return f"{int(remaining.total_seconds()//3600)}h {int((remaining.total_seconds()%3600)//60)}m", remaining
        except: pass
    return "0h 0m", timedelta(0)
def can_full_access():
    return is_admin() or has_active_subscription() or is_trial_active()

for k,v in [("logged_in",False),("username",""),("user",""),("page","Dashboard"),("chart","Bar Chart"),("selected_plan",None),("active_master","00_MASTER_ALL_9_AUTO (Recommended)"),("standard_tool","Questionnaire - Structured Questions")]:
    if k not in st.session_state: st.session_state[k]=v
if 'current_df' not in st.session_state:
    if NINE_DATASETS:
        first_key = list(NINE_DATASETS.keys())[0]
        st.session_state.current_df = NINE_DATASETS[first_key][1]
    else:
        st.session_state.current_df = pd.DataFrame({"Region":["Central","Eastern"],"Poverty_Rate_%":[20,30]})

if not st.session_state.logged_in:
    st.markdown("""<style>[data-testid="stSidebar"]{display:none;}header{visibility:hidden;}.stApp{background:radial-gradient(ellipse at top, #1E3A8A 0%, #0F172A 50%, #1E1B4B 100%)!important;}.login-card{background:white;padding:40px 35px;border-radius:20px;box-shadow:0 25px 70px rgba(0,0,0,0.4);text-align:center;margin-top:20px;border-top:8px solid #F59E0B;}.login-card h1{color:#1E3A8A!important;font-size:32px;font-weight:900;}</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown(f"""<div class="login-card"><div style="font-size:70px;">📊</div><h1>TIMAR ANALYTICS</h1><p style="font-size:18px!important;color:#1E3A8A!important;font-weight:900;">📊 Uganda's Smart Data Platform</p><p style="background:#FEF3C7;padding:10px;border-radius:10px;color:#1E3A8A!important;font-weight:900;">🔐 Secure Login</p></div>""", unsafe_allow_html=True)
        users = load_users()
        with st.form("login_form"):
            username = st.text_input("👤 Username"); password = st.text_input("🔒 Password", type="password")
            c1,c2 = st.columns(2)
            with c1: submit_login = st.form_submit_button("🔓 Log In", use_container_width=True, type="primary")
            with c2: submit_signup_toggle = st.form_submit_button("📝 Create Account", use_container_width=True)
            if submit_login:
                if username.lower()=="admin" and password==ADMIN_PASSWORD:
                    st.session_state.logged_in=True; st.session_state.username="Admin"; st.session_state.user="Admin"; st.rerun()
                elif username in users and users[username]==password:
                    st.session_state.logged_in=True; st.session_state.username=username; st.session_state.user=username; st.rerun()
                else: st.error("❌ Invalid")
            if submit_signup_toggle: st.session_state.show_signup = True
        if st.session_state.get("show_signup", False):
            with st.container(border=True):
                nu=st.text_input("Choose Username", key="s_u"); npw=st.text_input("Choose Password",type="password",key="s_p"); cpw=st.text_input("Confirm Password",type="password",key="s_c"); phone=st.text_input("Phone"); agree=st.checkbox("I agree to 24H trial")
                if st.button("🚀 Create & Start 24H Trial",type="primary",use_container_width=True):
                    users=load_users()
                    if npw!=cpw: st.error("Mismatch")
                    elif nu in users: st.error("Exists")
                    elif not agree: st.error("Agree")
                    else:
                        users[nu]=npw; save_json("users.json",{k:v for k,v in users.items() if k!="Admin"}); trials=load_json("trials.json",{}); trials[nu]={"start":datetime.now().isoformat(),"phone":phone}; save_json("trials.json",trials); st.success("✅ Created!"); st.balloons()
    st.stop()

df = st.session_state.current_df
MODULES = MODULES_ALL if is_admin() else [m for m in MODULES_ALL if m!= "Admin - Monitoring Panel"]

with st.sidebar:
    st.title("🌾 TIMAR ANALYTICS")
    if has_active_subscription(): st.success("✅ PAID - FULL ACCESS")
    elif is_trial_active():
        tl,_=get_trial_time_left(); st.warning(f"⏰ TRIAL: {tl} left")
    else:
        st.error("🔒 TRIAL EXPIRED")
        if st.button("💳 Pay Now", type="primary", use_container_width=True):
            st.session_state.page="Payment & Plans"; st.rerun()
    sel_mod = st.selectbox("📦 Modules", MODULES, index=MODULES.index(st.session_state.page) if st.session_state.page in MODULES else 0)
    st.session_state.page = sel_mod
    sel_chart = st.selectbox("📈 Chart Type", ALL_CHARTS)
    st.session_state.chart = sel_chart
    if st.button("🚪 Logout", width='stretch'): st.session_state.logged_in=False; st.rerun()

def render_chart(data, chart_type, col_name, title_suffix=""):
    if len(data)==0: return
    best_col = get_best_chart_column(data, col_name, chart_type)
    counts = data[best_col].value_counts().reset_index(); counts.columns = [best_col, "Count"]
    try:
        if chart_type=="Bar Chart": fig = px.bar(counts, x=best_col, y="Count", color=best_col); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Pie Chart": fig = px.pie(counts, names=best_col, values="Count", hole=0.3); st.plotly_chart(fig, use_container_width=True)
        elif chart_type=="Line Chart": fig = px.line(counts, x=best_col, y="Count", markers=True); st.plotly_chart(fig, use_container_width=True)
        else: st.dataframe(data.head(100), width='stretch')
    except Exception as e: st.error(f"Chart error: {e}")

if st.session_state.page == "Dashboard":
    st.header("Dashboard")
    st.metric("Total Rows", len(df))
    rel_cols = get_chartable_columns(df)
    st.dataframe(df[rel_cols].head(50) if rel_cols else df.head(50), use_container_width=True)
    render_chart(df, st.session_state.chart, df.columns[0], "Dashboard")

elif st.session_state.page == "Data Upload":
    st.header("📤 Data Upload - ANY TYPE (10 Types)")
    st.caption("Supports: CSV, XLSX, XLS, JSON, TXT, TSV, PARQUET, SAV, DTA, ODS")
    if not can_full_access():
        st.error("🚫 UPLOAD DISABLED - TRIAL EXPIRED - Pay to unlock")
        st.stop()
    uploaded_file = st.file_uploader("📁 Drag & drop ANY file", type=["csv","xlsx","xls","json","txt","tsv","parquet","sav","dta","ods"])
    if uploaded_file:
        temp_df = load_any_file(uploaded_file)
        if temp_df is not None:
            st.success(f"✅ {uploaded_file.name} | {len(temp_df)} rows | {len(temp_df.columns)} cols")
            st.dataframe(temp_df.head(50), use_container_width=True)
            if st.button("🔵 Set as Active", type="primary", use_container_width=True):
                st.session_state.current_df = temp_df; st.rerun()
    st.metric("Rows", len(df)); st.metric("Master Files", len(NINE_DATASETS))

elif st.session_state.page == "Research Module":
    st.header("🔬 Research Module - PhD Ready")
    t1, t2, t3, t4, t5 = st.tabs(["📄 Data View", "📊 Summary Stats", "🔗 Correlation & Regression", "🧪 Hypothesis Testing", "📥 Thesis Export"])
    with t1:
        rel_cols = get_chartable_columns(df)
        st.dataframe(df[rel_cols].head(100) if rel_cols else df.head(100), use_container_width=True)
    with t2:
        numeric_df = df.select_dtypes(include=[np.number])
        if not numeric_df.empty: st.dataframe(numeric_df.describe().T, use_container_width=True)
        else: st.dataframe(df.describe(include='all').T, use_container_width=True)
    with t3:
        st.subheader("Correlation & Regression - FIXED (No statsmodels)")
        all_numeric = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [c for c in all_numeric if not is_irrelevant_column(df, c)]
        if not numeric_cols: numeric_cols = all_numeric[:5]
        if len(numeric_cols) >= 2:
            c1,c2 = st.columns(2)
            with c1: x_col = st.selectbox("X - Independent", numeric_cols, key="res_x")
            with c2: y_col = st.selectbox("Y - Dependent", [c for c in numeric_cols if c!= x_col], key="res_y")
            try:
                temp = df[[x_col, y_col]].dropna()
                x = temp[x_col]; y = temp[y_col]
                if len(x) >= 2:
                    corr = x.corr(y)
                    slope, intercept = np.polyfit(x, y, 1)
                    y_pred = slope * x + intercept
                    ss_res = ((y - y_pred) ** 2).sum()
                    ss_tot = ((y - y.mean()) ** 2).sum()
                    r2 = 1 - (ss_res / ss_tot) if ss_tot!= 0 else 0
                    fig = px.scatter(temp, x=x_col, y=y_col, title=f"{y_col} vs {x_col}", opacity=0.6)
                    fig.add_scatter(x=x, y=y_pred, mode='lines', name=f'Regression', line=dict(color='red', width=3))
                    st.plotly_chart(fig, use_container_width=True)
                    m1,m2,m3 = st.columns(3)
                    m1.metric("Correlation (r)", f"{corr:.3f}")
                    m2.metric("R²", f"{r2:.3f}")
                    m3.metric("Equation", f"y={slope:.2f}x+{intercept:.2f}")
                    st.dataframe(df[numeric_cols].corr(), use_container_width=True)
            except Exception as e: st.error(f"Error: {e}")
        else: st.warning("Need 2+ numeric columns")
    with t4:
        st.subheader("Hypothesis Testing")
        cat_cols = [c for c in df.columns if df[c].dtype == 'object']
        num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if not is_irrelevant_column(df, c)]
        if cat_cols and num_cols:
            group_col = st.selectbox("Group by", cat_cols, key="hyp_group")
            value_col = st.selectbox("Value", num_cols, key="hyp_val")
            fig = px.box(df, x=group_col, y=value_col); st.plotly_chart(fig, use_container_width=True)
    with t5:
        st.subheader("Thesis Export")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "TIMAR_Research.csv", "text/csv")

elif st.session_state.page == "Admin - Monitoring Panel":
    if not is_admin(): st.error("⛔ Access Denied"); st.stop()
    st.header("🛡️ Admin - Monitoring Panel")
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Users","⏰ Trials","💳 Payments","📝 Logs"])
    with tab1:
        users = load_users(); st.metric("Total Users", len(users))
        st.dataframe(pd.DataFrame([{"Username":k} for k in users.keys()]), use_container_width=True)
    with tab2:
        trials = load_json("trials.json", {})
        rows=[]
        for k,v in trials.items():
            if isinstance(v, dict): rows.append({"User":k, "Start":v.get("start",""), "Phone":v.get("phone","")})
            else: rows.append({"User":k, "Start":str(v)})
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    with tab3:
        subs = load_json("subscriptions.json", {})
        st.dataframe(pd.DataFrame([{"User":k, "Plan":v.get("plan","") if isinstance(v,dict) else str(v)} for k,v in subs.items()]), use_container_width=True)
    with tab4:
        logs = load_json("timar_activity_log.json", []); st.dataframe(pd.DataFrame(logs[-100:][::-1]), use_container_width=True)

elif st.session_state.page == "Payment & Plans":
    st.title("💳 Payment & Plans")
    subs = load_json("subscriptions.json", {})
    if "selected_plan" not in st.session_state: st.session_state.selected_plan=None
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
        st.warning(f"### 📱 Pay To MTN MoMo: 0789876277 / 0755453313 - Tino Mary - UGX {prices[plan]:,}")
        txn=st.text_input("MoMo Transaction ID *"); proof_file = st.file_uploader("📤 Upload Proof *", type=["png","jpg","jpeg","pdf"])
        if st.button("🚀 Upload & Activate", type="primary", use_container_width=True):
            if not txn.strip(): st.error("Enter Txn")
            elif proof_file is None: st.error("Upload proof")
            else:
                os.makedirs("payment_proofs", exist_ok=True)
                proof_path = f"payment_proofs/{st.session_state.user}_{plan}_{txn}_{proof_file.name}"
                with open(proof_path, "wb") as f: f.write(proof_file.getbuffer())
                expires_date = (datetime.now()+timedelta(days=30)).isoformat()
                subs[st.session_state.user]={"plan":plan,"amount":prices[plan],"txn":txn,"expires":expires_date,"status":"ACTIVE"}; save_json("subscriptions.json", subs); st.success(f"✅ ACTIVATED! {plan}"); st.balloons(); st.rerun()

else:
    st.header(f"{st.session_state.page}")
    rel_cols = get_chartable_columns(df)
    st.dataframe(df[rel_cols].head(50) if rel_cols else df.head(50), use_container_width=True)
    render_chart(df, st.session_state.chart, df.columns[0], st.session_state.page)

st.markdown("""<div style="text-align:center;color:#1E3A8A;font-weight:bold;margin-top:30px;"><hr>🌾 TIMAR ANALYTICS © 2026</div>""", unsafe_allow_html=True)
