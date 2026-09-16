"""Consistent, readable chart cards independent of Streamlit's active theme."""

TEXT = "#243447"
GRID = "#e2e8f0"
AXIS = "#94a3b8"


def style_chart(fig):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Arial, sans-serif", size=14, color=TEXT),
        title_font=dict(color=TEXT, size=17),
        margin=dict(l=75, r=60, t=75, b=85, pad=8),
        legend=dict(
            font=dict(color=TEXT, size=13),
            bgcolor="#ffffff",
            orientation="h", x=0, xanchor="left", y=1.16, yanchor="bottom",
        ),
        hoverlabel=dict(bgcolor="#ffffff", font=dict(color=TEXT, size=13)),
    )
    axis_style = dict(
        visible=True, showticklabels=True,
        tickfont=dict(color=TEXT, size=13),
        title_font=dict(color=TEXT, size=14),
        title_standoff=18,
        ticks="outside", ticklen=5, tickcolor=AXIS,
        showline=True, linecolor=AXIS, linewidth=1,
        gridcolor=GRID, zerolinecolor=AXIS, automargin=True,
    )
    fig.update_xaxes(**axis_style)
    fig.update_yaxes(**axis_style)
    # Pie charts have no axes; give their legend room beneath the ring.
    if any(trace.type == "pie" for trace in fig.data):
        fig.update_layout(
            margin=dict(l=25, r=25, t=25, b=90),
            legend=dict(x=0.5, xanchor="center", y=-0.12, yanchor="top"),
        )
        fig.update_traces(textinfo="percent", textposition="outside",
                          textfont=dict(color=TEXT, size=13), selector=dict(type="pie"))
    return fig
