#! /usr/bin/python

import subprocess
import os
import sys


def Write( str, proc ):
	old_stdout = sys.stdout
	sys.stdout = proc.stdin
	print str
	sys.stdout = old_stdout
	return

def Read( proc ):
	old_stdin = sys.stdin
	sys.stdin = proc.stdout
	str = raw_input()
	sys.stdin = old_stdin
	return str

p = subprocess.Popen(sys.argv[1], stdin=subprocess.PIPE, stdout=subprocess.PIPE)


while 1:
   input = raw_input()
   Write(input, p)
   print Read(p)
   if input == "[quit]":
      break