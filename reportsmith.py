"""
reportsmith.py - version 1.04 tested using Python 2.7.5 on Windows 7 x64
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
	global confParser, outf, startTime
	
	confParser = SafeConfigParser()
	confParser.read('reportsmith.config')
	readArgs()
	
	logging.basicConfig(
		filename=confParser.get('general', 'logDir')+'ReportSmithLog-'+timeStamped()+'.log', 
		format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',level=logging.DEBUG)

	logger('Operation started', 'INFO')
	logger('Starting setup', 'INFO')
	
	outf = open(confParser.get('general', 'outputDir')+siteID+"-"+siteName+"-"+timeStamped()+".csv",'w')
	startTime = time.time()
	logger('Setup DONE', 'INFO')

def readArgs():
	global siteID,siteName
	argParser = argparse.ArgumentParser()
	argParser.add_argument('-s', '--site-id', action='store', dest='siteID',
						help='Assigns the value specified to the variable siteID')
	argParser.add_argument('-n', '--name', action='store', dest='siteName',
						help='Assigns the value specified to the variable siteID')
	argParser.add_argument('-r', '--report-id', action='store', dest='reportID',
						help='Assigns the value specified to the variable reportID, not being used in this version')
	argParser.add_argument('-v', '--version', action='version', version=confParser.get('general', 'version'))
	results = argParser.parse_args()
	siteID = str(results.siteID)
	siteName = str(results.siteName)
	#reportID = str(results.reportID) reserved for future use

def logger(msg, level):
	if confParser.get('general', 'consoleLogging') == 'on':
		print(level+":"+msg)
	if confParser.get('general', 'logging') == 'on':
		logging.log({'DEBUG':10, 'INFO':20, 'WARNING':30, 'ERROR':40, 'CRITICAL':50}.get(level), msg)
		
def timeStamped(fmt='%Y-%m-%d-%Hh-%Mm-%Ss'):
    return datetime.datetime.now().strftime(fmt)
	
def delimTest(s, ch):
    return len([i for i, letter in enumerate(s) if letter == ch])
	
def writeFile():
	logger('Writing header', 'INFO')
	for name in confParser.options('fields'):
		outf.write(confParser.get('fields', name)+',')
	outf.write('\n')
	logger('Writing header DONE', 'INFO')
	
	logger('Writing data', 'INFO')
	lineCount =0
	delimCount = int(confParser.get('data', 'delimCount'))
	for line in sys.stdin:
		#test each processed row of piped data for embedded delimiters
		if delimTest(line, "\t") != delimCount:
			logger('DELIMITER COUNT MISMATCH', 'CRITICAL')
			
		#remove any output delimiters from piped data
		if line.find(",") >= 0:
			logger('REMOVING EMBEDDED COMMA(S)\n'+ line, 'WARNING')
			line = line.replace(",", "")
		
		#insert siteID in column 0 of each row, and write the piped data
		line = line.split("\t")
		unixTime = int(line[1])#used below to convert time
		line.insert(0,siteID)
		line = ",".join(line)
		line = line[:-2] #comment this out to turn off newline suppression
		outf.writelines(line)
		outf.write(',')
		
		#convert and append DoW, HoD, DATE and TIME to each row
		timeTuple = time.localtime(unixTime)
		dayOfWeek = timeTuple.tm_wday
		week = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
		outf.write(week[dayOfWeek]+',')
		outf.write(str(timeTuple.tm_hour)+","+str(timeTuple.tm_mon)+"/"+str(timeTuple.tm_mday)+"/"+str(timeTuple.tm_year)+",")
		outf.write(str(timeTuple.tm_hour)+":"+str(timeTuple.tm_min)+":"+str(timeTuple.tm_sec)+'\n')
		
		lineCount += 1
	outf.close()
	logger('Wrote '+str(lineCount)+' lines', 'INFO')
	logger('Writing data DONE', 'INFO')
	
def upload():
	logger('Beginning FTP upload', 'INFO')
	FTPurl = confParser.get('ftp', 'url')
	FTPusername = confParser.get('ftp', 'username')
	FTPpassword = confParser.get('ftp', 'password')
	ftp = ftplib.FTP(FTPurl)
	file = outf.name
	ftp.login(FTPusername,FTPpassword)
	ext = os.path.splitext(file)[1]
	ftp.storlines("STOR " + file, open(file))
	logger('FTP upload DONE', 'INFO')
	
def teardown():
	logger('Cleaning up logs and tempfiles', 'INFO')
	finishTime = str(round(time.time() - startTime,1))
	logger('Operation completed in ' + finishTime + ' seconds.', 'INFO')
	sys.exit()

if __name__ == '__main__':
	setup()
	writeFile()
	#upload()
	teardown()