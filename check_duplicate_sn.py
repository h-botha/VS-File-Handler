# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 14:33:53 2024

@author: hbotha
"""

import pyodbc
import pandas as pd
import warnings
import requests

warnings.filterwarnings('ignore')

def checkDuplicateSN(PN, SN):
    
    df = QueryAlliance(PN, SN)
    df2 = QuerySyteline(PN, SN)
    
    dfs = [df, df2]
    
    for df in dfs:
        if df.shape[0] > 0:
            
            txID = df.iloc[0]['TransactionID']
            if "." in str(txID):
                AllianceOrSyteline = 'Alliance'
            else:
                AllianceOrSyteline = 'Syteline'
                
            print(f'''
                  WARNING: DUPLICATE SN DETECTED! THIS SN WAS SENT TO CUSTOMER!
                  \nDo not ship without verifying that this serial number (SN {SN}) has not already been shipped. Reference {AllianceOrSyteline} Transaction ID {txID}. 
                  \nSN {SN}
                  \nTransaction ID {txID}
                  ''')
                  
            return str(txID)
    else:
        return 0

def QuerySyteline(PN, SN):
    headers = {
        'Authorization': r'b/XdI6IQzCviZOGJ0E+002DoKUFOPmVDkwpQDbQjm3w/qkdxDUzmqvSYEZDCmJGWpA23OTlhFpxRHFz3WOsvay8V58XdIp/UIsr5TpCdMwvoO+jzjloJpqRoP6SsKySXtOhenXX+H16k2QrA3xgq+ndVVyqNZEqTN9l0Etwi2Z5tSKxCCew3+O1e+RcbUNJbOt62vDwNfMsco4sXkBnbKfgGeKutyPcF38tDBFoFvjMoBEbT5Zi1UXc5HhUybapY2eeJMpF33MpkON4opJp7AKUeAsFVBLKEuHVMHfhZSzaaIsz0D0ndOacBWfdT6Rb33cx/JGjiSLPs00B2gZUConN54TJvrsChHc7YbztWUddNsDYahPEW5KX6q6RlNYtJHXyKdicmLfRU0Ckw5JZcDrwqn1PcC/KL6zh1X9cePJgzD+ixqkgGGCVuCvFWQqrq2e84ISx5IJg3KBlyEsfmTAuaocXKmGIlWHbkc01G8Rinb3moHoKJPayV8Fi76TVu',
        'x-infor-MongooseConfig': 'PRD_SL_RANTEC'
        }
    response = requests.get(rf"http://INFORUTILPRD/IDORequestService/ido/load/SLSerials?properties=Item, SerNum, Stat, DerDestCustomer, TransNum&filter=Item = '{PN}' AND DerDestCustomer <> null", headers=headers)
    data = response.json()
    df = pd.json_normalize(data)
    df = pd.json_normalize(df['Items'][0])
    if df.shape[0] > 0:
        df['SerNum'] = pd.to_numeric(df['SerNum'])
        df = df.rename(columns={'TransNum': 'TransactionID'})
    else:
        df = pd.DataFrame()
    
    return df
    
def QueryAlliance(PN, SN):
    cnxn = pyodbc.connect(driver='{SQL Server}', host=r'los-osos-06.loroot.local\alliance', database='Rantec', user='PartsAndOrders', password='generaluse')
    
    query = f'''
    SELECT TransactionID, SNLotNumber
    FROM TransactionDetail
    WHERE PartNumber = '{PN}'
    AND ToDepartment = 'COGS'
    '''
    
    df = pd.read_sql(query, cnxn)
    cnxn.close()
    
    SN = int(SN)
    df['SNLotNumber'] = pd.to_numeric(df['SNLotNumber'])
    
    df = df[df['SNLotNumber'] == SN].head()
    
    return df

if __name__ == "__main__":
    
    SN = '301'
    PN = 'PL38509'
    df = checkDuplicateSN(PN, SN)