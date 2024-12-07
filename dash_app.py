import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import requests
import json
import threading

# Start Dash app
app = dash.Dash(__name__)
app.title = "Real-Time Data Streaming"

# Layout
app.layout = html.Div([
    html.H1("Real-Time Data Visualization", style={"textAlign": "center"}),
    
    # Dropdown for ticker selection
    html.Div([
        html.Label("Select Ticker:"),
        dcc.Dropdown(
            id="ticker-dropdown",
            options=[
                {"label": "BNS.TO", "value": "BNS.TO"},
                {"label": "CNQ.TO", "value": "CNQ.TO"},
                {"label": "THX.V", "value": "THX.V"},
                {"label": "TSAT.TO", "value": "TSAT.TO"}
            ],
            value="",  # Default value: All categories
        )
    ], style={"width": "50%", "margin": "auto"}),

    # Graph
    dcc.Graph(id="real-time-graph"),

    # Interval component for periodic updates
    dcc.Interval(
        id="interval-update",
        interval=1000,  # Update every second
        n_intervals=0  # Number of times the interval has passed
    )
])

# Global variables to store streamed data
streamed_timestamps = []
streamed_bid_values = []
active_ticker = None


# Function to fetch streaming data
def fetch_stream_data(ticker):
    global streamed_timestamps, streamed_bid_values
    timestamps, bid_values = [], []
    url = f"http://127.0.0.1:8000/stream?ticker={ticker}"
    try:
        response = requests.get(url, stream=True)
        for line in response.iter_lines():
            if line:
                event = line.decode("utf-8").replace("data: ", "").replace("\'", "\"")
                data = json.loads(event)
                for row in data:
                    timestamps.append(row['timestamp'])
                    bid_values.append(row['bid'])
                streamed_timestamps=timestamps
                streamed_bid_values=bid_values
    except Exception as e:
        print(f"Error fetching stream: {e}")


# Background thread to keep fetching data
def start_stream(ticker):
    thread = threading.Thread(target=fetch_stream_data, args=(ticker,), daemon=True)
    thread.start()


# Callback to update the graph
@app.callback(
    Output("real-time-graph", "figure"),
    [Input("ticker-dropdown", "value"), Input("interval-update", "n_intervals")]
)
def update_graph(ticker, n_intervals):
    global streamed_timestamps, streamed_bid_values, active_ticker

    # If ticker changes, restart the stream
    if ticker != active_ticker:
        start_stream(ticker)

    # Process streamed data for the graph
    if streamed_timestamps and streamed_bid_values:
        x_data = streamed_timestamps
        y_data = streamed_bid_values
    else:
        x_data, y_data = [], []

    # Create the graph
    return {
        "data": [go.Scatter(x=x_data, y=y_data, mode="lines+markers", name="Real-Time Data")],
        "layout": go.Layout(
            title="Real-Time Data",
            xaxis={"title": "Timestamp"},
            yaxis={"title": "Bid Value"},
            margin={"l": 40, "r": 40, "t": 40, "b": 40},
            height=500
        )
    }


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=False, host="127.0.0.1", port=8050)
