import pandas as pd, numpy as np
np.random.seed(999); n=1000
regions=["Central","Eastern","Northern","Western","West Nile","South West"]
data=[]
for i in range(n):
    age=int(np.random.randint(8,62)); gender=np.random.choice(["Female","Male"], p=[0.86,0.14])
    gbv="Defilement" if age<18 else np.random.choice(["Physical Assault","Sexual Assault","Domestic Violence","Early Marriage"])
    data.append({"ID":340+i,"Case_ID":f"GBV-UG-{10000+i}","Region":np.random.choice(regions),"District":np.random.choice(["Kampala","Gulu","Mbarara","Mbale"]),"Settlement":np.random.choice(["Host Community","Bidi Bidi","Nakivale"]),"Education":np.random.choice(["None","Primary","Secondary"]),"Gender":gender,"Age":age,"Age_Group":"0-17" if age<18 else "18-35","Marital_Status":np.random.choice(["Single","Married"]),"GBV_Type":gbv,"Perpetrator":np.random.choice(["Intimate Partner","Family Member","Stranger"]),"Location_Incident":np.random.choice(["Home","Water Point","School","Field"]),"Yield":1,"Water_Source":np.random.choice(["Borehole","Tap"]),"Irrigation":"No","Crop":"N/A","Reported":np.random.choice(["Yes","No"], p=[0.38,0.62]),"Reported_Within_72H":np.random.choice(["Yes","No"]),"Service_Sought":np.random.choice(["Health","Psychosocial","Legal"]),"Service_Provided":np.random.choice(["Yes","No"]),"Referral_Made":np.random.choice(["Health","Police"]),"Risk_Level":np.random.choice(["Low","Medium","High"]),"Repeat_Case":np.random.choice(["Yes","No"]),"Month":np.random.choice(["Jan","Feb","Mar"]),"Year":2024,"Income_UGX":int(np.random.randint(0,800000))})
pd.DataFrame(data).to_csv("GBV_Uganda_TIMAR_REAL.csv", index=False)
print("✅ GBV file created 1000 rows")