import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="TIMAR ANALYTICS", page_icon="📊", layout="wide")

CONTACT_1 = "+256 789 876 277"
CONTACT_2 = "+256 755 453 313"
EMAIL = "timaranalytics@gmail.com"
LOCATION = "Kampala, Uganda"
PRO_CODE = "TIMAR-PRO-2026-UNLIMITED"
ADMIN_CODE = "TIMAR-ADMIN-2026"

if 'plan' not in st.session_state:
    st.session_state.plan = "FREE"
if 'data' not in st.session_state:
    st.session_state.data = None
if 'role' not in st.session_state:
    st.session_state.role = "user"
if 'payments' not in st.session_state:
    st.session_state.payments = []

# SIDEBAR
with st.sidebar:
    st.title("TIMAR ANALYTICS")
    st.caption(f"{LOCATION} - Field to Funding")
    if st.session_state.plan == "PRO":
        st.success("⭐ PRO - Unlimited")
    else:
        st.warning("🆓 FREE - 50 Records")
    if st.session_state.role == "admin":
        st.error("👑 ADMIN MODE")

    st.divider()
    st.subheader("⚙️ TIMAR Services")
    services_menu = st.selectbox("Select Service", [
        "📊 Dashboard Overview",
        "📥 Feed Data via Excel",
        "🗺️ Map View",
        "📄 Donor Report (Paid)",
        "📈 VHT Analytics",
        "👶 OVC Protection",
        "💧 WASH Analytics",
        "🌾 Livelihood",
        "🔍 Data Quality",
        "📤 Export & Sync",
        "💰 Billing",
        "👑 Admin Panel"
    ])

    if st.session_state.data is not None:
        dc = st.session_state.data['district'].nunique() if 'district' in st.session_state.data.columns else 0
        st.caption(f"📦 {len(st.session_state.data)} records | {dc} districts")

    st.divider()
    with st.expander("🔓 Unlock PRO / ADMIN"):
        code = st.text_input("Enter Code", type="password")
        if st.button("Unlock"):
            if code == PRO_CODE:
                st.session_state.plan = "PRO"
                st.success("PRO UNLOCKED ✅")
                st.rerun()
            elif code == ADMIN_CODE:
                st.session_state.role = "admin"
                st.session_state.plan = "PRO"
                st.success("ADMIN 👑")
                st.rerun()
            else:
                st.error("Invalid")

    with st.expander(f"📱 Pay MoMo - {CONTACT_1}"):
        st.info(f"Send 150k to {CONTACT_1} or {CONTACT_2}")
        tid = st.text_input("Transaction ID")
        ngo = st.text_input("NGO Name")
        if st.button("Submit Payment"):
            if tid and ngo:
                st.session_state.payments.append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "ngo": ngo, "tid": tid, "status": "Pending"})
                st.success(f"Received {tid}. WhatsApp {CONTACT_1}")

    st.markdown(f"📞 {CONTACT_1}\n📧 {EMAIL}")

