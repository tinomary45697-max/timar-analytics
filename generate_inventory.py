import pandas as pd, numpy as np
np.random.seed(2024); n=1000
categories=["Food","NFI","WASH","Health","Agriculture","Shelter"]
items_map={"Food":["Maize Flour","Beans","Rice","Cooking Oil"],"NFI":["Blanket","Jerrycan","Mosquito Net"],"WASH":["Soap","Water Tank"],"Health":["Malaria Kit","Mama Kit"],"Agriculture":["Maize Seeds","Hoe"],"Shelter":["Cement","Iron Sheets"]}
data=[]
for i in range(n):
    cat=np.random.choice(categories); item=np.random.choice(items_map[cat]); stock=int(np.random.randint(0,5000)); cost=np.random.randint(2000,50000)
    data.append({"ID":340+i,"Item_Code":f"{cat[:3].upper()}-{1000+i}","Region":np.random.choice(["Central","Eastern","Northern","Western"]),"District":np.random.choice(["Kampala","Gulu","Mbarara","Yumbe"]),"Warehouse":f"{cat} Warehouse","Education":np.random.choice(["Primary","Secondary"]),"Category":cat,"Item_Name":item,"Crop":item,"Unit":np.random.choice(["Kg","Pcs","Kit"]),"Water_Source":"Borehole","Irrigation":"No","Stock_On_Hand":stock,"Stock_Reserved":int(stock*0.15),"Stock_Available":int(stock*0.85),"Yield":int(stock*cost/1000),"Unit_Cost_UGX":int(cost),"Total_Value_UGX":int(stock*cost),"Min_Stock_Level":200,"Max_Stock_Level":3000,"Status":"Low" if stock<200 else "Normal","Last_Stock_In":"2024-06-01","Last_Stock_Out":"2024-08-15","Expiry_Date":"2026-02-01" if cat in ["Food","Health"] else "N/A","Donor":np.random.choice(["UNHCR","WFP","UNICEF"]),"Income_UGX":int(stock*cost)})
pd.DataFrame(data).to_csv("Inventory_Uganda_TIMAR_REAL.csv", index=False)
print("✅ Inventory file created 1000 rows")