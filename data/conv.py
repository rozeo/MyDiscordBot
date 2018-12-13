import codecs
import json

l = []

with codecs.open("idolListBase.csv", "r", "utf-8") as fp:
	for s in fp.readlines():
		s = s.replace('\r\n', '')
		print(s)
		n, c, rgb, birth, name_ruby, cv_ruby, romanize = s.split(',')

		r = int(rgb[0] + rgb[1], 16)
		g = int(rgb[2] + rgb[3], 16)
		b = int(rgb[4] + rgb[5], 16)

		cc = c.split(' ')
		ca = cc[0]
		cb = ""
		if len(cc) > 1:
			cb = cc[1]

		ccr = cv_ruby.split(' ')
		cca = ccr[0]
		ccb = ""
		if len(ccr) > 1:
			ccb = ccr[1]

		cn = n.split(' ')
		cna = cn[0]
		cnb = ""
		if len(cn) > 1:
			cnb = cn[1]

		cnr = name_ruby.split(' ')
		cnra = cnr[0]
		cnrb = ""
		if len(cnr) > 1:
			cnrb = cnr[1]

		rom = romanize.split(' ')
		roma = rom[0]
		romb = ""
		if len(rom) > 1:
			romb = rom[1]

		l.append({
			"name": n,
			"a_name": cna,
			"b_name": cnb,

			"name_romanize": romanize,
			"a_name_romanize": roma,
			"b_name_romanize": romb,

			"name_ruby": name_ruby,
			"a_name_ruby": cnra,
			"b_name_ruby": cnrb,

			"cv_name":   c,
			"a_cv_name": ca,
			"b_cv_name": cb,

			"cv_name_ruby": cv_ruby,
			"a_cv_name_ruby": cca,
			"b_cv_name_ruby": ccb,

			"birth": birth,
			"birth_month": birth.split('/')[0],
			"birth_day": birth.split('/')[1],

			"color": {
				"r": r,
				"g": g,
				"b": b,
				"hex": rgb
			}
		})
with codecs.open('idolInfo.json', 'w', 'utf-8') as fp:
	json.dump(l, fp)