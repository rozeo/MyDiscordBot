from discord import *
import asyncio
from datetime import datetime
import collections
import youtube_dl
import re
import codecs
from functions import *
import copy
import random
import threading
import time
import os
import translate
import kotoha_player
from privval import *
import sys
import options
from idol_db import *

client = Client()
kot_player = None
current_vc = None
option = options.options()

active = True

music_list = []

kot_player = None
flg = False
connected = False

idolJson = GetIdolJson()

async def reload():
	update_servers(client)
	update_channels(client)
	option.load()

	await create_idol_roles(idolJson, client, find_server("ALLLIVE!!!"))

	await client.send_message(find_text_channel(option.get('debug_log_channel'))["obj"], "Options reloading on %s" % time_str())

@client.event
async def on_ready():
	global connected
	connected = True
	update_servers(client)
	update_channels(client)
	DEBUG("Bot has upcoming.")

	await create_idol_roles(idolJson, client, find_server("ALLLIVE!!!"))

	await client.send_message(find_text_channel(option.get('debug_log_channel'))["obj"], "Bot has upcoming on %s" % time_str())
	
@client.event
async def on_message(message):
	global player
	global active
	global music_list

	if message.author == client.user:
		return

	u = message.author.id

	# cmd
	if message.content.startswith("!!"):
		u = message.author.id
		_cmd = message.content[2::]
		c = re.split(r"\s", _cmd)
		cmd = c[0].lower()
		arg = c[1::] if len(c) >= 2 else []
		cvc = client.voice_client_in(message.server)
		channel = message.channel
		
		# master commands, ignore active state
		if u == ADMIN_USERID or u == SUB_ADMIN_USERID:
			if cmd == "view_log":
				log_str = build_debug_log()
				await client.send_message(find_text_channel(option.get('default_bot_text_channel'))["obj"], '```' + log_str + '```')
				
			if cmd == "change_active":
				if active:
					active = False
					DEBUG("bot deactivated.")
					await deactivate_bot()
					await client.send_message(find_text_channel(option.get('default_bot_text_channel'))["obj"], "[%s] bot機能を OFF にしましたよ。" % time_str())
				else:
					active = True
					DEBUG("bot activated.")
					await client.send_message(find_text_channel(option.get('default_bot_text_channel'))["obj"], "[%s] bot機能を ON にしましたよ。" % time_str())

		if cmd == "status":
			if active:
				await client.send_message(find_text_channel(option.get('default_bot_text_channel'))["obj"], "現在 bot機能は ON になっていますよ。")
			else:
				await client.send_message(find_text_channel(option.get('default_bot_text_channel'))["obj"], "現在 bot機能は OFF になっていますよ。")

		if cmd == "option":
			for a in arg:
				key = None
				val = None
				try:
					key, val = a.split('=')
					option.set(key, val)
				except:
					option.set(key, None)

				await client.send_message(find_text_channel(option.get('debug_log_channel'))["obj"], "Set option %s = %s" % (key, val))

		# need active state commands
		if not active:
			return
		
		if cmd == "join_only":
			await kot_player.join(arg, cvc, False)

		elif cmd == "join":
			await kot_player.join(arg, cvc, True)

		elif cmd == "madd":
			await kot_player.add(channel, arg, cvc)

		elif cmd == "maddqueue":
			await kot_player.add(channel, arg, cvc, True)

		elif cmd == "maddtop":
			await kot_player.add(channel, arg, cvc, False, True)

		elif cmd == "mnow":
			await kot_player.now(channel)

		elif cmd == "mplay":
			await kot_player.play(client.voice_client_in(message.server))
			return

		elif cmd == "mpause":
			kot_player.pause()
			return

		elif cmd == "mresume":
			kot_player.resume()
			return

		elif cmd == "mskip":
			kot_player.skip()

		elif cmd == "mqclear":
			await kot_player.mqclear(channel, arg)

		elif cmd == "view_list":
			await kot_player.view_list()

		elif cmd == "mqstate":
			await kot_player.mqstate(channel)

		elif cmd == "leave":
			await kot_player.leave()

		elif cmd == "update_list":
			kot_player.update_list()
			await client.send_message(find_text_channel(option.get('default_bot_text_channel'))["obj"], "楽曲リストを更新しましたよ。")

		# lang translation
		elif cmd == "translate":
			tocode = None
			fromcode = None
			f = []
			for s in arg:
				if s.startswith("code="):
					dummy, tocode = s.split("=")
					if not translate.isLangCode(tocode):
						tocode = None
				elif s.startswith("from="):
					dummy, fromcode = s.split("=")
					if not translate.isLangCode(fromcode):
						fromcode = None
				else:
					f.append(s)
			if f == []:
				return
			fromstr = " ".join(f)

			if fromcode == None:
				fromcode = translate.detect_language(fromstr)

			if tocode == fromcode:
				return

			if not translate.isLangCode(tocode):
				tocode = None

			if tocode == None:
				if fromcode == "ja":
					tocode = "ko"
				else:
					tocode = "ja"
					
			trans = translate.translateJAKOWithPAPAGO(fromstr, tocode, fromcode)
			if "error" in trans:
				DEBUG("Error occured, duaring translation.")
				await client.send_message(message.channel,
				"<@%s> うまく翻訳できませんでした。" % message.author.id)

			else:
				DEBUG("Translate %s -> %s" % (fromcode, tocode))
				await client.send_message(message.channel,
				"<@%s> %s から %s への翻訳ですよ。\n原文: %s\n翻訳: %s" % (message.author.id, 
					translate.code2lang(fromcode), translate.code2lang(tocode),
					fromstr, trans["text"]))
		
		elif cmd == "help":
			try:
				with codecs.open("help.txt", "r") as fp:
					s = fp.read()
					await client.send_message(message.channel, "```" + s + "```")
			except:
				pass

		elif cmd == "role":
			if len(arg) < 1:
				return

			add_roles = []
			rem_roles = []
			add_roles_name = []
			rem_roles_name = []
			for a in arg:
				rs = re.search(r"(\+|\-)(.*)", a)
				if not rs:
					continue

				rg = rs.groups()
				role_name = rg[1]

				role = find_idol_role(role_name)
				if role == None:
					continue

				if rg[0] == "+":
					await client.add_roles(message.author, role)
					add_roles_name.append(role.name)
				elif rg[0] == "-":
					await client.remove_roles(message.author, role)
					rem_roles_name.append(role.name)

			if len(add_roles_name) > 0 or len(rem_roles_name) > 0:
				await client.send_message(message.channel, 
					"役職を適用しました。\n追加した役職：%s\n外した役職：%s\n" % 
						(', '.join(add_roles_name), ', '.join(rem_roles_name)))

		elif cmd == "purge_role":
			if len(message.author.roles) > 0:
				for r in message.author.roles:
					await client.remove_roles(message.author, r)
				await client.send_message(message.channel, "役職をすべて削除しました。")

		elif cmd == "reload":
			await reload()

