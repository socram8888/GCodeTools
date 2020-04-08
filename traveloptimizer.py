#!/usr/bin/env python3

import sys

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

class Traveler:
	def __init__(self):
		self.travelLines = 0
		self.x = None
		self.y = None
		self.speed = None
		self.relative = False

	@property
	def traveling(self):
		return self.travelLines > 0

	def addMove(self, args):
		self.travelLines += 1

		x = args.get('X')
		y = args.get('Y')
		speed = args.get('F')

		if x is not None:
			x = float(x)
			if self.relative and self.x is not None:
				self.x += x
			else:
				self.x = x
		if y is not None:
			y = float(y)
			if self.relative and self.y is not None:
				self.y += y
			else:
				self.y = y
		if speed is not None:
			self.speed = float(speed)

	def buildTravel(self):
		if self.travelLines == 0:
			return ''

		travel = 'G0'
		if self.speed is not None:
			travel += ' F%d' % self.speed
		if self.x is not None:
			travel += ' X%d' % self.x
		if self.y is not None:
			travel += ' Y%d' % self.y
		travel += ' ; opt %i lines\r\n' % self.travelLines

		return travel

	def reset(self):
		self.x = None
		self.y = None
		self.speed = None
		self.travelLines = 0

	def buildAndReset(self):
		travel = self.buildTravel()
		self.reset()
		return travel

traveler = Traveler()
for line in sys.stdin:
	line = line.rstrip('\r\n')

	split = splitline(line)
	cmd = split[0] if len(split) > 0 else None
	accumulated = False

	if cmd == 'G0':
		_, args = parseline(split)
		if 'Z' not in args and 'E' not in args:
			traveler.addMove(args)
			accumulated = True

	if not accumulated:
		if traveler.traveling:
			print(traveler.buildAndReset(), end='')

		if cmd == 'G90':
			traveler.relative = False
		elif cmd == 'G91':
			traveler.relative = True

		print(line, end='\r\n')
