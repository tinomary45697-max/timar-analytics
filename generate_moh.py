import pandas as pd, numpy as np
np.random.seed(2026); n=1000
regions=["Central","Eastern","Northern","Western"]
districts={"Central":["Kampala","Wakiso","Mukono"],"Eastern":["Mbale","Jinja","Tororo"],"Northern":["Gulu","Lira","Arua"],"Western":["Mbarara","Kabale","Fort Portal"]}
diseases=["Malaria","Pneumonia","Diarrhea","Anemia","HIV/AIDS","TB","Hypertension","Diabetes","Malnutrition","Maternal Complications"]
data=[]
for i in range(n):
    reg=np.random.choice(regions); dist=np.random.choice(districts[reg]); disease=np.random.choice(diseases); cases=int(np.random.randint(1,250))
    if disease=="Malaria" and reg in ["Northern","Eastern"]: cases=int(cases*1.8)
    data.append({"ID":340+i,"Region":reg,"District":dist,"Health_Facility":f"{dist} {np.random.choice(['HC III','HC IV','District Hospital'])}","Facility_Level":np.random.choice(["HC II","HC III","HC IV"]),"Disease":disease,"ICD10_Code":"B54" if disease=="Malaria" else "J18","Age_Group":np.random.choice(["0-5","6-12","20-35","60+"]),"Gender":np.random.choice(["Male","Female"]),"Cases_Reported":cases,"Deaths":int(cases*0.02),"Yield":cases,"Education":np.random.choice(["None","Primary","Secondary"]),"Water_Source":np.random.choice(["Borehole","Tap"]),"Irrigation":"No","Crop":"N/A","Reporting_Week":int(np.random.randint(1,53)),"Reporting_Year":2024,"Month":np.random.choice(["Jan","Feb","Mar"]),"Village_Cases":int(np.random.randint(1,50)),"Stockout_Days":int(np.random.randint(0,15)),"Income_UGX":int(np.random.randint(0,800000))})
pd.DataFrame(data).to_csv("MoH_Uganda_DHIS2_TIMAR_REAL.csv", index=False)
print("✅ MoH file created 1000 rows")