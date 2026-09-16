# app.py - Interactive BI Analytics Dashboard
import streamlit as st
from chart_style import style_chart
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from metrics import previous_period, coverage_complete, percentage_change, profit_margin
import numpy as np

# Page config
st.set_page_config(
    page_title="Business Intelligence Dashboard",
    layout="wide",
    page_icon="chart_with_upwards_trend"
)

# Professional CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #f8f9fa;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #2c3e50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.875rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: #212529;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
    }
    
    .metric-change {
        color: #28a745;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .metric-change.negative {
        color: #dc3545;
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    .sidebar .sidebar-content {
        background-color: #2c3e50;
    }
    
    h1 {
        color: #212529;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    h2 {
        color: #495057;
        font-weight: 600;
        font-size: 1.25rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #6c757d;
        font-weight: 500;
        font-size: 1rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 1.5rem;
        background-color: white;
        border-radius: 4px;
        color: #495057;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2c3e50;
        color: white;
    }
    
    .dataframe {
        font-size: 0.875rem;
    }
</style>
""", unsafe_allow_html=True)

# Generate realistic sample data
@st.cache_data
def load_data():
    """Load realistic business data"""
    np.random.seed(42)
    
    # Generate 2 years of daily data
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    
    # Create realistic patterns
    base_revenue = 25000
    trend = np.linspace(0, 5000, len(dates))
    seasonality = 5000 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365)
    noise = np.random.normal(0, 2000, len(dates))
    
    data = pd.DataFrame({
        'Date': dates,
        'Revenue': (base_revenue + trend + seasonality + noise).clip(min=5000),
        'Region': np.random.choice(['North America', 'Europe', 'Asia Pacific', 'Latin America'], len(dates)),
        'Product': np.random.choice(['Analytics Platform', 'Data Integration', 'ML Suite', 'Reporting Tools'], len(dates)),
        'Customer_Segment': np.random.choice(['Enterprise', 'Mid-Market', 'Small Business'], len(dates)),
        'Channel': np.random.choice(['Direct Sales', 'Partner', 'Online'], len(dates))
    })
    
    # Calculate orders based on revenue with some randomness
    data['Orders'] = (data['Revenue'] / np.random.uniform(80, 150, len(dates))).astype(int)
    data['Cost'] = data['Revenue'] * np.random.uniform(0.4, 0.6, len(dates))
    data['Profit'] = data['Revenue'] - data['Cost']
    
    # Add time-based fields
    data['Month'] = data['Date'].dt.to_period('M').astype(str)
    data['Quarter'] = data['Date'].dt.to_period('Q').astype(str)
    data['Year'] = data['Date'].dt.year
    data['Day_of_Week'] = data['Date'].dt.day_name()
    data['Week_Number'] = data['Date'].dt.isocalendar().week
    
    # Calculated metrics
    data['Avg_Order_Value'] = data['Revenue'] / data['Orders']
    data['Profit_Margin'] = (data['Profit'] / data['Revenue'] * 100)
    
    return data

# Load data
df = load_data()

# Header
st.title("Business Intelligence Dashboard")
st.markdown("Interactive analytics using synthetic daily observations (2023-2024)")
st.markdown("---")

# Sidebar filters
with st.sidebar:
    st.header("Filters and Options")
    
    # Date range with presets
    st.subheader("Time Period")
    date_preset = st.radio(
        "Quick Select",
        ["Last 30 Days", "Last 90 Days", "Last 6 Months", "Year to Date", "Custom Range"],
        index=2
    )
    
    if date_preset == "Custom Range":
        min_date = df['Date'].min().date()
        max_date = df['Date'].max().date()
        date_range = st.date_input(
            "Select Date Range",
            value=(max_date - timedelta(days=180), max_date),
            min_value=min_date,
            max_value=max_date
        )
    else:
        max_date = df['Date'].max()
        if date_preset == "Last 30 Days":
            start_date = max_date - timedelta(days=29)
        elif date_preset == "Last 90 Days":
            start_date = max_date - timedelta(days=89)
        elif date_preset == "Last 6 Months":
            start_date = max_date - pd.DateOffset(months=6) + timedelta(days=1)
        else:  # Year to Date
            start_date = pd.Timestamp(f"{max_date.year}-01-01")
        date_range = (start_date.date(), max_date.date())
    
    st.markdown("---")
    
    # Dimension filters
    st.subheader("Dimensions")
    
    regions = st.multiselect(
        "Region",
        options=sorted(df['Region'].unique()),
        default=sorted(df['Region'].unique())
    )
    
    products = st.multiselect(
        "Product Line",
        options=sorted(df['Product'].unique()),
        default=sorted(df['Product'].unique())
    )
    
    segments = st.multiselect(
        "Customer Segment",
        options=sorted(df['Customer_Segment'].unique()),
        default=sorted(df['Customer_Segment'].unique())
    )
    
    channels = st.multiselect(
        "Sales Channel",
        options=sorted(df['Channel'].unique()),
        default=sorted(df['Channel'].unique())
    )
    
    st.markdown("---")
    
    # Comparison period
    st.subheader("Comparison")
    enable_comparison = st.checkbox("Compare with Previous Period")
    
    st.markdown("---")
    
    # View options
    st.subheader("Display Options")
    show_trend = st.checkbox("Show Trend Lines", value=True)
    aggregation_level = st.selectbox(
        "Aggregation Level",
        ["Daily", "Weekly", "Monthly"],
        index=2
    )

# A partially selected range must not silently switch to all-time data.
if len(date_range) != 2:
    st.info("Select both a start and an end date to view results.")
    st.stop()

start_date, end_date = date_range
if start_date > end_date:
    st.info("The end date must be on or after the start date.")
    st.stop()

dimension_mask = (
    df['Region'].isin(regions) & df['Product'].isin(products)
    & df['Customer_Segment'].isin(segments) & df['Channel'].isin(channels)
)
filtered_df = df.loc[
    dimension_mask & df['Date'].dt.date.between(start_date, end_date)
].copy()
if filtered_df.empty:
    st.info("No records match these filters. Select more dimensions or a wider date range.")
    st.stop()

st.caption(f"Selected period: {start_date:%d %b %Y} to {end_date:%d %b %Y} (inclusive).")
comparison_ready = False
if enable_comparison:
    comparison_start, comparison_end = previous_period(start_date, end_date)
    comparison_df = df.loc[
        dimension_mask & df['Date'].dt.date.between(comparison_start, comparison_end)
    ]
    st.caption(f"Previous period: {comparison_start:%d %b %Y} to {comparison_end:%d %b %Y} (inclusive).")
    if not (coverage_complete(df['Date'], comparison_start, comparison_end)
            and coverage_complete(df['Date'], start_date, end_date)):
        st.info("Comparison unavailable: the sample does not cover every date in both periods.")
    elif comparison_df.empty:
        st.info("Comparison unavailable: no previous-period records match these filters.")
    else:
        comparison_ready = True

# KPI Section
st.header("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

# Calculate KPIs
total_revenue = filtered_df['Revenue'].sum()
total_orders = filtered_df['Orders'].sum()
total_profit = filtered_df['Profit'].sum()
avg_profit_margin = profit_margin(total_profit, total_revenue)

if comparison_ready:
    comp_revenue = comparison_df['Revenue'].sum()
    comp_orders = comparison_df['Orders'].sum()
    comp_profit = comparison_df['Profit'].sum()
    comp_margin = profit_margin(comp_profit, comp_revenue)
    
    revenue_change = percentage_change(total_revenue, comp_revenue)
    orders_change = percentage_change(total_orders, comp_orders)
    profit_change = percentage_change(total_profit, comp_profit)
    margin_change = avg_profit_margin - comp_margin
else:
    revenue_change = orders_change = profit_change = margin_change = None

def metric_card(column, label, value, change, suffix="%"):
    change_html = ""
    if change is not None:
        css_class = "negative" if change < 0 else ""
        change_html = (
            f'<div class="metric-change {css_class}">'
            f'{change:+.1f}{suffix} vs Previous Period</div>'
        )
    elif comparison_ready:
        change_html = '<div class="metric-label">Change unavailable: zero or negative baseline</div>'
    with column:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>{change_html}</div>',
            unsafe_allow_html=True,
        )

metric_card(col1, "Total Revenue", f"${total_revenue:,.0f}", revenue_change)
metric_card(col2, "Total Orders", f"{total_orders:,}", orders_change)
metric_card(col3, "Total Profit", f"${total_profit:,.0f}", profit_change)
metric_card(col4, "Profit Margin", f"{avg_profit_margin:.1f}%", margin_change, "pp")
st.caption("Profit margin = total profit / total revenue. Margin changes are percentage points.")

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Product Analysis", "Customer Insights", "Detailed Data"])

with tab1:
    # Revenue trend
    st.subheader("Revenue Performance Over Time")
    
    # Aggregate based on selection
    if aggregation_level == "Daily":
        trend_data = filtered_df.groupby('Date').agg({
            'Revenue': 'sum',
            'Profit': 'sum',
            'Orders': 'sum'
        }).reset_index()
        x_col = 'Date'
    elif aggregation_level == "Weekly":
        filtered_df['Week'] = filtered_df['Date'].dt.to_period('W').astype(str)
        trend_data = filtered_df.groupby('Week').agg({
            'Revenue': 'sum',
            'Profit': 'sum',
            'Orders': 'sum'
        }).reset_index()
        x_col = 'Week'
    else:  # Monthly
        trend_data = filtered_df.groupby('Month').agg({
            'Revenue': 'sum',
            'Profit': 'sum',
            'Orders': 'sum'
        }).reset_index()
        x_col = 'Month'
    
    fig_revenue = go.Figure()
    
    fig_revenue.add_trace(go.Scatter(
        x=trend_data[x_col],
        y=trend_data['Revenue'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#2c3e50', width=2),
        marker=dict(size=6),
        hovertemplate='%{x}<br>Revenue: $%{y:,.0f}<extra></extra>'
    ))
    
    if show_trend and len(trend_data) >= 2:
        # Add trend line
        z = np.polyfit(range(len(trend_data)), trend_data['Revenue'], 1)
        p = np.poly1d(z)
        fig_revenue.add_trace(go.Scatter(
            x=trend_data[x_col],
            y=p(range(len(trend_data))),
            mode='lines',
            name='Trend',
            line=dict(color='#e74c3c', width=2, dash='dash'),
            hovertemplate='Trend: $%{y:,.0f}<extra></extra>'
        ))
    
    if show_trend and len(trend_data) < 2:
        st.caption("Trend line needs at least two time buckets; the selected data is still shown.")

    fig_revenue.update_layout(
        height=400,
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridcolor='#ecf0f1',
            title=aggregation_level
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#ecf0f1',
            title='Revenue ($)'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(style_chart(fig_revenue), use_container_width=True, theme=None)
    
    # Two column charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue Distribution by Region")
        region_data = filtered_df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)
        
        fig_region = go.Figure(data=[
            go.Bar(
                x=region_data.values,
                y=region_data.index,
                orientation='h',
                marker=dict(
                    color='#3498db',
                    line=dict(color='#2c3e50', width=1)
                ),
                hovertemplate='%{y}<br>Revenue: $%{x:,.0f}<extra></extra>'
            )
        ])
        
        fig_region.update_layout(
            height=350,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#ecf0f1', title='Revenue ($)'),
            yaxis=dict(title='Region'),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        
        st.plotly_chart(style_chart(fig_region), use_container_width=True, theme=None)
    
    with col2:
        st.subheader("Channel Performance")
        channel_data = filtered_df.groupby('Channel').agg({
            'Revenue': 'sum',
            'Orders': 'sum'
        }).reset_index()
        
        fig_channel = go.Figure(data=[
            go.Pie(
                labels=channel_data['Channel'],
                values=channel_data['Revenue'],
                hole=0.4,
                marker=dict(
                    colors=['#2c3e50', '#3498db', '#95a5a6'],
                    line=dict(color='white', width=2)
                ),
                hovertemplate='%{label}<br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>'
            )
        ])
        
        fig_channel.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            )
        )
        
        st.plotly_chart(style_chart(fig_channel), use_container_width=True, theme=None)

with tab2:
    st.subheader("Product Line Performance")
    
    # Product metrics
    product_metrics = filtered_df.groupby('Product').agg({
        'Revenue': 'sum',
        'Profit': 'sum',
        'Orders': 'sum'
    }).reset_index()
    
    product_metrics['Profit_Margin'] = product_metrics['Profit'] / product_metrics['Revenue'] * 100
    product_metrics['Avg_Order_Value'] = product_metrics['Revenue'] / product_metrics['Orders']
    product_metrics = product_metrics.sort_values('Revenue', ascending=False)
    
    # Product comparison chart
    fig_product = go.Figure()
    
    fig_product.add_trace(go.Bar(
        name='Revenue',
        x=product_metrics['Product'],
        y=product_metrics['Revenue'],
        marker_color='#2c3e50',
        yaxis='y',
        hovertemplate='Revenue: $%{y:,.0f}<extra></extra>'
    ))
    
    fig_product.add_trace(go.Scatter(
        name='Profit Margin',
        x=product_metrics['Product'],
        y=product_metrics['Profit_Margin'],
        marker_color='#e74c3c',
        yaxis='y2',
        mode='lines+markers',
        line=dict(width=3),
        marker=dict(size=10),
        hovertemplate='Profit Margin: %{y:.1f}%<extra></extra>'
    ))
    
    fig_product.update_layout(
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(title='Product Line'),
        yaxis=dict(
            title='Revenue ($)',
            showgrid=True,
            gridcolor='#ecf0f1'
        ),
        yaxis2=dict(
            title='Profit Margin (%)',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    st.plotly_chart(style_chart(fig_product), use_container_width=True, theme=None)
    
    # Product details table
    st.subheader("Product Performance Details")
    
    display_metrics = product_metrics.copy()
    display_metrics['Revenue'] = display_metrics['Revenue'].apply(lambda x: f"${x:,.0f}")
    display_metrics['Profit'] = display_metrics['Profit'].apply(lambda x: f"${x:,.0f}")
    display_metrics['Orders'] = display_metrics['Orders'].apply(lambda x: f"{x:,}")
    display_metrics['Profit_Margin'] = display_metrics['Profit_Margin'].apply(lambda x: f"{x:.1f}%")
    display_metrics['Avg_Order_Value'] = display_metrics['Avg_Order_Value'].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(
        display_metrics.rename(columns={
            'Product': 'Product Line',
            'Avg_Order_Value': 'AOV'
        }),
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.subheader("Customer Segment Analysis")
    
    # Segment performance
    segment_data = filtered_df.groupby('Customer_Segment').agg({
        'Revenue': 'sum',
        'Profit': 'sum',
        'Orders': 'sum'
    }).reset_index()
    
    segment_data['Avg_Order_Value'] = segment_data['Revenue'] / segment_data['Orders']
    segment_data = segment_data.sort_values('Revenue', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Segment revenue
        fig_segment = go.Figure(data=[
            go.Bar(
                x=segment_data['Customer_Segment'],
                y=segment_data['Revenue'],
                marker=dict(
                    color=['#2c3e50', '#34495e', '#7f8c8d'],
                    line=dict(color='white', width=1)
                ),
                text=segment_data['Revenue'],
                texttemplate='$%{text:,.0f}',
                textposition='outside',
                hovertemplate='%{x}<br>Revenue: $%{y:,.0f}<extra></extra>'
            )
        ])
        
        fig_segment.update_layout(
            height=350,
            title='Revenue by Customer Segment',
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(title='Customer Segment'),
            yaxis=dict(
                title='Revenue ($)',
                showgrid=True,
                gridcolor='#ecf0f1'
            ),
            showlegend=False
        )
        
        st.plotly_chart(style_chart(fig_segment), use_container_width=True, theme=None)
    
    with col2:
        # AOV comparison
        fig_aov = go.Figure(data=[
            go.Bar(
                x=segment_data['Customer_Segment'],
                y=segment_data['Avg_Order_Value'],
                marker=dict(
                    color=['#3498db', '#5dade2', '#85c1e9'],
                    line=dict(color='white', width=1)
                ),
                text=segment_data['Avg_Order_Value'],
                texttemplate='$%{text:,.0f}',
                textposition='outside',
                hovertemplate='%{x}<br>AOV: $%{y:,.0f}<extra></extra>'
            )
        ])
        
        fig_aov.update_layout(
            height=350,
            title='Average Order Value by Segment',
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(title='Customer Segment'),
            yaxis=dict(
                title='Average Order Value ($)',
                showgrid=True,
                gridcolor='#ecf0f1'
            ),
            showlegend=False
        )
        
        st.plotly_chart(style_chart(fig_aov), use_container_width=True, theme=None)

with tab4:
    st.subheader("Detailed Daily Observations")
    
    # Options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_rows = st.selectbox(
            "Rows to display",
            [10, 25, 50, 100, "All"],
            index=1
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ['Date', 'Revenue', 'Profit', 'Orders'],
            index=1
        )
    
    with col3:
        sort_order = st.radio(
            "Order",
            ['Descending', 'Ascending'],
            horizontal=True
        )
    
    # Prepare data
    display_df = filtered_df.copy()
    display_df = display_df.sort_values(
        sort_by,
        ascending=(sort_order == 'Ascending')
    )
    
    if show_rows != "All":
        display_df = display_df.head(show_rows)
    
    # Format for display
    display_columns = ['Date', 'Revenue', 'Profit', 'Orders', 'Profit_Margin', 
                      'Region', 'Product', 'Customer_Segment', 'Channel']
    display_df = display_df[display_columns].copy()
    
    st.dataframe(
        display_df.assign(**{column: display_df[column].map(fmt.format) for column, fmt in {
            'Revenue': '${:,.0f}',
            'Profit': '${:,.0f}',
            'Orders': '{:,}',
            'Profit_Margin': '{:.1f}%'
        }.items()}),
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Summary statistics
    st.subheader("Statistical Summary")
    
    summary_stats = filtered_df[['Revenue', 'Profit', 'Orders', 'Profit_Margin']].describe()
    st.dataframe(
        summary_stats.round(2),
        use_container_width=True
    )

# Export section
st.markdown("---")
st.header("Data Export")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # Export filtered data
    csv_filtered = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Export Filtered Data",
        data=csv_filtered,
        file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    # Export monthly summary
    monthly_summary = filtered_df.groupby('Month').agg({
        'Revenue': 'sum',
        'Profit': 'sum',
        'Orders': 'sum'
    }).reset_index()
    
    monthly_summary['Profit_Margin'] = monthly_summary['Profit'] / monthly_summary['Revenue'] * 100
    csv_summary = monthly_summary.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Export Monthly Summary",
        data=csv_summary,
        file_name=f"monthly_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col3:
    # Export product performance
    csv_product = product_metrics.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Export Product Analysis",
        data=csv_product,
        file_name=f"product_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col4:
    # Record count
    st.info(f"Total Records: {len(filtered_df):,}")

# Footer
st.markdown("---")
st.caption(f"View rendered: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Synthetic sample ends {df['Date'].max().strftime('%Y-%m-%d')}")

