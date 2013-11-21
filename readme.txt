"""
reportsmith.py - accepts command line argument to determine site-id, 
consumes delimited data on a pipe, writes data to a .csv, and uploads .csv via FTP
version 1.0 tested using Python 2.7.5 on Windows 7 x64
"""

usage: reportsmith.py [-h] [-s SITEID] [-n SITENAME] [-r REPORTID] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -s SITEID, --site-id SITEID
                        Assigns the value specified to the variable siteID
  -n SITENAME, --name SITENAME
                        Assigns the value specified to the variable siteID
  -r REPORTID, --report-id REPORTID
                        Assigns the value specified to the variable reportID,
                        not being used in this version
  -v, --version         show program's version number and exit


###reportsmith.config###
[data]
fieldCount = 6

[fields]
field0 = 'SITE_ID'
field1 = 'AD.ALM_DESC'
field2 = 'ADT.DESC'
field3 = 'RESPONSE_TIME'
field4 = 'DoW'
field5 = 'HoD'
field6 = 'DATE'
field7 = 'TIME'

[ftp]
url = ftp.statusops.com
username = emiller
password = t3$tt3$t