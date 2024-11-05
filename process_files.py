# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 09:40:45 2024

@author: hbotha
"""
import pandas as pd
import numpy as np
import os


def transform_data(csv_files):
    order = [0,5,2,4,1,3]
    dfs = []

    for file in csv_files:
        data = pd.read_csv(file, header=None).transpose().values.flatten()

        df = pd.DataFrame(data.reshape(-1, 2), columns=['Result Name', 'Result'])
        df = df[df['Result Name'] != 'DrawShapes']

        
        df['idx'] = range(len(df))
        df['View'] = df['Result'].apply(lambda x: 
            1 if 'Label' in str(x) else
            2 if 'Connector' in str(x) else
            3 if 'WedgelockDown' in str(x) else
            4 if 'WedgelockUp' in str(x) else
            5 if 'EjectorUp' in str(x) else
            6 if 'EjectorDown' in str(x) else 0
        )
        df['View'] = df['View'][0]
        # df = df[df['Result Name'] != 'CSV ID']
        dfs.append(df)

    to_db_df = pd.concat([dfs[i] for i in order]).sort_values(['View', 'idx'])
    return to_db_df
    
def main(directory, csv_files):
    to_db_df = transform_data(csv_files)
    
    return(to_db_df)
                
# if __name__ == "__main__":
#     csv_files = [os.path.join(r'VS Output', file) for file in os.listdir(r'VS Output') if file.endswith('.csv')]
#     df = transform_data(csv_files)
