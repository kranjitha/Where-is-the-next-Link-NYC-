import json
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from plotly import graph_objs as go
import plotly.express as px


from math import sin, cos, sqrt, atan2, radians
from math import radians, cos, sin, asin, sqrt


from location_finder import *

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.css.append_css({
    "external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"
})



ret_fig = []

### token for mapbox dark theme
token = open("C:\workspace\school\Courses\Data Science for Smart cities\Project\dash\data\mapbox_token").read() # you will need your own token

### reading in pay phone location_df and house df
hou_df = pd.read_csv(r'C:\workspace\school\Courses\Data Science for Smart cities\Project\dash\data\housing.csv')
fig_temp = px.bar()

df = pd.read_pickle("C:\workspace\school\Courses\Data Science for Smart cities\Project\dash\data\payphone.pkl")


df.number_of_phones = df.number_of_phones.astype(float)
df.latitude = df.latitude.astype(float)
df.longitude = df.longitude.astype(float)


## plotting payphones by borough
fig_fix = px.scatter_mapbox(df, lat="latitude", lon="longitude", 
                        hover_name="street_name", hover_data=["company_name"],
                        color_discrete_sequence=px.colors.qualitative.Plotly, 
                        color = "borough", zoom=9)


fig_fix.update_layout(mapbox_style="dark", mapbox_accesstoken=token, 
                    mapbox = dict(
                                center=dict(
                                lat=40.730610,
                                lon=-73.835242
                                )
                            )
                        )

fig_fix.update_layout(
            legend=dict(
            x=0,
            y=1,
            traceorder="normal",
            font=dict(
                family="sans-serif",
                size=12,
                color="black"
            ),
            bgcolor="LightSteelBlue",
            bordercolor="Black",
            borderwidth=2)
    )

fig_fix.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

fig_fix.layout.dragmode = "select"


################################### Layout of the dash app ######################################


app.layout = html.Div([

        html.Div([

            #one column margin
            html.Div([
            ], className = "one columns" ),
            
            html.Div([
                html.H3("Where is the next LinkNYC?"), 
            ], className = "six columns"),

            html.Div([
                html.Label(
                    [
                        "Multi dynamic Dropdown",
                        dcc.Dropdown(id="my-multi-dynamic-dropdown"),
                    ]
                )

            ], className = "five columns")
            
        ], className = "row"),


        html.Div([

             html.Div([], className = "one columns" ),
            
            html.Div([
                html.P("Wondering what could be the best places to replace payphone booths with link NYC? drag the area on map to see it yourself! This process might take a few seconds.. Hang in there!! We are trying our best to enhance your experience")

            ], className = "six columns"),


            html.Div([
            html.Label
            (
                [
                    "Input val",
            dcc.Input(
                id="k-val",
                type="number",
                placeholder="Select no of locations")
                ]
            )

            ], className = "two columns"),

            html.Div([
                html.Label(
                    [
                        "Multi dynamic Dropdown",
                        dcc.Dropdown(id="my-multi-amic-dropdown", multi=True),
                    ]
                )

            ], className = "three columns")
                        
        ], className = "row"),


        html.Div([
            
            html.Div([], className = "one columns" ),

            html.Div([
                dcc.Graph(id = "First", figure = fig_fix, )
            ], className = "six columns"),


            html.Div([], className = "one columns" ),

            html.Div([
                dcc.Graph(id = "second", figure = fig_temp )
            ], className = "five columns")


        ], id = 'op1', className = "row"),


html.Div(id = "op")

])

###############################function to wrap figures in html Divs#########################################
def return_div(fig1, fig2):

    
    return html.Div([

                html.Div([

                    html.Div([], className = "one columns" ),

                    html.Div([
                        dcc.Graph(id = "First", figure = fig1 )
                    ], className = "six columns"),


                    html.Div([], className = "one columns" ),

                        html.Div([
                            dcc.Graph(id = "second", figure = fig2 )
                        ], className = "five columns")

                    ], className = "row")
                ])



#################################### call back ####################################################################

@app.callback(

    Output('op1','children'),
    [Input('First', 'selectedData')])
def display_relayout_data(selectedData):

    out = []
    data = []


    if selectedData is None:
        return return_div(fig_fix, fig_temp)



    points = selectedData["points"]


    if len(points) == 0:
        return return_div(fig_fix, fig_temp)

    

    for n, point in enumerate(points):

        data.append((point["lat"], point["lon"]))


    sub_ph = pd.DataFrame(data, columns = ["latitude", "longitude"])

    print(sub_ph.latitude.dtype)
    # sub_ph["latitude"] = sub_ph["latitude"].astype(float)
    # sub_ph['longitude'] = sub_ph["longitude"].astype(float)

    
    sub_hou = hou_df[["Latitude",
    'Longitude',
    "Low Income Units",
    "Very Low Income Units", 
    "Extremely Low Income Units"]].reset_index(drop = True)


    k = min(10, len(points))
    loc_df = k_location_query(sub_ph, sub_hou, k)

    sub_hou = sub_hou.dropna()

    print(loc_df.dtypes)

    loc_df.latitude = loc_df.latitude.astype(float)


    # fig_abc = fig_fix
    # fig_abc.update_layout(zoom = 12)
    #return json.dumps(selectedData["points"][0]["lon"], indent = 2)

    fig = px.scatter_mapbox(loc_df, lat="latitude", lon="longitude",  size = "no_of_low_inc_units",  
                             zoom=9
                             )

    fig.update_layout(mapbox_style="dark", 
                    mapbox_accesstoken=token,
                    mapbox = dict(
                        center=dict(
                    lat=40.730610,
                    lon=-73.835242
            )
                    ),

                    

    )




    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})



    fig2 = px.bar(loc_df, y='no_of_low_inc_units')

    out.append(fig)
    out.append(fig2)

    return return_div(fig,fig2)





if __name__ == '__main__':
    app.run_server(debug = True)