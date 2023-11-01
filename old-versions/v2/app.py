import pandas as pd
import plotly.express as px

from os import listdir
from os.path import isfile, join

from dash import *

def import_gdf(filename: str, folderPath: str, cols: list, sortby: str):

    df = pd.read_csv(f'{folderPath}{filename}', sep=';', header = None)
    df.columns = cols
    outdf = df.sort_values(by=sortby, ignore_index=True)

    return outdf

def build_gdb(folderPath: str, start: str, cols: list, sortby: str):

    onlyfiles = [f for f in listdir(folderPath) if isfile(join(folderPath, f))]

    end = ".txt"
    dictgdf = {}
    for f in onlyfiles:
        n = int( f[len(start):-len(end)] )
        dictgdf[n] = import_gdf(f, folderPath, cols, sortby)

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

addressesCols = ['name', 'nCommuters', 'vacancies', 'newHomes', 'nIn', 'nOut', 'rent', 'lon', 'lat']
commutersCols = ['name', 'home', 'jobPlace', 'maxRent', 'travelTime', 'happy', 'patience', 'initialPatience', 'homeLon', 'homeLat']
addressesGDB = build_gdb('Addresses/', 'Addresses', addressesCols, 'nIn')
commutersGDB = build_gdb('Commuters/', 'Commuters', commutersCols, 'travelTime')
nCycles = len(addressesGDB)
allCyclesAddressesGDF = merge_all_cycles(addressesGDB)
allCyclesCommutersGDF = merge_all_cycles(commutersGDB)



# Initialize the app
myapp = Dash(__name__)
myapp.title = 'DPSIR model'
app = myapp.server

# App layout
myapp.layout = html.Div([
    html.Div(children='Select a cycle number on the numberline or the input cell below.', style={'padding-bottom':'16px'}),
    # dcc.Slider(min=0, max=nCycles-1, step=1, value=0, marks= {i:str(i) if i%(round(nCycles/200)*10) == 0 else '' for i in range(nCycles)}, id='cycle-slider'),
    dcc.Slider(min=0, max=nCycles-1, step=1, value=0, id='cycle-slider'),
    html.Div(dcc.Input(id='input-cycle', type='number', placeholder=0, style= {'margin-bottom': '16px'})),
    html.Hr(),
    html.Div(children='Select which attribute to represent by which symbology feature - Addresses.'),
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
    ], style= {'display':'flex'}),

    html.Hr(),
    html.Div(children="Select attribute to plot its means' time series on the y axis."),
    html.Div([
        html.Div(
            dcc.RadioItems(options=['nCommuters', 'vacancies', 'newHomes', 'nIn', 'nOut'], value='nIn', id='means-radio-a'),    
            style={'display': 'inline-block', 'padding-top': '100px'}
        ),
        html.Div(
        dcc.Graph(figure={}, id='means-a', style= {'margin': '0px'}),
        style={'display': 'inline-block'}
        )
    ], style= {'display':'flex'}),
    
    html.Hr(),
    html.Hr(),

    html.Div(children='Select which attribute to represent by which symbology feature - Commuters.'),
    html.Div([
        html.Div([
            html.Div([
                html.Div(
                    html.Label(html.B('Circle size')), style = {'padding-bottom': '6px'}
                ),                
                dcc.RadioItems(options=['maxRent', 'travelTime', 'patience'], value='maxRent', id='size-radio-c')
            ], style= {'padding-right':'20px'}),
            html.Div([
                html.Div(
                    html.Label(html.B('Circle color')), style = {'padding-bottom': '6px'}
                ),   
                dcc.RadioItems(options=['maxRent', 'travelTime', 'happy', 'patience'], value='travelTime', id='color-radio-c')
            ])
            
        ], style= {'display':'flex', 'padding-top': '100px'}),
        html.Div(
            dcc.Graph(figure={}, id='map-c')
        )
    ], style= {'display':'flex'}),
    html.Hr(),
    html.Div(children='Click on a commuter on the map and select which attribute to plot on the y axis.'),
    html.Div([
        html.Div(
            dcc.RadioItems(options=['travelTime', 'happy', 'patience'], value='travelTime', id='plot-radio-c'),    
            style={'display': 'inline-block', 'padding-top': '100px'}
        ),
        html.Div(
        dcc.Graph(figure={}, id='plot-c', style= {'margin': '0px'}),
        style={'display': 'inline-block'}
        )
    ], style= {'display':'flex'}),

    html.Hr(),
    html.Div(children="Select attribute to plot its means' time series on the y axis."),
    html.Div([
        html.Div(
            dcc.RadioItems(options=['travelTime', 'happy', 'patience'], value='travelTime', id='means-radio-c'),    
            style={'display': 'inline-block', 'padding-top': '100px'}
        ),
        html.Div(
        dcc.Graph(figure={}, id='means-c', style= {'margin': '0px'}),
        style={'display': 'inline-block'}
        )
    ], style= {'display':'flex'})

])


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


