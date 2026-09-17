import io
import zipfile
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from revenue import generate_data, balances, movement, monthly_metrics, cohorts, MONTHS
from chart_style import style_chart, NAVY, TEAL, CORAL

st.set_page_config(page_title='Revenue Atlas | Commercial Analytics',page_icon='◈',layout='wide')
st.markdown('''<style>
.block-container {max-width:1400px;padding-top:2.2rem;padding-bottom:3rem;}
h1,h2,h3 {letter-spacing:-.025em;}
[data-testid="stMetric"] {background:#fff;border:1px solid #dce5e8;border-radius:12px;padding:18px;}
[data-testid="stMetricLabel"] {color:#516575;}
[data-testid="stMetricValue"] {color:#16324f;font-weight:650;}
[data-testid="stSidebar"] {border-right:1px solid #dce5e8;}
.eyebrow {color:#087f8c;font-size:.75rem;letter-spacing:.18em;font-weight:700;margin-bottom:8px;}
.hero-note {color:#516575;font-size:1.05rem;max-width:820px;}
</style>''',unsafe_allow_html=True)

@st.cache_data
def load(): return generate_data()
customers, subscriptions, ledger, cancellations = load()
with st.sidebar:
    st.markdown('### ◈ Revenue Atlas')
    st.caption('COMMERCIAL ANALYTICS WORKSPACE')
    page=st.radio('Explore',['Executive overview','Revenue movements','Customer retention','Customer explorer','Data & definitions'],label_visibility='collapsed')
    st.divider()
    month=st.selectbox('Reporting month',list(MONTHS),index=len(MONTHS)-1,format_func=lambda x:x.strftime('%B %Y'))
    region=st.multiselect('Region',sorted(customers.region.unique()),default=sorted(customers.region.unique()))
    segment=st.multiselect('Segment',sorted(customers.segment.unique()),default=sorted(customers.segment.unique()))
    channel=st.multiselect('Acquisition channel',sorted(customers.channel.unique()),default=sorted(customers.channel.unique()))
    st.divider()
    st.caption('SIMULATED BUSINESS · USD\n\n600 fictional accounts. Monthly subscriptions, January 2023–December 2025. No live company data.')

scope=customers[customers.region.isin(region)&customers.segment.isin(segment)&customers.channel.isin(channel)]
if scope.empty:
    st.info('No accounts match these filters. Select at least one region, segment and channel.')
    st.stop()
matrix=balances(scope,ledger[ledger.customer_id.isin(scope.customer_id)])
history=monthly_metrics(matrix,month)
k=movement(matrix,month)
known=scope[scope.cohort<=month]
if known.empty:
    st.info('No customers had joined in this reporting month. Choose a later month or broaden your filters.')
    st.stop()

st.markdown('<div class="eyebrow">REVENUE ATLAS / '+page.upper()+'</div>',unsafe_allow_html=True)
st.title(page)
st.markdown('<p class="hero-note">Understand where recurring revenue comes from, what changes it, and which customers stay.</p>',unsafe_allow_html=True)
st.caption(f'{month:%B %Y} · {len(known):,} acquired accounts in scope · USD · Synthetic portfolio demonstration')


def money(x): return f'${x:,.0f}'
def pct(x): return f'{x:.1f}%' if pd.notna(x) else '—'
def chart(fig,height=370): st.plotly_chart(style_chart(fig,height),use_container_width=True,theme=None)
def download(frame,label,filename):
    st.download_button(label,frame.to_csv(index=False).encode(),filename,'text/csv')
def line(frame,ys,names,colors,ytitle):
    fig=go.Figure()
    for y,name,color in zip(ys,names,colors):
        fig.add_trace(go.Scatter(x=frame.month,y=frame[y],name=name,mode='lines+markers',line=dict(color=color,width=3),marker_size=5))
    fig.update_layout(yaxis_title=ytitle,xaxis_title=None,hovermode='x unified')
    return fig

