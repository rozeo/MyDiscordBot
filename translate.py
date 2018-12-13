import requests
import json
import codecs
from privval import *

DETECT_ENDPOINT = "https://translation.googleapis.com/language/translate/v2/detect"
TRANSLATE_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"

LANG_JSON = "/home/share/discord/lang.json"

PAPAGO_ENDPOINT = "https://openapi.naver.com/v1/papago/n2mt"

def load_lang():
	js = None
	try:
		with codecs.open(LANG_JSON, "r") as fp:
			js = json.loads(fp.read())
	except FileNotFoundError:
		pass

	return js

LANG_LIST = load_lang()

def arr2qstring(arrr):
	arr = []
	for i in arrr.keys():
		arr.append(i + "=" + arrr[i])
	return "&".join(arr)

def detect_language(message):
	query = {
	  "q": message,
	  "key": API_KEY
	}

	response = requests.get(DETECT_ENDPOINT + "?" + arr2qstring(query)).json()
	return response["data"]["detections"][0][0]["language"]

def translate2any(message, code="ko", fr=None):

	query = {
		"q": message,
		"target": code,
		"format": "text",
		"key": API_KEY
	}

	if fr != None:
		query["source"] = fr

	response = requests.get(TRANSLATE_ENDPOINT + "?" + arr2qstring(query)).json()
	try:
		if fr == None:
			return {
					"text": response["data"]["translations"][0]["translatedText"],
	  				"from": response["data"]["translations"][0]["detectedSourceLanguage"],
	  				"to": code
			}
		else:
			return {
					"text": response["data"]["translations"][0]["translatedText"],
	  				"from": fr,
	  				"to": code
			}
	except KeyError:
		return {"error": True}


# https://developers.naver.com/apps/#/myapps/aGX2eZ2D4K0R3n_9c4kn/overview
def translateJAKOWithPAPAGO(message, to, frm=None):
	query = {
		"target": to,
		"text": message
	}

	if frm != None:
		query["source"] = frm

	qstring = arr2qstring(query)
	response = requests.post(PAPAGO_ENDPOINT, data=query, headers={
		"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
		"X-Naver-Client-Id": PAPAGO_CLIENT_ID,
		"X-Naver-Client-Secret": PAPAGO_CLIENT_SECRET
	}).json()

	try:
		return {
			"text": response["message"]["result"]["translatedText"],
		  	"from": response["message"]["result"]["srcLangType"],
		  	"to":   response["message"]["result"]["tarLangType"]
		}
		
	except KeyError:
		return {"error": True}

def code2lang(code):
	try:
		return LANG_LIST[code]
	except KeyError:
		return "不明な言語"

def isLangCode(code):
	try:
		s = LANG_LIST[code]
		print("correct")
		return True
	except KeyError:
		return False
