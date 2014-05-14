#! /usr/bin/python
########################################################################
# Scan for closest Open NIC servers and set the system to use them.
# Copyright (C) 2014  Carl J Smith
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################
import os, sys, re
from time import sleep
########################################################################
def loadFile(fileName):
	try:
		print "Loading :",fileName
		fileObject=open(fileName,'r');
	except:
		print "Failed to load :",fileName
		return False
	fileText=''
	lineCount = 0
	for line in fileObject:
		fileText += line
		sys.stdout.write('Loading line '+str(lineCount)+'...\r')
		lineCount += 1
	print "Finished Loading :",fileName
	fileObject.close()
	if fileText == None:
		return False
	else:
		return fileText
	#if somehow everything fails return fail
	return False
########################################################################
def writeFile(fileName,contentToWrite):
	# figure out the file path
	filepath = fileName.split(os.sep)
	filepath.pop()
	filepath = os.sep.join(filepath)
	# check if path exists
	if os.path.exists(filepath):
		try:
			fileObject = open(fileName,'w')
			fileObject.write(contentToWrite)
			fileObject.close()
			print 'Wrote file:',fileName
		except:
			print 'Failed to write file:',fileName
			return False
	else:
		print 'Failed to write file, path:',filepath,'does not exist!'
		return False
########################################################################
def downloadFile(fileAddress):
	from urllib2 import urlopen
	try:
		print "Downloading :",fileAddress
		downloadedFileObject = urlopen(str(fileAddress))
	except:
		print "Failed to download :",fileAddress
		return False
	lineCount = 0
	fileText = ''
	for line in downloadedFileObject:
		fileText += line
		sys.stdout.write('Loading line '+str(lineCount)+'...\r')
		lineCount+=1
	downloadedFileObject.close()
	print "Finished Loading :",fileAddress
	return fileText
########################################################################
#Function that opens a xml file and reads data from a set of tags
def xmlTagValues(fileName,tagValue):
	'''Open a file (fileName) and search line by line through the 
	file for every occurrence of a xml tag (tagValue) and return the 
	values inside each of the tags in an array. If no values are 
	found the function will return the value (None). NOTE: This can 
	not find multiples of the same tag if they are on the same 
	line.'''
	from re import sub,search,findall
	#open the specified file
	fileObject = open(fileName,'r')
	# create local variables to be used latter
	temp = ''
	totalTags = 0
	values = []
	# loop through the lines in the file
	for i in fileObject:
		if i[:1] != '#':
			# remove all newlines and tabs
			i = sub('\n','',i)
			i = sub('\t+','',i)
			temp += i
			if search(('<'+tagValue+'>'),i) != None:
				totalTags += 1
	# close the file to save memory
	fileObject.close()
	# if the tag specified by the user was not found in the file return
	# None
	if totalTags == 0:
		return None
	else:
		# Loop through the string as many times as the tag is found
		for x in range(len(findall(('<'+tagValue+'>'),temp))):
			# Find the front and back of the value inside the tags to cut it out
			front = (temp.find(('<'+tagValue+'>'))+len(('<'+tagValue+'>')))
			back = temp.find(('</'+tagValue+'>'))
			# add the values into the (values) array
			values.append(temp[front:back])
			# cut the temp string up to the end of the last string worked on
			temp = temp[(back+len(tagValue+'>')):]
		return values
########################################################################
def grabXmlValues(inputString, tagValue):
	'''Gets all xml values from a text string matching the search value
	and returns an array'''
	from re import sub,search,findall
	tagValue = str(tagValue)# just in case
	totalTags = inputString.find(tagValue)
	values = []
	temp = inputString
	if totalTags == -1:
		#~ print 'XML values do not exist for '+tagValue
		return []
	else:
		# Loop through the string as many times as the tag is found
		#~ while temp.find(('<'+tagValue+'>')):
		for x in range(len(findall(('<'+tagValue+'>'),temp))):
			# Find the front and back of the value inside the tags to cut it out
			front = (temp.find(('<'+tagValue+'>'))+len(('<'+tagValue+'>')))
			back = temp.find(('</'+tagValue+'>'))
			# add the values into the (values) array
			values.append(temp[front:back])
			#~ print 'CUT','front',front,'back',back,'lenth',len(temp) # DEBUG
			#~ print temp[front:back]
			# cut the temp string up to the end of the last string worked on
			temp = temp[(back+len(tagValue+'>')):]
		return values
########################################################################
def replaceLineInFile(fileName,stringToSearchForInLine,replacementText):
	# open file
	temp = loadFile(fileName)
	# if file exists append, if not write
	newFileText = ''
	if temp != False:
		temp = temp.split('\n')
		for line in temp:
			if line.find(stringToSearchForInLine) == -1:
				newFileText += line+'\n'
			else:
				if replacementText != '':
					print 'Replacing line:',line
					print 'With:',replacementText
					newFileText += replacementText+'\n'
				else:
					print 'Deleting line:',line
	else:
		return False
	writeFile(fileName,newFileText)
########################################################################
downloadData = False
retryCounter = 0
# download webpage that shows closest dns servers
while downloadData == False: # try to download the file 10 times
	downloadData = downloadFile('http://www.opennicproject.org/nearest-servers/')
	if retryCounter >= 10:
		# fail and exit if the server list page fails to download
		print 'ERROR: Server list failed to download, program will now exit.'
		exit()
	elif downloadData == False:
		print 'Waiting 5 seconds before retry...'
		sleep(5)
	retryCounter += 1
# start work on ripping out ip addresses of dns servers
downloadData = grabXmlValues(grabXmlValues(downloadData,'div class="post-entry"')[0],'p')[0].split('\n')
data = []
# split each line pulled out and look for nbsp in em to split on
for index in downloadData:
	if '&nbsp' in index:
		temp = index.split('&nbsp')[0]
		if temp != None:
			data.append(temp)
# ip addresses are stored in data so start building line to insert in config
temp = 'prepend domain-name-servers '
for index in data:
	temp += index+', '
temp += '\n'
temp = temp.replace(', \n',';')
# insert the line in the config
replaceLineInFile('/etc/dhcp/dhclient.conf','prepend domain-name-servers',temp)
print 'New dns settings will be applied on next system restart.'
