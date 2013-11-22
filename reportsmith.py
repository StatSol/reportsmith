"""
reportsmith.py - version 1.03 tested using Python 2.7.5 on Windows 7 x64
- Accepts command line argument to determine site-id and SiteName
- Allows for commonly configurable settings to be edited via reportsmith.config
- Consumes delimited data on a pipe
- Writes data to a .csv
- Uploads .csv via FTP
"""

import ftplib
import os
import argparse
import datetime
import sys
import time
import logging
from ConfigParser import SafeConfigParser

def setup():
	os.chdir("C:\\Users\\user\\Desktop\\reportsmith")
	global confParser, outf, startTime, consoleLogging, fileLogging
	
	confParser = SafeConfigParser()
	confParser.read('reportsmith.config')
	
	fileLogging = confParser.get('general', 'logging')
	consoleLogging = confParser.get('general', 'consoleLogging')
	logging.basicConfig(filename='ReportSmithLog-'+timeStamped()+'.log', format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',level=logging.DEBUG)

	logger('Operation started', 'info')
	logger('Starting setup', 'info')
	readArgs()
	outf = open(siteName+"-"+siteID+"-"+timeStamped()+".csv",'w')
	startTime = time.time()
	logger('Setup DONE', 'info')

def readArgs():
	argParser = argparse.ArgumentParser()
	argParser.add_argument('-s', '--site-id', action='store', dest='siteID',
						help='Assigns the value specified to the variable siteID')
	argParser.add_argument('-n', '--name', action='store', dest='siteName',
						help='Assigns the value specified to the variable siteID')
	argParser.add_argument('-r', '--report-id', action='store', dest='reportID',
						help='Assigns the value specified to the variable reportID, not being used in this version')
	argParser.add_argument('-v', '--version', action='version', version='%(prog)s 1.03')
	results = argParser.parse_args()
	global siteID,siteName
	siteID = str(results.siteID)
	siteName = str(results.siteName)
	#reportID = str(results.reportID) reserved for future use

def logger(msg, level):
	if consoleLogging == 'on':
		print(level+":"+msg)
	loggingLevel = {'debug':10, 'info':20, 'warning':30, 'error':40, 'critical':50}
	if fileLogging == 'on':
		logging.log(loggingLevel[level], msg)

def timeStamped(fmt='%Y-%m-%d-%Hh-%Mm-%Ss'):
    return datetime.datetime.now().strftime(fmt)
	
def findOccurences(s, ch):
	#used to test for embedded delimiters
    return [i for i, letter in enumerate(s) if letter == ch]
	
def writeFile():
	logger('Writing header', 'info')
	for name in confParser.options('fields'):
		fieldValue = confParser.get('fields', name)
		fieldValue = fieldValue.replace("'", "")
		outf.write(fieldValue)
		outf.write(',')
	outf.write('\n')
	logger('Writing header DONE', 'info')
	
	logger('Writing data', 'info')
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
	logger('Writing data DONE', 'info')
	
def upload():
	logger('Beginning FTP upload', 'info')
	FTPurl = confParser.get('ftp', 'url')
	FTPusername = confParser.get('ftp', 'username')
	FTPpassword = confParser.get('ftp', 'password')
	ftp = ftplib.FTP(FTPurl)
	file = outf.name
	ftp.login(FTPusername,FTPpassword)
	ext = os.path.splitext(file)[1]
	ftp.storlines("STOR " + file, open(file))
	logger('FTP upload DONE', 'info')
	
def teardown():
	logger('Cleaning up logs and tempfiles', 'info')
	finishTime = str(round(time.time() - startTime,1))
	logger('Operation completed in ' + finishTime + ' seconds.', 'info')
	sys.exit

if __name__ == '__main__':
	setup()
	writeFile()
	#upload()
	teardown()