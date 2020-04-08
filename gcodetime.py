#!/usr/bin/env python3

import sys
import argparse
import io
import datetime
from math import *

def splitline(line):
	comment = line.find(';')
	if comment >= 0:
		line = line[:comment]
	line = line.strip()
	return line.split()

def parseline(split):
	command = split[0]
	parsed = {}
	for arg in split[1:]:
		parsed[arg[0]] = arg[1:]
	return command, parsed

parser = argparse.ArgumentParser(description='G-Code printing time estimator')
parser.add_argument('-f', '--file', help='Gcode file', type=argparse.FileType('r'), default=sys.stdin)
args = parser.parse_args()

class Head:
	def __init__(self):
		self.x = 0
		self.y = 0
		self.z = 0
		self.extruder = 0
		self.speed = 1500
		self.relative = False
		self.relativeExtruder = False
		self.totalTime = 0
		self.totalDistance = 0
		self.totalFilament = 0

	def setRelative(self, status):
		self.relative = status
		self.setExtruderRelative(status)

	def setExtruderRelative(self, status):
		self.relativeExtruder = status

	def home(self):
		self.travelTo(x=0, y=0, z=0)

	def move(self, args):
		mapping = {
			'E': 'extruder',
			'F': 'speed',
			'X': 'x',
			'Y': 'y',
			'Z': 'z'
		}

		parsed = {}
		for key, value in args.items():
			parsed[mapping[key]] = float(value)

		self.travelTo(**parsed)

	def travelTo(self, x=None, y=None, z=None, extruder=None, speed=None):
		if extruder is not None:
			if self.relativeExtruder:
				extruderDif = extruder / 1000
				self.extruder += extruder
			else:
				extruderDif = (extruder - self.extruder) / 1000
				self.extruder = extruder

			self.totalFilament += extruderDif
		else:
			extruderDif = 0

		if speed is not None:
			self.speed = speed

		self.x, xDif = self._travelAxis(self.x, x)
		self.y, yDif = self._travelAxis(self.y, y)
		self.z, zDif = self._travelAxis(self.z, z)

		dist = sqrt(xDif ** 2 + yDif ** 2 + zDif ** 2) / 1000
		self.totalDistance += dist

		# Speed is mm/min, translate to m/s
		time = 60 * 1000 * dist / self.speed
		self.totalTime += time

		return dist, time, extruderDif

	def _travelAxis(self, cur, new):
		if new is None:
			return cur, 0

		if self.relative:
			return cur + new, new

		return new, cur - new

head = Head()
for line in args.file:
	line = line.rstrip('\r\n')

	split = splitline(line)
	if len(split) == 0:
		continue

	cmd = split[0]
	if cmd == 'G0' or cmd == 'G1':
		_, args = parseline(split)
		head.move(args)
	elif cmd == 'G28':
		head.home()
	elif cmd == 'G90':
		head.setRelative(False)
	elif cmd == 'G91':
		head.setRelative(True)
	elif cmd == 'M82':
		head.setExtruderRelative(False)
	elif cmd == 'M83':
		head.setExtruderRelative(True)

print('Distance: %f m' % head.totalDistance)
hours = datetime.timedelta(seconds=head.totalTime)
print('Time: %f seg (%s)' % (head.totalTime, hours))
print('Filament: %f m' % head.totalFilament)
