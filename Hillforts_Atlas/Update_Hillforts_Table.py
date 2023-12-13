'''
Created on Dec 8, 2023

@author: Karl
'''

import arcpy, sys, openpyxl
from general_functions import console, console_breakline, prcnt_complete
from functions_excel import excel_worksheet_to_list

def update_table(current_fc, update_fc, index_fieldname):
    
    # Get field lists for both feature classes (ignore OID and SHAPE).
    cur_flist = [f.name for f in arcpy.ListFields(current_fc)]
    upd_flist = [f.name for f in arcpy.ListFields(update_fc)]
    
    # Create field list that excludes OID and shape.
    mod_cur_flist = [i for i in cur_flist if i not in ["OBJECTID", "OBJECTID_1", "Shape"]] #KLUDGE!! OBJECTID(_1) is flipped in different datasets, no clue why...
    mod_upd_flist = [i for i in upd_flist if i not in ["OBJECTID", "OBJECTID_1", "Shape"]]
    '''
    # Check that field lists are equivalent.
    if False in [upd_flist[i] in cur_flist[i] for i in range(0,len(cur_flist))]:
        
        print("ERROR: Input feature classes do not have the same fields.")
        print("")
        print("MISMATCHED FIELDS:")
        print([upd_flist[i] for i in range(0,len(cur_flist)) if upd_flist[i] not in cur_flist[i]])
        print("")
        print("Closing script...")
        sys.exit()
    '''
    # Get field index for index field (yeah yeah I know).
    def field_index_index_field(field_list):
        for i, j in enumerate(field_list):
            if j == index_fieldname:
                return i
    field_index = field_index_index_field(mod_cur_flist)
        
    # Generate dictionary
    upd_dict = {}
    
    
    
    # Use read cursor to loop through update features.
    with arcpy.da.SearchCursor(update_fc, mod_upd_flist) as search_cursor: #@UndefinedVariableFromImport
        
        for row in search_cursor:
            
            # Update upd_dict so that Hillfort ID: [row]
            iter_id = row[field_index]
            upd_dict[iter_id] = row
    
    del search_cursor
    
    # Use update cursor to loop through current features.
    with arcpy.da.UpdateCursor(current_fc, mod_cur_flist) as update_cursor: #@UndefinedVariableFromImport
        
        for row in update_cursor:
            
            update_row = []
            
            iter_id = row[field_index]
            
            if iter_id in upd_dict.keys():
            
                upd_row = upd_dict[iter_id]
                
                for row_idx in range(0,len(mod_cur_flist)):
                    
                    current_val = row[row_idx]
                    update_val = upd_row[row_idx]
                    
                    if current_val != update_val and update_val not in [None, ""]:
                        
                        update_row.append(update_val)
                    
                        try:
                            print("Changed '{}' to '{}'.".format(current_val, update_val))
                        except:
                            print("Changed SOMETHING WITH A SPECIAL CHARACTER to SOMETHING ELSE WITH A SPECIAL CHARACTER")
                        
                    else:
                        
                        update_row.append(current_val)
                        
            else:
                
                update_row = row
            
            # Update row.     
            update_cursor.updateRow(update_row)
            
    del update_cursor
    
    print("Script finished.")
    
    
    
    
current_fc = r"C:\GIS\Hillforts_Atlas\Hillforts\Hillforts_2.gdb\xHillforts"
update_fc = r"C:\GIS\Hillforts_Atlas\Hillforts\Hillforts_2.gdb\Hillforts_update"
index_fieldname = "Atlas_Number"

update_table(current_fc, update_fc, index_fieldname)