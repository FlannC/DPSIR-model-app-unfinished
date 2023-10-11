import pandas as pd
import plotly.express as px

from os import listdir
from os.path import isfile, join

from dash import *

def import_gdf(filename, folderPath = 'Addresses/'):

    df = pd.read_csv(f'{folderPath}{filename}', sep=';', header = None)
    df.columns = ['name', 'nCommuters', 'vacancies', 'newHomes', 'nIn', 'nOut', 'rent', 'lon', 'lat']
    df = df.sort_values(by='nIn', ignore_index=True)

    # Convert df with lat lon to gdf
    # geom = [Point(xy) for xy in zip(df.lon, df.lat)]
    # df = df.drop(columns= ['lon', 'lat'])
    # outgdf = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geom)

    # Version without gpd
    outgdf = df

    return outgdf

def build_gdb(folderPath = 'Addresses/'):

    onlyfiles = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]

    start = "Addresses"
    end = ".txt"
    dictgdf = {}
    for f in onlyfiles:
        n = int( f[len(start):-len(end)] )
        dictgdf[n] = import_gdf(f, folderPath)

    sortedgdb = dict(sorted(dictgdf.items()))
    return sortedgdb


addressesGDB = build_gdb()
nCycles = len(addressesGDB)

# Initialize the app
myapp = Dash(__name__)
app = myapp.server

# App layout
myapp.layout = html.Div([
    html.Div(children='Select a cycle number on the numberline or the input cell below.'),
    html.Hr(),
    dcc.Slider(min=0, max=nCycles-1, step=1, value=0, id='cycle-slider'),
    html.Div(dcc.Input(id='input-cycle', type='number', placeholder=0)),
    dcc.Graph(figure={}, id='map'),
    
    html.Div(children='Select which attribute to represent by which symbology feature.'),
    html.Hr(),
    html.Div([
        html.Label('Circle size', style={'padding-right': '62px'}),
        html.Label('Circle color')
    ]),
    dcc.RadioItems(options=['nCommuters', 'vacancies', 'newHomes', 'nIn', 'nOut', 'rent'], value='nCommuters', id='size-radio', style={'display': 'inline-block', 'padding-right':'28px'}),
    dcc.RadioItems(options=['nCommuters', 'vacancies', 'newHomes', 'nIn', 'nOut', 'rent'], value='nIn', id='color-radio', style={'display': 'inline-block'})
])

# Interactive map
@callback(
    Output(component_id='map', component_property='figure'),
    Input(component_id='cycle-slider', component_property='value'),
    Input('size-radio', 'value'),
    Input('color-radio', 'value')
)
def update_graph(cycleNo, sizefield, colorfield):    
    gdf = addressesGDB[cycleNo]
    fig = px.scatter_mapbox(gdf, lat= gdf.lat, lon= gdf.lon, color= colorfield, size= sizefield, zoom= 11)
    fig.update_layout(mapbox_style="open-street-map")
    return fig


@callback(
    Output('cycle-slider', 'value'),
    Input('input-cycle', 'value')
)
def matchSliderToInput(n):
    if n is not None:
        return n
    else:
        return 0
    

@callback(
    Output('input-cycle', 'value'),
    Input('cycle-slider', 'value') 
)
def matchInputToSlider(n):
    if n is not None:
        return n
    else:
        return 0

# Run the app
if __name__ == '__main__':
    myapp.run(debug=True)

