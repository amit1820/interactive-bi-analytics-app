"""Explicit high-contrast chart styling, unaffected by Streamlit's chart theme."""
NAVY='#16324f'
TEAL='#087f8c'
CORAL='#cf654c'


def style_chart(fig, height=370):
    fig.update_layout(template='plotly_white',height=height,paper_bgcolor='#ffffff',
        plot_bgcolor='#ffffff',font=dict(family='Arial, sans-serif',size=13,color=NAVY),
        margin=dict(l=65,r=30,t=55,b=60),
        legend=dict(orientation='h',y=1.12,x=0,font=dict(color=NAVY)),
        hoverlabel=dict(bgcolor='white',font_color=NAVY))
    fig.update_xaxes(automargin=True,tickfont_color=NAVY,title_font_color=NAVY,
                     showline=True,linecolor='#c6d1d8',gridcolor='#edf1f3')
    fig.update_yaxes(automargin=True,tickfont_color=NAVY,title_font_color=NAVY,
                     showline=True,linecolor='#c6d1d8',gridcolor='#edf1f3')
    return fig