# Interactive map for addresses
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

# Interactive plot for addresses 
@callback(
    Output(component_id='plot', component_property='figure'),    
    Input('plot-radio', 'value'),
    Input('map', 'clickData')
)
def update_plot(yfield, clickdata):
    address = clickdata['points'][0]['hovertext']
    xdata = allCyclesAddressesGDF[allCyclesAddressesGDF.name == address]['cycleNo']
    ydata = allCyclesAddressesGDF[allCyclesAddressesGDF.name == address][yfield]
    rent = allCyclesAddressesGDF[allCyclesAddressesGDF.name == address]['rent'].reset_index(drop=True)[0]
    n= address[9:]

    fig_plot = px.scatter(x= xdata, y=ydata, title=f'Graph of {yfield} for address number {n}, rent is {rent}.')
    fig_plot.update_traces(mode='lines+markers')

    fig_plot.update_xaxes(title= "Cycle") 
    fig_plot.update_yaxes(title= yfield)
    fig_plot.update() 

    return fig_plot

# Interactive means time series for addresses 
@callback(
    Output(component_id='means-a', component_property='figure'),    
    Input('means-radio-a', 'value'),
)
def update_means(yfield):
    xdata = allCyclesAddressesGDF['cycleNo'].unique()
    ydata = allCyclesAddressesGDF.groupby(['cycleNo']).mean()[yfield]

    fig_plot = px.scatter(x= xdata, y=ydata, title=f'Graph of mean of {yfield} for all addresses.')
    fig_plot.update_traces(mode='lines+markers')

    fig_plot.update_xaxes(title= "Cycle") 
    fig_plot.update_yaxes(title= f'Mean of {yfield}')
    fig_plot.update() 

    return fig_plot



# Interactive map for commuters
@callback(
    Output(component_id='map-c', component_property='figure'),
    Input(component_id='cycle-slider', component_property='value'),
    Input('size-radio-c', 'value'),
    Input('color-radio-c', 'value')
)
def update_map(cycleNo, sizefield, colorfield):    
    gdf = commutersGDB[cycleNo]
    fig_map = px.scatter_mapbox(gdf, lat= gdf.homeLat, lon= gdf.homeLon, hover_name='name', color= colorfield, zoom= 11)
    fig_map.update_layout(mapbox_style="open-street-map")
    return fig_map

# Interactive plot for commuters 
@callback(
    Output(component_id='plot-c', component_property='figure'),    
    Input('plot-radio-c', 'value'),
    Input('map-c', 'clickData')
)
def update_plot(yfield, clickdata):
    commuter = clickdata['points'][0]['hovertext']
    xdata = allCyclesCommutersGDF[allCyclesCommutersGDF.name == commuter]['cycleNo']
    ydata = allCyclesCommutersGDF[allCyclesCommutersGDF.name == commuter][yfield]
    maxRent = allCyclesCommutersGDF[allCyclesCommutersGDF.name == commuter]['maxRent'].reset_index(drop=True)[0]
    n= commuter[10:]

    fig_plot = px.scatter(x= xdata, y=ydata, title=f'Graph of {yfield} for commuter number {n}, rent is {maxRent}.')
    fig_plot.update_traces(mode='lines+markers')

    fig_plot.update_xaxes(title= "Cycle") 
    fig_plot.update_yaxes(title= yfield)
    fig_plot.update() 

    return fig_plot

# Interactive means time series for commuters 
@callback(
    Output(component_id='means-c', component_property='figure'),    
    Input('means-radio-c', 'value'),
)
def update_means(yfield):
    xdata = allCyclesCommutersGDF['cycleNo'].unique()
    ydata = allCyclesCommutersGDF.groupby(['cycleNo']).mean()[yfield]

    fig_plot = px.scatter(x= xdata, y=ydata, title=f'Graph of mean of {yfield} for all commuters.')
    fig_plot.update_traces(mode='lines+markers')

    fig_plot.update_xaxes(title= "Cycle") 
    fig_plot.update_yaxes(title= f'Mean of {yfield}')
    fig_plot.update() 

    return fig_plot




# Run the app
if __name__ == '__main__':
    myapp.run(debug=True)

