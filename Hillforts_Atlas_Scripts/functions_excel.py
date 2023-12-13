'''
Created on Dec 8, 2023

@author: Karl
'''

# -*- coding: utf-8 -*-
'''
Created on 25 Sep 2021

These functions extract data from the template.

@version 1.0
@author: KJSmith
'''

# Import modules.
#import openpyxl

#===============================================================================
# WORKSHEET DIMENSIONS.
#===============================================================================

# Returns the maximum number of columns in a worksheet by counting down from the 'max columns'.
# openpyxl sometimes screws this up and returns too many columns.
# This function only counts the header row - if there is data inside columns without a header, they will be left out.
def max_columns(in_ws): # Checks header.
    max_columns = in_ws.max_column
    
    for i in reversed(range(1,max_columns+1)):
        read_cell = in_ws.cell(row=1,column=i).value
        if read_cell != None:
            return i

# Returns the maximum number of rows by counting down from the 'max row' until any data is found within 'max columns'.
# As above, openpyxl looks at the excel doc's formatting, which can be screwy.
def max_rows(in_ws,in_max_columns):
    start_row = in_ws.max_row
    for i in reversed(range(1,start_row+1)):
        check_vals = [in_ws.cell(row=i,column=j).value for j in range(1,in_max_columns+1)]
        if check_vals.count(None) != len(check_vals):
            return i

# Returns the x and y dimensions of a workbook using the formulas above.
def worksheet_dimensions(in_ws):
    
    # Get maximum columns.
    max_cs = max_columns(in_ws)
    
    # Get maximum rows.
    max_rs = max_rows(in_ws, max_cs)
    
    # Return list.
    return [max_rs, max_cs]

#===============================================================================
# EXTRACTION.
#===============================================================================

# Produces list of lists, where each sublist represents a row.
def excel_worksheet_to_list(in_ws, header_only=False, data_only=False): # data_only excludes header.
    
    # Generate list.
    out_list = []
    
    # Get maximum rows and columns.
    max_rows, max_columns = worksheet_dimensions(in_ws)
    
    # Change max_rows if only header is requested.
    if header_only:
        max_rows = 1
        
    # Change start row if requested.
    if data_only:
        start_row = 2
    else:
        start_row = 1
    
    
    # Iterate through rows.
    for row_number in range(start_row,max_rows+1):
        
        # Extract line.
        line = [in_ws.cell(row=row_number,column=column_number).value for column_number in range(1,max_columns+1)]
        
        # Add line to list.
        out_list.append(line)
        
    return out_list