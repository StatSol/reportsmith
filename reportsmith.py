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
	
def delimTest(s, ch):
    return len([i for i, letter in enumerate(s) if letter == ch])
	
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
	delimCount = int(confParser.get('data', 'delimCount'))
	for line in sys.stdin:
		#test each processed row of piped data for embedded delimiters
		if delimTest(line, "\t") != delimCount:
			logger('EMBEDDED DELIMITER LINE '+ line, 'warning')
			print(delimCount,delimTest(line, "\t"))
			
		#remove any output delimiters from piped data
		line = line.replace(",", "")
		if line.find(",") >= 0:
			print("COMMA: ", line)
		
		#insert siteID in column 0 of each row, and write the piped data
		line = line.split("\t")
		line.insert(0,siteID)
		line = ",".join(line)
		line = line[:-2] #comment this out to turn off newline suppression
		outf.writelines(line)
		outf.write(',')
		
		#convert and append DoW, HoD, DATE and TIME to each row
		unixTime = int(line[1])
		timeTuple = time.localtime(unixTime)
		dayOfWeek = timeTuple.tm_wday
		week = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
		outf.write(week[dayOfWeek])
		outf.write(',')
		outf.write(str(timeTuple.tm_hour)+","+str(timeTuple.tm_mon)+"/"+str(timeTuple.tm_mday)+"/"+str(timeTuple.tm_year)+",")
		outf.write(str(timeTuple.tm_hour)+":"+str(timeTuple.tm_min)+":"+str(timeTuple.tm_sec))


		
		outf.write('\n')
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
	sys.exit()

if __name__ == '__main__':
	setup()
	writeFile()
	upload()
	teardown()