import json
import codecs

IDOL_JSON_FILE = "data/idolInfo.json"

js = None
def GetIdolJson():
	global js

	if js != None:
		return js

	with codecs.open(IDOL_JSON_FILE, "r", "utf-8") as fp:
		js = json.loads(fp.read())
	return js