import pandas as pd, numpy as np
np.random.seed(777); n=1000
regions=["Central","Eastern","Northern","Western"]
livelihoods=["Subsistence Farming","Commercial Farming","Casual Labor","Small Business","Salaried Employment","Livestock","Fishing","Boda Boda","Construction","Charcoal Burning"]
data=[]
for i in range(n):
    reg=np.random.choice(regions); liv=np.random.choice(livelihoods)
    inc=800000 if liv=="Salaried Employment" else 150000
    if liv=="Salaried Employment": inc=np.random.randint(800000,4000000)
    elif liv=="Commercial Farming": inc=np.random.randint(500000,3000000)
    elif liv=="Subsistence Farming": inc=np.random.randint(80000,600000)
    else: inc=np.random.randint(100000,900000)
    y=round(float(np.random.uniform(0.5,6.5)),2) if "Farming" in liv else 0.5
    data.append({"ID":340+i,"Region":reg,"District":np.random.choice(["Kampala","Gulu","Mbarara","Mbale"]),"Education":np.random.choice(["None","Primary","Secondary","University"]),"Gender_HH_Head":np.random.choice(["Male","Female"]),"Age_HH_Head":int(np.random.randint(19,75)),"Household_Size":int(np.random.randint(2,11)),"Dependents":int(np.random.randint(0,5)),"Livelihood_Main":liv,"Livelihood_Secondary":np.random.choice(livelihoods),"Crop":np.random.choice(["Maize","Beans","Coffee"]),"Yield":y,"Farm_Size_Acres":round(float(np.random.uniform(0.2,6)),1),"Water_Source":np.random.choice(["Rain","Borehole"]),"Irrigation":np.random.choice(["No","Yes"]),"Livestock_TLU":round(float(np.random.uniform(0,8)),1),"Food_Insecurity_Score":int(np.random.randint(0,11)),"Food_Consumption_Score":int(np.random.randint(21,112)),"Months_Food_Secure":int(np.random.randint(2,13)),"Coping_Strategy_Index":int(np.random.randint(0,35)),"Savings_UGX":int(np.random.randint(0,1000000)),"Loan_UGX":int(np.random.randint(0,500000)),"Income_UGX":int(inc),"Expenditure_Food_Pct":int(np.random.randint(35,85)),"Shocks_Last_Year":np.random.choice(["None","Drought","Flood","Price Rise"]),"Assistance_Received":np.random.choice(["None","Cash","Food"])})
pd.DataFrame(data).to_csv("Livelihood_Uganda_TIMAR_REAL.csv", index=False)
print("✅ Livelihood file created 1000 rows")