import pandas as pd, numpy as np
np.random.seed(111); n=1000
sectors=["Food Security","WASH","Health","Protection","Education","Livelihood"]
data=[]
for i in range(n):
    sector=np.random.choice(sectors); target=float(np.random.uniform(50,95)); achieved=target*np.random.uniform(0.55,1.25)
    yield_val=round(achieved/target*100,1)
    status="Achieved" if yield_val>=100 else "On Track" if yield_val>=80 else "At Risk" if yield_val>=50 else "Off Track"
    data.append({"ID":340+i,"Project_Code":f"UG-2024-{1000+i}","Region":np.random.choice(["Central","Eastern","Northern","Western"]),"District":np.random.choice(["Kampala","Gulu","Mbarara"]),"Education":np.random.choice(["None","Primary","Secondary"]),"Sector":sector,"Indicator":np.random.choice(["% HH with Improved Water","% HH with Latrine","% Children Immunized"]),"Indicator_Type":np.random.choice(["Outcome","Output"]),"Crop":sector,"Water_Source":"Borehole","Irrigation":"No","Baseline":round(target*0.6,1),"Target":round(target,1),"Achieved":round(achieved,1),"Yield":yield_val,"Variance":round(achieved-target,1),"Achievement_Status":status,"Reporting_Period":np.random.choice(["Q1 2024","Q2 2024"]),"Month":"Jan","Year":2024,"Beneficiaries_Target":int(np.random.randint(500,20000)),"Beneficiaries_Reached":int(np.random.randint(300,22000)),"Budget_UGX":int(np.random.randint(5000000,200000000)),"Expenditure_UGX":int(np.random.randint(3000000,180000000)),"Donor":np.random.choice(["USAID","EU","UNHCR"]),"Implementing_Partner":np.random.choice(["World Vision","IRC","DRC"]),"Income_UGX":int(np.random.randint(100000,2000000))})
pd.DataFrame(data).to_csv("ME_Uganda_TIMAR_REAL.csv", index=False)
print("✅ M&E file created 1000 rows")