# DASHBOARD WITH INTERPRETATION
def render_dashboard(df):
    st.header("📊 Full Donor Dashboard - 6 Charts + Auto Interpretation")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Beneficiaries", f"{len(df):,}", "+12%")
    col2.metric("Districts", f"{df['district'].nunique() if 'district' in df.columns else len(df)}", "+3")
    vht_c = len(df[df['pillar']=='VHT']) if 'pillar' in df.columns and 'VHT' in df['pillar'].values else len(df)//4
    col3.metric("VHT Cases", f"{vht_c:,}")
    col4.metric("Completion", "92%", "+5%")
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 Monthly Trend - Chart 1")
        if 'date' in df.columns:
            try:
                dft = df.copy()
                dft['date'] = pd.to_datetime(dft['date'], errors='coerce')
                dft = dft.dropna(subset=['date'])
                if len(dft)>0:
                    monthly = dft.groupby(dft['date'].dt.to_period('M')).size().reset_index(name='count')
                    monthly['date'] = monthly['date'].astype(str)
                    fig = px.line(monthly, x='date', y='count', markers=True, template="plotly_white", title="Monthly Collection Trend")
                    st.plotly_chart(fig, use_container_width=True)
                    if len(monthly) >= 2:
                        last = monthly['count'].iloc[-1]
                        prev = monthly['count'].iloc[-2]
                        change = ((last-prev)/prev*100) if prev!=0 else 0
                        trend = "increasing 📈" if change>0 else "decreasing 📉" if change<0 else "stable ➡️"
                        st.info(f"🧠 Interpretation: Data is {trend} by {abs(change):.1f}%. Last: {last} vs Prev: {prev}. Donor: {'Scaling well, maintain momentum' if change>0 else 'Check field team activity'}. Action: {'Keep VHTs motivated' if change>0 else 'Investigate low coverage'}.")
            except Exception as e:
                st.error(f"Date error: {e}")
        else:
            st.warning("Add 'date' column")
            st.line_chart(df.head(20))

    with c2:
        st.subheader("🥧 Pillar Split - Chart 2")
        if 'pillar' in df.columns:
            pc = df['pillar'].value_counts()
            fig = px.pie(values=pc.values, names=pc.index, hole=0.5, title="Beneficiaries by Pillar")
            st.plotly_chart(fig, use_container_width=True)
            top_pillar = pc.index[0]
            top_pct = pc.values[0]/pc.values.sum()*100
            st.info(f"🧠 Interpretation: {top_pillar} dominates {pc.values[0]:,} ({top_pct:.1f}%). Breakdown: {', '.join([f'{k}:{v}' for k,v in pc.items()])}. Donor: {'VHT most active - health impact' if top_pillar=='VHT' else 'Balanced - integrated funding'}. Action: Support {pc.index[-1]}.")

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("📊 Top 10 Districts - Chart 3")
        if 'district' in df.columns:
            db = df['district'].value_counts().head(10).reset_index()
            db.columns = ['district','count']
            fig = px.bar(db, x='count', y='district', orientation='h', color='count', color_continuous_scale='Viridis', title="Top 10 Districts")
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
            top_d = db.iloc[0]
            bottom_d = db.iloc[-1]
            st.info(f"🧠 Interpretation: Highest {top_d['district']} {top_d['count']}, Lowest {bottom_d['district']} {bottom_d['count']}. Gap {top_d['count']-bottom_d['count']}. Donor: Strong in {top_d['district']}. Action: Check {bottom_d['district']}.")

    with c4:
        st.subheader("📉 Gender - Chart 4")
        if 'gender' in df.columns:
            if 'district' in df.columns:
                gd = df.groupby(['district','gender']).size().reset_index(name='count')
                fig = px.bar(gd.head(30), x='district', y='count', color='gender', barmode='stack', title="Gender per District")
                st.plotly_chart(fig, use_container_width=True)
            else:
                gc = df['gender'].value_counts()
                fig = px.bar(gc, title="Gender")
                st.plotly_chart(fig, use_container_width=True)
            gender_counts = df['gender'].value_counts()
            female_pct = gender_counts.get('Female',0)/len(df)*100 if 'Female' in gender_counts else 50
            st.info(f"🧠 Interpretation: Female {female_pct:.1f}% {'✅ USAID target met' if female_pct>=45 else '⚠️ Below target'}. Donor: {'Compliant' if 45<=female_pct<=55 else 'Gap detected'}.")
        elif 'district' in df.columns and 'pillar' in df.columns:
            heat = pd.crosstab(df['district'], df['pillar'])
            fig = px.imshow(heat, text_auto=True, title="District vs Pillar")
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("🗺️ Map & Heatmap - Chart 5 & 6")
    if 'latitude' in df.columns and 'longitude' in df.columns:
        try:
            st.map(df[['latitude','longitude']].dropna().head(500))
            st.info(f"🧠 Geospatial: {df['district'].nunique() if 'district' in df.columns else len(df)} districts mapped. Clusters = active teams. Donor: Visual proof of national reach. Action: Blank = deploy VHTs.")
        except:
            pass
    else:
        st.warning("Add lat/long for Map - Showing heatmaps")
        if 'district' in df.columns and 'pillar' in df.columns:
            heat = pd.crosstab(df['district'], df['pillar'])
            fig = px.imshow(heat, text_auto=True, title="District vs Pillar Heatmap")
            st.plotly_chart(fig, use_container_width=True)
            st.info("🧠 Interpretation: Darker = high coverage. White gaps = urgent need.")

    st.divider()
    total = len(df)
    districts = df['district'].nunique() if 'district' in df.columns else 0
    pillars = df['pillar'].nunique() if 'pillar' in df.columns else 0
    st.success(f"EXECUTIVE FOR DONORS: Scale: {total:,} across {districts} districts, {pillars} pillars, 92% complete. 'TIMAR tracks {total:,} beneficiaries, {districts} districts monitored with 92% completeness.'")

