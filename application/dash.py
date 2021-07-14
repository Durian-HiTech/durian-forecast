###############################################################################
#                                MAIN                                         #
###############################################################################

# Setup
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from settings import config, about
from python.data import Data
from python.model import Model
from python.result import Result



# Read data
data = Data()
data.get_data()



# App Instance
app = dash.Dash(name=config.name, assets_folder=config.root+"/application/static", external_stylesheets=[dbc.themes.LUX, config.fontawesome])
app.title = config.name



# Navbar
navbar = dbc.Nav(className="nav nav-pills", children=[
])



# Input
inputs = dbc.FormGroup([
    html.H4("请选择国家或地区"),
    dcc.Dropdown(id="country", options=[{"label":x,"value":x} for x in data.countrylist], value="World")
]) 



# App Layout
app.layout = dbc.Container(fluid=True, children=[
    ## Top
    html.H1(config.name, id="nav-pills"),
    navbar,
    html.Br(),

    ## Body
    dbc.Row([
        ### input + panel
        dbc.Col(md=3, children=[
            inputs, 
            html.Br(),
            html.Div(id="output-panel")
        ]),
        ### plots
        dbc.Col(md=9, children=[
            dbc.Col(html.H4("预测从今天开始的未来30天的新冠病例数据"), width={"size":6,"offset":3}), 
            dbc.Tabs(className="nav nav-pills", children=[
                dbc.Tab(dcc.Graph(id="plot-total"), label="累计确诊"),
                dbc.Tab(dcc.Graph(id="plot-active"), label="活跃病例")
            ])
        ])
    ])
])



# Python functions for about navitem-popover
@app.callback(output=Output("about","is_open"), inputs=[Input("about-popover","n_clicks")], state=[State("about","is_open")])
def about_popover(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(output=Output("about-popover","active"), inputs=[Input("about-popover","n_clicks")], state=[State("about-popover","active")])
def about_active(n, active):
    if n:
        return not active
    return active



# Python function to plot total cases
@app.callback(output=Output("plot-total","figure"), inputs=[Input("country","value")]) 
def plot_total_cases(country):
    data.process_data(country) 
    model = Model(data.dtf)
    model.forecast()
    model.add_deaths(data.mortality)
    result = Result(model.dtf)
    return result.plot_total(model.today)



# Python function to plot active cases
@app.callback(output=Output("plot-active","figure"), inputs=[Input("country","value")])
def plot_active_cases(country):
    data.process_data(country) 
    model = Model(data.dtf)
    model.forecast()
    model.add_deaths(data.mortality)
    result = Result(model.dtf)
    return result.plot_active(model.today)
    

    
# Python function to render output panel
@app.callback(output=Output("output-panel","children"), inputs=[Input("country","value")])
def render_output_panel(country):
    data.process_data(country) 
    model = Model(data.dtf)
    model.forecast()
    model.add_deaths(data.mortality)
    result = Result(model.dtf)
    peak_day, num_max, total_cases_until_today, total_cases_in_30days, active_cases_today, active_cases_in_30days = result.get_panel()
    peak_color = "white" if model.today > peak_day else "red"
    panel = html.Div([
        html.H4(country),

        dbc.Card(
            dbc.CardBody(
                [
                    html.H4("截止到当日的累计确诊数：", className="card-title"),
                    html.H4("{:,.0f}".format(total_cases_until_today), className="card-subtitle"),
                    html.Br(),
                    html.H4("最近30天内的累计确诊数：", className="card-title"),
                    html.H4("{:,.0f}".format(total_cases_in_30days), className="card-subtitle"),
                    html.Br(),
                    html.H4("今日活跃病例数：", className="card-title"),
                    html.H4("{:,.0f}".format(active_cases_today), className="card-subtitle"),
                    html.Br(),
                    html.H4("近30天内的活跃病例数：", className="card-title"),
                    html.H4("{:,.0f}".format(active_cases_in_30days), className="card-subtitle"),
                    html.Br(),
                    html.H4("峰值新增日：", className="card-title"),
                    html.H4(peak_day.strftime("%Y-%m-%d"), className="card-subtitle"),
                    html.P(
                        "当日含 {:,.0f} 个病例".format(num_max),
                        className="card-text",
                    ),
                ]
            ),
            style={"width": "21rem"},
        )
    ])
    return panel