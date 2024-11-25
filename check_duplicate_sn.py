# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 14:33:53 2024

@author: hbotha
"""

import pyodbc
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

def checkDuplicateSN(SN):
    cnxn = pyodbc.connect(driver='{SQL Server}', host=r'los-osos-06.loroot.local\alliance', database='Rantec', user='PartsAndOrders', password='generaluse')
    
    query = '''
    SELECT TransactionID, SNLotNumber
    FROM TransactionDetail
    WHERE PartNumber = 'PL39669'
    AND ToDepartment = 'COGS'
    '''
    
    df = pd.read_sql(query, cnxn)
    cnxn.close()
    
    SN = int(SN)
    df['SNLotNumber'] = pd.to_numeric(df['SNLotNumber'])
    
    df = df[df['SNLotNumber'] == SN].head()
    
    if df.shape[0] > 0:
        txID = df.iloc[0]['TransactionID']
        print(f'''
              WARNING: DUPLICATE SN DETECTED! THIS SN WAS SENT TO CUSTOMER!
              \nDo not ship without verifying that this serial number (SN {SN}) has not already been shipped. Reference Alliance Transaction ID {txID}. 
              \nSN {SN}
              \nTransaction ID {txID}
              ''')
        return str(txID)
    else:
        return 0


if __name__ == "__main__":
    
    SN = '4005'
    df = checkDuplicateSN(SN)