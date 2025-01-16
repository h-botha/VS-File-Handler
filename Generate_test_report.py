# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 11:53:20 2024

@author: hbotha
"""
import os
import shutil
import pyodbc
import pandas as pd
from fpdf import FPDF
import warnings
import re
warnings.filterwarnings("ignore")

# ICP FAIL SN
# 003219

# ICP PASS SN
# 3368
    
def queryDB(SN, testdb):
    
    SN = str(int(SN)).zfill(6)
    
    # db_path = r"\\rantec-ut-fs\Utah Test Engineering$\ATE Test\Test Results\HDMSys ATE\L3Harris_ICP-TR3_TestLog.mdb"
    # db_path = r"V:\Public\Hendrik B\L3Harris_ICP-TR3_TestLog.mdb"
    # dst_path = r"L3Harris_ICP-TR3_TestLog.mdb"
    
    # db_copy_path = shutil.copyfile(db_path, dst_path)
    
    query=str("""
    SELECT `UnitID`.`WorkOrder`, `UnitID`.`PartNo`, `UnitID`.`SerNo`, `UnitID`.`OperatorID`, `UnitID`.`TestDate`, `UnitID`.`StartTime`, `UnitID`.`TestTime`, `UnitID`.`TestScript`, `UnitID`.`CustPartNo`, `UnitID`.`TestType`, `TestResults`.`TestStep`, `TestResults`.`TestRef`, `TestResults`.`TestName`, `TestResults`.`MeasVal`, `TestResults`.`Units`, `TestResults`.`Min`, `TestResults`.`Max`, `TestResults`.`Fail`, `TestResults`.`ETime`, `UnitID`.`SWVersion`, `UnitID`.`CustPO`, `UnitID`.`CustPartNo`, `UnitID`.`TestSystem`
    FROM   `TestResults` `TestResults` INNER JOIN `UnitID` `UnitID` ON `TestResults`.`TestID`=`UnitID`.`TestID`
    WHERE `UnitID`.`SerNo`="""+"'"+SN+"'")
    
    ICP_utah_tc_conn_str = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    rf"DBQ={testdb};ReadOnly=1"
    )
    
    try:
        cnxn = pyodbc.connect(ICP_utah_tc_conn_str, ReadOnly=True)
        df = pd.read_sql(query, cnxn)
        
    except Exception as e:
        print('Error', e)
    
    finally:
        cnxn.close()
    
    # os.remove(db_copy_path)
    
    df = df[df['TestDate'] == df['TestDate'].max()]
    return df

def getHeaderDF(df):
    df = df.loc[:, ~df.columns.duplicated()]
    hlist = df[[
                'WorkOrder',
                'TestType',
                'TestScript',
                'SWVersion',
                'PartNo',
                'CustPartNo',
                'CustPO',
                'SerNo',
                'TestDate',
                'TestTime',
                'OperatorID',
                'TestSystem']
               ].head(1).to_numpy().tolist()[0]
    hlist = ['8DXS5'] + hlist
    return hlist

def get_reportDF(df):
    df = df[['TestStep','TestRef','TestName','Min','Max','MeasVal','Units','Fail','ETime']].reset_index(drop='True')
    
    df['Min'][df['Min'] != ''] = df['Min']+df['Units']
    df['Max'][df['Max'] != ''] = df['Max']+df['Units']
    df['MeasVal'][df['MeasVal'] != ''] = df['MeasVal']+df['Units']
    
    if df['Fail'].eq('').all():
        judgement = 1
    else:
        judgement = 0
        
    df['Fail'][df['Fail'] == ''] = 'Pass'
    
    df[['Min', 'Max', 'MeasVal']] = df[['Min', 'Max', 'MeasVal']].applymap(lambda x: '0' if x == 'False' else x)
    df[['Min', 'Max', 'MeasVal']] = df[['Min', 'Max', 'MeasVal']].applymap(lambda x: '1' if x == 'True' else x)

    df['MeasVal'] = df[['MeasVal']].applymap(lambda x: 'Erasing' if 'Erasing' in x else x)
    
    df = df[['TestStep','TestRef','TestName','Min','Max','MeasVal','Fail','ETime']].sort_values(by='TestStep')
    
    return df, judgement
    

class PDF(FPDF):
    def __init__(self, H, judgement):
            super().__init__('L')
            self.H = H
            self.judgement = judgement
    
    def header(self):
        if self.judgement == 1:
            PF = 'PASS'
            RGB = [100, 237, 121]
        else:
            PF = 'FAIL'
            RGB = [232, 74, 46]
        
        if self.page_no() == 1:
            self.set_font('Times', 'B', 12)
            self.set_x(110)
            self.cell(80, 7.5, 'Rantec Power Systems Test Report', 0, 1, 'C')
            self.set_x(135)
            # self.set_xy(250, 3)
            self.set_fill_color(RGB[0], RGB[1], RGB[2])
            self.cell(30, 5, str(PF), 1, 0, 'C', True)
            header_offset = 15
        
        self.set_text_color(0, 0, 0)
    
        header_sections = [
            {'label': ['Work Order:', 'Test Proc:', 'Test Script:', 'ATE SW Ver:'], 'xy': (5, 10), 'values': self.H[1:5]},
            {'label': ['Rantec P/N:', 'Cust P/N:', 'Cust PO:', 'Serial No:'], 'xy': (120, 10), 'values': self.H[5:9]},
            {'label': ['Test Started:', 'Test Time:', 'Operator ID:', 'ATE System:'], 'xy': (225, 10), 'values': self.H[9:13]},
            {'label': ['CAGE Code:'], 'xy': (70, 10), 'values': [self.H[0]]}
        ]
        if self.page_no() > 1:
            header_offset = 0
            
        for section in header_sections:
            labels = section['label']
            values = section['values']
            x, y = section['xy']
    
            self.set_font('Times', 'B', 10)
            self.set_xy(x, y+header_offset)
            for label in labels:
                self.cell(30, 4, label, 0, 2, 'R')
            
            self.set_font('Times', '', 10)
            self.set_xy(x + 30, y+header_offset)
            for value in values:
                #if missing header value (usually CustPO/CustPN) 
                if value == "":
                    self.set_fill_color(250, 237, 0)
                    self.cell(30, 4, str(value), 0, 2, 'L', True)
                # if Test Proc not final ATP
                elif (section == header_sections[0] 
                      and value == values[1] 
                      and value != re.findall(r"ATP39669 Rev [A-Z]", values[1])[0]
                      ):
                    self.set_fill_color(250, 237, 0)
                    self.cell(30, 4, str(value), 0, 2, 'L', True)
                else:
                    self.cell(30, 4, str(value), 0, 2, 'L')
    
        self.set_font('Times', 'B', 11)
        self.set_xy(10, 27+header_offset)
        column_headers = [
            {'label': 'Step', 'width': 14, 'align': 'C'},
            {'label': 'Test Ref', 'width': 25, 'align': 'C'},
            {'label': 'Test Description', 'width': 110, 'align': 'L'},
            {'label': 'Min Limit', 'width': 25, 'align': 'C'},
            {'label': 'Max Limit', 'width': 25, 'align': 'C'},
            {'label': 'Meas Value', 'width': 25, 'align': 'C'},
            {'label': 'Result', 'width': 20, 'align': 'C'},
            {'label': 'Elapsed Time', 'width': 30, 'align': 'C'}
        ]
    
        for column in column_headers:
            self.cell(column['width'], 5, column['label'], 0, 0, column['align'])
        
        self.set_line_width(0.6)
        self.line(10, self.get_y() + 5, 285, self.get_y() + 5)
        self.ln(5)
        
    def footer(self):
        self.set_y(-13)
        self.set_line_width(0.6)
        self.line(10,self.get_y(),285,self.get_y())
        self.set_text_color(0, 0, 0)
        
        self.set_font('Times', 'I', 8)
        
        self.cell(275/2,5,'Rantec Power Systems Inc', 0, 0, 'L')
        self.cell(275/2,5, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'R')

def generateReport(ReportDF, judgement, H, output_path):
    w = [15,25,110,25,25,25,20,30]
    align = ['C','C','L','C','C','C','C','C']
    pdf = PDF(H, judgement)
    pdf.set_auto_page_break(True, margin = 10)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 10)
    if pdf.page_no() == 1:
        header_offset = 15
    else:
        header_offset = 0
    pdf.set_y(32 + header_offset)
    
    pcount = 0
    fcount = 0
    for index, row in ReportDF.iterrows():
        pdf.set_text_color(0, 0, 0)
        if row[6] != 'Pass':
            pdf.set_text_color(255, 0, 0)
            fcount += 1
        else:
            pcount += 1
            
        for j, col in enumerate(row):
            if j in [3,4,5] and len(str(col)) > 12:
                pdf.set_font('Times', '', 9)
                pdf.cell(w[j], 5, str(col), 0, 0, align[j])
                pdf.set_font('Times', '', 10)
            else:
                pdf.cell(w[j], 5, str(col), 0, 0, align[j])
        
        pdf.line(10,pdf.get_y(),285,pdf.get_y())
        pdf.ln(5)
    pdf.line(10,pdf.get_y(),285,pdf.get_y())
    
    pdf.set_font('Times', 'B', 10)
    pdf.set_text_color(0,0,0)
    pdf.cell(40, 5, f'Total Tests = {pcount+fcount}', 0, 0)
    pdf.cell(40, 5, f'Passed = {pcount}', 0, 0)
    pdf.cell(40, 5, f'Failed = {fcount}', 0, 0)
    
    test_report_pdf = pdf.output(os.path.join(output_path,f'{H[8]}_test_report.pdf'), 'F')
    
    # os.startfile(os.path.join(output_path,f'{H[8]}_test_report.pdf'))

    return test_report_pdf
      
def main(SN, testdb, output_path, CustPO, CustPN):
    # testdb = r"\\rantec-ut-fs\Utah Test Engineering$\ATE Test\Test Results\HDMSys ATE\L3Harris_ICP-TR3_TestLog.mdb"
    # SN = input("Enter Serial Number: ")
    df = queryDB(SN, testdb)
    H = getHeaderDF(df)
    H[6] = CustPN
    H[7] = CustPO
    reportDF, judgement = get_reportDF(df)
    test_report_pdf = generateReport(reportDF, judgement, H, output_path)
    
    return test_report_pdf


if __name__ == "__main__":
    testdb = r"\\rantec-ut-fs\Utah Test Engineering$\ATE Test\Test Results\HDMSys ATE\L3Harris_ICP-TR3_TestLog.mdb"
    # SN = input("Enter Serial Number: ")
    SN = 3405
    output_path = r"C:\Users\hbotha\Desktop\Code Projects"
    CustPO = 'test'
    CustPN = 'test'
    test_report_pdf = main(SN, testdb, output_path, CustPO, CustPN)


