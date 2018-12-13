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
from privval import *

class kotoha_player:
	
	# discord.Client
	def __init__(self, client, option):
		self.client = client
		self.music_list = update_list()

		self.played = False
		self.playing = None
		self.player = None
		self.mqueue = collections.deque()
		self.current_vc = None
		self.option = option

	async def force_reset():
		self.mqueue.clear()
		self.player.stop()
		await self.leave()

	async def join(self, arg, cvc, play=True):
		to = None
		try:
			to = arg[0]
		except (KeyError, IndexError):
			to = option.get('default_voice_channel') # default

		vc = find_voice_channel(to)

		if vc != None:
			v = cvc
			if vc["obj"] == cvc:
				return
			if cvc != None:
				await cvc.move_to(vc["obj"])
			else:
				v = await self.client.join_voice_channel(vc["obj"])

			DEBUG("Join to VC, channel \"%s\"" % (to))
			self.current_vc = v

			if len(self.mqueue) > 0 and self.player == None:
				await self.play(v)

	async def add(self, channel, arg, cvc, only=False, top=False):
		if arg == []:
				return

		if arg[0].startswith("http"):
			url = arg[0]
			v = ""
			
			# url validate
			if url.find("youtube.com") >= 0:

				uri, argument = url.split("?")
				arg_list = argument.split("&")
				url = uri + "?"
				v = ""

				for a in arg_list:
					if a.startswith("v="):
						v = a
						break

				if v == "":
					play_end_callback()
					return

			elif arg[0].find("youtu.be") >= 0:

				m = re.match(r"^.*\/([^\/]*)$", arg[0])
				if m == None:
					return

				v = "v=" + m.groups()[0]
				
			else:
					return

			url = "https://www.youtube.com/watch?" + v
			if top:
				self.mqueue.appendleft({"type": 1, "url": url})
				DEBUG("[%s] Add queue top, %s" % (time_str(), url))
				await self.client.send_message(channel, "%s\nをキューの先頭に追加しましたよ。" % (url))

			else:
				self.mqueue.append({"type": 1, "url": url})
				DEBUG("[%s] Add queue, %s" % (time_str(), url))
				await self.client.send_message(channel, "%s\nをキューに追加しましたよ。" % (url))

			if not self.played and not only:
				await self.play(cvc)

		elif arg[0].startswith("id:") or arg[0] == "random":
			num = ""
			if arg[0] == "random":
				num = random.randint(1, len(self.music_list))
			else:
				d, num = arg[0].split(":")
				try:
					num = int(num) - 1
					if len(self.music_list) <= num:
						return
					if num < 0:
						return
				except ValueError:
					return
			
			info = self.music_list[num]
			tag = gen_tag(info)
			file = MUSIC_DIR + "/" + info["prefix"] + "/" + tag + " " + info["name"] + "." + info["ext"]

			data = {
				"type": 0,
				"file": file,
				"name": info["name"],
				"tag": tag,
				"prefix": info["prefix"]
			}
			if top:
				self.mqueue.appendleft(data)
				DEBUG("Add queue top, [%s%s] %s" % (gen_prefix(info), tag, info["name"]))
				await self.client.send_message(channel, "[%s%s] %s\nをキューの先頭に追加しましたよ。" % (gen_prefix(info), tag, info["name"]))
			else:
				self.mqueue.append(data)
				DEBUG("Add queue, [%s%s] %s" % (gen_prefix(info), tag, info["name"]))
				await self.client.send_message(channel, "[%s%s] %s\nをキューに追加しましたよ。" % (gen_prefix(info), tag, info["name"]))

			if not self.played and not only:
				await self.play(cvc)

	async def play(self, cvc):
		if self.played == True:
			return
		if cvc == None:
			return
		if len(self.mqueue) == 0:
			DEBUG("Request play, bad no item in queue.")
			if self.option.get('radio_mode') == "1":
				self.play_end_callback()
			return

		self.played = True
		m = self.mqueue.popleft()

		ydl_opt = {
			"debug_printtraffic": False,
			"quiet": True,
			"postprocessor_args": "--audio-quality 5 --buffer-size 16K --skip-download"
		}
		
		for_tls_reconnect_op = {
			"-reconnect": 1,
			"-reconnect_streamed": 1,
			"-reconnect_delay_max": 5
		}

		options = "-threads 8 -bufsize 16777216 -vn -b:a 256k"
		boptions = "-nostdin"

		if m["type"] == 1:
			try:
				self.player = await cvc.create_ytdl_player(m["url"], ytdl_options=ydl_opt, after=lambda: self.play_end_callback(),
							headers=for_tls_reconnect_op, options=options, before_options=boptions)
			except youtube_dl.utils.DownloadError:
				self.play_end_callback()
				return
			DEBUG("Play music, %s" % (m["url"]))

		elif m["type"] == 0:
			try:
				self.player = cvc.create_ffmpeg_player(m["file"], after=lambda: self.play_end_callback(), options=options, before_options=boptions)
			except FileNotFoundError:
				play_end_callback()
				return
			DEBUG("Play music, [%s%s] %s" % (gen_prefix(m), m["tag"], m["name"]))

		self.playing = m

		self.player.start()

	def play_end_callback(self):
		self.played = False
		self.player = None
		self.playing = None

		# radio mode
		if self.option.get("radio_mode") == "1" and len(self.mqueue) == 0:
			num = random.randint(1, len(self.music_list))
			info = self.music_list[num]
			tag = gen_tag(info)
			file = MUSIC_DIR + "/" + info["prefix"] + "/" + tag + " " + info["name"] + "." + info["ext"]

			data = {
				"type": 0,
				"file": file,
				"name": info["name"],
				"tag": tag,
				"prefix": info["prefix"]
			}
			self.mqueue.append(data)

		asyncio.run_coroutine_threadsafe(self.play(self.current_vc), self.client.loop)

	def resume(self):
		if self.player != None:
			if not self.player.is_playing():
				self.player.resume()

	def pause(self):
		if self.player != None:
			if self.player.is_playing():
				self.player.pause()

	def skip(self):
		if self.player != None:
			self.player.stop()

	async def mqclear(self, channel, arg):
		if arg != []:
			try:
				number = int(arg[0]) - 1
			except ValueError:
				return

			if number < 0:
				return

			s = copy.deepcopy(self.mqueue)
			self.mqueue.clear()
			cnt = 0
			for i in s:
				if number != cnt:
					self.mqueue.append(i)
				cnt += 1

			DEBUG("Delete from queue, number %d." % (number + 1))
			await self.client.send_message(channel, "キュー番号: %d を削除しましたよ。" % (number + 1))

		else:
			self.mqueue.clear()
			DEBUG("Delete all in queue.")
			await self.client.send_message(channel, "キューの中身を全て削除しましたよ。")

	async def leave(self):
		if self.current_vc != None:
			await self.current_vc.disconnect()
			self.current_vc = None

	async def now(self, channel):
		if self.playing == None:
				await self.client.send_message(channel, "今は何も再生されていませんよ。")
		
		else:
			if self.playing["type"] == 0:
				await self.client.send_message(channel, "今は [%s%s] %s を再生中です。" % (gen_prefix(self.playing), self.playing["tag"], self.playing["name"]))
			elif self.playing["type"] == 1:
				await self.client.send_message(channel, "今は %s を再生中です。" % self.playing["url"])
		

	async def mqstate(self, channel):
		await self.client.send_message(channel, "キュー内の再生待ち数は %d 曲(動画)ですよ。\n!!mskip で飛ばすことも可能ですよ。\n" % (len(self.mqueue)))
		if len(self.mqueue) > 0:
			await self.client.send_message(channel, "現在のキュー内の一覧はこちらです。\n%s" % (self.queue_list()))

	def queue_list(self):
		s = "```"
		c = 1
		for q in self.mqueue:
			s += str(c) + ". "
			if q["type"] == 1:
				s += q["url"]
			elif q["type"] == 0:
				prefix = gen_prefix(q)
				s += "[%s%s] %s" % (prefix, q["tag"], q["name"])
			s+= "\n"
			c += 1
		s += "```"
		return s

	async def view_list(self):
		await self.client.send_message(find_text_channel(self.option.get('default_bot_text_channel'))["obj"], "現在の登録されている曲一覧はこちらです。\n")
		for l in self.view_local_list():
			await self.client.send_message(find_text_channel(self.option.get('default_bot_text_channel'))["obj"], l)

	def view_local_list(self):
		l = []
		s = "```"
		for m in self.music_list:
			prefix = gen_prefix(m)
			s += "%d: [%s%s] %s\n" % (m["id"] + 1, prefix, gen_tag(m), m["name"])
			if len(s) > 1500:
				s += "```"
				l.append(s)
				s = "```"
		s += "```"
		l.append(s)
		return l

	def update_list(self):
		self.music_list = update_list()
