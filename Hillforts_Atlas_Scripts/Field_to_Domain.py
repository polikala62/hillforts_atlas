'''
Created on Oct 23, 2023

@author: kjsmi
'''

import arcpy, os, datetime
from general_functions import console, console_breakline, prcnt_complete

# Set processing variables.
arcpy.env.overwriteOutput = True
generate_domains = True
generate_output_fc = True
populate_output_fc = True

# Set input variables.
in_fc = r"C:\GIS\Hillforts_Atlas\Hillforts\Hillforts.gdb\Hillforts"
string_fields_list = [] # List of fields to transform into coded values.
numeric_fields_list = []

out_fc = r"C:\GIS\Hillforts_Atlas\Hillforts\test.gdb\test_hillforts"
out_gdb, out_filename = os.path.split(out_fc)

#------------------------------------------------------------------------------ 

# TODO: Split dictionaries into "in" and "out" versions.
#    Maybe actually create classes if I can remember how to do that?
class field_data():
    # Variables for input.
    in_field_name = ""
    in_field_alias = ""
    in_field_length = 1
    in_field_min = 1
    in_field_max = 1
    # Variables for output.
    out_field_type = ""
    out_field_length = 1
    # Code-value dictionary.
    val_code_dict = {}

# Create lists and dictionaries to create output.
coded_val_dict = {"No_Yes":{"No":1, "Yes":2}} # Format: dict[fieldname] = {field_code_dict}
field_domain_dict = {} # Format: dict[fieldname] = domain name
field_length_dict = {"No_Yes":3} # Format: dict[fieldname] = max field length
field_alias_dict = {} # Format: dict[fieldname] = field alias
field_minmax_dict = {} # Format: dict[fieldname] = [min, max]
field_type_dict = {} # Format: dict[fieldname] = type string.
out_field_type_dict = {}

# List of domains to process - should be list of valus for field_domain_dict.
coded_domains_list = ["No_Yes_domain"] # Have No_Yes_domain as default.
range_domains_list = []
all_domains_list = coded_domains_list + range_domains_list

# List input fields (used in several steps below).
in_fields = arcpy.ListFields(in_fc)
in_fieldnames = [i.name for i in in_fields]

#------------------------------------------------------------------------------ 

# Use dictionary to format types for Create Domain.
tr_types_dict = {"Double":"DOUBLE", "Integer":"LONG", "Single":"FLOAT", "SmallInteger":"SHORT",
                 "String":"TEXT"}

# Populate field_alias_dict and field_type_dict.
for field in in_fields:
    field_alias_dict[field.name] = field.aliasName
    if field.type in tr_types_dict.keys():
        field_type_dict[field.name] = tr_types_dict[str(field.type)]
        out_field_type_dict[field.name] = tr_types_dict[str(field.type)]
    else:
        field_type_dict[field.name] = field.type
        out_field_type_dict[field.name] = field.type

#------------------------------------------------------------------------------ 
# List fields.
for field_idx, field in enumerate(in_fields):
    if field.type == "String":
        string_fields_list.append(field.name)
    elif field.type in ["Double", "Integer", "Single", "SmallInteger"]:
        numeric_fields_list.append(field.name)

#------------------------------------------------------------------------------ 
console_breakline("-", "+", 75)
console("Started script 'Field_to_Domain'.")
console("")
console("Input features: {}".format(in_fc))
console("Input contains {} string fields.".format(len(string_fields_list)),2)
console("Input contains {} numeric fields.".format(len(numeric_fields_list)),2)
console("")
console("Output features: {}".format(out_fc))
console("")

#------------------------------------------------------------------------------ 
console("Gathering unique values from fields...")

all_fields_list = string_fields_list + numeric_fields_list

domains_count = 0

# Generate coded value dict for each field.
for field_name in in_fieldnames:
    
    # Create list to hold row values.
    row_vals = []
    
    # Populate list with unique values.
    with arcpy.da.SearchCursor(in_fc, [field_name]) as search_cursor: #@UndefinedVariableFromImport
        
        for row in search_cursor:
            
            if row[0] not in row_vals and row[0] != None:
                
                row_vals.append(row[0])
    
    del search_cursor
    
    # Check that there are values in list (that not all values are None).
    if len(row_vals) > 0:
        
        if field_name in string_fields_list:
        
            # Sort list alphabetically.
            sorted_row_vals = sorted(row_vals)
            
            # Update field_length_dict.
            field_length_dict[field_name] = max([len(i) for i in sorted_row_vals])
            
            # Replace domain dict with 'no_yes_domain' if appropriate.
            if sorted_row_vals == ["No", "Yes"]:
                
                field_domain_dict[field_name] = "No_Yes_domain"
                
            else:
                
                # Create subdict.
                field_code_dict = {} # Format: dict[val] = code
                for i, j in enumerate(sorted_row_vals):
                    field_code_dict[j] = (i + 1)
                    domains_count += 1
                    
                # Add subdict to coded vals dict.
                coded_val_dict[field_name] = field_code_dict
                
                field_domain_dict[field_name] = "{}_domain".format(field_name)
                
                coded_domains_list.append("{}_domain".format(field_name))
                all_domains_list.append("{}_domain".format(field_name))
                
        elif field_name in numeric_fields_list:
            
            # Update field_length_dict.
            field_length_dict[field_name] = max([len(str(i)) for i in row_vals])
            
            # Update minmax dict.
            field_minmax_dict[field_name] = [int(min(row_vals)), int(max(row_vals))+1] # Round down and up to nearest integer.
            
            domains_count += 1
            
            # Add domain to dictionary.
            field_domain_dict[field_name] = "{}_domain".format(field_name)
            
            range_domains_list.append("{}_domain".format(field_name))
            all_domains_list.append("{}_domain".format(field_name))
            
    else:
        field_length_dict[field_name] = 1

