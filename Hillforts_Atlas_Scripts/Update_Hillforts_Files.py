'''
Created on Nov 11, 2023

@author: kjsmi
'''

from Field_to_Domain_3 import field_to_domain

pr_gdb = r"C:\GIS\Hillforts_Atlas\Hillforts\Hillforts_1.gdb"

pr_list = [[r"xHillforts", r"Hillforts",
            ["Alternative_Name_s_","Annex_Summary","Atlas_URL","Boundary_Comments","Chevaux_de_Frise_Comments","Data_Comments",
            "Dating_Evidence__Comments","Display_Name","Ditches_Comments","Dominant_Topographic_Feature",
            "Enclosing_Surface__Comments","Enclosing_Works_Comments","Enclosing_Works_Summary","Entrances_Comments","Entrances",
            "Entrances_Summary","Excavated_Evidence__Comments","Finds__Comments","Gang_Working_Comments","HER",
            "HER_Primary_Record_Number","HER_Second_Identifier","Hillfort_Type__Comments","Historic_County","Individual_Group",
            "Interior_Aerial__Comments","Interior_Excavation__Comments","Interior_Geophysics__Comments","Interior_Summary",
            "Interpretation_Comments","Investigations","Investigations_Summary","Land_Use__Comments",
            "Monument_Condition__Comments","Name","NMR_Monument_Number","NMR_Record_Number","NMR_Resource","NMR_URL",
            "Number_of_Ramparts_by_Quadrant_Comments","Original_Entrances_Comments","Post_Hillfort_Activity_Comments",
            "Pre_Hillfort_Activity_Comments","Ramparts_Comments","Record_URL","References","Scheduled_Monument_Number",
            "Second_Country","Second_Current_County_or_Unitary_Authority","Second_Current_Parish_Community_Council_Townland",
            "Second_HER","Second_HER_Primary_Record_Number","Second_Historic_County","Site_Name","Summary_Description",
            "Surface_Evidence__Comments","Topographic_Position__Comments","Water_Source__Comments","Wikidata_URL"]],
            [r"xDating_Evidence", r"Dating_Evidence",
             ["Site_Name","Dating_Evidence_Comments"]],
            [r"xEntrances", r"Entrances",
             ["Site_Name","Entrances_Summary","Entrance_Comments"]],
            [r"xInvestigations", r"Investigations",
             ["Site_Name","Investigation_Comments"]],
            [r"xReferences", r"References",
             ["Hillfort","Reference"]]
            ]

for i in pr_list:
    print("")
    print(i[0])
    print("")
    pr_in_fc, pr_out_fc, exclude_list = i
    
    in_fc = r"{}\{}".format(pr_gdb, pr_in_fc)
    out_fc = r"{}\{}".format(pr_gdb, pr_out_fc)
    
    field_to_domain(in_fc, out_fc, exclude_list)
    print("")
    