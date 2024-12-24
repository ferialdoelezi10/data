from flask import Flask, render_template
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

app = Flask(__name__)

@app.route("/")
def index():
    # Read the Excel file, specifying the header row and column names
    data = pd.read_excel("co2_data.xlsx", header=0, names=['Year', 'CO2'])

    # Filter the data to include only desired years
    data = data[(data['Year'] >= 1959) & (data['Year'] <= 2023)]
    data['Year'] = data['Year'].astype(int)  # Ensure 'Year' is integer

    # Create the figure
    fig = go.Figure()

    # Add the initial trace for the line with markers
    fig.add_trace(go.Scatter(
        x=data['Year'],
        y=data['CO2'],
        mode='lines+markers',  # Add markers to the line
        line=dict(color='blue'),  # Line color
        marker=dict(size=8, color='blue', symbol='circle'),  # Marker customization
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
            name=str(data['Year'].iloc[i - 1])  # Name frame based on year
        )
        for i in range(1, len(data) + 1)
    ]
    fig.frames = frames

    # Configure the play/pause buttons and slider
    fig.update_layout(
        updatemenus=[
            dict(
                type='buttons',
                showactive=True,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            dict(
                                frame=dict(duration=700, redraw=True),
                                fromcurrent=True
                            )
                        ]
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
                            dict(
                                mode="immediate",
                                frame=dict(duration=500, redraw=True),
                                transition=dict(duration=0)
                            )
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

    # Add layout details
    fig.update_layout(
        title="Average carbon dioxide (CO₂) levels in the atmosphere worldwide from 1959 to 2023",
        xaxis=dict(
            title="Year",
            tickmode='linear',  # Ensure only integer years are shown
            dtick=5,  # Display every 5th year for better readability
            range=[1959, 2023]  # Limit the x-axis range
        ),
        yaxis=dict(
            title="CO2 Concentration (ppm)",
            range=[310, 420],  # Fixed y-axis range
            autorange=False  # Disable auto-scaling
        ),
        hovermode="x unified"
    )

    # Convert the Plotly graph to HTML
    line_graph_html = pio.to_html(fig, full_html=False)

    # Render the HTML template with the graph embedded
    return render_template('index.html', line_graph_html=line_graph_html)

if __name__ == "__main__":
    app.run(debug=True)