async def deactivate_bot():
	await kot_player.force_reset()


async def logout():
	global connected
	connected = False
	await client.logout()

def watcher():
	while True:
		try:
			with open(KILL_FLAG, "r") as fp:
				fp.close()
				break
		except FileNotFoundError:
			time.sleep(1)
			continue
	os.system("/bin/rm -f %s" % KILL_FLAG)
	print("Stopping ...")
	global flg
	flg = True
	DEBUG("Stopping ...")
	asyncio.run_coroutine_threadsafe(logout(), client.loop)
	DEBUG("Logout bot, bye.")

async def main(loop):
	t = threading.Thread(target=watcher)
	t.start()

	global kot_player
	kot_player = kotoha_player.kotoha_player(client, option)
	while not flg:
	  try:
	  	if not connected:
	                await client.login(DISCORD_APP_KEY)
	                await client.connect()
	  except:
	  	try:
	  		await client.logout()
	  	except:
	  		DEBUG("System: Logout failed." % time_str())
	  		pass
	  	
	  	await client.close()
	  	info = sys.exc_info()
	  	DEBUG("System\n Exception:\n\t%s\n\t%s\n\t%s\n" % (info[0], info[1], info[2]))
	  	await asyncio.sleep(option.get('reconnect_wait'))
	  	DEBUG("System: Reconnecting.")
	  	
	t.join()

loop = asyncio.get_event_loop()
try:
	loop.run_until_complete(main(loop))
	loop.close()
except KeyboardInterrupt:
	if connected:
		try:
			loop.run_until_complete(logout())
		except:
			pass