#------------------------------------------------------------------------------ 
if generate_domains:
    
    console("Creating {} entries in {} domains...".format(domains_count, len(all_domains_list)))
    
    domains_start_time = datetime.datetime.now()
    domains_pr_count = 0
    domains_total = domains_count
    
    domains_pr_list = []
    
    # Loop through domains.
    for domain_name in all_domains_list:
        
        field_name = domain_name.split("_domain")[0]
        
        if domain_name in coded_domains_list:
            
            # Create table.
            arcpy.management.CreateTable(out_gdb, domain_name)
            arcpy.management.AddField(os.path.join(out_gdb, domain_name), field_name="CODE", field_type="SHORT")
            arcpy.management.AddField(os.path.join(out_gdb, domain_name), field_name="VALUE", field_type="TEXT", field_length=field_length_dict[field_name])
            
            # Create insert cursor for domain tables.
            domain_table_cursor = arcpy.da.InsertCursor(os.path.join(out_gdb, domain_name), ["CODE", "VALUE"]) #@UndefinedVariableFromImport
            
            for val in coded_val_dict[field_name].keys():
                
                domain_table_cursor.insertRow([coded_val_dict[field_name][val], val])
                
            del domain_table_cursor
            
            # Convert table to domain.
            arcpy.management.TableToDomain(os.path.join(out_gdb, domain_name), "CODE", "VALUE", out_gdb, domain_name, "Generated procedurally at {}".format(datetime.datetime.now()), "REPLACE")
            
            out_field_type_dict[field_name] = "SHORT"
            
            domains_pr_list.append(domain_name)
            
        elif domain_name in range_domains_list:
            try:
                arcpy.management.CreateDomain(out_gdb, domain_name, "Generated procedurally at {}".format(datetime.datetime.now()), field_type_dict[field_name], "RANGE")
                arcpy.management.SetValueForRangeDomain(out_gdb, domain_name, min_value=field_minmax_dict[field_name][0], max_value=field_minmax_dict[field_name][1])
            except:
                pass
            
        domains_pr_count += 1
            
        prcnt_complete(domains_pr_count, domains_total, 10, domains_start_time, leading_spaces=2, leading_text="")

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
    
    # Create output features.
    arcpy.management.CreateFeatureclass(out_gdb, out_filename, geometry_type=in_desc.shapeType, has_m=geom_str(in_desc.hasM), has_z=geom_str(in_desc.hasZ), spatial_reference=in_desc.spatialReference)
    
    # Delete describe object.
    del in_desc
    
    console("Adding fields to output...",2)
    
    addfields_start_time = datetime.datetime.now()
    addfields_pr_count = 0
    addfields_total = len(in_fields)
    
    # Add fields to features.
    for field in in_fields:
        
        if field.name not in ["OBJECTID", "Shape"] and field.name in field_domain_dict.keys():
            '''
            console(out_fc)
            console(field.name)
            console(out_field_type_dict[field.name])
            console(field_length_dict[field.name])
            console(field_alias_dict[field.name])
            console(field_domain_dict[field.name])
            '''
            arcpy.management.AddField(out_fc, 
                                      field_name=field.name, 
                                      field_type=out_field_type_dict[field.name], 
                                      field_length=field_length_dict[field.name],
                                      field_alias=field_alias_dict[field.name], 
                                      field_domain=field_domain_dict[field.name])
            
        elif field.name not in ["OBJECTID", "Shape"]:
            #print(out_fc, field.name, field.type)
            arcpy.management.AddField(out_fc, 
                                      field_name=field.name, 
                                      field_type=field.type, 
                                      field_length=field_length_dict[field.name], 
                                      field_alias=field_alias_dict[field.name])
            
        addfields_pr_count += 1
        
        prcnt_complete(addfields_pr_count, addfields_total, 10, addfields_start_time, leading_spaces=4, leading_text="")
    
#------------------------------------------------------------------------------ 
if populate_output_fc:
    
    console("Populating output features...")
    
    # Create insert cursor for output.
    out_cursor = arcpy.da.InsertCursor(out_fc, in_fieldnames) #@UndefinedVariableFromImport
    
    # Loop through input.
    with arcpy.da.SearchCursor(in_fc, in_fieldnames) as search_cursor_2: #@UndefinedVariableFromImport
        for row in search_cursor_2:
            
            out_row = []
            
            for idx, val in enumerate(row):
                
                field_name = in_fieldnames[idx]
                if field_name in coded_val_dict.keys():
                
                    if len(coded_val_dict[field_name]) > 0 and val != None:
                        
                        out_row.append(coded_val_dict[field_name][val])
                    
                    # If list is empty, make all values None.
                    else:
                        out_row.append(None)
                
                # If field name is not in dictionary, it has been skipped.
                else:
                    out_row.append(val)
            
            # Add values to output.
            out_cursor.insertRow(out_row)

console("Script finished.")
console_breakline("-", "+", 75)