import requests
import pickle
import pandas as pd


def get_finlab_data(dataset):
    url = f"https://github.com/twfxjjbw/stockinfo/raw/main/{dataset}.bin"
    r = requests.get(url)
    return pickle.loads(r.content)


if __name__ == "__main__":
    broker_mapping = get_finlab_data("broker_mapping")
    broker_transactions = get_finlab_data("broker_transactions")
    broker_transactions["date"] = pd.to_datetime(broker_transactions.index)
    broker_transactions = broker_transactions.merge(
        broker_mapping, on="broker", how="left"
    )
    broker_transactions.set_index("date", inplace=True)
    print(broker_transactions)
    selected_data = broker_transactions.loc[
        (broker_transactions.index == "2023-08-02")
        & (broker_transactions["stock_id"] == "2330")
    ]

    # selected_data = broker_transactions.loc['2023-07-28']
    print(selected_data.to_markdown())
