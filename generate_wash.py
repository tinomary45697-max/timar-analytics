import pandas as pd, numpy as np
np.random.seed(555); n=1000
regions=["Central","Eastern","Northern","Western"]
districts={"Central":["Kampala","Wakiso"],"Eastern":["Mbale","Jinja"],"Northern":["Gulu","Arua","Moroto"],"Western":["Mbarara","Kabale"]}
data=[]
for i in range(n):
    reg=np.random.choice(regions); dist=np.random.choice(districts[reg])
    ws=np.random.choice(["Borehole","Protected Spring","Tap/Piped","Unprotected Well","River/Lake"]
    lpcd=round(float(np.random.uniform(5,35)),1) if ws in ["Borehole","Tap/Piped"] else round(float(np.random.uniform(2,15)),1)
    data.append({"ID":340+i,"Region":reg,"District":dist,"Sub_County":f"{dist} Central","Village":f"Village {np.random.randint(1,50)}","Education":np.random.choice(["None","Primary","Secondary"]),"Water_Source":ws,"Water_Source_Improved":"Yes" if ws in ["Borehole","Protected Spring","Tap/Piped"] else "No","Distance_to_Source_M":int(np.random.randint(50,3000)),"Time_to_Source_Min":int(np.random.randint(5,45)),"Yield":lpcd,"Jerrycans_Per_Day":int(np.random.randint(2,10)),"Irrigation":np.random.choice(["No","Yes"]),"Crop":np.random.choice(["Maize","Beans"]),"Sanitation_Type":np.random.choice(["VIP Latrine","Traditional Latrine","Open Defecation"]),"Open_Defecation_Free":np.random.choice(["Yes","No"]),"Handwashing_Facility":np.random.choice(["Yes with Soap","No Facility"]),"Water_Treatment":np.random.choice(["Boiling","None"]),"Functionality":np.random.choice(["Functional","Non-Functional"]),"Management_Type":np.random.choice(["WUC","Private Operator"]),"Household_Size":int(np.random.randint(2,12)),"Monthly_Water_Cost_UGX":int(np.random.randint(0,20000)),"Diarrhea_Cases_Last_Month":int(np.random.randint(0,5)),"Income_UGX":int(np.random.randint(100000,1500000))})
pd.DataFrame(data).to_csv("WASH_Uganda_MWE_TIMAR_REAL.csv", index=False)
print("✅ WASH file created 1000 rows")