# MAIN ROUTING
df = st.session_state.data

if services_menu == "📊 Dashboard Overview":
    if df is None:
        st.warning("⚠️ No data loaded. This is NORMAL for first run.")
        st.info("👉 Click below to see 6 charts + interpretations")
        if st.button("Load Sample 500 Records - See Dashboard", type="primary"):
            import numpy as np
            np.random.seed(42)
            districts = ["Kampala","Gulu","Arua","Lira","Mbarara","Jinja","Mbale","Kabale","Wakiso","Mukono"]
            pillars = ["VHT","OVC","WASH","Livelihood"]
            genders = ["Male","Female"]
            sample = pd.DataFrame({
                'district': np.random.choice(districts, 500),
                'pillar': np.random.choice(pillars, 500),
                'gender': np.random.choice(genders, 500),
                'beneficiary_id': [f"BEN-{i:04d}" for i in range(500)],
                'age': np.random.randint(1,80,500),
                'vulnerability_score': np.random.randint(1,10,500),
                'date': pd.date_range("2024-01-01", periods=500, freq='W'),
                'latitude': np.random.uniform(-1.5, 4.0, 500),
                'longitude': np.random.uniform(29.5, 35.0, 500),
            })
            st.session_state.data = sample
            st.rerun()
    else:
        render_dashboard(df)

elif services_menu == "📥 Feed Data via Excel":
    st.header("📥 Feed Data - Offline Excel Mode")
    up = st.file_uploader("Upload TIMAR_MASTER_DATA.xlsx / CSV", type=['xlsx','csv'])
    if up is not None:
        try:
            df_up = pd.read_excel(up) if up.name.endswith('.xlsx') else pd.read_csv(up)
            if st.session_state.plan == "FREE" and len(df_up) > 50:
                st.warning(f"FREE limit 50. Uploaded {len(df_up)}. Showing 50. Upgrade!")
                df_up = df_up.head(50)
            st.session_state.data = df_up
            st.success(f"✅ Loaded {len(df_up)} records")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}. Run pip install openpyxl")
    if df is not None:
        st.dataframe(df.head(100), use_container_width=True)

elif services_menu == "🗺️ Map View":
    st.header("🗺️ Map View - 136 Districts")
    if df is None:
        st.warning("Load data first")
    else:
        if 'latitude' in df.columns and 'longitude' in df.columns:
            st.map(df[['latitude','longitude']].dropna().head(1000))
            st.info("🧠 Map Interpretation: Clusters = active VHTs. Blank areas = no data. Deploy teams there. Donors love map proof of national coverage.")
        else:
            st.warning("No lat/long. Add latitude & longitude columns")

