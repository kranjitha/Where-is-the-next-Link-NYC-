from math import sin, cos, sqrt, atan2, radians
from math import radians, cos, sin, asin, sqrt
import pandas as pd 
import numpy as np


def haversine(lon1, lat1, lon2, lat2):
  # convert decimal degrees to radians 
  lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
 
  # haversine formula 
  dlon = lon2 - lon1 
  dlat = lat2 - lat1 
  a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
  c = 2 * asin(sqrt(a)) 
  r = 6371 # Radius of earth in kilometers. Use 3956 for miles
  return c * r

def count_units(df, ind_excluded):
    return np.sum(df[~df.index.isin(ind_excluded)].values)
    
def find_best_loc(sub_ph, sub_hou, hou_ind, ph_ind):

    sub_ph["no_of_low_inc_units"] = sub_ph[~sub_ph.index.isin(ph_ind)]["Data frames"].apply(
                                    lambda x : count_units(x,hou_ind  ))


    #if sub_ph[~sub_ph.index.isin(ph_ind)]["count"] is not empty():
    ind = sub_ph[~sub_ph.index.isin(ph_ind)]["no_of_low_inc_units"].idxmax()

    ph_ind = np.union1d(ph_ind, ind)



    # no_units = np.sum(sub_hou[["Low Income Units","Very Low Income Units",
    #                    "Extremely Low Income Units"]][sub_hou.index.isin(np.setdiff1d(sub_ph.loc[ind,:]["indices"], hou_ind))].values)


    hou_ind = np.union1d(hou_ind, sub_ph.loc[ind,"Data frames"].index)

    lat = float(sub_ph["latitude"].loc[ind])
    lon = float(sub_ph["longitude"].loc[ind])
    no_units = float(sub_ph["no_of_low_inc_units"].loc[ind])

    return hou_ind, ph_ind, (lat, lon, no_units)

    
def k_location_query(sub_ph, sub_hou, k):

    R = 6373.0
    index_list = []
    hou_ind = np.array([])
    ph_ind = np.array([])
    res = []


    
    sub_ph[["latitude", "longitude"]] = sub_ph[["latitude", "longitude"]].astype(float)

    for val in sub_ph.values:

        dict_low_inc = {}

        lat = val[0]
        lon = val[1]

        f = np.vectorize(haversine)

        distances = f(lon, lat , sub_hou["Longitude"], 
                        sub_hou["Latitude"])

        

        print(distances)

        

        indices = np.argwhere(distances <= 0.2)
        print(indices)
        indices = indices.reshape(-1,)

        sub_df = sub_hou[sub_hou.index.isin(indices)]

        no_units = sub_df["Low Income Units"] + sub_df["Very Low Income Units"] + sub_df["Extremely Low Income Units"]

        





        index_list.append(no_units)

    sub_ph["Data frames"] = index_list






    while(k>0):
        print(k)

        hou_ind, ph_ind, no = find_best_loc(sub_ph, sub_hou, hou_ind, ph_ind)

        res.append(no)

        k = k-1


    location_df = pd.DataFrame(data = res, columns = ["latitude","longitude", "no_of_low_inc_units"])
    return location_df

if __name__ == "__main__":

    phone_df = pd.read_pickle("C:\workspace\school\Courses\Data Science for Smart cities\Project\df.pkl")
    hou_df = pd.read_csv(r'C:\workspace\school\Courses\Data Science for Smart cities\Project\housing.csv')


    new_hou_df = hou_df.dropna(how='any', subset=['Latitude', 'Longitude'])
    sub_hou = new_hou_df[["Latitude",'Longitude',"Low Income Units","Very Low Income Units", "Extremely Low Income Units"]].reset_index(drop = True)

    sub_ph = phone_df[["latitude", "longitude"]].reset_index(drop = True)


    loc_df = k_location_query(sub_ph, sub_hou, 10)
    print(loc_df)













        
