import pandas as pd


# Loading data from a CSV file
def load_data(file_path: str):
    data = pd.read_csv(file_path)
    return data
