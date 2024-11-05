# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 14:22:31 2024

@author: hbotha
"""

import os
os.environ['path'] += r';C:\Program Files\UniConvertor-2.0rc5\dlls'
import cairosvg
import re
import io
from PIL import Image
import tempfile

def svg_to_png(svg_file, jpg_file):
    
    base_name = os.path.splitext(jpg_file)[0]
    png_file = f"{base_name}.png"
    
    png_data = cairosvg.svg2png(url=svg_file, output_width=4400, output_height=3296)
    img = Image.open(io.BytesIO(png_data))

    background = Image.open(jpg_file)
    # img = img.convert('RGB')
    
    background.paste(img,mask=img)
    background.save(png_file, 'png', quality=90)
    
    return png_file

def modify_svg_header(svg_content, new_x, new_y, new_width, new_height):
    svg_content = re.sub(r'x="[^"]*"', f'x="{new_x}"', svg_content, count=1)
    svg_content = re.sub(r'y="[^"]*"', f'y="{new_y}"', svg_content, count=1)
    svg_content = re.sub(r'width="[^"]*"', f'width="{new_width}"', svg_content, count=1)
    svg_content = re.sub(r'height="[^"]*"', f'height="{new_height}"', svg_content, count=1)
    
    
    return svg_content


def main(svg_file, jpg_file, out_dir):
    
    # Create a named temporary file and get its path
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.svg', mode='w+', dir=out_dir)

    output_file = temp_file.name
    temp_file.close()  # Close the file object
    
    # Read the original SVG file
    with open(svg_file, 'r') as f:
        svg = f.read()
        modified_svg = modify_svg_header(svg, "0", "0", "4400", "3296")
    
    # Write to the temporary file using its path
    with open(output_file, 'w') as f:
        f.write(modified_svg)
    
    png = svg_to_png(output_file, jpg_file)
    
    jpg_basename = os.path.splitext(jpg_file)[0]
    
    os.rename(png, jpg_basename+'.png')
    
    return png


    

    
    