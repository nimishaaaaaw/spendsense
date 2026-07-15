import pandas as pd
from app.core.categorizer import categorize_df

raw = pd.read_csv('data/transactions_raw.csv')
truth = pd.read_csv('data/transactions_truth.csv')

assert len(raw) == len(truth), "row count mismatch"

result = categorize_df(raw).reset_index(drop=True)
truth = truth.reset_index(drop=True)

correct = (result['Merchant'] == truth['TrueMerchant']).sum()
total = len(result)
print(f'Merchant accuracy: {correct}/{total} = {correct/total*100:.1f}%')

wrong = pd.DataFrame({
    'Description': raw['Description'],
    'Predicted': result['Merchant'],
    'TrueMerchant': truth['TrueMerchant'],
})[result['Merchant'] != truth['TrueMerchant']]
print(wrong.to_string())