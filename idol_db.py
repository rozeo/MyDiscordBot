import json
import codecs
import copy

IDOL_JSON_FILE = "data/idolInfo.json"

js = None
def GetIdolJson():
	global js

	if js != None:
		return copy.deepcopy(js)

	with codecs.open(IDOL_JSON_FILE, "r", "utf-8") as fp:
		js = json.loads(fp.read())

	return copy.deepcopy(js)

def build_stat_str(data):
	return '\n'.join([
		"属性： " + data["type"],
		"名前： " + data["name"],
		"読み仮名： " + data["name_ruby"],
		"ローマ字表記： " + data["name_romanize"],
		"CV： " + data["cv_name"],
		"",
		"誕生日： " + data["birth"],
		"出身地： " + data['birthplace'],
		"",
		"身長： " + data["stat"]["height"] + " cm",
		"体重： " + data["stat"]["weight"] + " kg",
		"血液型： " + data["stat"]["blood_type"],
		("スリーサイズ： B%s W%s H%s" % 
			(data["stat"]["three_size"]["B"], data["stat"]["three_size"]["W"], data["stat"]["three_size"]["H"])),
		"利き手： " + data["stat"]["handness"],
		"星座： " + data["stat"]["constellation"],
		"",
		"趣味： " + data["stat"]["hobby"],
		"特技： " + data["stat"]["skill"],
		"好きなもの： " + data["stat"]["favorite"],
		"",
		"アイドルカラー",
		"\tHEX： #" + data["color"]["hex"],
		"\tRGB： %d, %d, %d" % (data["color"]["r"], data["color"]["g"], data["color"]["b"]),
	])