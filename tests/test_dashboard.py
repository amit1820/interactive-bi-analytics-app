from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from metrics import previous_period, coverage_complete, percentage_change, profit_margin

APP = str(Path(__file__).resolve().parents[1] / 'app.py')

@pytest.mark.parametrize('start,end', [(date(2024,3,1),date(2024,3,1)), (date(2024,3,1),date(2024,3,30)), (date(2024,1,1),date(2024,6,30))])
def test_equal_nonoverlapping_periods(start,end):
    a,b=previous_period(start,end)
    assert (b-a).days == (end-start).days
    assert b == start-timedelta(days=1)


def test_missing_date_is_incomplete_even_with_duplicate_rows():
    assert not coverage_complete(pd.to_datetime(['2024-01-01','2024-01-01','2024-01-03']),date(2024,1,1),date(2024,1,3))
    assert coverage_complete(pd.date_range('2024-01-01','2024-01-03'),date(2024,1,1),date(2024,1,3))


def test_metric_definitions():
    assert percentage_change(120,100) == 20
    assert percentage_change(120,0) is None
    assert percentage_change(120,-10) is None
    assert profit_margin(10+90,100+300) == 25


def app():
    probe = "\nfor key in ['comparison_ready', 'filtered_df', 'comparison_df', 'revenue_change', 'avg_profit_margin', 'product_metrics', 'monthly_summary', 'fig_revenue', 'df']:\n    if key in globals(): st.session_state[key] = globals()[key]\n"
    at=AppTest.from_string(Path(APP).read_text() + probe, default_timeout=30).run()
    assert not at.exception
    return at


def custom(at, dates):
    at.sidebar.radio[0].set_value('Custom Range').run()
    at.sidebar.date_input[0].set_value(dates).run()
    assert not at.exception
    return at


def test_default_and_comparison_match_totals():
    at=app()
    at.sidebar.checkbox[0].check().run()
    assert not at.exception
    assert at.session_state['comparison_ready']
    current=at.session_state['filtered_df']
    prior=at.session_state['comparison_df']
    assert len(current)==len(prior)
    assert at.session_state['revenue_change'] == pytest.approx((current.Revenue.sum()/prior.Revenue.sum()-1)*100)
    assert at.session_state['avg_profit_margin'] == pytest.approx(current.Profit.sum()/current.Revenue.sum()*100)
    for key in ['product_metrics','monthly_summary']:
        grouped=at.session_state[key]
        assert (grouped.Profit_Margin == grouped.Profit/grouped.Revenue*100).all()


@pytest.mark.parametrize('preset,days',[('Last 30 Days',30),('Last 90 Days',90)])
def test_presets_are_exact(preset,days):
    at=app()
    at.sidebar.radio[0].set_value(preset).run()
    assert not at.exception
    assert len(at.session_state['filtered_df'])==days


def test_empty_filter_and_recovery():
    at=app()
    options=at.sidebar.multiselect[0].options
    at.sidebar.multiselect[0].set_value([]).run()
    assert not at.exception
    assert 'No records match' in at.info[0].value
    assert len(at.get('plotly_chart'))==0
    at.sidebar.multiselect[0].set_value(options).run()
    assert not at.exception
    assert len(at.get('plotly_chart'))>0


@pytest.mark.parametrize('level',['Daily','Weekly','Monthly'])
def test_single_date_skips_trend(level):
    at=custom(app(),(date(2024,12,31),date(2024,12,31)))
    at.sidebar.selectbox[0].set_value(level).run()
    assert not at.exception
    assert len(at.session_state['fig_revenue'].data)==1
    assert len(at.session_state['filtered_df'])==1


def test_partial_date_range_does_not_show_all_time():
    at=custom(app(),(date(2024,12,1),))
    assert 'Select both' in at.info[0].value
    assert len(at.get('plotly_chart'))==0


def test_incomplete_comparison_is_hidden():
    at=custom(app(),(date(2023,1,1),date(2023,1,31)))
    at.sidebar.checkbox[0].check().run()
    assert not at.exception
    assert not at.session_state['comparison_ready']
    assert at.session_state['revenue_change'] is None
    assert 'does not cover' in at.info[0].value


def test_no_matching_prior_records_is_hidden():
    at=custom(app(),(date(2024,12,31),date(2024,12,31)))
    df=at.session_state['df']
    current=df.iloc[-1]
    previous=df.iloc[-2]
    dimensions=['Region','Product','Customer_Segment','Channel']
    i=next(i for i,d in enumerate(dimensions) if current[d]!=previous[d])
    at.sidebar.multiselect[i].set_value([current[dimensions[i]]]).run()
    at.sidebar.checkbox[0].check().run()
    assert not at.exception
    assert not at.session_state['comparison_ready']
    assert 'no previous-period records' in at.info[0].value
