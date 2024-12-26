from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)

@app.route("/")
def index():
    # Load the Excel file
    data = pd.read_excel("co2_data.xlsx", header=0, names=['Year', 'CO2'])

    # Filter the data for the desired range
    data = data[(data['Year'] >= 1959) & (data['Year'] <= 2023)]
    data['Year'] = data['Year'].astype(int)

    # Create the figure
    fig = go.Figure()

    # Add the CO2 line with markers
    fig.add_trace(go.Scatter(
        x=data['Year'],
        y=data['CO2'],
        mode='lines+markers',
        line=dict(color='blue'),
        marker=dict(size=8, color='blue', symbol='circle'),
        name='CO2 Concentration'
    ))

    # Add animation frames
    frames = [
        go.Frame(
            data=[
                go.Scatter(
                    x=data['Year'][:i],
                    y=data['CO2'][:i],
                    mode='lines+markers',
                    line=dict(color='blue'),
                    marker=dict(size=8, color='blue', symbol='circle')
                )
            ],
            name=str(data['Year'].iloc[i - 1])
        )
        for i in range(1, len(data) + 1)
    ]
    fig.frames = frames

    # Add annotations for specific years
    annotations = [
        {"Year": 1970, "Text": "<a href='https://en.wikipedia.org/wiki/Earth_Day'>Environmental Movement</a>"},
        {"Year": 1997, "Text": "<a href='https://unfccc.int/kyoto_protocol'>Kyoto Protocol Signed</a>"},
        {"Year": 2015, "Text": "<a href='https://unfccc.int/process-and-meetings/the-paris-agreement/the-paris-agreement'>Paris Agreement</a>"},
        {"Year": 2021, "Text": "<a href='https://www.reuters.com/business/environment/global-co2-emissions-fossil-fuels-hit-record-high-2023-report-2023-12-05/'>Record CO2 Levels</a>"}
    ]

    for annotation in annotations:
        if annotation["Year"] in data['Year'].values:
            fig.add_annotation(
                x=annotation["Year"],
                y=data.loc[data['Year'] == annotation["Year"], 'CO2'].values[0],
                text=annotation["Text"],
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40
            )

    # Configure play/pause buttons and slider
    fig.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                showactive=True,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, dict(frame=dict(duration=700, redraw=True), fromcurrent=True)]
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate")]
                    )
                ]
            )
        ],
        sliders=[
            dict(
                active=0,
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [str(data['Year'].iloc[k])],
                            dict(mode="immediate", frame=dict(duration=500, redraw=True), transition=dict(duration=0))
                        ],
                        label=str(data['Year'].iloc[k])
                    )
                    for k in range(len(data))
                ],
                x=0, y=0,
                currentvalue=dict(font=dict(size=12), prefix="Year: ", visible=True),
                len=1.0
            )
        ]
    )

    # Add layout details and remove grid lines
    fig.update_layout(
        title="Average carbon dioxide (CO₂) levels in the atmosphere worldwide from 1959 to 2023",
        xaxis=dict(
            title="Year",
            tickmode='linear',
            dtick=5,
            range=[1959, 2023],
            showgrid=False  # Remove x-axis grid lines
        ),
        yaxis=dict(
            title="CO2 Concentration (ppm)",
            range=[310, 420],
            showgrid=False  # Remove y-axis grid lines
        ),
        hovermode="x unified",
        dragmode=False  # Disable dragging and zooming
    )

    # Convert Plotly graph to HTML
    line_graph_html = pio.to_html(fig, full_html=False)

    # Render the HTML template with the graph
    return render_template('index.html', line_graph_html=line_graph_html)

if __name__ == "__main__":
    app.run(debug=True)
