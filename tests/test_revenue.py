from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest
from revenue import generate_data, balances, movement, cohorts, MONTHS

@pytest.fixture(scope='module')
def dataset(): return generate_data()


def test_relational_integrity_and_billing(dataset):
    c,s,i,x=dataset
    assert len(c)==600 and c.customer_id.is_unique and s.subscription_id.is_unique and i.invoice_id.is_unique
    assert not i.duplicated(['customer_id','month']).any()
    assert set(i.customer_id)==set(c.customer_id)
    assert set(i.subscription_id)==set(s.subscription_id)
    assert (i.mrr==i.invoice_amount).all()
    assert (i.mrr>0).all()
    joined=i.merge(s,on=['customer_id','subscription_id'])
    assert (joined.month>=joined.start_month).all()
    assert (joined.cancellation_month.isna()|(joined.month<joined.cancellation_month)).all()
    assert len(x)==s.cancellation_month.notna().sum()
    for row in x.itertuples():
        prior=i[(i.customer_id==row.customer_id)&(i.month==row.month-pd.offsets.MonthBegin())]
        assert prior.mrr.iloc[0]==row.lost_mrr


def test_all_bridges_reconcile_in_each_segment(dataset):
    c,_,i,_=dataset
    for seg in [None,*c.segment.unique()]:
        subset=c if seg is None else c[c.segment==seg]
        matrix=balances(subset,i[i.customer_id.isin(subset.customer_id)])
        for month in MONTHS:
            k=movement(matrix,month)
            assert k['opening']+k['new']+k['expansion']-k['contraction']-k['churn']==k['closing']
            assert 0<=k['grr']<=100 or np.isnan(k['grr'])
            assert k['closing']==i[(i.customer_id.isin(subset.customer_id))&(i.month==month)].invoice_amount.sum()


def test_known_movement_fixture():
    # Existing expansion, contraction, cancellation and a new customer.
    matrix=pd.DataFrame({MONTHS[0]:[100,200,300,0],MONTHS[1]:[150,180,0,90]})
    k=movement(matrix,MONTHS[1])
    assert [k[x] for x in ['opening','new','expansion','contraction','churn','closing']]==[600,90,50,20,300,420]
    assert k['nrr']==pytest.approx(55)
    assert k['grr']==pytest.approx(280/600*100)
    assert k['logo_churn']==pytest.approx(100/3)


def test_cohorts_do_not_use_future_data(dataset):
    c,_,i,_=dataset
    m=balances(c,i)
    for revenue in [False,True]:
        table,_=cohorts(c,m,MONTHS[12],revenue)
        assert (table[0]==100).all()
        assert table.loc['2024-01',1:].isna().all()
        assert table.index.max()=='2024-01'
        if not revenue: assert (table.diff(axis=1).drop(columns=0).fillna(0)<=0).all().all()


def test_reproducible(dataset):
    for expected,actual in zip(dataset,generate_data()):pd.testing.assert_frame_equal(expected,actual)


APP=str(Path(__file__).resolve().parents[1]/'app.py')
@pytest.mark.parametrize('page',['Executive overview','Revenue movements','Customer retention','Customer explorer','Data & definitions'])
def test_pages_and_early_month(page):
    at=AppTest.from_file(APP,default_timeout=30).run()
    at.sidebar.radio[0].set_value(page).run()
    assert not at.exception
    at.sidebar.selectbox[0].select_index(0).run()
    assert not at.exception


def test_empty_filters_and_recovery():
    at=AppTest.from_file(APP,default_timeout=30).run()
    regions=at.sidebar.multiselect[0].options
    at.sidebar.multiselect[0].set_value([]).run()
    assert not at.exception and 'No accounts match' in at.info[0].value
    at.sidebar.multiselect[0].set_value(regions).run()
    assert not at.exception and len(at.metric)==4


def test_retention_switch_and_search():
    at=AppTest.from_file(APP,default_timeout=30).run()
    at.sidebar.radio[0].set_value('Customer retention').run()
    next(r for r in at.radio if r.label=='Retention measure').set_value('Revenue retention').run()
    assert not at.exception
    at.sidebar.radio[0].set_value('Customer explorer').run()
    at.text_input[0].set_value('not-an-account').run()
    assert not at.exception and 'No accounts match' in at.info[0].value
