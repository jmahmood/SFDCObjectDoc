#!/usr/bin/env python
# encoding: utf8

import sys
import os
from optparse import OptionParser
from ConfigParser import ConfigParser

config = ConfigParser()
config.read('sfdc.config')
source = config.get('sfdc', 'source')
output = config.get('sfdc', 'output')

parser = OptionParser(version="1.0")

parser.add_option("-s", "--source", dest="source",
                  help="The directory from which you wish to copy the files",
                  metavar="SOURCEDIR")

parser.add_option("-o", "--output",
                  dest="output", metavar="OUTPUTDIR",
                  help="The directory to which you wish to save the template files.")

(options, args) = parser.parse_args()

if args:
    print "ERROR"
    print "Aborting due to unrecognized arguments:\n {}".format("\n\t".join(args))
    sys.exit(0)

if not source and not options.source:
    print "ERROR"
    print "You must pass a directory.\n (example goes here)"
    sys.exit(0)

if not output and not options.output:
    print "ERROR"
    print "You must pass the output directory.\n (example goes here)"
    sys.exit(0)

if options.source:
    source = options.source

if options.output:
    output = options.output

from extract import generate_all_templates
generate_all_templates(source, output)
