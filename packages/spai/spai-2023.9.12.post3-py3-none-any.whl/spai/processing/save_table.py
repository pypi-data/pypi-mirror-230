import pandas as pd

def save_table(data, columns, table_name, storage):
    # columns number must be equal to data number of columns
    if len(columns) != len(data):
        raise ValueError("columns number must be equal to data number of columns")
    df = pd.DataFrame([data], columns=columns)                          
    storage.create(data=df, name=table_name)
    return df