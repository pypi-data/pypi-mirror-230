Current Version: 2.0.2

Patch Notes: 

===========================================================================

[2.0.2]: Fixed issue with returning data 

===========================================================================

[2.0.1]: Added new module for scanning excel sheets with the command "search_excel_file(sheet_name, keyword, row_offset, column_offset, search_in_column, search_in_row). 

sheet_name: Name of the sheet within the file you would like to search through

keyword: Keywords you would like to search for, format ["keyword1", "keyword2"]

row_offset: Number of rows offset the target would you like to read from

column_offset: Number of column offset the target would you like to read from

search_in_column: Defaults to "None" lets you pick a specific column to read from, ex. "A", "B", or "C"

search_in_row: Defaults to "None" lets you pick a specific column to read from, ex. 1, 2, or 3


===========================================================================

[1.5.3]: Fixed patchnotes formating 

===========================================================================

[1.5.2]: Fixed issue where writeToSheet() would just create a new sheet and delete the previous data

===========================================================================

[1.5.1]: Creating a new "build" added an auto spreadsheet creating and updating function for use with both robot and manual data tracking, 

- added createNewSheet(): to create the sheet (names the sheet the current date)

- added writeToSheet(): Use to write data to the created sheet although running "createNewSheet()" is not required as the function will create one if a sheet under the current date cannot be located. Format for the function is writeToSheet(Row, Column, data)

===========================================================================

[0.5.2]: "Added equations for "limelight" functions"

===========================================================================

[0.5.1]: "Started Unstable build 0.5"

===========================================================================

reminder to py -m build
and py -m twine upload --repository pypi dist/*