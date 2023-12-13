'''
Created on Oct 23, 2023

@author: kjsmi
'''

import arcpy, os, datetime
from general_functions import console, console_breakline, prcnt_complete

def field_to_domain(in_fc, out_fc, exclude_field_list):

    # Set processing variables.
    arcpy.env.overwriteOutput = True
    generate_domains = True
    generate_output_fc = True
    populate_output_fc = True
    
    #out_fc = r"C:\GIS\Hillforts_Atlas\Hillforts\Hillforts.gdb\Hillforts"
    out_gdb, out_filename = os.path.split(out_fc)
    
    #------------------------------------------------------------------------------ 
    
    # TODO: Split dictionaries into "in" and "out" versions.
    #    Maybe actually create classes if I can remember how to do that?
    field_dict:{"in_name":"",
                "in_alias":"",
                "in_type":"",
                "in_length":1,
                "in_min":1,
                "in_max":1,
                "out_domain_name":"",
                "out_type":"",
                "out_length":1,
                "is_string":False,
                "is_numeric":False,
                "val_code_dict":{}}
    
    #------------------------------------------------------------------------------ 
    console_breakline("-", "+", 75)
    console("Started script 'Field_to_Domain'.")
    console("")
    
    #------------------------------------------------------------------------------ 
    # Get field information from input.
    console("Collecting field data from input...")
    
    # List input fields.
    in_fields = arcpy.ListFields(in_fc)
    
    # Use dictionary to format types for Create Domain.
    tr_types_dict = {"Double":"DOUBLE", "Integer":"LONG", "Single":"FLOAT", "SmallInteger":"SHORT",
                     "String":"TEXT",
                     "OID":"OID", "Geometry":"SHAPE"}
    
    # Create output field list, containing field_data objects.
    out_field_list = []
    
    # Create class for each field.
    for field in in_fields:
        
        # Set booleans based on field type.
        if tr_types_dict[str(field.type)] == "TEXT":
            field_is_string = True
        else:
            field_is_string = False
            
        if tr_types_dict[str(field.type)] in ["DOUBLE", "LONG", "FLOAT", "SHORT"]:
            field_is_numeric = True
        else:
            field_is_numeric = False
        
        field_dict = {"in_name":field.name,
                      "in_alias":field.aliasName,
                      "in_type":tr_types_dict[str(field.type)],
                      "in_length":1,
                      "in_min":1,
                      "in_max":1,
                      "out_domain":"",
                      "out_type":tr_types_dict[str(field.type)], # Set out type to in type by default.
                      "out_length":1,
                      "out_min":1,
                      "out_max":1,
                      "is_string":field_is_string,
                      "is_numeric":field_is_numeric,
                      "val_code_dict":{}}
        
        # Exclude OID field from output.
        if field.type not in ["OID"]:
        
            out_field_list.append(field_dict)
        
    #console([i["in_name"] for i in out_field_list])
    #------------------------------------------------------------------------------ 
    console("Gathering unique values from fields...")
    
    # Create 'No_Yes_domain' from scratch.
    domain_dict = {"Hillforts_No_Yes_domain":{"val_code_dict":{"No":"No", "Yes":"Yes"},"type":"CODED","length":3,"min":1,"max":1,"datatype":"TEXT"}}
    
    def dict_to_string(in_dict):
        pr_list = []
        for i in in_dict.keys():
            pr_list.append(str(i))
            pr_list.append(str(in_dict[i]))
        return "".join(pr_list)
    
    def lookup_dict(in_dict):
        out_dict = {}
        for i in in_dict.keys():
            vcdict = dict_to_string(in_dict[i]["val_code_dict"])
            out_dict[vcdict] = i
        return out_dict
    
    # Create counter to hold domain values.
    domain_value_count = 2 # Counting noyes.
    
    # Generate coded value dict for each field.
    for field_dict in out_field_list:
        
        # Calculate number of created domains.
        domain_count = len(domain_dict.keys())
        
        # Get list of coded value lists to check against.
        domain_lookup_dict = lookup_dict(domain_dict)
        
        # Create list to hold row values.
        row_vals = []
        
        
        out_feature_count = 0
        
        # Populate list with unique values.
        with arcpy.da.SearchCursor(in_fc, [field_dict["in_name"]]) as search_cursor: #@UndefinedVariableFromImport
            
            for row in search_cursor:
                
                out_feature_count += 1
                
                if row[0] not in row_vals and row[0] != None:
                    
                    # KLUDGE!
                    try:
                        row_vals.append(row[0].replace("http:","https:"))
                    except:
                        row_vals.append(row[0])
        
        del search_cursor
        
        # Check that there are values in list (that not all values are None), and that the field has not been excluded.
        if len(row_vals) > 0:
        
            # Sort list alphabetically.
            sorted_row_vals = sorted(row_vals)
            '''
            # Create subdict.
            val_code_dict = {} # Format: dict[val] = code
            for i, j in enumerate(sorted_row_vals):
                val_code_dict[j] = (i + 1)
            '''
            
            # Create subdict.
            val_code_dict = {} # Format: dict[val] = code
            for i in sorted_row_vals:
                val_code_dict[i] = i
            
            field_dict["val_code_dict"] = val_code_dict
        
            # Set domain.
            pr_domain_name = "{}_{}_domain".format(out_filename, field_dict["in_name"])
            
            # If codes already exist as a domain, look it up and add it as an attribute.
            if dict_to_string(val_code_dict) in domain_lookup_dict.keys():
                
                field_dict["out_domain"] = domain_lookup_dict[dict_to_string(val_code_dict)]
            
            elif field_dict["in_type"] in ["DOUBLE", "LONG", "FLOAT", "SHORT", "TEXT"]:
                
                field_dict["out_domain"] = pr_domain_name
                
                domain_dict[pr_domain_name] = {}
                domain_dict[pr_domain_name]["val_code_dict"] = field_dict["val_code_dict"]
                
                # Populate domain type dict.
                if field_dict["in_type"] == "TEXT":
                    domain_dict[pr_domain_name]["type"] = "CODED"
                    # Update field_length_dict.
                    field_dict["out_length"] = max([len(str(i)) for i in row_vals])
                    #field_dict["out_length"] = len(str(len(row_vals)))
                    domain_dict[pr_domain_name]["length"] = max([len(str(i)) for i in row_vals])
                else:
                    domain_dict[pr_domain_name]["type"] = "RANGE"
                    # Update field_length_dict.
                    field_dict["out_length"] = max([len(str(i)) for i in row_vals])
                    domain_dict[pr_domain_name]["length"] = max([len(str(i)) for i in row_vals])
                    
                    # Update min/max (if numeric), and add domain information.
                    field_dict["out_min"] = int(min(row_vals))
                    domain_dict[pr_domain_name]["min"] = int(min(row_vals))-1
                    field_dict["out_max"] = int(max(row_vals))+1 # Round down and up to nearest integer.
                    domain_dict[pr_domain_name]["max"] = int(max(row_vals))+1
                    
                    domain_dict[pr_domain_name]["datatype"] = field_dict['in_type']
                    
                domain_value_count += len(field_dict["val_code_dict"].keys())
                    
            # Check whether field is excluded.
            if field_dict["in_name"] in exclude_field_list:
                field_dict["out_length"] = max([len(i) for i in row_vals])
                field_dict["out_domain"] = ""
                domain_dict.pop(pr_domain_name)
                
            else:
                field_dict["out_length"] = max([len(str(i)) for i in row_vals])
            '''
            else:
                # Set output type based on whether or not the output is coded.
                if field_dict["in_type"] == "TEXT":
                    # Set the out type to 'short'.
                    field_dict["out_type"] = "TEXT"
            '''
    #------------------------------------------------------------------------------ 
    if generate_domains:
        
        console("Creating {} entries in {} domains...".format(domain_value_count, domain_count))
        
        domains_start_time = datetime.datetime.now()
        domains_pr_count = 0
        
        domains_pr_list = []
        
        # Get list of existing domains.
        domain_desc = arcpy.Describe(out_gdb)
        out_domains_list = domain_desc.domains
        
        # Delete pre-existing domains.
        for domain_name in domain_dict.keys():
            if domain_name in out_domains_list:
                try:
                    arcpy.management.DeleteDomain(out_gdb, domain_name)
                except:
                    console("COULDN'T DELETE DOMAIN: {}".format(domain_name))
                    pass
        
        # Loop through domains.
        for domain_name in domain_dict.keys():
            
            coded_val_dict = domain_dict[domain_name]['val_code_dict']
            
            if domain_dict[domain_name]['type'] == "CODED":
                
                # Create table.
                arcpy.management.CreateTable(out_gdb, domain_name)
                arcpy.management.AddField(os.path.join(out_gdb, domain_name), field_name="CODE", field_type="TEXT", field_length=domain_dict[domain_name]['length'])
                arcpy.management.AddField(os.path.join(out_gdb, domain_name), field_name="VALUE", field_type="TEXT", field_length=domain_dict[domain_name]['length'])
                
                # Create insert cursor for domain tables.
                domain_table_cursor = arcpy.da.InsertCursor(os.path.join(out_gdb, domain_name), ["CODE", "VALUE"]) #@UndefinedVariableFromImport
                
                for val in coded_val_dict.keys():
                    
                    domain_table_cursor.insertRow([coded_val_dict[val], val])
                    
                del domain_table_cursor
                
                # Convert table to domain.
                arcpy.management.TableToDomain(os.path.join(out_gdb, domain_name), "CODE", "VALUE", out_gdb, domain_name, "Generated procedurally at {}".format(datetime.datetime.now()), "REPLACE")
                
                domains_pr_list.append(domain_name)
                
                # Delete table.
                arcpy.Delete_management(os.path.join(out_gdb, domain_name))
                
            elif domain_dict[domain_name]['type'] == "RANGE":
            
                arcpy.management.CreateDomain(out_gdb, domain_name, "Generated procedurally at {}".format(datetime.datetime.now()), domain_dict[domain_name]['datatype'], "RANGE")
                arcpy.management.SetValueForRangeDomain(out_gdb, domain_name, min_value=int(domain_dict[domain_name]['min']), max_value=int(domain_dict[domain_name]['max']))
            
            domains_pr_count += 1
                
            prcnt_complete(domains_pr_count, domain_count, 10, domains_start_time, leading_spaces=2, leading_text="")
    
    #------------------------------------------------------------------------------ 
    if generate_output_fc:
        
        console("Creating output features...")
        
        # Get values from input.
        in_desc = arcpy.Describe(in_fc)
        
        def geom_str(in_bool):
            if in_bool:
                return "ENABLED"
            else:
                return "DISABLED"
        
        if in_desc.dataType == "Table":
            
            arcpy.management.CreateTable(out_gdb, out_filename)
            
        elif in_desc.dataType == "FeatureClass":
        
            # Create output features.
            arcpy.management.CreateFeatureclass(out_gdb, out_filename, geometry_type=in_desc.shapeType, has_m=geom_str(in_desc.hasM), has_z=geom_str(in_desc.hasZ), spatial_reference=in_desc.spatialReference)
        
        # Delete describe object.
        del in_desc
        
        console("Adding {} fields to output...".format(len(out_field_list)),2)
        
        addfields_start_time = datetime.datetime.now()
        addfields_pr_count = 2 # Count OID and SHAPE
        addfields_total = len(in_fields)
        
        # Generate coded value dict for each field.
        for field_dict in out_field_list:
            
            if field_dict["out_type"] not in ["OID", "SHAPE"] and field_dict["in_name"] not in ["OBJECTID"]:
            
                if field_dict["out_domain"] != "":
                    
                    arcpy.management.AddField(out_fc, 
                                              field_name=field_dict["in_name"], 
                                              field_type=field_dict["out_type"], 
                                              field_length=field_dict["out_length"],
                                              field_alias=field_dict["in_alias"], 
                                              field_domain=field_dict["out_domain"])
                
                else:
                    
                    arcpy.management.AddField(out_fc, 
                                              field_name=field_dict["in_name"], 
                                              field_type=field_dict["out_type"], 
                                              field_length=field_dict["out_length"],
                                              field_alias=field_dict["in_alias"])
                    
                addfields_pr_count += 1
            
            prcnt_complete(addfields_pr_count, addfields_total, 10, addfields_start_time, leading_spaces=4, leading_text="")
        
    #------------------------------------------------------------------------------ 
    if populate_output_fc:
        
        console("Populating output features...")
        
        output_start_time = datetime.datetime.now()
        output_pr_count = 0
        
        # Create variable for fieldnames.
        in_fieldnames = [i["in_name"] for i in out_field_list]
        
        # Create insert cursor for output.
        out_cursor = arcpy.da.InsertCursor(out_fc, in_fieldnames) #@UndefinedVariableFromImport
        
        def find_field_dict(in_fname, flist):
            
            for fdict in flist:
                if fdict['in_name'] == in_fname:
                    return fdict
                
            return ""
        
        # Loop through input.
        with arcpy.da.SearchCursor(in_fc, in_fieldnames) as search_cursor_2: #@UndefinedVariableFromImport
            for row in search_cursor_2:
                
                out_row = []
                
                for idx, val in enumerate(row):
                    
                    # KLUDGE!
                    try:
                        keyval = val.replace("http:","https:")
                    except:
                        keyval = val
                    
                    field_name = in_fieldnames[idx]
                    
                    field_dict = find_field_dict(field_name, out_field_list)
                    '''
                    console(field_name)
                    console(in_fieldnames)
                    console(field_dict)
                    console(out_field_list)
                    '''
                    if field_dict != "":
                        
                        if field_dict["out_domain"] != "" and field_dict['in_type'] == "TEXT":
                            
                            coded_val_dict = field_dict['val_code_dict']
                            
                            if len(coded_val_dict) > 0 and keyval != None:
                                
                                out_row.append(coded_val_dict[keyval])
                            
                            # If list is empty, make all values None.
                            else:
                                out_row.append(None)
                    
                        # If field name is not in dictionary, it has been skipped.
                        else:
                            out_row.append(keyval)
                    
                    # If field name is not in dictionary, it has been skipped.
                    else:
                        out_row.append(keyval)
                
                # Add values to output.
                out_cursor.insertRow(out_row)
                output_pr_count += 1
                
                prcnt_complete(output_pr_count, out_feature_count, 10, output_start_time, leading_spaces=2, leading_text="")
                
    console("Script finished.")
    console_breakline("-", "+", 75)