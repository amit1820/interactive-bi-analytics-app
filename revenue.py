"""Deterministic monthly subscription ledger and reconciled SaaS metrics."""
import numpy as np
import pandas as pd

MONTHS = pd.date_range('2023-01-01', '2025-12-01', freq='MS')


def generate_data(seed=42):
    rng = np.random.default_rng(seed)
    customers, subscriptions, ledger, cancellations = [], [], [], []
    for i in range(600):
        cid = f'AC-{i+1:04d}'
        start = int(rng.integers(0, 34))
        segment = rng.choice(['Enterprise', 'Growth', 'Starter'], p=[.18,.42,.4])
        region = rng.choice(['Europe', 'North America', 'Asia Pacific'])
        channel = rng.choice(['Direct', 'Partner', 'Organic'])
        base = {'Enterprise':2400, 'Growth':650, 'Starter':150}[segment]
        price = int(round(base * rng.uniform(.8,1.2)))
        customers.append(dict(customer_id=cid, account=f'Account {i+1:03d}', segment=segment,
                              region=region, channel=channel, cohort=MONTHS[start]))
        churn = None
        for j in range(start,len(MONTHS)):
            if j > start:
                risk = {'Enterprise':.012,'Growth':.025,'Starter':.042}[segment]
                if rng.random() < risk:
                    churn = MONTHS[j]
                    cancellations.append(dict(subscription_id=f'S-{cid}', customer_id=cid,
                                              month=churn, lost_mrr=price))
                    break
                movement = rng.random()
                if movement < .07:
                    price = int(round(price * 1.15))
                elif movement < .11:
                    price = max(20,int(round(price * .9)))
            ledger.append(dict(invoice_id=f'I-{cid}-{j:02d}', subscription_id=f'S-{cid}',
                               customer_id=cid, month=MONTHS[j], mrr=price, invoice_amount=price))
        subscriptions.append(dict(subscription_id=f'S-{cid}', customer_id=cid,
                                  start_month=MONTHS[start], cancellation_month=churn))
    return (pd.DataFrame(customers),pd.DataFrame(subscriptions),pd.DataFrame(ledger),
            pd.DataFrame(cancellations,columns=['subscription_id','customer_id','month','lost_mrr']))


def balances(customers, ledger):
    return ledger.pivot(index='customer_id',columns='month',values='mrr').reindex(
        index=customers.customer_id, columns=MONTHS).fillna(0)


def movement(matrix, month):
    month = pd.Timestamp(month)
    current = matrix[month]
    previous = matrix[month - pd.offsets.MonthBegin()] if month != MONTHS[0] else current * 0
    continuing = (previous > 0) & (current > 0)
    delta = current - previous
    opening = float(previous.sum())
    new = float(current[previous == 0].sum())
    expansion = float(delta[continuing & (delta > 0)].sum())
    contraction = float(-delta[continuing & (delta < 0)].sum())
    churn = float(previous[current == 0].sum())
    retained = float(current[previous > 0].sum())
    opening_accounts = int((previous > 0).sum())
    return dict(month=month, opening=opening, new=new, expansion=expansion,
                contraction=contraction, churn=churn, closing=float(current.sum()),
                active=int((current > 0).sum()),
                nrr=retained/opening*100 if opening else np.nan,
                grr=(opening-contraction-churn)/opening*100 if opening else np.nan,
                logo_churn=((previous > 0)&(current == 0)).sum()/opening_accounts*100 if opening_accounts else np.nan)


def monthly_metrics(matrix, end):
    return pd.DataFrame([movement(matrix,m) for m in MONTHS if m <= pd.Timestamp(end)])


def cohorts(customers, matrix, end, revenue=False):
    """Unobserved cohort ages stay NaN; denominator is original cohort size/MRR."""
    end = pd.Timestamp(end)
    result, sizes = {}, {}
    for cohort, group in customers[customers.cohort <= end].groupby('cohort'):
        block = matrix.loc[group.customer_id]
        sizes[cohort.strftime('%Y-%m')] = len(group)
        original = block[cohort].sum() if revenue else len(group)
        values = {}
        for age, month in enumerate(MONTHS[MONTHS >= cohort]):
            if month > end: break
            numerator = block[month].sum() if revenue else (block[month] > 0).sum()
            values[age] = numerator / original * 100
        result[cohort.strftime('%Y-%m')] = values
    return pd.DataFrame.from_dict(result,orient='index').sort_index(), sizes
