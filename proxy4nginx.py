#!/usr/bin/python
#
# Automates the creation and deletion of a simple reverse proxy vhost for nginx.
#
# Author: Samy Baiwir 

import sys
import argparse
import os
from subprocess import call

# general parameters
install_path	= '/opt/proxy4nginx'
vhost_path	= '/etc/nginx/conf.d'
vhost_name	= 'proxy'
template	= 'config.local'

# unify paths with trailing /
if not vhost_path.endswith('/'): vhost_path += '/'
if not install_path.endswith('/'): install_path += '/'

# main functions definition
def proxy_enable(args):
	# build the new proxy_pass destination
	proxy_pass = ''

	if args.https:
	  proxy_pass += 'https://'
	else:
	  proxy_pass += 'http://'

	proxy_pass += args.URL

	# edit the nginx config file with the new value based on template
	if args.verbose: print 'Edit vhost.conf with \'%s\' as new proxy_pass destination' % (proxy_pass)

	replacement = {'$_PROXYPASS_$':proxy_pass}

	with open(install_path + template) as infile, open(install_path + "vhost.conf", 'w') as outfile:
	    for line in infile:
	        for src, target in replacement.iteritems():
	            line = line.replace(src, target)
	        outfile.write(line)

	# create the symlink in nginx vhost directory
	if not os.path.isfile(vhost_path + vhost_name + ".conf"):
		if args.verbose: print 'Create the %s symlink' % (vhost_name + ".conf")
		os.symlink(install_path + "vhost.conf", vhost_path + vhost_name + ".conf")

def proxy_disable(args):
        # delete the symlink in nginx vhost directory
	if not os.path.isfile(vhost_path + vhost_name + ".conf"):
                print "proxy4nginx already disabled..."
		sys.exit()

	else:
		if args.verbose: print 'Delete the %s symlink' % (vhost_path + vhost_name + ".conf")
		os.remove(vhost_path + vhost_name + ".conf")

# args management
parser = argparse.ArgumentParser(description='Automates the creation and deletion of a simple reverse proxy vhost for nginx.')
parser.add_argument('-v', '--verbose', action='store_true', help='blah blah blah...')

subparsers = parser.add_subparsers()

parser_enable = subparsers.add_parser('enable', help='create the proxy vhost')
parser_enable.add_argument('URL', help='fully-qualified domain name (ex: intranet.int or 192.168.1.1)')
parser_enable.add_argument('-s', '--https', action='store_true', help='use https instead of http')
parser_enable.set_defaults(func=proxy_enable)

parser_disable = subparsers.add_parser('disable', help='delete the proxy virtualhost')
parser_disable.set_defaults(func=proxy_disable)

args = parser.parse_args()
args.func(args)

# reload nginx configuration
if args.verbose: print 'Reload nginx configuration'
call("systemctl reload nginx", shell=True)
