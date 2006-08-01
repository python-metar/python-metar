#!/usr/bin/env python
#
# simple command-line driver for metar parser
#
import sys, os
from metar import Metar
import string
import getopt
import profile, pstats

def usage():
  program = os.path.basename(sys.argv[0])
  print "Usage: ",program,"[-s] [<file>]"
  print """Options:
  <file> ... a file containing METAR reports to parse
  -q ....... run "quietly" - just report parsing error.
  -s ....... run silently. (no output)
  -p ....... run with profiling turned on.
This program reads lines containing coded METAR reports from a file
and prints human-reable reports.  Lines are taken from stdin if no
file is given.  For testing purposes, the script can run silently,
reporting only when a METAR report can't be fully parsed.
"""
  sys.exit(1)

files = []
silent = False
report = True
debug = False
prof = False

try:
  opts, files = getopt.getopt(sys.argv[1:], 'dpqs')
  for opt in opts:
    if opt[0] == '-s':
      silent = True
      report = False
    elif opt[0] == '-q':
      report = False
    elif opt[0] == '-d':
      debug = True
      Metar.debug = True
    elif opt[0] == '-p':
      prof = True
except:
  usage()

def process_line(line):
  """Decode a single input line."""
  line = line.strip()
  if len(line) and line[0] in string.uppercase:
    try:
      obs = Metar.Metar(line)
      if report:
        print "--------------------"
        print obs.str()
    except Metar.ParserError, err:
      if not silent:
        print "--------------------"
        print "METAR code: ",line
        print string.join(err.args,", ")

def process_files(files):
  """Decode METAR lines from the given files."""
  for file in files:
    fh = open(file,"r")
    for line in fh.readlines():
      process_line(line)

if files:
  if prof:
    profile.run('process_files(files)')
  else:
    process_files(files)
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

if prof:
  ps = pstats.load('metar.prof')
  print ps.strip_dirs().sort_stats('time').print_stats()