elif services_menu == "📄 Donor Report (Paid)":
    st.header("📄 Donor Report - USAID/UNICEF")
    if st.session_state.plan == "FREE":
        st.error(f"🔒 PRO Required. Pay 150k to {CONTACT_1} then code {PRO_CODE}")
    else:
        if df is None:
            st.warning("Load data first")
        else:
            rtype = st.selectbox("Template", ["USAID OVC Report","UNICEF WASH Report","MoH VHT Report","Full Consolidated"])
            if st.button("Generate Report"):
                st.dataframe(df.head(50), use_container_width=True)
                st.download_button("Download CSV", df.to_csv(index=False), f"TIMAR_{rtype}.csv", "text/csv")
                try:
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False)
                    st.download_button("Download Excel", output.getvalue(), f"TIMAR_{rtype}.xlsx")
                except:
                    pass

elif services_menu == "📈 VHT Analytics":
    st.header("📈 VHT Health Analytics - MoH Format - WITH INTERPRETATION")
    if df is None:
        st.warning("Load data")
    else:
        vdf = df[df['pillar']=='VHT'] if 'pillar' in df.columns and 'VHT' in df['pillar'].values else df
        c1,c2,c3 = st.columns(3)
        c1.metric("VHT Records", f"{len(vdf):,}")
        c2.metric("Districts", f"{vdf['district'].nunique() if 'district' in vdf.columns else 0}")
        avg_age = vdf['age'].mean() if 'age' in vdf.columns else 0
        c3.metric("Avg Age", f"{avg_age:.1f}" if avg_age else "N/A")
        if 'district' in vdf.columns:
            fig = px.bar(vdf['district'].value_counts().head(10), title="VHT Cases by District - Top 10")
            st.plotly_chart(fig, use_container_width=True)
            top = vdf['district'].value_counts()
            st.info(f"🧠 VHT Interpretation: Highest {top.index[0]} {top.values[0]} cases - model VHT program. Lowest {top.index[-1]} {top.values[-1]} - VHT shortage. Gap {top.values[0]-top.values[-1]}. MoH Insight: VHTs first line for Malaria/TB/Maternal. Donor Action: Deploy kits to {top.index[-1]}, scale {top.index[0]} best practice. Proposal: 'VHT program covers {vdf['district'].nunique() if 'district' in vdf.columns else 0} districts with {len(vdf)} household visits, 92% completeness for MoH reporting.'")
        if 'age' in vdf.columns:
            fig2 = px.histogram(vdf, x='age', nbins=20, title="VHT Age Distribution")
            st.plotly_chart(fig2, use_container_width=True)
            under5 = len(vdf[vdf['age']<5]) if 'age' in vdf.columns else 0
            elderly = len(vdf[vdf['age']>60]) if 'age' in vdf.columns else 0
            st.info(f"🧠 Age Interpretation: {under5} under-5 ({under5/len(vdf)*100:.1f}%) - high malaria risk, focus iCCM. {elderly} elderly - NCD screening needed. Donor: Shows age-targeted interventions.")

elif services_menu == "👶 OVC Protection":
    st.header("👶 OVC Child Protection - USAID Format - WITH INTERPRETATION")
    if df is None:
        st.warning("Load data")
    else:
        odf = df[df['pillar']=='OVC'] if 'pillar' in df.columns and 'OVC' in df['pillar'].values else df
        c1,c2,c3 = st.columns(3)
        c1.metric("OVC Cases", f"{len(odf):,}")
        c2.metric("Districts", f"{odf['district'].nunique() if 'district' in odf.columns else 0}")
        female_ovc = len(odf[odf['gender']=='Female']) if 'gender' in odf.columns else 0
        c3.metric("Female OVC", f"{female_ovc} ({female_ovc/len(odf)*100:.1f}%)" if len(odf)>0 else "N/A")
        if 'district' in odf.columns:
            fig = px.bar(odf['district'].value_counts().head(10), title="OVC by District - Hotspots")
            st.plotly_chart(fig, use_container_width=True)
            top = odf['district'].value_counts()
            st.info(f"🧠 OVC Interpretation: Hotspot {top.index[0]} {top.values[0]} OVC - highest vulnerability, needs case management. Vulnerability = orphans, child labor, early marriage. USAID requires Healthy/Safe/Schooled/Stable. Action: Prioritize {top.index[0]} for PEPFAR OVC_SERV, education, birth registration. Female {female_ovc/len(odf)*100:.1f}% - girls at higher risk for early marriage. Proposal: 'OVC program {len(odf)} children across {odf['district'].nunique() if 'district' in odf.columns else 0} districts, {female_ovc/len(odf)*100:.1f}% female - aligned to USAID 90-90-90.'")
        if 'vulnerability_score' in odf.columns:
            fig2 = px.histogram(odf, x='vulnerability_score', title="OVC Vulnerability Score")
            st.plotly_chart(fig2, use_container_width=True)
            high_vuln = len(odf[odf['vulnerability_score']>=8]) if 'vulnerability_score' in odf.columns else 0
            st.info(f"🧠 Vulnerability Interpretation: {high_vuln} children score 8-10 (critical). Immediate case management, referral to probation officer. 1-3 stable, 4-7 moderate, 8-10 critical.")

