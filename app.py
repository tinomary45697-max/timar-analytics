import streamlit as st
import pandas as pd
import numpy as np
import os, json
from datetime import datetime

st.set_page_config(page_title="TIMAR ANALYTICS", layout="wide")

st.markdown("""
<style>
section[data-testid="stSidebar"]{background:#1E3A8A!important}
section[data-testid="stSidebar"] label{color:white!important}
section[data-testid="stSidebar"] div[data-baseweb="select"]>div{background:#D4AF37!important}
section[data-testid="stSidebar"] div[data-baseweb="select"] span{color:white!important}
section[data-testid="stSidebar"] svg{fill:white!important}
.stApp { background-color: #FFFFFF!important; }
[data-testid="stHeader"] { background: rgba(0,0,0,0)!important; }
.main.block-container { background-color: #FFFFFF!important; }
div[data-testid="stDataFrame"], div[data-testid="stDataEditor"],.stTable {
  background-color: white!important;
  border: 1px solid #E5E7EB!important;
  border-radius: 10px!important;
}
div[data-testid="stDataFrame"] thead tr th {
  background-color: #1E3A8A!important;
  color: white!important;
}
div[data-testid="stDataFrame"] tbody tr {
  background-color: white!important;
  color: #1E293B!important;
}
div[data-testid="stPlotlyChart"], [data-testid="stVegaLiteChart"] {
  background-color: white!important;
  border-radius: 10px!important;
  border: 1px solid #E5E7EB!important;
}
.stButton > button {
  background: linear-gradient(90deg, #D4AF37 0%, #B8960C 100%)!important;
  color: white!important;
  font-weight: bold!important;
  border-radius: 8px!important;
  border: none!important;
  height: 44px!important;
}
.stButton > button:hover { background: #1E3A8A!important; color: #D4AF37!important; }
div[data-testid="stMetric"] {
  background-color: white!important;
  border-top: 4px solid #D4AF37!important;
  border: 1px solid #E5E7EB!important;
  border-radius: 12px!important;
}
h1, h2, h3 { color: #1E3A8A!important; }
h2 { border-left: 6px solid #D4AF37; padding-left: 12px; }
</style>
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
    if st.session_state.get("plan","FREE_TRIAL")!="FREE_TRIAL": return True,"Paid Active"
    trials=load_json("trials.json",{})
    if user not in trials:
        trials[user]={"start":datetime.now().isoformat()}; save_json("trials.json",trials); return True,"24.0h left"
    start=datetime.fromisoformat(trials[user]["start"]); left=24-(datetime.now()-start).total_seconds()/3600
    if left<=0: return False,"Expired"
    return True,f"{left:.1f}h left"
def is_admin(): return st.session_state.get("user","").lower()=="admin"
def is_trial_ok():
    ok,msg = check_trial(st.session_state.get("user","")); return ok

for k in ["logged_in","user","plan","page","tool","metool","chart","current_df","lang_name","selected_plan","selected_plan_key"]:
    if k not in st.session_state:
        if k=="logged_in": st.session_state[k]=False
        elif k=="user": st.session_state[k]=""
        elif k=="plan": st.session_state[k]="FREE_TRIAL"
        elif k=="page": st.session_state[k]="Dashboard"
        elif k=="tool": st.session_state[k]="Overview - All Data"
        elif k=="metool": st.session_state[k]="LogFrame - Logical Framework 4x4"
        elif k=="chart": st.session_state[k]="Bar Chart"
        elif k=="current_df": st.session_state[k]=generate_sample_data()
        elif k=="lang_name": st.session_state[k]="English"
        else: st.session_state[k]=None

if not st.session_state.logged_in:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    header {visibility: hidden;}
 .stApp { background: linear-gradient(135deg, #0F2C5C 0%, #1E3A8A 50%, #1E40AF 100%)!important; }
 .login-card { background: white; padding: 40px 35px; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); text-align: center; margin-top: 40px; }
 .login-card h1 { color: #1E3A8A; font-size: 28px; font-weight: 800; margin-bottom: 5px; }
 .login-card p { color: #6B7280; font-size: 14px; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""<div class="login-card"><h1>🌾 TIMAR ANALYTICS</h1><p>Uganda's Smart Data Platform | Sign in to your account</p></div>""", unsafe_allow_html=True)
        users = load_users()
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        st.write("")
        c1,c2 = st.columns(2)
        with c1:
            if st.button("Sign In", use_container_width=True):
                if username.lower()=="admin" and password==ADMIN_PASSWORD:
                    st.session_state.logged_in=True; st.session_state.user="Admin"; st.session_state.plan="ADMIN_FREE"; log_activity("Admin","LOGIN"); st.rerun()
                elif username in users and users[username]==password:
                    st.session_state.logged_in=True; st.session_state.user=username; trials=load_json("trials.json",{});
                    if username not in trials: trials[username]={"start":datetime.now().isoformat()}; save_json("trials.json",trials)
                    log_activity(username,"LOGIN"); st.rerun()
                else: st.error("Invalid username or password")
        with c2:
            if st.button("Sign Up 24h Trial", use_container_width=True): st.session_state.show_signup = True
        if st.session_state.get("show_signup", False):
            with st.container(border=True):
                st.markdown("### Create Account - 24h FREE TRIAL")
                nu=st.text_input("Choose Username",key="s_u"); npw=st.text_input("Choose Password",type="password",key="s_p"); cpw=st.text_input("Confirm",type="password",key="s_c"); phone=st.text_input("Phone"); agree=st.checkbox("I agree to start 24hr trial")
                if st.button("Create & Start Trial",type="primary",use_container_width=True):
                    users=load_users()
                    if not nu or not npw: st.error("Required")
                    elif npw!=cpw: st.error("No match")
                    elif nu in users: st.error("Exists")
                    elif not agree: st.error("Agree")
                    else: users[nu]=npw; save_json("users.json",users); trials=load_json("trials.json",{}); trials[nu]={"start":datetime.now().isoformat(),"phone":phone}; save_json("trials.json",trials); log_activity(nu,"SIGNUP"); st.success(f"{nu} created! Now login"); st.balloons()
    st.stop()

