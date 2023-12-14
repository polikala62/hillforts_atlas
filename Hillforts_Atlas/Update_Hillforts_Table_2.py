# -*- coding: utf-8 -*-
'''
Created on Dec 8, 2023

@author: Karl
'''

import arcpy, openpyxl
#from general_functions import console, console_breakline, prcnt_complete
from functions_excel import excel_worksheet_to_list

def isnumeric(val):
    try:
        testval = float(val) #@UnusedVariable
        return True
    except:
        return False

#------------------------------------------------------------------------------ 

def valstrip(val):
    if val == None:
        return None
    try:
        int(val)
        return val
    except:
        changes = [val]
        
        # Strip returns, newlines, and other nuisances.
        #changes.append(changes[-1].replace("\n","\n"))
        changes.append(changes[-1].replace("\r","\n"))
        #changes.append(changes[-1].replace("\t",""))
        changes.append(changes[-1].replace("_x000D_","\n"))
        
        # Replace special characters.
        changes.append(changes[-1].replace("_x0018_","'"))
        changes.append(changes[-1].replace("_x0019_","'"))
        changes.append(changes[-1].replace("a_x0002_","â'"))
        changes.append(changes[-1].replace("e_x0002_","ê"))
        changes.append(changes[-1].replace("e_x0001_","é"))
        
        # Strip consecutive spaces.
        while "  " in changes[-1]:
            changes.append(changes[-1].replace("  ", " "))
        
        while "\n\n\n" in changes[-1]:
            changes.append(changes[-1].replace("\n\n\n", "\n\n"))
        
        # Return None if there is no data left.
        if changes[-1] in ["", "\n", "\n\n"]:
            return None
        else:
            return changes[-1]
        
#------------------------------------------------------------------------------ 

def update_table(current_fc, update_excel, index_fieldname):
    
    # For troubleshooting / producing reports.
    update_features = False
    
    # Get field lists for both feature classes (ignore OID and SHAPE).
    cur_flist = [f.name for f in arcpy.ListFields(current_fc)]
    
    # Read update spreadsheet to list of lists.
    wb = openpyxl.load_workbook(filename=update_excel)
    ws = wb.worksheets[0]
    
    # Create field list that excludes OID and shape.
    mod_cur_flist = [i for i in cur_flist if i not in ["OBJECTID", "OBJECTID_1", "Shape"]] #KLUDGE!! OBJECTID(_1) is flipped in different datasets, no clue why...
    
    # Get list of fields in excel spreadsheet.
    upd_field_list = excel_worksheet_to_list(ws, header_only=True)[0]
    
    # Get field list for spreadsheet, where fields exist in current features.
    mod_upd_flist = [j for i, j in enumerate(upd_field_list) if j in mod_cur_flist]
    
    # Get indices for fields in spreadsheet, where fields exist in current features.
    mod_upd_idxlist = [i for i, j in enumerate(upd_field_list) if j in mod_cur_flist]
    
    # Get values from excel spreadsheet.
    upd_vals = excel_worksheet_to_list(ws, data_only=True)
    
    mod_vals = []
    
    for row in upd_vals:
        
        mod_rowvals = []
        
        for idx, val in enumerate(row):
            
            if idx in mod_upd_idxlist:
                
                if val == None:
                    
                    mod_rowvals.append(None)
                    
                else:
                
                    if isnumeric(val):
                        
                        mod_rowvals.append(val)
                        
                    else:
                        
                        mod_rowvals.append(valstrip(val))
                
        mod_vals.append(mod_rowvals)
        
    # Get field index for index field (yeah yeah I know).
    def field_index_index_field(field_list):
        for i, j in enumerate(field_list):
            if j == index_fieldname:
                return i
    
    #cur_field_index = field_index_index_field(mod_cur_flist)
    
    mod_field_index = field_index_index_field(mod_upd_flist)
    #print(cur_field_index, mod_field_index)
    # Generate dictionary
    upd_dict = {}
    
    for row in mod_vals:
        
        upd_dict[row[mod_field_index]] = row
    
    # Use update cursor to loop through current features.
    with arcpy.da.UpdateCursor(current_fc, mod_upd_flist) as update_cursor: #@UndefinedVariableFromImport
        
        for row in update_cursor:
            
            row_updated = False
            
            update_row = []
            
            iter_id = row[mod_field_index]
            
            if iter_id in upd_dict.keys():
            
                upd_row = upd_dict[iter_id]
                
                for row_idx in range(0,len(mod_upd_flist)):
                    
                    iter_fname = mod_upd_flist[row_idx]
                    
                    current_val = valstrip(row[row_idx])
                    update_val = valstrip(upd_row[row_idx])
                    
                    if isnumeric(current_val) and isnumeric(update_val):
                        #print(current_val,update_val)
                        if abs(float(current_val)) - abs(float(update_val)) > 0.00001:
                        
                            update_row.append(update_val)
                            row_updated = True
                            print("{}${}${}${}".format(iter_id, iter_fname, current_val, update_val))
                            
                        else:
                            
                            update_row.append(current_val)
                    
                    elif current_val != update_val and update_val not in [None, ""]:
                        
                        update_row.append(update_val)
                        row_updated= True
                        
                        try:
                            print("{}${}${}${}".format(iter_id, iter_fname, current_val, update_val))
                        except:
                            print("{}${}$<<COULD NOT PRINT CHARACTER>>$<<COULD NOT PRINT CHARACTER>>".format(iter_id, iter_fname))
                            
                    else:
                        
                        update_row.append(current_val)
            
            # Update row.           
            if row_updated and update_features:
                
                update_cursor.updateRow(update_row)
                
            
    del update_cursor
    
    print("Script finished.")
    
current_fc = "C:\\GIS\\Hillforts_Atlas\\Hillforts\\Hillforts_2.gdb\\xHillforts"
update_fc = "C:\\GIS\\Hillforts_Atlas\\Hillforts\\Update_Features\\sofa_02.xlsx"
index_fieldname = "Atlas_Number"

update_table(current_fc, update_fc, index_fieldname)