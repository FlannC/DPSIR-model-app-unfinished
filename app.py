import pandas as pd
import plotly.express as px

from os import listdir
from os.path import isfile, join

from dash import *

def import_gdf(filename, folderPath = 'Addresses/'):

    df = pd.read_csv(f'{folderPath}{filename}', sep=';', header = None)
    df.columns = ['name', 'nCommuters', 'vacancies', 'newHomes', 'nIn', 'nOut', 'rent', 'lon', 'lat']
    outdf = df.sort_values(by='nIn', ignore_index=True)

    return outdf

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

def merge_all_cycles(ingdb):
    for i in ingdb:
        gdf = ingdb[i]
        gdf['cycleNo'] = i
        if i == 0:
            outgdf = gdf
        else:
            outgdf = pd.concat([outgdf, gdf], ignore_index=True)
    
    return outgdf


addressesGDB = build_gdb()
nCycles = len(addressesGDB)
allCyclesGDF = merge_all_cycles(addressesGDB)

# Initialize the app
myapp = Dash(__name__)
app = myapp.server

# App layout
myapp.layout = html.Div([
    html.Div(children='Select a cycle number on the numberline or the input cell below.', style={'padding-bottom':'16px'}),
    dcc.Slider(min=0, max=nCycles-1, step=1, value=0, marks= {i:str(i) if i%(round(nCycles/200)*10) == 0 else '' for i in range(nCycles)}, id='cycle-slider'),
    html.Div(dcc.Input(id='input-cycle', type='number', placeholder=0, style= {'margin-bottom': '16px'})),
    html.Hr(),
    html.Div(children='Select which attribute to represent by which symbology feature.'),
    html.Div([
        html.Div([
            html.Div([
                html.Div(
                    html.Label(html.B('Circle size')), style = {'padding-bottom': '6px'}
                ),                
                dcc.RadioItems(options=['nCommuters', 'vacancies', 'newHomes', 'nIn', 'nOut', 'rent'], value='nCommuters', id='size-radio')
            ], style= {'padding-right':'20px'}),
            html.Div([
                html.Div(
                    html.Label(html.B('Circle color')), style = {'padding-bottom': '6px'}
                ),   
                dcc.RadioItems(options=['nCommuters', 'vacancies', 'newHomes', 'nIn', 'nOut', 'rent'], value='nIn', id='color-radio')
            ])
            
        ], style= {'display':'flex', 'padding-top': '100px'}),
        html.Div(
            dcc.Graph(figure={}, id='map')
        )
    ], style= {'display':'flex'}),
    html.Hr(),
    html.Div(children='Click on an address on the map and select which attribute to plot on the y axis.'),
    html.Div([
        html.Div(
            dcc.RadioItems(options=['nCommuters', 'vacancies', 'newHomes', 'nIn', 'nOut'], value='nCommuters', id='plot-radio'),    
            style={'display': 'inline-block', 'padding-top': '100px'}
        ),
        html.Div(
        dcc.Graph(figure={}, id='plot', style= {'margin': '0px'}),
        style={'display': 'inline-block'}
        )
    ], style= {'display':'flex'})
])


# Interactive map
@callback(
    Output(component_id='map', component_property='figure'),
    Input(component_id='cycle-slider', component_property='value'),
    Input('size-radio', 'value'),
    Input('color-radio', 'value')
)
def update_map(cycleNo, sizefield, colorfield):    
    gdf = addressesGDB[cycleNo]
    fig_map = px.scatter_mapbox(gdf, lat= gdf.lat, lon= gdf.lon, hover_name='name', color= colorfield, size= sizefield, zoom= 11)
    fig_map.update_layout(mapbox_style="open-street-map")
    return fig_map

# Interactive plot
@callback(
    Output(component_id='plot', component_property='figure'),    
    Input('plot-radio', 'value'),
    Input('map', 'clickData')
)
def update_plot(yfield, clickdata):
    address = clickdata['points'][0]['hovertext']
    xdata = allCyclesGDF[allCyclesGDF.name == address]['cycleNo']
    ydata = allCyclesGDF[allCyclesGDF.name == address][yfield]
    rent = allCyclesGDF[allCyclesGDF.name == address]['rent'].reset_index(drop=True)[0]
    n= address[9:]

    fig_plot = px.scatter(x= xdata, y=ydata, title=f'Graph of {yfield} for address number {n}, rent is {rent}.')
    fig_plot.update_traces(mode='lines+markers')

    fig_plot.update_xaxes(title= "Cycle") 
    fig_plot.update_yaxes(title= yfield)
    fig_plot.update() 

    return fig_plot



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