st.markdown("""<div style="background: linear-gradient(90deg, #1E3A8A 0%, #1E40AF 50%, #D4AF37 100%); padding:15px; border-radius:15px; margin-bottom:15px; text-align:center;"><h1 style="color:white!important; -webkit-text-fill-color:white; margin:0;">🌾 TIMAR ANALYTICS 📊</h1><p style="color:#FEF3C7; margin:0; font-weight:bold;">Uganda's Smart Data Platform | All 15 Modules |</p></div>""", unsafe_allow_html=True)

ok,msg=check_trial(st.session_state.user)
if not ok and not is_admin() and st.session_state.page!="Payment & Plans":
    st.warning("⚠️ Trial Expired - Please upgrade to continue"); st.session_state.page="Payment & Plans"

with st.sidebar:
    st.markdown("""<div style="background:white; padding:10px; border-radius:10px; text-align:center; margin-bottom:10px;"><h2 style="color:#1E3A8A!important; margin:0;">🌾 TIMAR</h2><p style="color:#D4AF37!important; font-weight:bold; margin:0; font-size:12px;">Tino Mary</p></div>""", unsafe_allow_html=True)
    st.caption(f"👤 {st.session_state.user} | ⏰ {msg}"); st.divider()
    mods = MODULES_ADMIN if is_admin() else MODULES_USER
    sel_mod = st.selectbox("Select Module", mods, index=mods.index(st.session_state.page) if st.session_state.page in mods else 0, label_visibility="collapsed", key="sb_mod")
    st.session_state.page = sel_mod
    st.markdown(f"<div style='background:#D4AF37; color:white!important; padding:6px; border-radius:8px; font-weight:bold; font-size:13px; text-align:center; margin-bottom:15px;'>✅ {sel_mod}</div>", unsafe_allow_html=True)
    sel_tool = st.selectbox("Select Collection Tool", STANDARD_TOOLS, index=STANDARD_TOOLS.index(st.session_state.tool) if st.session_state.tool in STANDARD_TOOLS else 0, label_visibility="collapsed", key="sb_tool")
    st.session_state.tool = sel_tool
    sel_me = st.selectbox("Select M&E Tool", ME_TOOLS, index=ME_TOOLS.index(st.session_state.metool) if st.session_state.metool in ME_TOOLS else 0, label_visibility="collapsed", key="sb_me")
    st.session_state.metool = sel_me
    sel_chart = st.selectbox("Select Chart", ALL_CHARTS, index=ALL_CHARTS.index(st.session_state.chart) if st.session_state.chart in ALL_CHARTS else 0, label_visibility="collapsed", key="sb_chart")
    st.session_state.chart = sel_chart
    sel_lang = st.selectbox("Select Language", list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(st.session_state.lang_name), label_visibility="collapsed", key="sb_lang")
    st.session_state.lang_name = sel_lang
    st.divider()
    if st.button("🔄 Load 520 Sample Data", width='stretch', key="sb_load"):
        st.session_state.current_df = generate_sample_data(); log_activity(st.session_state.user, "LOAD 520 SAMPLE"); st.success("520 sample loaded")
    if st.button("🚪 Logout", width='stretch', key="sb_logout"):
        log_activity(st.session_state.user, "LOGOUT"); st.session_state.logged_in=False; st.rerun()

