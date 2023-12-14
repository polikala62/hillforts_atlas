DESCRIPTION:

These scripts were written to get the Hillforts Atlas back online. There are workarounds and 
kludges that will need to be sorted before they can be used for anything else.

Most things are controlled using hardcoded filepaths. The most recent paths are still in the code.

Some scripts are set to NOT produce output, for testing purposes. In this case output should be 
controlled by a boolean near the beginning of the function.

SCRIPTS:

"Field_to_Domain" creates domains based on values in a data table.
	- Version 1 is an early version and is not functional.
	- Version 2 creates integer coded-values.
	- Version 4 creates text coded-values.
	
"functions_excel" contains functions for reading Ecxel files. Copied from FLAME scripts.

"general_functions" contains functions for console output.

"Update_Hillforts_Files" coordinates "Field_to_Domain" for multiple feature classes. It also controls exceptions to domain-generation.

"Update_Hillforts_Table" checks a feature class table against an excel spreadsheet.
	- Version 1 is an early version and may not be functional.
	- Version 2 is functional.