#!/usr/bin/env python
#
# simple command-line driver for metar parser
#
import sys
from metar import Metar
import string
import getopt

def usage():
  program = os.path.basename(sys.argv[0])
  print "Usage: ",program,"[-s] [<file>]"
  print """Options:
  <file> ... a file containing METAR reports to parse
  -s ....... run silently - just report parsing error.
This program reads lines containing coded METAR reports from a file
and prints human-reable reports.  Lines are taken from stdin if no
file is given.  For testing purposes, the script can run silently,
reporting only when a METAR report can't be fully parsed.
"""
  sys.exit(1)

files = []
silent = False

try:
  opts, files = getopt.getopt(sys.argv[1:], 's')
  for opt in opts:
    if opt[0] == '-s':
      silent = True
except:
  usage()

def process_line(line):
  """Decode a single input line."""
  line = line.strip()
  if len(line) and line[0] in string.uppercase:
    try:
      obs = Metar.Metar(line)
      if not silent:
        print "--------------------"
        print "METAR code: ",line
        print obs.string()
    except Metar.ParserError, err:
      print "--------------------"
      print "METAR code: ",line
      print string.join(err.args,", ")

if files:
  for file in files:
    fh = open(file,"r")
    for line in fh.readlines():
      process_line(line)
else:
   # read lines from stdin 
  while True:
    try:
      line = sys.stdin.readline()
      if line == "":
        break
      process_line(line)
    except KeyboardInterrupt:
      break
