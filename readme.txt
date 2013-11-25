reportsmith.py - version 1.03 tested using Python 2.7.5 on Windows 7 x64
- Accepts command line argument to determine site-id and SiteName
- Allows for commonly configurable settings to be edited via reportsmith.config
- Consumes delimited data on a pipe
- Writes data to a .csv
- Uploads .csv via FTP

cat sample.csv | python reportsmith.py -s 1234 -n "Test Site"

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

###logging levels###
Level	Numeric value
CRITICAL	50
ERROR	40
WARNING	30
INFO	20
DEBUG	10
NOTSET	0 (not used in this module)

\\statsol\\utils

#TODO error handling try/except >> log
#TODO make logfile path configurable via config file, default is statsol/trace
#TOD) make .csv output file configurable via config file, default is statsol/trace/sched_report_files/

#TODO change repeat of str() method in date conversion section
#TODO include rowcount in log output for "finished writing" event
#TODO field mapping in config file to change order of piped values so Alfredo doesn't have to mess with pipe code to change order
#TODO catch extra delimiters and handle exception AND LOG THIS WITH WARNING
#TODO logfile rentention/cleanup (config file)
#TODO local .csv retention/cleanup (config file)
#TODO read delimiter from config file.  \t did not parse and is hardcoded in this version, others like "," do work
#TODO pull version number from config