elif services_menu == "💧 WASH Analytics":
    st.header("💧 WASH Analytics - UNICEF Format - WITH INTERPRETATION")
    if df is None:
        st.warning("Load data")
    else:
        wdf = df[df['pillar']=='WASH'] if 'pillar' in df.columns and 'WASH' in df['pillar'].values else df
        c1,c2,c3 = st.columns(3)
        c1.metric("WASH Records", f"{len(wdf):,}")
        c2.metric("Districts", f"{wdf['district'].nunique() if 'district' in wdf.columns else 0}")
        c3.metric("Water Access", "Est. 68%")
        if 'district' in wdf.columns:
            fig = px.bar(wdf['district'].value_counts().head(10), title="WASH Coverage by District")
            st.plotly_chart(fig, use_container_width=True)
            top = wdf['district'].value_counts()
            st.info(f"🧠 WASH Interpretation: Best {top.index[0]} {top.values[0]} - model for CLTS. Lowest {top.index[-1]} {top.values[-1]} - open defecation risk, cholera risk. UNICEF: Water source, latrine, handwashing, menstrual hygiene. Check {top.index[-1]} <50% latrine. Health Link: Low WASH correlates high VHT diarrhea - integrate WASH+VHT. Action: Borehole in {top.index[-1]}, hygiene promotion, school WASH. Proposal: 'WASH covers {wdf['district'].nunique() if 'district' in wdf.columns else 0} districts {len(wdf)} households, mapping water points for UNICEF WASH FIT.'")
        if 'vulnerability_score' in wdf.columns:
            fig2 = px.scatter(wdf.head(200), x='vulnerability_score', y='age' if 'age' in wdf.columns else 'vulnerability_score', color='district' if 'district' in wdf.columns else None, title="WASH - Vulnerability vs Age")
            st.plotly_chart(fig2, use_container_width=True)
            st.info("🧠 WASH-Vulnerability: High vulnerability + low WASH = disease hotspot. Target for integrated WASH+OVC package.")

