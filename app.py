import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

totals = pd.read_csv('data/CE_totals.csv')
totals = totals.replace("China (People's Republic of)", "China")
totals = totals[(totals['Country'] != 'OECD - Europe')]
totals = totals[(totals['Country'] != 'OECD - Total')]
totals = totals[totals['Pollutant'] != 'Greenhouse gases']
year = 2012
year_data = totals[totals['Year'] == year]
total_data = year_data[year_data['VAR'] == 'TOTAL']
year_group_pollutant = total_data.groupby(by = 'Pollutant')['Value'].sum()





app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True


fossil_bar =  go.Figure(go.Bar(x = year_group_pollutant[::-1], y = year_group_pollutant.index[::-1], orientation='h',marker=dict(color='#f5961d')))
fossil_bar.update_layout(
    title = 'Types of Greenhouse Gases Emitted in the Atmosphere',
    font = dict(
        color = 'lightgray',
        family = 'Arial Bold'
    ),
    paper_bgcolor = '#172e54',
    plot_bgcolor = 'lightgray',
    xaxis = dict(
        gridcolor = 'white'
    ),
    yaxis = dict(
        gridcolor = 'white'
    )
)

fossil_pie = go.Figure(go.Pie(labels = year_group_pollutant.index, values = year_group_pollutant, hole = .4,))
fossil_pie.update_layout(
    title = "Percentage of Each Fossil Fuel Relative to each other in 2012",
    paper_bgcolor = '#12153b',
    font = dict(
        color = 'lightgray',
    )
)

#######################################################################

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H1('Carbon Emissions Around the Globe', style = {'color':'lightgray'}),
                html.P('Some notable countries are missing data since not all countries have data for all years',
                    style = {
                        'color':'lightgray',
                        'font-size':'20px'
                    }),
                html.P('Emission are taken without including LULUCF (land uses, land use change, and forestry) emissions in mind',
                    style = {
                        'color':'lightgray',
                        'font-size':'20px'
                    })
                ], style = {'width':'39%', 'float':'left','padding-left':'5px' }),
            #html.P("Missing data from some countries not providing proper data in some years"),
            #html.P("Data is not including LULUCF (Land use, land use change, and forestry)"),
            dcc.Graph(figure = fossil_bar,
                style = {
                    'width':'58%',
                    'float':'left'
                }),
            ],style = {
                'width':'43%',
                'float':'left',
                'backgroundColor':'#172e54',
                'display':'inline'
            }
        ),
        dcc.Graph('emissions_map',
            config={
                'scrollZoom':False
            },
            style = {
                'width':'57%',
                'float':'left',
                'margin':'auto'
            }),
    ],style = {
        'width':'100%',
    }),
    html.Div([
        html.Div(
            dcc.RadioItems(
                id = 'pollutant_dropdown',
                options = [{'label':i, 'value':i} for i in totals.Pollutant.unique()],
                value = 'Carbon dioxide',

            ),
            style = {
                'width':'43%',
                'backgroundColor':'#172e54',
                'color':'lightgray'
            }
        ),
    ], style = {
        'width':'100%',
        'backgroundColor':'#12153b'
    }),
    html.Div(id = 'clean_data', style = {'display':'none'}),
    dcc.Graph('Greenhouse_gases_graph',
        style = {
            'width':'43%',
            'float':'left'
        }),
    html.Div(
        dcc.Graph(figure = fossil_pie),
        style = {
            'width':'57%',
            'float':'left'
        }
    )
])

#######
## page 2
###########

#######################
# first page
######################
@app.callback(
    Output('clean_data', 'children'),
    [Input('pollutant_dropdown', 'value')]
)

def clean_data(pollutant_dropdown_value):
    ## find largest value for the most recent year for the given pollutant
    entered_pollutant = totals[totals['Pollutant'] == pollutant_dropdown_value]
    entered_pollutant_max_year = entered_pollutant[entered_pollutant['Year'] == 2012]
    top_7_countries_list = list(entered_pollutant_max_year.sort_values(by = 'Value', ascending = False).head(7).Country)
    countries_plus_polutant = entered_pollutant.query('Country == {}' .format(top_7_countries_list))
    total_emission = countries_plus_polutant[countries_plus_polutant['Variable']=='Total  emissions excluding LULUCF']
    return (total_emission.to_json(orient='split'))


### map
@app.callback(
    Output('emissions_map', 'figure'),
    [Input('pollutant_dropdown', 'value')]
)

def create_map(pollutant_dropdown_value):
    entered_pollutant = totals[totals['Pollutant'] == pollutant_dropdown_value]
    entered_pollutant_max_year = entered_pollutant[entered_pollutant['Year'] == 2012]
    total_emission = entered_pollutant_max_year[entered_pollutant_max_year['Variable']=='Total  emissions excluding LULUCF']
    dff = total_emission
    trace = go.Choropleth(
        locations = dff.Country,
        locationmode = 'country names',
        z = dff.Value,
    )
    return{
        'data':[trace],
        'layout':go.Layout(
            title_text = ('{} Map in 2012' .format(dff.POL.iloc[0])),
            font = dict(
                color = 'white'
            ),
            geo = go.layout.Geo(
                lataxis_showgrid=True,
                lonaxis_showgrid=True,
                showocean = True,
                oceancolor = 'lightblue'
            ),
        paper_bgcolor = '#12153b',


        ),
    }

### country_ghg graph
@app.callback(
    Output('Greenhouse_gases_graph', 'figure'),
    [Input('clean_data', 'children')]
)

def ghg_graph(json_data):
    dff = pd.read_json(json_data, orient='split')
    fig = px.line(dff, x='Year', y='Value', color= 'Country', title = ('Top 7 Countries: Carbon Emissions from {}(thousand metric ton of carbon) vs Year' .format(dff.POL.iloc[0])),
    labels = {
        'Value':'Carbon Emissions',
    }
    )
    fig.update_layout(
        title = ('Top {} Releasing Countries (that there is sufficient data for)  ' .format(dff.Pollutant.iloc[0])),
        font = dict(
            color = 'lightgray',
            family = 'Arial Bold'
        ),
        paper_bgcolor = '#172e54',
        plot_bgcolor = 'lightgray',
        xaxis = dict(
            gridcolor = 'white'
        ),
        yaxis = dict(
            gridcolor = 'white'
        )
    )

    return fig



if __name__ == '__main__':
    app.run_server(debug=True)














####
