import dash
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import numpy as np
import pandas as pd

# Get data
start = np.datetime64('2015-01-01')
end = np.datetime64('2019-07-25')
startdt = start.astype('datetime64[ns]')
enddt = end.astype('datetime64[ns]')
terms = [1,12,24,36,48,60]
def generatedata(term):
    shock = np.random.randint(10,20)
    date_rng = np.arange(start,end)
    df = pd.DataFrame(date_rng, columns=['Date'])
    df['Rate'] = np.random.randint(0,100,size=(len(date_rng)))
    df['Shocked'] = df['Rate']+shock
    # simulate 10% days missing
    df = df.sample(frac=0.8)
    df=df.sort_values(by='Date')
    df['Term']=term
    return df
def generatedata_loop(terms):
    return pd.concat(generatedata(t) for t in terms).sort_values(by=['Term','Date'])
curves = ['CurveA','CurveB','CurveC'] # 3 curves worth of data
data = {x:generatedata_loop(terms) for x in curves}
stepsize = np.timedelta64(30, 'D') / np.timedelta64(1, 'ns') # step every 30 days
datelist = {x:data[x]['Date'].unique() for x in curves}

# Initial figure
X = data['CurveA'].loc[data['CurveA']["Date"]==start]
traces=[go.Scatter(x=X['Term'], y=X['Rate'], name='Baseline')]
traces.append(go.Scatter(x=X['Term'], y=X['Shocked'], name='Shocked'))
layout=go.Layout(showlegend=True,uirevision='static',
                 xaxis={'title': 'Term (months)','title_text':'Rate (%)'},
                 yaxis={'title': 'Rate (%)', 'title_text':'Term (months)','range':[0,120]},
                 title_text=str(start)[:10])
figorig = go.Figure(data=traces, layout=layout)

# Subroutines
def closestvaliddate(inp,datelist):
    dist = abs(datelist-np.datetime64(inp,"ns")) # input is date in integer form
    mindist = min(dist) #  divide by np.timedelta64(1, 'D') to get days
    return datelist[dist==mindist][0]

# Start application
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

######################################
####### App layout ###################
######################################
app.layout = html.Div([
    dcc.Dropdown(id="curve-type", multi=False, value="CurveA", style={"width": "30%"},
                 options=[{"label": x, "value": x} for x in curves]),
    dcc.Graph(id='graph-shocks'),
    html.Div(children=[dcc.Slider(id='date-slider',min=startdt,max=enddt,step=stepsize,value=startdt,
         updatemode='drag',marks={int(x):str(x)[:10] for x in [startdt,enddt]})
           ], style={"width": "80%","margin":"auto"}) # range(1993,2020,5)
])

@app.callback(Output('graph-shocks', 'figure'),
    [Input('date-slider', 'value'),Input('curve-type', 'value')]) # , [State('graph-shocks', 'figure')]
def update_figure(inpdate,curve):
    selecteddate = closestvaliddate(inpdate,datelist[curve])
    X = data[curve].loc[data[curve]["Date"]==selecteddate]
    traces = [go.Scatter(x=X['Term'], y=X['Rate'], name='Baseline')]
    traces.append(go.Scatter(x=X['Term'], y=X['Shocked'], name='Shocked'))
    fig = go.Figure(data=traces, layout=layout)
    fig.layout.update(title_text=str(selecteddate)[:10])
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)
