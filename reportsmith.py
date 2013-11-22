"""
reportsmith.py - accepts command line argument to determine site-id, 
consumes delimited data on a pipe, writes data to a .csv, and uploads .csv via FTP
version 1.02 tested using Python 2.7.5 on Windows 7 x64
"""

#HIGH
#TODO field mapping in config file to change order of piped values so Alfredo doesn't have to mess with pipe code to change order
#TODO logic in writeRows() to build DoW, HoD, Date, & Time fields
#TODO path to reportsmith.config needs to be hardcoded.

#MED
#TODO catch extra delimiters and handle exception
#TODO logging
#TODO logfile rentention/cleanup (config file)
#TODO local .csv retention/cleanup (config file)
#TODO read delimiter from config file.  \t did not parse and is hardcoded in this version, others like "," do work
#TODO error handling try/except

#LOW
#TODO matplotlib chart option

import ftplib
import os
import argparse
import datetime
import sys
import time
from ConfigParser import SafeConfigParser

def setup():
	#setup configparser @ ./reportsmith.config, assign some values from config and command line args, ready the .csv for writing, start a timer
	os.chdir("C:\\Users\\user\\Desktop\\reportsmith") #changes CWD focus to this module's directory
	global confParser, outf, startTime, consoleLogging
	confParser = SafeConfigParser()
	confParser.read('reportsmith.config')
	consoleLogging = confParser.get('general', 'consoleLogging')
	if consoleLogging == 'on':
		print('Beginning setup...'),
	readArgs() #processes readargs() function to populate global vars from command line args
	outf = open(siteName+"-"+siteID+"-"+timeStamped()+".csv",'w') #open .csv for writing
	startTime = time.time()
	if consoleLogging == 'on':
		print("DONE")

def readArgs():
	#read arguments from the command line and assign values passed from those arguments
	argParser = argparse.ArgumentParser()
	argParser.add_argument('-s', '--site-id', action='store', dest='siteID',
						help='Assigns the value specified to the variable siteID')
	argParser.add_argument('-n', '--name', action='store', dest='siteName',
						help='Assigns the value specified to the variable siteID')
	argParser.add_argument('-r', '--report-id', action='store', dest='reportID',
						help='Assigns the value specified to the variable reportID, not being used in this version')
	argParser.add_argument('-v', '--version', action='version', version='%(prog)s 1.02')
	results = argParser.parse_args()
	global siteID,siteName
	siteID = str(results.siteID)
	siteName = str(results.siteName)
	#reportID = str(results.reportID)
	
def timeStamped(fmt='%Y-%m-%d-%Hh-%Mm-%Ss'):
	#timestamp as name in output file to prevent overwrites and provide output history
    return datetime.datetime.now().strftime(fmt)
	
def findOccurences(s, ch):
	#used to test for embedded delimiters
    return [i for i, letter in enumerate(s) if letter == ch]
	
def writeFile():
	#write header row from config data
	if consoleLogging == 'on':
		print('Writing header...'),
	for name in confParser.options('fields'):
		fieldValue = confParser.get('fields', name)
		fieldValue = fieldValue.replace("'", "")
		outf.write(fieldValue)
		outf.write(',')
	outf.write('\n')
	if consoleLogging == 'on':
		print("DONE")
	
	"""
	#write csv out line by line from stdin
	print('Writing rows...'),
	fieldCount = int(confParser.get('data', 'fieldCount'))-1#determine number of fields, to be used to catch extra delimiters in data values
	for line in sys.stdin:
		#masterList.append(line) #uncomment if you want to manipulate (do math) on the data as a list.  be sure to declare masterlist = []
		#line = line[:-2] #uncomment this in cases where you'd like remove the /n newline from the last value in each line
		outf.write(siteID)
		outf.write(',')
		test = findOccurences(line, "\t")#configure delimiter here
		line = line.replace("\t", ",")#configure delimiter here
		outf.writelines(line)
	outf.close()
	print("DONE")
	"""
	
	#write csv out line by line from stdin
	#we read string from stdin, break it apart into a list(), insert some values from config and command line args
	#do string manipulation on some list values, then join it back to a comma delimited list to write to file.
	if consoleLogging == 'on':
		print('Writing rows...'),
	fieldCount = int(confParser.get('data', 'fieldCount'))-1#determine number of fields, to be used to catch extra delimiters in data values
	for line in sys.stdin:
		#masterList.append(line) #uncomment if you want to manipulate (do math) on the data as a list.  be sure to declare masterlist = []
		#line = line[:-2] #uncomment this in cases where you'd like remove the /n newline from the last value in each line
		
		test = findOccurences(line, "\t")#configure delimiter here
		line = line.split("\t")#configure delimiter here
		line.insert(0,siteID) #first column
		
	
		line = ",".join(line)
		outf.writelines(line)
	outf.close()
	if consoleLogging == 'on':
		print("DONE")
	
def upload():
	#upload a file via ftp using credentials in ./reportsmith.config
	if consoleLogging == 'on':
		print('Beginning FTP upload...'),
	FTPurl = confParser.get('ftp', 'url')
	FTPusername = confParser.get('ftp', 'username')
	FTPpassword = confParser.get('ftp', 'password')
	ftp = ftplib.FTP(FTPurl)
	file = outf.name
	ftp.login(FTPusername,FTPpassword)
	ext = os.path.splitext(file)[1]
	ftp.storlines("STOR " + file, open(file))
	if consoleLogging == 'on':
		print("DONE")
	
def teardown():
	#log, and clean up logs and local versions of the .csv
	finishTime = str(round(time.time() - startTime,1))
	if consoleLogging == 'on':
		print("Operation completed in " + finishTime + " seconds.")
	sys.exit

if __name__ == '__main__':
	setup()
	writeFile()
	#upload()
	teardown()