# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 10:03:56 2024

@author: hbotha
"""

import pandas as pd
import sqlite3
from datetime import datetime

def main(db_path, df, sn_value, wo_value):
    judgement = append_db(db_path, df, sn_value, wo_value)
    output_df = get_db_entry(db_path)
    return output_df, judgement
    
    
def append_db(db_path, df, sn_value, wo_value):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS VS_Results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifier TEXT NOT NULL,
        workorder TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        judgement TEXT NOT NULL
    )''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS VS_Result_Details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vs_result_id INTEGER,
        result_name TEXT NOT NULL,
        result_value TEXT,
        view INTEGER NOT NULL,
        FOREIGN KEY (vs_result_id) REFERENCES VS_Results (id)
    )''')
    
    judgement = get_judgement(df)
    timestamp = datetime.now().isoformat()
    
    cursor.execute('''INSERT INTO VS_Results (identifier, workorder, timestamp, judgement)
                   VALUES (?, ?, ?, ?)
                   ''',
                  (sn_value, wo_value, timestamp, judgement)
                  )
    
    vs_result_id = cursor.lastrowid
    for _, row in df.iterrows():
        result_name = row['Result Name']
        result_value = row['Result']
        current_view = row['View']
    
        cursor.execute('''
                       INSERT INTO VS_Result_Details (vs_result_id, result_name, result_value, view) 
                       VALUES (?, ?, ?, ?)
                       ''',
                       (vs_result_id, result_name, result_value, current_view)
                       )
    conn.commit()
    conn.close()
    return judgement

def get_db_entry(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Get the latest entry from VS_Results
    cursor.execute('''
    SELECT id, identifier, timestamp 
    FROM VS_Results 
    ORDER BY timestamp DESC 
    LIMIT 1
    ''')
    main_result = cursor.fetchone()
    
    if main_result:
        vs_result_id, sn_value, timestamp = main_result

        cursor.execute('''
        SELECT result_name, result_value, view
        FROM VS_Result_Details 
        WHERE vs_result_id = ?
        ORDER BY view, id
        ''', 
        (vs_result_id,)
        )
        details = cursor.fetchall()

        df = pd.DataFrame(details, columns=['Name', 'Result', 'View'])
        df['sn_value'] = sn_value
        df['timestamp'] = timestamp
    else:
        df = pd.DataFrame()
    
    df['Result'].loc[(df['Name'] == 'Inspector Override') & (df['Result'].str.contains('0'))] = 'FALSE'
    df['Result'].loc[(df['Name'] == 'Inspector Override') & (df['Result'].str.contains('1'))] = 'TRUE'
    
    # Replace 1 w/ PASS, 0 w/ FAIL
    df.loc[df['Result'] == '1', 'Result'] = 'PASS'
    df.loc[df['Result'] == '0', 'Result'] = 'FAIL'

    conn.close()
    return df
    
def get_judgement(df):
    judgement_df = df[df['Result Name']=='Overall Judgement'].dropna(how='any')
    if judgement_df['Result'].astype(int).sum() == len(judgement_df):
        judgement = 'PASS'
        if df['Result'][df['Result Name']=='Inspector Override'].dropna(how='any').astype(int).sum() > 0:
            judgement = 'PASS (Overridden)'
    else:
        judgement = 'FAIL'
    return judgement
