# -*- coding: utf-8 -*-
"""
Created on Tue Jul  8 09:07:34 2025

@author: hbotha
"""

import requests
import pandas as pd
import sqlite3

def QuerySyteline(PN, SN):
    headers = {
        'Authorization': r'b/XdI6IQzCviZOGJ0E+002DoKUFOPmVDkwpQDbQjm3w/qkdxDUzmqvSYEZDCmJGWpA23OTlhFpxRHFz3WOsvay8V58XdIp/UIsr5TpCdMwvoO+jzjloJpqRoP6SsKySXtOhenXX+H16k2QrA3xgq+ndVVyqNZEqTN9l0Etwi2Z5tSKxCCew3+O1e+RcbUNJbOt62vDwNfMsco4sXkBnbKfgGeKutyPcF38tDBFoFvjMoBEbT5Zi1UXc5HhUybapY2eeJMpF33MpkON4opJp7AKUeAsFVBLKEuHVMHfhZSzaaIsz0D0ndOacBWfdT6Rb33cx/JGjiSLPs00B2gZUConN54TJvrsChHc7YbztWUddNsDYahPEW5KX6q6RlNYtJHXyKdicmLfRU0Ckw5JZcDrwqn1PcC/KL6zh1X9cePJgzD+ixqkgGGCVuCvFWQqrq2e84ISx5IJg3KBlyEsfmTAuaocXKmGIlWHbkc01G8Rinb3moHoKJPayV8Fi76TVu',
        'x-infor-MongooseConfig': 'PRD_SL_RANTEC'
        }
    response = requests.get(rf"http://INFORUTILPRD/IDORequestService/ido/load/SLSerials?filter=Item='{PN}'&properties=RefNum, SerNum", headers=headers)
    data = response.json()
    df = pd.json_normalize(data)
    df = pd.json_normalize(df['Items'][0])
    df['SerNum'] = pd.to_numeric(df['SerNum'])
    
    try:
        WO = df[df['SerNum'] == int(SN)]['RefNum'].iloc[0]
    except Exception as e:
        print(e)
        print("fallback to legacy SN log...")
        WO = QuerySNLog(PN, SN)
    return WO

def QuerySNLog(PN, SN):
    SN = int(SN)
    sn_conn = sqlite3.connect(r'\\rantec-ut-fs\ftp image\db\sn_log.db')
    query = f"""
    SELECT *
    FROM SNs
    WHERE "P/N" = '{PN}'
    """
    sn_log = pd.read_sql(query, sn_conn)
    sn_log['S/N'] = pd.to_numeric(sn_log['S/N'])
    
    try:
        WO = sn_log[sn_log['S/N'] == SN]['WO'].iloc[0]
    except IndexError:
        # print('Serial Number Invalid. No Work Order attached.')
        WO = 'N/A'
    return WO
    
if __name__ == "__main__":
    PN = 'PL38509'
    SN = '3356'
    WO, sn_log = QuerySyteline(PN, SN)
