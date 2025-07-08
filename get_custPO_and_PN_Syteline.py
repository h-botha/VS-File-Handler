# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 07:43:26 2025

@author: hbotha
"""

import pyodbc
import pandas as pd
import requests

# OLD ALLIANCE INTERFACE:
# def main(PN):
#     cnxn = pyodbc.connect(driver='{SQL Server}', host=r'los-osos-06.loroot.local\alliance', database='Rantec', user='PartsAndOrders', password='generaluse')
    
#     query = f'''
#     SELECT SONumber, PartXReference
#     FROM SODetail
#     WHERE PartNumber = '{PN}'
#     AND ClosedFlag = 'False'
#     '''
    
#     SODetail = pd.read_sql(query, cnxn).drop_duplicates()
    
#     CustPN = SODetail['PartXReference'].drop_duplicates().sort_values().tolist()
#     SODetail = SODetail['SONumber'].tolist()
#     if len(SODetail) > 1:
#         SONumbers = tuple(SODetail)
    
#         custPO_query = f'''
#         SELECT SONumber, CustomerPO
#         FROM SOHeader
#         WHERE SONumber IN {SONumbers}
#         AND ClosedFlag = 'False'
#         '''
#     else:
#         SONumber = SODetail[0]
    
#         custPO_query = f'''
#         SELECT SONumber, CustomerPO
#         FROM SOHeader
#         WHERE SONumber = '{SONumber}'
#         AND ClosedFlag = 'False'
#         '''
    
#     CustPO = pd.read_sql(custPO_query, cnxn)
#     CustPO = CustPO['CustomerPO'].tolist()
    
#     return [CustPO, CustPN]
    
def main(PN):
    headers = {
        'Authorization': r'b/XdI6IQzCviZOGJ0E+002DoKUFOPmVDkwpQDbQjm3w/qkdxDUzmqvSYEZDCmJGWpA23OTlhFpxRHFz3WOsvay8V58XdIp/UIsr5TpCdMwvoO+jzjloJpqRoP6SsKySXtOhenXX+H16k2QrA3xgq+ndVVyqNZEqTN9l0Etwi2Z5tSKxCCew3+O1e+RcbUNJbOt62vDwNfMsco4sXkBnbKfgGeKutyPcF38tDBFoFvjMoBEbT5Zi1UXc5HhUybapY2eeJMpF33MpkON4opJp7AKUeAsFVBLKEuHVMHfhZSzaaIsz0D0ndOacBWfdT6Rb33cx/JGjiSLPs00B2gZUConN54TJvrsChHc7YbztWUddNsDYahPEW5KX6q6RlNYtJHXyKdicmLfRU0Ckw5JZcDrwqn1PcC/KL6zh1X9cePJgzD+ixqkgGGCVuCvFWQqrq2e84ISx5IJg3KBlyEsfmTAuaocXKmGIlWHbkc01G8Rinb3moHoKJPayV8Fi76TVu',
        'x-infor-MongooseConfig': 'PRD_SL_RANTEC'
        }
    response = requests.get(rf"http://INFORUTILPRD/IDORequestService/ido/load/SLCOItems?filter=Item='{PN}' AND DerCoitemShipped ='0'&properties=DerCustPo, CustItem", headers=headers)
    data = response.json()
    df = pd.json_normalize(data)
    df = pd.json_normalize(df['Items'][0])
    df = df[['DerCustPo', 'CustItem']]
    CustPO = df['DerCustPo'].drop_duplicates().tolist()
    CustPN = df['CustItem'].drop_duplicates().tolist()
    return [CustPO, CustPN]

if __name__ == "__main__":
    PN = 'PL38509'
    lists = main(PN)
    print(lists)
    
    