#! /usr/bin/python

# scan index of servers with urllib2 its a webpage

# use xml scan code to find td

# regex match patters of ip addresses in index created before

# ping each of the ip addresses which are dns servers and sort them in order of lowest ping time to highest

# edit /etc/dhcp/dhclient.conf 

# edit line with string "prepend domain-name-servers"

# insert "prepend domain-name-servers ip1, ip2, ip3;"

# ip1, ip2, etc would be the lowest ping times found above.

# for good measure just add the entire list of ip addresses since if one can not be used the next will be checked, this will not waste much and will add lots of robustness

# done, tell user settings will be applied on reboot, although perhaps pulling down the network and turning it back on may work, attempt testing of this latter
