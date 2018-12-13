from functions import *
import codecs

class options():
	def __init__(self):
		self.option = {}

		DEBUG("Initialize options.")
		self.load()

	def set(self, key, val):
		self.option[key] = val
		DEBUG("Set option %s = %s" % (key, val))

	def get(self, key):
		try:
			return self.option[key]
		except:
			return None

	def load(self):
		# load default option
		self.option = {}
		try:
			with codecs.open('option.ini', 'r') as fp:
				for s in fp.readlines():
					s = s.replace('\n', '')
					try:
						key, val = s.split('=')
						self.set(key, val)
					except:
						continue
		except FileNotFoundError:
			pass