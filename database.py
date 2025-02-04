import pandas as pd
import os  
import datetime as dt

class db:
    def __init__(self):
        self.transactions = self.transactions_init()
        self.cc = pd.read_csv(r'db\country_codes.csv', index_col=0)
        self.customers = pd.read_csv(r'db\customers.csv', index_col=0)
        self.prod_info = pd.read_csv(r'db\prod_cat_info.csv')

    @staticmethod
    def transactions_init():
        src = r'db\transactions'
        transaction_frames = [pd.read_csv(os.path.join(src, filename), index_col=0) for filename in os.listdir(src)]
        transactions = pd.concat(transaction_frames, ignore_index=True)

        def convert_dates(x):
            try:
                return dt.datetime.strptime(x, '%d-%m-%Y')
            except:
                return dt.datetime.strptime(x, '%d/%m/%Y')

        transactions['tran_date'] = transactions['tran_date'].apply(lambda x: convert_dates(x))
        return transactions

    def merge(self):
        df = self.transactions.join(
            self.prod_info.drop_duplicates(subset=['prod_cat_code'])
            .set_index('prod_cat_code')['prod_cat'], on='prod_cat_code', how='left'
        )
        df = df.join(
            self.prod_info.drop_duplicates(subset=['prod_sub_cat_code'])
            .set_index('prod_sub_cat_code')['prod_subcat'], on='prod_subcat_code', how='left'
        )
        df = df.join(
            self.customers.join(self.cc, on='country_code')
            .set_index('customer_Id'), on='cust_id'
        )

        df['total_amt'] = df['total_amt'] / 1000
        df['tran_date'] = pd.to_datetime(df['tran_date'], errors='coerce')
        self.merged = df

        required_columns = ['Store_type', 'cust_id', 'transaction_id', 'total_amt']
        missing_columns = [col for col in required_columns if col not in self.merged.columns]

        if missing_columns:
            print(f"Brakujące kolumny: {missing_columns}")
        else:
            print("Wszystkie wymagane kolumny są obecne")

        missing_data = self.merged[required_columns].isnull().sum()

        if missing_data.any():
            print("Brakujące dane w kolumnach:")
            print(missing_data[missing_data > 0])
        else:
            print("Brakujące dane w wymaganych kolumnach: brak")   

        print("Podgląd danych po scaleniu:")
        print(self.merged.head())
        print("Zakres dat:", self.merged['tran_date'].min(), self.merged['tran_date'].max())
    
        return self.merged

        
