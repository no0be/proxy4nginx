#!/usr/bin/python
#
# Edit the nginx configuration to quickly change
# the proxy_pass destination on-demand.
#
# Written by: Samy BAIWIR
# https://twitter.com/gilgha
#
import sys
import argparse
import os
from subprocess import call

# general parameters
proxy4nginx_dir	= '/opt/proxy4nginx'
nginx_dir		= '/etc/nginx'
configfile 		= 'proxy4nginx.conf'
templatefile 	= 'config_template'
virtualhost		= 'proxy'

# random manipulations on general parameters
if not nginx_dir.endswith('/'): nginx_dir += '/'
if not proxy4nginx_dir.endswith('/'): proxy4nginx_dir += '/'

# constructed general parameters :-)
sitesenabled_path	= nginx_dir + 'sites-enabled/' + virtualhost
configfile_path		= proxy4nginx_dir + configfile
templatefile_path 	= proxy4nginx_dir + templatefile

# main functions definition
def proxy_enable(args):
	# build the new proxy_pass destination
	proxy_pass = ''

	if args.https:
	  proxy_pass += 'https://'
	else:
	  proxy_pass += 'http://'

	proxy_pass += args.URL

	# edit the nginx configfile file with the new value based on the templatefile
	if args.verbose: print 'Edit %s with \'%s\' as new proxy_pass destination' % (configfile, proxy_pass)

	replacement = {'$_PROXYPASS_$':proxy_pass}

	with open(templatefile_path) as infile, open(configfile_path, 'w') as outfile:
	    for line in infile:
	        for src, target in replacement.iteritems():
	            line = line.replace(src, target)
	        outfile.write(line)

	# create the symlink in sites-enabled nginx directory
	if not os.path.isfile(sitesenabled_path):
		if args.verbose: print 'Create the %s symlink' % sitesenabled_path
		os.symlink(configfile_path, sitesenabled_path)

def proxy_disable(args):
        # delete the symlink in sites-enabled nginx directory
	if not os.path.isfile(sitesenabled_path):
                print "proxy4nginx already disabled..."
		sys.exit()

	else:
		if args.verbose: print 'Delete the %s symlink' % sitesenabled_path
		os.remove(sitesenabled_path)

# args management
parser = argparse.ArgumentParser(description='Edit the nginx configuration to quickly change the proxy_pass destination.')
parser.add_argument('-v', '--verbose', action='store_true', help='blah blah blah...')

subparsers = parser.add_subparsers()

parser_enable = subparsers.add_parser('enable', help='enable the proxy virtualhost')
parser_enable.add_argument('URL', help='fully-qualified domain name (ex: gateway.lan or 192.168.1.1)')
parser_enable.add_argument('-s', '--https', action='store_true', help='use https instead of http')
parser_enable.set_defaults(func=proxy_enable)

parser_disable = subparsers.add_parser('disable', help='disable the proxy virtualhost')
parser_disable.set_defaults(func=proxy_disable)

args = parser.parse_args()
args.func(args)

# reload nginx configuration
call("/etc/init.d/nginx reload", shell=True)