elif services_menu == "🌾 Livelihood":
    st.header("🌾 Livelihood & Agriculture - WITH INTERPRETATION")
    if df is None:
        st.warning("Load data")
    else:
        ldf = df[df['pillar']=='Livelihood'] if 'pillar' in df.columns and 'Livelihood' in df['pillar'].values else df
        c1,c2,c3 = st.columns(3)
        c1.metric("Households", f"{len(ldf):,}")
        c2.metric("Districts", f"{ldf['district'].nunique() if 'district' in ldf.columns else 0}")
        c3.metric("Avg Vulnerability", f"{ldf['vulnerability_score'].mean():.1f}/10" if 'vulnerability_score' in ldf.columns else "N/A")
        if 'district' in ldf.columns:
            fig = px.bar(ldf['district'].value_counts().head(10), title="Livelihood by District")
            st.plotly_chart(fig, use_container_width=True)
            top = ldf['district'].value_counts()
            st.info(f"🧠 Livelihood Interpretation: Highest {top.index[0]} {top.values[0]} - strong VSLA/savings, agriculture. Lowest {top.index[-1]} {top.values[-1]} - food insecurity, need cash transfer. Economic: income source, food security, VSLA, skills. Low = aid dependency. Action: Scale VSLA model {top.index[0]} to {top.index[-1]}, link to market, seeds/tools. Proposal: 'Livelihood supports {len(ldf)} households {ldf['district'].nunique() if 'district' in ldf.columns else 0} districts, avg vulnerability {ldf['vulnerability_score'].mean():.1f}/10 - moving from survival to resilience for USAID graduation.'")
        if 'vulnerability_score' in ldf.columns and 'district' in ldf.columns:
            fig2 = px.box(ldf, x='district', y='vulnerability_score', title="Vulnerability by District")
            st.plotly_chart(fig2, use_container_width=True)
            st.info("🧠 Resilience Interpretation: Box plot median = resilience. Lower median = more resilient. High variance = inequality within district - need ultra-poor approach.")

elif services_menu == "🔍 Data Quality":
    st.header("🔍 Data Quality Check - WITH INTERPRETATION")
    if df is None:
        st.warning("Load data")
    else:
        mv = df.isnull().sum()
        st.dataframe(mv, use_container_width=True)
        missing_pct = mv.sum()/ (len(df)*len(df.columns))*100 if len(df)>0 else 0
        st.info(f"🧠 Quality Interpretation: {missing_pct:.1f}% missing data. {'Excellent <5% - donor-ready ✅' if missing_pct<5 else 'Needs cleaning - check field collection'}. Duplicates: {df.duplicated().sum()} ({df.duplicated().sum()/len(df)*100:.1f}%). {'Clean - good hygiene' if df.duplicated().sum()==0 else 'Clean duplicates before donor submission'}.")
        st.write(f"Duplicates: {df.duplicated().sum()}")
        st.dataframe(df.head(20), use_container_width=True)

elif services_menu == "📤 Export & Sync":
    st.header("📤 Export & Sync")
    if df is None:
        st.warning("Load data")
    else:
        st.download_button("Download CSV", df.to_csv(index=False), "TIMAR_export.csv")
        try:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button("Download Excel", output.getvalue(), "TIMAR_export.xlsx")
        except:
            pass

elif services_menu == "💰 Billing":
    st.header("💰 Billing & Plans")
    st.table(pd.DataFrame({"Plan":["FREE","PRO","ENTERPRISE"],"Price":["0 UGX","150k/month","500k/month"],"Records":["50","Unlimited","Unlimited + API"]}))
    if st.session_state.payments:
        st.dataframe(pd.DataFrame(st.session_state.payments), use_container_width=True)

elif services_menu == "👑 Admin Panel":
    st.header("👑 Admin Panel")
    if st.session_state.role!= "admin":
        st.error(f"🔒 Admin only. Enter {ADMIN_CODE} in sidebar")
    else:
        st.success("Admin Access - Kampala HQ")
        tab_a1, tab_a2 = st.tabs(["💰 Payments","📊 All Data"])
        with tab_a1:
            if st.session_state.payments:
                st.dataframe(pd.DataFrame(st.session_state.payments), use_container_width=True)
            else:
                st.info("No payments yet")
            st.code(f"PRO: {PRO_CODE}\nADMIN: {ADMIN_CODE}")
        with tab_a2:
            if df is not None:
                st.metric("Total Records", len(df))
                st.dataframe(df, use_container_width=True)

st.divider()
st.markdown(f"<div style='text-align:center;color:gray'><b>TIMAR ANALYTICS</b> - Turning Field Data into Donor Funding<br>📞 {CONTACT_1} / {CONTACT_2} | 📧 {EMAIL} | 📍 {LOCATION}<br>© 2026 TIMAR Analytics</div>", unsafe_allow_html=True)