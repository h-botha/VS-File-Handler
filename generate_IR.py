# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 11:07:12 2024

@author: hbotha
"""

import os
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import merge_svg_jpg


def main(df, output_path, sn_value, wo_value, judgement, graphics_photos, normal_photos):
    pdf = PDF(sn_value, wo_value, judgement, graphics_photos, normal_photos)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', '', 11)

    
    k = 0 # increments for photos on page 2
    for i, row in df.iterrows():

        if i == 0:
            pdf.cell(60, 5, 'Result Name', 0, 0, 'C')
            pdf.cell(40, 5, 'Result', 0, 0, 'C')
            pdf.cell(100, 5, 'Photo', 0, 1, 'C')
        
        name, result = row['Name'], row['Result']
        if name in ['Overall Judgement', 'CSV ID']:
            pdf.set_font('Arial', 'B', 11)
            if name == 'Overall Judgement':
                pdf.set_text_color(0, 200, 0) if result == 'PASS' else pdf.set_text_color(255, 0, 0)
        # if name == 'DrawShapes':
        #     continue
                

        pdf.cell(60, 10, name, 1, 0)
        pdf.cell(40, 10, str(result), 1, 1)
        pdf.set_text_color(0, 0, 0)
        
        if i == 0:
            y0 = pdf.get_y()
            y = pdf.get_y() - 10
            for j in range(3):
                pdf.image(pdf.graphics_photos[j], x=115, y=y, w=90)
                y += 80
            pdf.set_y(y0)
        
        if pdf.page_no() == 2 and k == 0:
            k += 1
            y0 = pdf.get_y()
            y = pdf.get_y() - 10
            for j in range(3, len(graphics_photos)):
                pdf.image(pdf.graphics_photos[j], 115, y, 90)
                y += 80
            pdf.set_y(y0)
        
        pdf.set_font('Arial', '', 11)
    
    pdf.add_page()
    
    i = 0
    y = pdf.get_y()
    y0 = y
    for i in range(len(pdf.normal_photos)):
        if i <= 1:
            pdf.image(pdf.normal_photos[i], 25, y, 160)
            y += 125
        if i == 2 or i == 4:
            pdf.add_page()
            pdf.set_y(y0)
            y = y0
            pdf.image(pdf.normal_photos[i], 25, y, 160)
            y += 125
            pdf.image(pdf.normal_photos[i+1], 25, y, 160)
        
    pdf.output(os.path.join(output_path, f'{sn_value}_report.pdf'), 'F')
    
    os.startfile(os.path.join(output_path, f'{sn_value}_report.pdf'))
    
    for file in os.listdir(output_path):
        if file.endswith(('.png', '.svg')) or (file.endswith('.jpg') and 'Graphics' not in file):
            try:
                os.remove(os.path.join(output_path, file))
            except Exception as e:
                continue
    
class PDF(FPDF):
    def __init__(self, sn_value, wo_value, judgement, graphics_photos, normal_photos, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sn_value = sn_value
        self.wo_value = wo_value
        self.judgement = judgement
        
        print(f'Generating report for SN {sn_value}')
        
        order = [1, 0, 4, 5, 3, 2]
        outdir = os.path.dirname(sorted(graphics_photos)[0])
        
        self.normal_photos = [sorted(normal_photos)[i] for i in order]
        self.graphics_photos = [sorted(graphics_photos)[i] for i in order]
        
        i=0
        for photo in self.graphics_photos:
            self.graphics_photos[i] = merge_svg_jpg.main(self.graphics_photos[i], self.normal_photos[i], outdir)
            i += 1
        
    def header(self):
        try:
            logo = r'C:\Keyence Final Inspect\RANTEC-LOGO-CMYK TAGLINE F.jpg'
            self.image(logo, x=143, y=5, w=60)
        except Exception as e:
            logo = r"C:\Users\hbotha\Desktop\Code Projects\RANTEC-LOGO-CMYK TAGLINE F.jpg"
            self.image(logo, x=143, y=5, w=60)
            
        self.set_text_color(0,0,0)
        self.set_font('Arial', 'B', 12)
        self.set_y(5)
        self.cell(90, 5, f'P/N: PL39669 S/N: {self.sn_value}', 0, 1, 'L')
        self.cell(38, 5, 'Overall Pass/Fail:', 0, 0, 'L')
        self.set_text_color(0, 200, 0) if self.judgement == 'PASS' else self.set_text_color(255, 0, 0)
        self.cell(10, 5, self.judgement.upper(), 0, 1, 'L')
        self.set_text_color(0, 0, 0)
        self.cell(90, 5, self.wo_value, 0, 1, 'L')
        self.cell(90, 5, str(datetime.now().strftime("%m/%d/%Y, %H:%M:%S")), 0, 0, 'L')
        self.ln(10)

    def footer(self):
        self.set_text_color(0,0,0)
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')