#!/usr/bin/env python3
"""\
Simple g-code streaming script
"""
 
import serial
import time
import argparse
import sys
import logging

logging.getLogger().setLevel(logging.DEBUG)

parser = argparse.ArgumentParser(description='This is a basic gcode sender. http://crcibernetica.com')
parser.add_argument('-p', '--port', help='Input USB port', required=True)
parser.add_argument('-f', '--file', help='Gcode file name', type=argparse.FileType('r'), default=sys.stdin)
args = parser.parse_args()

def stripline(line):
	comment = line.find(';')
	if comment >= 0:
		line = line[:comment]
	line = line.strip()
	return line

def waitforwait(port):
	logging.debug('Waiting for wait')
	while True:
		line = port.readline().decode('ascii').rstrip('\r\n')
		if line is None or line == '':
			raise Exception('Line time out')
		if line == 'wait':
			return
		logging.debug('Ignoring line: %s', line)

def sendline(port, line):
	line = line.encode('ascii') + b'\r\n'
	for retry in range(5):
		port.write(line)

		while True:
			reply = port.readline().decode('ascii').rstrip('\r\n')

			if reply == 'Resend:1':
				break

			if reply[0:3] == 'ok ':
				return reply[3:] == '0'

			if reply == 'wait':
				return True

			logging.debug('Ignoring line: %s', reply)

logging.info('Opening serial port %s', args.port)
with serial.Serial(args.port, 115200, timeout=5) as port:
	logging.info('Waking up printer')
	port.write(b'\r\n\r\n')
	port.flushInput()
	waitforwait(port)

	logging.info('Sending gcode')
	for line in args.file:
		line = stripline(line)
		if line != '':
			logging.info('Command: %s', line)
			result = sendline(port, line)
			if not result:
				logging.critical('Command failed - aborting', result)
				break
