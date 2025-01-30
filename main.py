# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 15:12:33 2024

@author: hbotha
"""

import os
import time
from time import sleep
from datetime import datetime
import pandas as pd
import shutil
import sqlite3
import warnings
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import db_operations
import process_files
import generate_IR
import check_duplicate_sn
import check_uid_grade
import Generate_test_report
import get_custPO_and_PN

warnings.filterwarnings('ignore')

def get_PN():
    PN_options = ['PL39669', 'PL39710']
    print(f"Select current Rantec PN (enter corresponding number 1-{len(PN_options)} on the left and press Enter):")
    for index, PN in enumerate(PN_options, 1):
        print(f"{index}. {PN}")
    PN_choice = int(input('Enter number here: '))
    PN = PN_options[PN_choice-1]
    print(PN)
    return PN
    
# Get CustPO and CustPN from Alliance
def get_custPO_PN(rantec_PN):
    custPO_options = get_custPO_and_PN.main(rantec_PN)[0]
    if len(custPO_options) == 1: 
        CustPO = custPO_options[0]
    else:
        print(f"Select current Customer PO (enter corresponding number 1-{len(custPO_options)} on the left and press Enter):")
        for index, PO in enumerate(custPO_options, 1):
            print(f"{index}. {PO}")
        
        CustPO_choice = int(input('Enter number here: '))
        try:
            CustPO = custPO_options[CustPO_choice-1]
        except Exception as e:
            print("Selection Invalid or CustPO query failed. Test report generation disabled.")
            CustPO = None
        
    custPN_options = get_custPO_and_PN.main(rantec_PN)[1]
    if len(custPN_options) == 1: 
        CustPN = custPN_options[0]
    else:
        print(f"Select current Customer PN (enter corresponding number 1-{len(custPN_options)} on the left and press Enter):")
        for index, PN in enumerate(custPN_options, 1):
            print(f"{index}. {PN}")
        
        CustPN_choice = int(input('Enter number here: '))
        try:
            CustPN = custPN_options[CustPN_choice-1]
        except Exception as e:
            print("Selection Invalid or CustPN query failed. Test report generation disabled.")
            CustPN = None
        
    # print(CustPO, CustPN)
    return CustPO, CustPN
    
class CsvFileHandler(FileSystemEventHandler):
    def __init__(self, directory_to_watch, PN):
        self.directory_to_watch = directory_to_watch
        self.PN = PN
        self.observer = Observer()
        self.stateCount = 0
        self.csv_files = set()
        self.graphics_files = set()
        self.jpg_files = set()
        self.png_files = set()
        self.sn_value = None
        self.wo_value = None
        self.passfail = None
        self.shapelist = None
        self.running = True
        self.csv_pn1 = None
        self.csv_pn2 = None


        self.mapping = {
            0: "Label",
            1: "Connector",
            2: "WedgelockDown",
            3: "WedgelockUp",
            4: "EjectorUp",
            5: "EjectorDown"
        }
        self.files_added = {key: {'csv': False, 'jpg': False, 'svg': False} for key in self.mapping}
                
    def start(self, copytestfiles):
        self.cleardirectory()
        self.observer.schedule(self, self.directory_to_watch, recursive=False)
        self.observer.start()
        print(f"Inspection Report Generator for {self.PN}")
        print(f"Monitoring directory: {self.directory_to_watch}")
        
        if copytestfiles == True:
            self.copytestfiles()
        try:
            while True:
                time.sleep(0.1)
                # self.process_input()
        except KeyboardInterrupt:
            self.running = False
            self.observer.stop()
            print("Monitoring stopped by user.")
        self.observer.join()
    
    def cleardirectory(self):
        for file in os.listdir(self.directory_to_watch):
            if '.csv' in file or '.png' in file or '.jpg' in file or '.svg' in file:
                os.remove(os.path.join(self.directory_to_watch, file))

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.jpg') and 'Graphics' in event.src_path:
            return
        
        if event.src_path.endswith('.csv') and 'PL39669' in event.src_path and 'Label' in event.src_path:
            self.csv_pn1 = 'PL39669'
        if event.src_path.endswith('.csv') and 'PL39710' in event.src_path and 'Label' in event.src_path:
            self.csv_pn1 = 'PL39710'
        
        if event.src_path.endswith('.csv') and 'PL39669' in event.src_path and 'WedgelockDown' in event.src_path:
            self.csv_pn2 = 'PL39669'
        if event.src_path.endswith('.csv') and 'PL39710' in event.src_path and 'WedgelockDown' in event.src_path:
            self.csv_pn2 = 'PL39710'
        
        # if self.csv_pn1 and self.csv_pn2:
        #     self.verifyPN()
        #     print('test')
        
        if '_' and 'Label' in event.src_path:
            self.sn_value = event.src_path.split('\\')[-1].split('_')[0]
            self.wo_value = self.getWO()
    
        if event.src_path.endswith(('csv', '.jpg', '.svg')) and self.stateCount in self.mapping:
            if self.mapping[self.stateCount] in event.src_path:

                if '.csv' in event.src_path:
                    self.csv_files.add(event.src_path)
                    self.files_added[self.stateCount]['csv'] = True

                if '.jpg' in event.src_path:
                    self.jpg_files.add(event.src_path)
                    self.files_added[self.stateCount]['jpg'] = True
                
                if '.svg' in event.src_path:
                    self.graphics_files.add(event.src_path)
                    self.files_added[self.stateCount]['svg'] = True
                    
                # print(f'File Added: {str(event.src_path)}')
                
                if (self.files_added[self.stateCount]['csv'] and 
                    self.files_added[self.stateCount]['jpg'] and 
                    self.files_added[self.stateCount]['svg']):
                    
                    self.stateCount += 1
                    
                    if 'Graphics' in event.src_path:
                        print(f'Files detected for {os.path.splitext(event.src_path)[0].split("_Graphics")[0]}')
                    else:
                        print(f'Files detected for {os.path.splitext(event.src_path)[0]}')
                    
        if event.src_path.endswith('png') and 'FinishInspection' in event.src_path:
            if self.stateCount == 6 and len(self.csv_files) == 6 and len(self.graphics_files) == 6:
                self.stateCount = 0
                self.verifyPN()
                self.isDuplicateSN = check_duplicate_sn.checkDuplicateSN(self.sn_value)
                dirs = self.move_and_rename()
                localdir = dirs[0]
                networkdir = dirs[1]
                sleep(1)
                self.generatePDF(localdir)
                
                shutil.move(localdir, networkdir)
                
                db_operations.insert_report_path(db_path, networkdir)
                
                os.startfile(os.path.join(networkdir, f'{self.sn_value}_report.pdf'))
                
                self.csv_files.clear()
                self.graphics_files.clear()
                self.png_files.clear()
                self.cleardirectory()
                self.csv_pn1 = None
                self.csv_pn2 = None
                        
                self.files_added = {key: {'csv': False, 'jpg': False, 'svg': False} for key in self.mapping}
    
    def verifyPN(self):
        if self.PN == self.csv_pn1 and self.PN == self.csv_pn2:
            PN_OK = True
        else:
            PN_OK = False
            print(f"""
                  WARNING: POTENTIAL PART NUMBER MISMATCH
                  CHOSEN PN: {self.PN}
                  LABEL PNs: {self.csv_pn1, self.csv_pn2}
                  """)
        return PN_OK
        
    def generatePDF(self, report_directory):
        self.mapping = {
            0: "Label",
            1: "Connector",
            2: "WedgelockDown",
            3: "WedgelockUp",
            4: "EjectorUp",
            5: "EjectorDown"
        }
        
        graphics_photos = sorted(
            [os.path.join(report_directory, file) for file in os.listdir(report_directory) if 'Graphics' in file and '.svg' in file],
            key=lambda x: next(i for i, name in self.mapping.items() if name in x)
            )
        
        normal_photos = sorted(
            [os.path.join(report_directory, file) for file in os.listdir(report_directory) if 'Graphics' not in file and '.jpg' in file],
            key=lambda x: next(i for i, name in self.mapping.items() if name in x)
            )

        data = process_files.main(directory_to_watch, self.csv_files)
        report_df, judgement = db_operations.main(db_path, data, self.PN, self.sn_value, self.wo_value)
        
        UID_Grade = check_uid_grade.main(self.PN, str(self.sn_value))
        UID_report_path = UID_Grade[1]
        
        shutil.copy(UID_report_path, os.path.join(report_directory, "UID REPORT - "+os.path.basename(UID_report_path)))
        
        generate_IR.main(report_df, report_directory, self.PN, self.sn_value, self.wo_value, judgement, graphics_photos, normal_photos, self.isDuplicateSN, UID_Grade)
        
        db_operations.insert_report_path(db_path, report_directory)
        
        if CustPO and CustPN:
            try:
                print(f'Generating test report for SN {self.sn_value}...')
                test_report_pdf = Generate_test_report.main(self.PN, self.sn_value, testdb, report_directory, CustPO, CustPN)
            except Exception as e:
                test_report_pdf = None
                print(f'WARNING: Test data for SN{self.sn_value} not found. See error: {e}')
    
    def move_and_rename(self):
        directoryName = 'SN_'+str(self.sn_value)
        if os.path.isdir(os.path.join(IR_Archive, directoryName)) or os.path.isdir(os.path.join(self.directory_to_watch, directoryName)):
            directoryName = directoryName+" "+datetime.now().strftime("%m-%d-%y-%H%M%S")
        
        # Create the directory outside the loop
        try:
            os.mkdir(os.path.join(self.directory_to_watch, directoryName))
        except Exception as e:
            print(f"Error creating directory: {e}")
            return None
    
        moved_files_count = 0
        for file in os.listdir(self.directory_to_watch):
            if file.endswith('jpg') or file.endswith('svg'):
                name = os.path.splitext(os.path.basename(file))[0]
                source = os.path.join(self.directory_to_watch, file)
                if file.endswith('jpg'):
                    destination = os.path.join(self.directory_to_watch, directoryName, name+'.jpg')
                if file.endswith('svg'):
                    destination = os.path.join(self.directory_to_watch, directoryName, name+'.svg')
                    
                try:
                    shutil.move(source, destination)
                    moved_files_count += 1
                except Exception as e:
                    print(f"Error moving file {source} to {destination}: {e}")
        
        localdir = os.path.join(self.directory_to_watch, directoryName)
        networkdir = os.path.join(IR_Archive, directoryName)
        
        if moved_files_count > 0:
            return [localdir, networkdir]
        else:
            return None

    def getWO(self):
        sn_value = int(self.sn_value)
        sn_conn = sqlite3.connect(sn_db)
        query = f"""
        SELECT WO
        FROM SNs
        WHERE "P/N" = '{self.PN}' AND "S/N" = '{sn_value}'
        """
        sn_log = pd.read_sql(query, sn_conn)
        
        try:
            WO = sn_log['WO'].iloc[0]
        except IndexError:
            # print('Serial Number Invalid. No Work Order attached.')
            WO = 'N/A'
        return WO

    def copytestfiles(self):
        
        directory_to_watch = self.directory_to_watch
        for file in os.listdir(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files'):

            if 'Label' in file:
                shutil.copy(os.path.join(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files', file), os.path.join(directory_to_watch, file))
                sleep(0.1)
        for file in os.listdir(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files'):
            if 'Connector' in file:
                shutil.copy(os.path.join(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files', file), os.path.join(directory_to_watch, file))
                sleep(0.1)
        for file in os.listdir(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files'):
            if 'WedgelockDown' in file:
                shutil.copy(os.path.join(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files', file), os.path.join(directory_to_watch, file))
                sleep(0.1)
        for file in os.listdir(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files'):
            if 'WedgelockUp' in file:
                shutil.copy(os.path.join(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files', file), os.path.join(directory_to_watch, file))
                sleep(0.1)     
        for file in os.listdir(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files'):
            if 'EjectorUp' in file:
                shutil.copy(os.path.join(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files', file), os.path.join(directory_to_watch, file))
                sleep(0.1)
        for file in os.listdir(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files'):
            if 'EjectorDown' in file:
                shutil.copy(os.path.join(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files', file), os.path.join(directory_to_watch, file))
                sleep(0.1)
        for file in os.listdir(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files'):
            if 'FinishInspection' in file:
                shutil.copy(os.path.join(r'C:\Users\hbotha\VS_File_Handler V2.x\Test Files', file), os.path.join(directory_to_watch, file))
                sleep(0.1)

if __name__ == "__main__":
    #SET RUN MODE (0 for running in UT, 1 for testing in CA)
    runmode = 0
    rantec_PN = get_PN()
    testdb = r"\\rantec-ut-fs\Utah Test Engineering$\ATE Test\Test Results\HDMSys ATE\L3Harris_ICP-TR3_TestLog.mdb"
    CustPO, CustPN = get_custPO_PN(rantec_PN)
    
    if runmode == 0:
        directory_to_watch = r'C:\Keyence Final Inspect\VS Output'
        # directory_to_watch = r'C:/Users/hbotha/VS_File_Handler 2-1/VS-File-Handler/VS Output'
        db_path = r'\\rantec-ut-fs\ftp image\db\VS_Results.db'
        IR_Archive = rf'\\rantec-ut-fs\ftp image\Inspection Results Archive\{rantec_PN}'
        sn_db = r'\\rantec-ut-fs\ftp image\db\sn_log.db'
        copytestfiles = False
    else:
        directory_to_watch = r'VS Output'
        db_path = r'VS_Results.db'
        IR_Archive = rf'Inspection Results Archive\{rantec_PN}'
        sn_db = r'sn_log.db'
        copytestfiles = True
        
    event_handler = CsvFileHandler(directory_to_watch, rantec_PN)
    event_handler.start(copytestfiles)