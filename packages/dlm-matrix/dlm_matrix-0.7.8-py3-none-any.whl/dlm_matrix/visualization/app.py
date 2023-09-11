import dash
from dash.dependencies import Input, Output
from dash import html, dcc
import plotly.express as px
from dlm_matrix.visualization.psychedelic import plot_3d_scatter_psychedelic


# Function to create the application
def create_dash_app(df):
    if df.empty:
        raise ValueError("The provided DataFrame is empty")

    # Create a Dash appx
    app = dash.Dash(__name__)

    # Create a Dash layout that includes a Graph component and RangeSlider components
    app.layout = html.Div(
        style={
            "width": "100%",
            "height": "100vh",
            "display": "flex",
            "flex-direction": "column",
        },
        children=[
            dcc.Graph(id="3d_scatter"),
            html.Label("Depth X Filter:"),
            dcc.RangeSlider(
                id="depth_x_slider",
                min=df["depth_x"].min(),
                max=df["depth_x"].max(),
                value=[df["depth_x"].min(), df["depth_x"].max()],
                step=0.1,
                marks={
                    i: f"{i:.1f}"
                    for i in range(
                        int(df["depth_x"].min()), int(df["depth_x"].max()) + 1
                    )
                },
            ),
            html.Label("Sibling Y Filter:"),
            dcc.RangeSlider(
                id="sibling_y_slider",
                min=df["sibling_y"].min(),
                max=df["sibling_y"].max(),
                value=[df["sibling_y"].min(), df["sibling_y"].max()],
                step=0.1,
                marks={
                    i: f"{i:.1f}"
                    for i in range(
                        int(df["sibling_y"].min()), int(df["sibling_y"].max()) + 1
                    )
                },
            ),
            html.Label("Sibling Count Z Filter:"),
            dcc.RangeSlider(
                id="sibling_count_z_slider",
                min=df["sibling_count_z"].min(),
                max=df["sibling_count_z"].max(),
                value=[df["sibling_count_z"].min(), df["sibling_count_z"].max()],
                step=0.1,
                marks={
                    i: f"{i:.1f}"
                    for i in range(
                        int(df["sibling_count_z"].min()),
                        int(df["sibling_count_z"].max()) + 1,
                    )
                },
            ),
            html.Label("Select colorscale:"),
            dcc.Dropdown(
                id="colorscale_dropdown",
                options=[
                    {"label": i, "value": i} for i in px.colors.named_colorscales()
                ],
                value="Rainbow",
            ),
            html.Label("Select interactivity mode:"),
            dcc.RadioItems(
                id="dragmode_radioitems",
                options=[{"label": i, "value": i} for i in ["orbit", "turntable"]],
                value="orbit",
            ),
            html.Label("Display line traces:"),
            dcc.Checklist(
                id="line_traces_checkbox",
                options=[{"label": "Show line traces", "value": "show"}],
                value=["show"],  # Value is a list
            ),
        ],
    )

    # Callback for updating the figure
    @app.callback(
        Output("3d_scatter", "figure"),
        [
            Input("depth_x_slider", "value"),
            Input("sibling_y_slider", "value"),
            Input("sibling_count_z_slider", "value"),
            Input("colorscale_dropdown", "value"),
            Input("dragmode_radioitems", "value"),
            Input("line_traces_checkbox", "value"),
        ],
    )
    def update_figure(
        depth_x_range,
        sibling_y_range,
        sibling_count_z_range,
        colorscale,
        dragmode,
        line_traces_value,
    ):
        filtered_df = df[
            (df["depth_x"].between(*depth_x_range))
            & (df["sibling_y"].between(*sibling_y_range))
            & (df["sibling_count_z"].between(*sibling_count_z_range))
        ]

        return plot_3d_scatter_psychedelic(
            filtered_df,
            colorscale=colorscale,
            dragmode=dragmode,
        )

    return app