if page=='Executive overview':
    cols=st.columns(4)
    cols[0].metric('Monthly recurring revenue',money(k['closing']),money(k['closing']-k['opening'])+' vs prior month' if k['opening'] else None)
    cols[1].metric('Annualized run rate',money(k['closing']*12),help='Current MRR × 12. Not realized annual revenue or a forecast.')
    cols[2].metric('Active customers',f"{k['active']:,}")
    cols[3].metric('Net revenue retention',pct(k['nrr']),help='Current MRR from customers active last month / their prior MRR. Excludes new customers.')
    st.write('')
    left,right=st.columns([1.65,1])
    with left:
        st.subheader('The recurring revenue trajectory')
        chart(line(history,['closing'],['MRR'],[TEAL],'Monthly recurring revenue ($)'))
    with right:
        st.subheader('What changed this month')
        change=k['closing']-k['opening']
        st.markdown(f"**MRR {'increased' if change>=0 else 'decreased'} by {money(abs(change))}.**")
        st.write(f"New customers contributed {money(k['new'])}; existing customers added {money(k['expansion'])} through expansion.")
        st.write(f"Cancellations removed {money(k['churn'])}, while contraction removed {money(k['contraction'])}.")
        st.info('Inspect the revenue bridge to separate acquisition growth from retention performance.')
        st.caption('Narrative calculated from the selected month and filters.')
    left,right=st.columns(2)
    with left:
        st.subheader('Revenue mix by segment')
        mix=known.assign(mrr=known.customer_id.map(matrix[month])).groupby('segment').mrr.sum().sort_values()
        chart(go.Figure(go.Bar(x=mix.values,y=mix.index,orientation='h',marker_color=TEAL)).update_layout(xaxis_title='MRR ($)',yaxis_title=None),320)
    with right:
        st.subheader('Existing-customer revenue retention')
        fig=line(history,['nrr','grr'],['Net retention','Gross retention'],[TEAL,NAVY],'Retention (%)')
        fig.add_hline(y=100,line_dash='dot',line_color=CORAL)
        chart(fig,320)
    with st.expander('How to read these numbers'):
        st.write('Net retention can exceed 100% when expansion offsets losses. Gross retention excludes expansion. The first month has no opening base, so retention is unavailable. Figures are month-end balances, not cash collections.')
    download(history,'Download monthly metrics','monthly_metrics.csv')

elif page=='Revenue movements':
    st.subheader('From opening MRR to closing MRR')
    fig=go.Figure(go.Waterfall(x=['Opening','New','Expansion','Contraction','Churn','Closing'],
        measure=['absolute','relative','relative','relative','relative','total'],
        y=[k['opening'],k['new'],k['expansion'],-k['contraction'],-k['churn'],0],
        text=[money(k[x]) for x in ['opening','new','expansion','contraction','churn','closing']],
        textposition='outside',increasing_marker_color=TEAL,decreasing_marker_color=CORAL,totals_marker_color=NAVY,
        connector_line_color='#bac7ce'))
    fig.update_layout(yaxis_title='Monthly recurring revenue ($)',showlegend=False)
    chart(fig,450)
    st.caption('Opening + new + expansion − contraction − churn = closing MRR. New means first subscription month; this sample has no reactivations.')
    a,b,c=st.columns(3)
    a.metric('Expansion',money(k['expansion']))
    b.metric('Revenue lost',money(k['churn']+k['contraction']))
    c.metric('Customer churn rate',pct(k['logo_churn']),help='Customers lost this month / customers active at the start of the month.')
    st.subheader('Growth components over time')
    fig=go.Figure()
    for col,label,color,sign in [('new','New',TEAL,1),('expansion','Expansion','#66bfb5',1),('contraction','Contraction','#e8ad8b',-1),('churn','Churn',CORAL,-1)]:
        fig.add_bar(x=history.month,y=history[col]*sign,name=label,marker_color=color)
    fig.update_layout(barmode='relative',yaxis_title='Change in MRR ($)')
    chart(fig)
    download(history,'Download revenue bridge','revenue_bridge.csv')

elif page=='Customer retention':
    mode=st.radio('Retention measure',['Customer retention','Revenue retention'],horizontal=True)
    table,sizes=cohorts(scope,matrix,month,revenue=mode=='Revenue retention')
    st.subheader('How each acquisition cohort develops')
    st.caption('Rows group customers by first subscription month. Columns show months since joining. Blank cells are not yet observed, not zero retention.')
    z=table.to_numpy()
    labels=[f'{row} · {sizes[row]} accounts' for row in table.index]
    fig=go.Figure(go.Heatmap(z=z,x=[f'M{c}' for c in table.columns],y=labels,
        colorscale=[[0,'#f0f5f5'],[.5,'#71b8b5'],[1,TEAL]],zmin=0,zmax=max(100,float(np.nanmax(z))),
        colorbar=dict(title='%'),hoverongaps=False,
        hovertemplate='%{y}<br>%{x}: %{z:.1f}%<extra></extra>'))
    fig.update_layout(xaxis_title='Months since first subscription',yaxis=dict(autorange='reversed'))
    chart(fig,max(440,len(table)*25+140))
    st.caption('Customer retention divides active accounts by the original cohort size. Revenue retention divides current cohort MRR by its first-month MRR; expansion can take it above 100%. Small cohorts can fluctuate sharply.')
    st.subheader('Compare at the same customer age')
    age=st.selectbox('Months after joining',list(table.columns),index=min(6,len(table.columns)-1))
    observed=table[age].dropna().rename('retention_pct').rename_axis('cohort').reset_index()
    observed['starting_accounts']=observed.cohort.map(sizes)
    st.dataframe(observed.round(1),hide_index=True,use_container_width=True)
    download(table.reset_index(names='cohort'),'Download cohort retention','cohort_retention.csv')

