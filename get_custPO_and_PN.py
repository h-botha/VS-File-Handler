# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 07:43:26 2025

@author: hbotha
"""

import pyodbc
import pandas as pd

def main(PN):
    cnxn = pyodbc.connect(driver='{SQL Server}', host=r'los-osos-06.loroot.local\alliance', database='Rantec', user='PartsAndOrders', password='generaluse')
    
    query = f'''
    SELECT SONumber, PartXReference
    FROM SODetail
    WHERE PartNumber = '{PN}'
    AND ClosedFlag = 'False'
    '''
    
    SODetail = pd.read_sql(query, cnxn).drop_duplicates()
    
    CustPN = SODetail['PartXReference'].drop_duplicates().sort_values().tolist()
    SODetail = SODetail['SONumber'].tolist()
    
    SONumbers = tuple(SODetail)
    
    custPO_query = f'''
    SELECT SONumber, CustomerPO
    FROM SOHeader
    WHERE SONumber IN {SONumbers}
    AND ClosedFlag = 'False'
    '''
    
    CustPO = pd.read_sql(custPO_query, cnxn)
    CustPO = CustPO['CustomerPO'].tolist()
    
    return [CustPO, CustPN]
    
    

if __name__ == "__main__":
    PN = 'PL39669'
    lists = main(PN)
    
    