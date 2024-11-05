# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 13:12:10 2024

@author: hbotha
"""
import os
import shutil
import tempfile
import merge_svg_jpg


# out_dir = r'\\\\rantec-ut-fs\\ftp image\\Inspection Results Archive\\PL39669\\SN_02969 11-05-24-132443'
out_dir = r'V:\Public\Hendrik B\RI AOI\test\vdrive'


svg = os.path.join(out_dir, "02969_Connector_Graphics_T0000_01_CAM_Normal.svg")
jpg = os.path.join(out_dir, "02969_Connector_Graphics_T0000_01_CAM_Normal.jpg")
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.svg', mode='w+', dir=out_dir)


newFile = merge_svg_jpg.main(svg, jpg, out_dir)

print(newFile)