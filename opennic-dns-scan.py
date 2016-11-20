#! /usr/bin/python
########################################################################
# Scan for closest Open NIC servers and set the system to use them.
# Copyright (C) 2016  Carl J Smith
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
from urllib2 import urlopen
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
def replaceLineInFile(fileName,stringToSearchForInLine,replacementText):
	# open file
	temp = loadFile(fileName)
	# if file exists append, if not write
	newFileText = ''
	if temp != False:
		temp = temp.split('\n')
		for line in temp:
			if line.find(stringToSearchForInLine) == -1:
				newFileText += line.strip()+'\n'
			else:
				if replacementText != '':
					print 'Replacing line:',line
					print 'With:',replacementText
					newFileText += replacementText.strip()+'\n'
				else:
					print 'Deleting line:',line
	else:
		return False
	# Remove groups of three or more blank lines
	while newFileText.find('\n\n\n') != -1:
		newFileText = newFileText.replace('\n\n\n','\n')
	# write the file
	writeFile(fileName,newFileText)
########################################################################
if '--help' in sys.argv:
	print('#'*80)
	print('Scan for closest Open NIC servers and set the system to use them.')
	print('Copyright (C) 2016  Carl J Smith')
	print('')
	print('This program is free software: you can redistribute it and/or modify')
	print('it under the terms of the GNU General Public License as published by')
	print('the Free Software Foundation, either version 3 of the License, or')
	print('(at your option) any later version.')
	print('')
	print('This program is distributed in the hope that it will be useful,')
	print('but WITHOUT ANY WARRANTY; without even the implied warranty of')
	print('MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the')
	print('GNU General Public License for more details.')
	print('')
	print('You should have received a copy of the GNU General Public License')
	print('along with this program.  If not, see <http://www.gnu.org/licenses/>.')
	print('#'*80)
	print('--help')
	print('    Display this help menu.')
	print('--only-opennic')
	print('    Do not append opendns and google public dns to the')
	print('    dns nameservers used by the system.')
	print('-s')
	print('    Skip the given number of entries returned from opennic.')
	print('    ex) "opennic-dns-scan -s 2" would skip the first two')
	print('    entries returned.')
	print('--remove')
	print('    Remove changes to dns settings on system.')
	exit()
########################################################################
if '--remove' in sys.argv:
	# reset all the custom dns back to localhost
	line = 'prepend domain-name-servers 127.0.0.1'
	replaceLineInFile('/etc/dhcp/dhclient.conf','prepend domain-name-servers',line)
	writeFile('/etc/network/interfaces.d/custom-dns','')
	exit()
########################################################################
downloadData = False
retryCounter = 0
# download webpage for opennic dns servers using opennic web api
while downloadData == False: # try to download the file 10 times
	downloadData = downloadFile('http://api.opennicproject.org/geoip/?bare')
	if retryCounter >= 10:
		# fail and exit if the server list page fails to download
		print 'ERROR: Server list failed to download, program will now exit.'
		exit()
	elif downloadData == False:
		print 'Waiting 5 seconds before retry...'
		sleep(5)
	retryCounter += 1
# start work on ripping out ip addresses of dns servers
data = downloadData.split('\n')
# skip given number of ips given in opennic results
if '-s' in sys.argv:
	data = data[int(sys.argv[sys.argv.index('-s')+1]):]
# the order of resolution will be opennic,opendns,google public dns
# so add opendns and google dns to the end of the nameservers list
if '--only-opennic' not in sys.argv:
	# add the opendns domain name servers
	data.append('208.67.222.222')
	data.append('208.67.220.220')
	# add the google domain name servers
	data.append('8.8.8.8')
	data.append('8.8.4.4')
################################################################################
# change the prepend dns servers in /etc/dhcp/dhclient.conf
line = 'prepend domain-name-servers '
# add all the ips to generate the line containing setting the dns servers
for ip in data:
	# ignore blank lines
	if ip != '':
		line += ip+', '
line += '\n'
line = line.replace(', \n',';')
# insert the line in the config
replaceLineInFile('/etc/dhcp/dhclient.conf','prepend domain-name-servers',line)
################################################################################
# now update the /etc/network/interfaces.d/custom-dns
line = 'dns-nameservers '
for ip in data:
	# ignore blank lines
	if ip != '':
		line += ip+' '
writeFile('/etc/network/interfaces.d/custom-dns',line)
################################################################################
print 'New dns settings will be applied on next system restart.'