elif page=='Customer explorer':
    st.subheader('Trace the account behind the aggregate')
    search=st.text_input('Search account name or ID')
    accounts=known.assign(current_mrr=known.customer_id.map(matrix[month]))
    accounts['status']=np.where(accounts.current_mrr>0,'Active','Cancelled')
    if search: accounts=accounts[accounts.account.str.contains(search,case=False,regex=False)|accounts.customer_id.str.contains(search,case=False,regex=False)]
    if accounts.empty:
        st.info('No accounts match this search.'); st.stop()
    st.dataframe(accounts.sort_values('current_mrr',ascending=False),hide_index=True,use_container_width=True)
    cid=st.selectbox('Inspect account',accounts.customer_id,format_func=lambda x:accounts.set_index('customer_id').loc[x,'account']+' · '+x)
    row=accounts.set_index('customer_id').loc[cid]
    st.caption(f"{row['segment']} · {row['region']} · acquired {row['cohort']:%B %Y} · {row['status']}")
    account_history=matrix.loc[cid, (matrix.columns>=row['cohort']) & (matrix.columns<=month)].rename('mrr').reset_index()
    account_history.columns=['month','mrr']
    chart(line(account_history,['mrr'],['Account MRR'],[TEAL],'MRR ($)'))
    st.subheader('Supporting invoices through the reporting month')
    invoices=ledger[(ledger.customer_id==cid)&(ledger.month<=month)]
    st.dataframe(invoices,hide_index=True,use_container_width=True)
    download(accounts,'Download selected accounts','accounts.csv')

else:
    st.subheader('A transparent, reproducible demonstration')
    st.write('Revenue Atlas models a fictional monthly subscription business. Every invoice joins to a subscription and account. Amounts are USD, with no taxes, discounts, annual contracts, delinquency or proration. Cancellations take effect at the beginning of a month; no invoice is generated for that month.')
    st.write('The generator uses seed 42. Account segments affect starting prices and monthly cancellation probabilities; customers can expand or contract. These are illustrative assumptions, not estimated behavior or evidence of commercial impact.')
    st.dataframe(pd.DataFrame([
        ['MRR','Sum of active monthly subscription amounts at month end'],
        ['Annualized run rate','MRR × 12; not realized revenue or a forecast'],
        ['NRR','Current MRR from the opening customer base / opening MRR'],
        ['GRR','(Opening MRR − contraction − churn) / opening MRR'],
        ['Customer churn','Lost opening customers / opening active customers'],
        ['Cohort retention','Surviving customers / original customers in that acquisition month'],
    ],columns=['Metric','Definition']),hide_index=True,use_container_width=True)
    st.info('Filters use fixed acquisition attributes and apply to both sides of comparisons. Reporting month limits charts and exports; future cohort ages stay blank. No targets or predictive risk scores are invented.')
    st.subheader('Download the linked source tables')
    st.caption('Export respects the current dimension filters and reporting month.')
    ids=set(known.customer_id)
    subs=subscriptions[subscriptions.customer_id.isin(ids)].copy()
    subs.loc[subs.cancellation_month>month,'cancellation_month']=pd.NaT
    tables={'customers':known,'subscriptions':subs,
        'invoices':ledger[ledger.customer_id.isin(ids)&(ledger.month<=month)],
        'cancellations':cancellations[cancellations.customer_id.isin(ids)&(cancellations.month<=month)]}
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w',zipfile.ZIP_DEFLATED) as z:
        for name,frame in tables.items(): z.writestr(name+'.csv',frame.to_csv(index=False))
    st.download_button('Download source tables (.zip)',buf.getvalue(),'revenue_atlas_source.zip','application/zip')

st.divider()
st.caption('REVENUE ATLAS · Built by Amit Kumar · Simulated data, explicit definitions, traceable results')
st.markdown('[Portfolio](https://amitkumaranalytics.com) · [Source code](https://github.com/amit1820/interactive-bi-analytics-app)')
