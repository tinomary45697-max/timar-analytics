import pandas as pd, numpy as np
np.random.seed(123); n=1000
settlements = {"West Nile":["Bidi Bidi","Imvepi","Rhino Camp","Lobule","Palorinya"],"South West":["Nakivale","Kyaka II","Kyangwali","Rwamwanja","Oruchinga"],"Mid West":["Kiryandongo"],"Central":["Kampala Urban"]}
origins=["South Sudan","DRC","Somalia","Burundi","Rwanda","Eritrea","Ethiopia","Sudan"]
data=[]
for i in range(n):
    region=np.random.choice(list(settlements.keys())); sett=np.random.choice(settlements[region])
    data.append({"ID":340+i,"Case_ID":f"UNHCR-UG-{10000+i}","Region":region,"Settlement":sett,"District":"Yumbe" if sett=="Bidi Bidi" else "Arua","Country_Origin":np.random.choice(origins),"Arrival_Year":int(np.random.randint(2016,2026)),"Years_In_Uganda":2026-int(np.random.randint(2016,2026)),"Gender_HH_Head":np.random.choice(["Female","Male"]),"Age_HH_Head":int(np.random.randint(18,78)),"Education":np.random.choice(["None","Primary","Secondary","University"]),"Household_Size":int(np.random.randint(1,11)),"Children_U18":int(np.random.randint(0,5)),"Vulnerability":np.random.choice(["Woman at Risk","Unaccompanied Child","Elderly","Disability","Single Parent","None"]),"Water_Source":np.random.choice(["Borehole","Tap","River"]),"Irrigation":np.random.choice(["No","Yes"]),"Crop":np.random.choice(["Maize","Beans","Cassava","Vegetables","None"]),"Yield":round(float(np.random.uniform(0.1,3.5)),2),"Assistance_Type":np.random.choice(["Food","Cash","NFI","WASH"]),"Protection_Concern":np.random.choice(["None","GBV Risk","Child Protection","Food Insecurity"]),"Income_UGX_Month":int(np.random.randint(0,500000))})
pd.DataFrame(data).to_csv("UNHCR_Uganda_TIMAR_REAL.csv", index=False)
print("✅ UNHCR REAL file created 1000 rows")