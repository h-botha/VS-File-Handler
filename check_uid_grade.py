# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 13:39:07 2024

@author: hbotha
"""

import os
import re
from pypdf import PdfReader

def main(PN, SN):
    
    try:
        uid_report_path = get_UID_report(PN, int(str(SN)))
        Datamatrix_SN = read_UID_PDF(uid_report_path)[0]
        
        if int(str(Datamatrix_SN)) != int(str(SN)):
            print(f'WARNING: Could not retrieve UID Label Score for SN {SN}')
            return "N/A"
        
        UID_Grade = read_UID_PDF(uid_report_path)[1]
        if PN == 'PL38509':
            print(f"ISO29158 (AIM-DPM) Grade: {UID_Grade}")
        else:
            print(f"ISO15415 Grade: {UID_Grade}")
        
        return [UID_Grade, uid_report_path]
        
    except Exception as e:
        print(f'WARNING: Could not retrieve UID Label Score for SN{SN}. {e}')
        return "N/A"

def get_UID_report(PN, SN):
    SN = str(int(SN))
    if PN == 'PL38509':
        PN = 'PL38509 HE-LVPS'
    UID_directory = rf'\\RPS-RANTEC-DFS\Corridor\qa_test\qa_test\UID Label Scores\{PN}'
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
    
    try:
        SN_match = re.search(SN_pattern, text).group(1)
        UID_match = re.search(UID_grade_pattern, text).group(1)
    
    except Exception:
        SN_pattern = r"<GS>SEQ (\d{5})<RS>"
        UID_grade_pattern = r"ISO29158 \(AIM-DPM\) ([A-F] \(\d+\.\d+\))"
        
        SN_match = re.search(SN_pattern, text).group(1)
        UID_match = re.search(UID_grade_pattern, text).group(1)
    
    return [SN_match, UID_match]

if __name__ == "__main__":
    PN = 'PL38509'
    UID_directory = rf'\\RPS-RANTEC-DFS\Corridor\qa_test\qa_test\UID Label Scores\{PN}'
    main(PN, 5406)
            