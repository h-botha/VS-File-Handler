# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 13:39:07 2024

@author: hbotha
"""

import os
import re
from pypdf import PdfReader

def main(SN):
    
    try:
        uid_report_path = get_UID_report(int(str(SN)))
        Datamatrix_SN = read_UID_PDF(uid_report_path)[0]
        
        if int(str(Datamatrix_SN)) != int(str(SN)):
            print(f'WARNING: Could not retrieve UID Label Score for SN {SN}')
            return "N/A"
        
        UID_Grade = read_UID_PDF(uid_report_path)[1]
        print(f"ISO15415 Grade: {UID_Grade}")
        
        return [UID_Grade, uid_report_path]
        
    except Exception as e:
        print(f'WARNING: Could not retrieve UID Label Score for SN{SN}')
        return "N/A"

def get_UID_report(SN):
    SN = str(int(SN))
    UID_directory = r'\\RPS-RANTEC-DFS\Corridor\qa_test\qa_test\UID Label Scores\PL39669'
    for root, dirs, files in os.walk(UID_directory):
        for file in files:
            if "SN"+SN in file:
                uid_report_path = os.path.join(root,file)
                break
    return uid_report_path

def read_UID_PDF(uid_report_path):
    reader = PdfReader(uid_report_path)
    page = reader.pages[0]
    text = page.extract_text()

    
    SN_pattern = r"<GS>SEQ (\d{5})<GS>"
    UID_grade_pattern = r"ISO15415 ([A-F] \(\d+\.\d+\))"
    
    SN_match = re.search(SN_pattern, text).group(1)
    UID_match = re.search(UID_grade_pattern, text).group(1)

    
    return [SN_match, UID_match]

if __name__ == "__main__":
    UID_directory = r'\\RPS-RANTEC-DFS\Corridor\qa_test\qa_test\UID Label Scores\PL39669'
    main(3002)
            