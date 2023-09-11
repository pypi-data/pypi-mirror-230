import pandas as pd
import plotly.graph_objects as go
import numpy as np
from typing import Union
import plotly.express as px


def wrap_text(text, max_len=100):
    lines = text.split("\n")
    wrapped_lines = []
    for line in lines:
        while len(line) > max_len:
            cut_at = line.rfind(" ", 0, max_len)
            if cut_at == -1:  # No spaces in this line
                cut_at = max_len
            wrapped_lines.append(line[:cut_at])
            line = line[cut_at:].lstrip()  # Remove leading spaces
        wrapped_lines.append(line)
    return "<br>".join(wrapped_lines)


def agg_funcs():
    aggs = {
        "count": len,
        "sum": np.sum,
        "avg": np.mean,
        "median": np.median,
        "rms": lambda x: np.sqrt(np.mean(np.square(x))),
        "stddev": np.std,
        "min": np.min,
        "max": np.max,
        "first": lambda x: x.iloc[0],
        "last": lambda x: x.iloc[-1],
    }
    return aggs


def plot_3d_scatter_psychedelic(
    file_path_or_dataframe: Union[str, pd.DataFrame],
    text_column: str = "text",
    label_column: str = "cluster_label",
    columns_to_agg: list = ["x", "y", "z"],
    aggregate_func: callable = None,
    colorscale: str = "Rainbow",
    dragmode: str = "turntable",
    show: bool = False,
):
    if isinstance(file_path_or_dataframe, str):
        # Load DataFrame from csv file
        result3d = pd.read_csv(file_path_or_dataframe)
    elif isinstance(file_path_or_dataframe, pd.DataFrame):
        result3d = file_path_or_dataframe
    else:
        raise ValueError(
            "file_path_or_dataframe must be either a file path or a DataFrame"
        )

    result3d.drop(columns=["embeddings"], errors="ignore", inplace=True)

    result3d[text_column] = result3d[text_column].astype(str)

    result3d["formatted_content"] = result3d[text_column].apply(wrap_text)

    rainbow_scale = px.colors.sequential.Rainbow
    system_colors = [
        rainbow_scale[int(i)]
        for i in np.linspace(0, len(rainbow_scale) - 1, len(result3d[label_column]))
    ]

    # Adding coordinate information to the hover text
    result3d["formatted_content_umap"] = (
        "UMAP: "
        + "(x: "
        + result3d["x"].astype(str)
        + ", y: "
        + result3d["y"].astype(str)
        + ", z: "
        + result3d["z"].astype(str)
        + ")<br>"
        + "Content: "
        + result3d["formatted_content"]
    )

    result3d["formatted_content_coord"] = (
        "Coordinates: "
        + "(depth_x: "
        + result3d["depth_x"].astype(str)
        + ", sibling_y: "
        + result3d["sibling_y"].astype(str)
        + ", sibling_count_z: "
        + result3d["sibling_count_z"].astype(str)
        + ")<br>"
        + "Content: "
        + result3d["formatted_content"]
    )

    if aggregate_func is not None:
        # Check if a valid aggregate function is given
        if aggregate_func not in agg_funcs().keys():
            raise ValueError(
                f"Invalid aggregate function. Choose from {list(agg_funcs().keys())}"
            )

        # Apply the aggregate function to the selected columns for each unique label
        grouped = result3d.groupby(label_column)
        aggregated_data = (
            grouped[columns_to_agg].agg(agg_funcs()[aggregate_func]).reset_index()
        )

        # Merge the aggregated data with the original data
        result3d = pd.merge(
            result3d,
            aggregated_data,
            on=label_column,
            how="left",
            suffixes=("", "_agg"),
        )

    # Scatter trace for UMAP coordinates
    scatter_trace_umap = go.Scatter3d(
        x=result3d["x"],
        y=result3d["y"],
        z=result3d["z"],
        mode="markers",
        marker=dict(
            size=4,
            color=system_colors,
            colorscale=colorscale,
            line=dict(color="powderblue", width=2),
            opacity=0.7,
            symbol="circle",
            sizemode="diameter",
        ),
        hoverinfo="text",
        hovertext=result3d["formatted_content_umap"],
        name="UMAP",
    )

    # Scatter trace for original coordinates
    scatter_trace_coord = go.Scatter3d(
        x=result3d["depth_x"],
        y=result3d["sibling_y"],
        z=result3d["sibling_count_z"],
        mode="markers",
        marker=dict(
            size=4,
            color=system_colors,
            colorscale=colorscale,
            line=dict(color="powderblue", width=2),
            opacity=0.7,
            symbol="circle",
            sizemode="diameter",
        ),
        hoverinfo="text",
        hovertext=result3d["formatted_content_coord"],
        name="Coordinates",
    )

    # Line trace for UMAP coordinates
    line_trace_umap = go.Scatter3d(
        x=result3d["x"],
        y=result3d["y"],
        z=result3d["z"],
        mode="lines",
        line=dict(
            color="white",
            colorscale="Rainbow",
            width=1,
            cmin=0,
            cmax=1,
        ),
        hoverinfo="none",
    )

    # Line trace for original coordinates
    line_trace_coord = go.Scatter3d(
        x=result3d["depth_x"],
        y=result3d["sibling_y"],
        z=result3d["sibling_count_z"],
        mode="lines",
        line=dict(
            color="white",
            colorscale="Rainbow",
            width=1,
            cmin=0,
            cmax=1,
        ),
        hoverinfo="none",
    )

    # Add menu and layout
    updatemenus = [
        dict(
            type="buttons",
            showactive=False,
            buttons=list(
                [
                    dict(
                        args=[{"visible": [True, True, True, True]}],
                        label="Show All",
                        method="update",
                    ),
                    dict(
                        args=[{"visible": [True, True, False, False]}],
                        label="Show UMAP",
                        method="update",
                    ),
                    dict(
                        args=[{"visible": [False, False, True, True]}],
                        label="Show Coordinates",
                        method="update",
                    ),
                ]
            ),
            direction="down",
            pad={"r": 10, "t": 10},
            x=0.1,
            xanchor="left",
            y=1.1,
            yanchor="top",
        ),
    ]

    layout = dict(
        title="Chain of Memories",
        showlegend=True,
        updatemenus=updatemenus,
        scene=dict(
            xaxis=dict(showbackground=False, gridcolor="Black"),
            yaxis=dict(showbackground=False, gridcolor="Black"),
            zaxis=dict(showbackground=False, gridcolor="Black"),
            camera=dict(
                up=dict(x=0, y=0, z=1),
                eye=dict(x=-1.5, y=-1.5, z=1.5),
                center=dict(x=0, y=0, z=0),
            ),
            dragmode=dragmode,
        ),
        font_family="Arial",
        font_color="White",
        title_font_family="Arial",
        title_font_color="White",
        legend_title_font_color="White",
        paper_bgcolor="Black",
        plot_bgcolor="Black",
        hoverlabel=dict(bgcolor="Black", font_color="White"),
        coloraxis_colorbar=(
            go.layout.Colorbar(
                title="Color Scale",
                titleside="right",
                tickmode="array",
                tickvals=[min(result3d["labels"]), max(result3d["labels"])],
                ticktext=["Low", "High"],
            )
            if "color" in result3d.columns
            else None
        ),
    )

    fig = go.Figure(
        data=[
            scatter_trace_umap,
            line_trace_umap,
            scatter_trace_coord,
            line_trace_coord,
        ],
        layout=layout,
    )

    fig.update_layout(
        scene=dict(
            xaxis=dict(
                title=dict(text="UMAP x"),
                titlefont=dict(color="White"),
                tickfont=dict(color="White"),
            ),
            yaxis=dict(
                title=dict(text="UMAP y"),
                titlefont=dict(color="White"),
                tickfont=dict(color="White"),
            ),
            zaxis=dict(
                title=dict(text="UMAP z"),
                titlefont=dict(color="White"),
                tickfont=dict(color="White"),
            ),
        )
    )

    fig.update_layout(
        scene2=dict(
            xaxis=dict(
                title=dict(text="Depth x"),
                titlefont=dict(color="White"),
                tickfont=dict(color="White"),
            ),
            yaxis=dict(
                title=dict(text="Sibling y"),
                titlefont=dict(color="White"),
                tickfont=dict(color="White"),
            ),
            zaxis=dict(
                title=dict(text="Sibling Count z"),
                titlefont=dict(color="White"),
                tickfont=dict(color="White"),
            ),
        )
    )
    if show:
        return fig.show()
    else:
        return fig
