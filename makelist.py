import os
import json
import subprocess
import codecs
import re
from privval import *

def makelist():
	cmd = "cd " + PREFIX_MUSIC_DIR + " && find " + MUSIC_DIR_NAME + " | sort"
	finder = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True).stdout

	js = []
	cnt = 0
	for s in finder.readlines():
		s = s.decode('utf-8').replace('\n', '')
		if os.path.isdir(PREFIX_MUSIC_DIR + '/' + s):
			continue

		full = s.split("/")[1::]
		if len(full) == 0:
			continue

		prefix = []
		name = full[-1]
		fullname = name
		for i in range(0, len(full) - 1):
			prefix.append(full[i])
		
		m = re.match(r"^(.*)\.([^\.]*)$", name)
		if m == None:
                	continue

		name, ext = m.groups()
		
		r = re.match(r"^([^\s]*)\s(.*)$", name)
		if r == None:
			continue
		tag, name = r.groups()
		r = re.match(r"^([^-\s]*)-?(\d*)$", tag)
		if r == None:
			continue
		tag, trackno = r.groups()
		
		js.append({
			"id": cnt,
			"prefix": "/".join(prefix),
			"tag": tag,
			"no": trackno,
			"name": name,
			"ext": ext
		})
		cnt += 1
	with codecs.open(LIST_FILE, 'w', 'utf-8') as out:
		out.write(json.dumps(js))
	os.system("cp %s %s" % (LIST_FILE, NGINX_LIST_FILE))

if __name__ == "__main__":
	makelist()
