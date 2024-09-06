import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data using pandas
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
app.title = "Automobile Sales Statistics Dashboard"

# List of years 
year_list = sorted(data['Year'].unique())  # Dynamically generate the list of years

# Create the layout of the app
app.layout = html.Div([
    # Title of the dashboard
    html.H1(
        "Automobile Sales Statistics Dashboard", 
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'fontSize': 24
        }
    ),
    
    # Dropdown for selecting report type
    html.Div([
        dcc.Dropdown(
            id='dropdown-statistics',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
            ],
            placeholder='Select a report type',
            value='Yearly Statistics',
            style={
                'width': '80%',
                'padding': '3px',
                'fontSize': '20px',
                'text-align-last': 'center'
            }
        ),
    ], style={'padding': '10px'}),
    
    # Dropdown for selecting year
    html.Div([
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            placeholder='Select Year',
            value=year_list[0],  # Default to the first year
            style={
                'width': '80%',
                'padding': '3px',
                'fontSize': '20px',
                'text-align-last': 'center'
            }
        ),
    ], style={'padding': '10px'}),
    
    # Division for output display
    html.Div([
        html.Div(id='output-container', className='chart-grid', style={'display': 'flex'}),
    ])
])

# Callback to enable/disable year dropdown based on report type selection
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    return selected_statistics != 'Yearly Statistics'

# Callback to update output container based on selections
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, selected_year):
    if selected_statistics == 'Recession Period Statistics':
        # Filter the data for recession periods
        recession_data = data[data['Recession'] == 1]
        
        # Plot 1: Automobile sales fluctuate over Recession Period (year wise)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, 
                x='Year', 
                y='Automobile_Sales',
                title="Average Automobile Sales Fluctuation Over Recession Period")
        )

        # Plot 2: Calculate the average number of vehicles sold by vehicle type
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales, 
                x='Vehicle_Type', 
                y='Automobile_Sales', 
                title="Average Number of Vehicles Sold by Vehicle Type During Recession")
        )

        # Plot 3: Pie chart for total expenditure share by vehicle type during recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec, 
                values='Advertising_Expenditure', 
                names='Vehicle_Type', 
                title="Total Expenditure Share by Vehicle Type During Recession")
        )

        # Plot 4: Bar chart for the effect of unemployment rate on vehicle type and sales
        unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data, 
                x='unemployment_rate', 
                y='Automobile_Sales', 
                color='Vehicle_Type', 
                labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
                title='Effect of Unemployment Rate on Vehicle Type and Sales')
        )

        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)], style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)], style={'display': 'flex'})
        ]
    
    elif selected_statistics == 'Yearly Statistics' and selected_year:
        # Filter the data for the selected year
        yearly_data = data[data['Year'] == selected_year]

        # Plot 1: Yearly Automobile sales using line chart
        yas = yearly_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(yas, 
                x='Year', 
                y='Automobile_Sales', 
                title="Yearly Automobile Sales")
        )

        # Plot 2: Total Monthly Automobile sales using line chart
        mas = yearly_data.groupby('Month')['Automobile_Sales'].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(mas, 
                x='Month', 
                y='Automobile_Sales', 
                title='Total Monthly Automobile Sales')
        )

        # Plot 3: Average number of vehicles sold during the given year by vehicle type
        avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        Y_chart3 = dcc.Graph(
            figure=px.bar(avr_vdata, 
                x='Vehicle_Type', 
                y='Automobile_Sales', 
                title=f'Average Vehicles Sold by Vehicle Type in the Year {selected_year}')
        )

        # Plot 4: Total Advertisement Expenditure for each vehicle using pie chart
        exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        Y_chart4 = dcc.Graph(
            figure=px.pie(exp_data, 
                values='Advertising_Expenditure', 
                names='Vehicle_Type', 
                title='Total Advertisement Expenditure by Vehicle Type')
        )

        return [
            html.Div(className='chart-item', children=[html.Div(children=Y_chart1), html.Div(children=Y_chart2)], style={'display': 'flex'}),
            html.Div(className='chart-item', children=[html.Div(children=Y_chart3), html.Div(children=Y_chart4)], style={'display': 'flex'})
        ]

    else:
        return None  # Return None if no statistics or year is selected

# Run the Dash app
if __name__ == '__main__':
    app.run_server()
