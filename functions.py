from discord import *
from datetime import datetime
import codecs
import re
import os
import makelist
import json
import collections
from privval import *
from idol_db import *

channels = []
servers = []
idol_roles = []
debug_log = collections.deque()
def time_str():
	return datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def DEBUG(s):
	debug_log.append("[%s] %s\n" % (time_str(), s))
	if len(debug_log) > DEBUG_LOG_COUNT:
		debug_log.popleft()

	with codecs.open(DEBUG_FILE, "a+", "utf-8") as fp:
		fp.write("[%s] %s\n" % (time_str(), s))
		print("[%s] %s" % (time_str(), s))

def build_debug_log():
	s = ""
	for l in debug_log:
		s += l + "\n"
	return s

def update_servers(client):
	servers.clear()
	for s in client.servers:
		servers.append(s)

def find_server(name):
	for s in servers:
		if s.name == name:
			return s
	return None

def update_channels(client):
	channels.clear()
	for c in client.get_all_channels():
		if c.type == ChannelType.text or c.type == ChannelType.voice:
			channels.append({
				"name": c.name,
				"type": c.type,
				"obj": c
			})

def find_text_channel(name):
	for c in channels:
		if c["name"] == name and c["type"] == ChannelType.text:
			return c
	return None

def find_voice_channel(name):
	for c in channels:
		if c["name"] == name and c["type"] == ChannelType.voice:
			return c
	return None

def gen_tag(js):
	tag = js["tag"]
	if js["no"] != "":
		tag += "-" + js["no"]
	return tag

def gen_prefix(js):
	prefix = js["prefix"]
	if prefix != "":
		prefix += ":"
	return prefix
	

def update_music_list():
	cnt = 0
	music_list = []
	js = None
	try:
		with codecs.open(LIST_FILE, "r", "utf_8") as fp:
			return json.loads(fp.read())
	except FileNotFoundError:
		DEBUG("Not found list file. no updating list.")
		return []

def update_list():
	makelist.makelist()
	return update_music_list()

async def create_idol_roles(iList, client, server):
	if server == None:
		return

	idol_roles.clear()

	# restore roles
	for ir in server.roles:
		if not isIdolRole(ir.name):
			continue

		idol_roles.append(ir)
		DEBUG("Restore role, %s" % ir.name)

	for i in iList:
		role_name = i["a_name_romanize"].upper()
		if find_idol_role(role_name) != None:
			continue

		DEBUG('Create role, %s' % role_name)
		idol_roles.append(await client.create_role(
			server, name=role_name, colour=Colour(int(i["color"]["hex"], 16))))

def find_idol_role(name):
	for i in idol_roles:
		if i.name == name:
			return i
	return None

def isIdolRole(name):
	for i in GetIdolJson():
		if name == i["a_name_romanize"].upper():
			return True
	return False

def search_idols(query):
	idols = GetIdolJson()
	result = []
	for q in query:
		for i in range(0, len(idols)):
			if idols[i] == None:
				continue

			if re.search(r"%s" % q, idols[i]["name"]):
				result.append(idols[i])
				idols[i] = None
				continue

			if re.search(r"%s" % q, idols[i]["cv_name"]):
				result.append(idols[i])
				idols[i] = None
				continue

			if re.search(r"%s" % q, idols[i]["name_ruby"]):
				result.append(idols[i])
				idols[i] = None
				continue

			if re.search(r"%s" % q, idols[i]["name_romanize"]):
				result.append(idols[i])
				idols[i] = None
				continue


			if re.search(r"%s" % q, idols[i]["birth"]):
				result.append(idols[i])
				idols[i] = None
				continue


	return result