df=st.session_state.current_df
if st.session_state.page=="Dashboard":
    st.header(f"Dashboard | {st.session_state.tool} | {st.session_state.chart}")
    c1,c2,c3,c4,c5=st.columns(5)
    c1.metric("Records",len(df)); c2.metric("Regions",df["Region"].nunique()); c3.metric("Avg Age",f"{df['Age'].mean():.1f}"); c4.metric("Avg Income",f"UGX {df['Income'].mean():,.0f}"); c5.metric("Avg Yield",f"{df['Yield_Tons'].mean():.1f}")
    filt=df.copy()
    if st.session_state.tool!="Overview - All Data" and "Collection_Tool" in df.columns and st.session_state.tool in df["Collection_Tool"].unique().tolist(): filt=df[df["Collection_Tool"]==st.session_state.tool]
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
    st.header(f"📊 Analytics | {st.session_state.tool}")
    filt=df.copy()
    if st.session_state.tool!="Overview - All Data" and st.session_state.tool in df["Collection_Tool"].unique().tolist(): filt=df[df["Collection_Tool"]==st.session_state.tool]
    st.dataframe(filt.head(100), width='stretch')
    st.bar_chart(filt["Region"].value_counts())
elif st.session_state.page=="Data Upload":
    st.header("Data Upload")
    up=st.file_uploader("Upload CSV/Excel",type=["csv","xlsx","xls"])
    if up:
        try:
            ndf=pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
            st.session_state.current_df=ndf; st.success(f"{len(ndf)} rows ACTIVE!"); st.dataframe(ndf.head(100),width='stretch')
        except Exception as e: st.error(str(e))
    else: st.dataframe(df.head(50),width='stretch')
elif st.session_state.page=="Payment & Plans":
    st.header("💳 Payment & Plans")
    
    cols=st.columns(3)
    for i,(key,plan) in enumerate(PLANS.items()):
        if key=="ADMIN_FREE": continue
        with cols[i%3]:
            with st.container(border=True):
                st.subheader(plan["name"])
                st.metric("Price", f"UGX {plan['price']:,}")
                st.write(plan.get("desc",""))
                
                # PAY BUTTON
                if st.button(f"Pay {plan['name']}", key=f"pay_{key}"):
                    st.session_state.selected_plan = key
                    st.session_state.show_payment_uploader = True
    
        # ===== RESTORED: UPLOAD + AUTO CONFIRMATION WITH YOUR MOMO =====
    if st.session_state.get("show_payment_uploader", False):
        st.markdown("---")
        plan = PLANS[st.session_state.selected_plan]
        st.subheader(f"Pay for {plan['name']}")
        
        # === YOUR MTN MOMO DETAILS - ONLY SHOWS AFTER CLICKING PAY ===
        with st.container(border=True):
            st.markdown("### 💰 Pay Using MTN Mobile Money")
            st.markdown(f"""
            **Amount:** UGX {plan['price']:,}
            
            **MTN MoMo Number:** `0789876277`
            
            **Names:** Tino Mary
            
            **Steps:**
            1. Go to MTN MoMo Menu
            2. Send Money to **0789876277 - Tino Mary**
            3. Enter Amount: **UGX {plan['price']:,}**
            4. After paying, upload the confirmation SMS screenshot/receipt below
            """)
            st.warning("⚠️ Please include your name in MoMo reference")
        
        st.markdown("### 📤 Upload Proof After Payment")
        up_pay = st.file_uploader("Upload MoMo Receipt / Screenshot", type=["png","jpg","jpeg","pdf"], key="payment_proof_final")
        
        if up_pay:
            # Save proof
            os.makedirs("uploads/payments", exist_ok=True)
            path = f"uploads/payments/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{up_pay.name}"
            with open(path, "wb") as f:
                f.write(up_pay.getbuffer())
            
            # AUTO CONFIRMATION
            st.session_state.payment_status = "CONFIRMED"
            st.session_state.payment_plan = st.session_state.selected_plan
            st.session_state.payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.payment_proof_path = path
            
            st.success("✅ Payment Proof Received & AUTO-CONFIRMED!")
            st.success(f"Plan {plan['name']} Activated for UGX {plan['price']:,}")
            st.balloons()
            
            if up_pay.type.startswith("image"):
                st.image(up_pay, width=350, caption="Your Payment Proof")
            
            if st.button("Continue to Dashboard"):
                st.session_state.page = "Dashboard"
                st.rerun()
else:
    st.header(f"{st.session_state.page}")
    st.dataframe(df.head(100), width='stretch')

st.markdown("""<div style="text-align:center; color:#1E3A8A; font-weight:bold; margin-top:30px;"><hr>🌾 TIMAR ANALYTICS © 2026 | Blue & Gold |<br></div>""", unsafe_allow_html=True)
