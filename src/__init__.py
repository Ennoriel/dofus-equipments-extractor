import requests
import lxml.html as lh
import re
from lxml import etree
import time


def getPage(url):
	while True:
		page = requests.get(url)
		if page.status_code == 200:
			break
		elif page.status_code == 429:
			print('HTTP code 429, waiting : ' + str(int(page.headers['retry-after']) + 5) + 's.')
			time.sleep(int(page.headers['retry-after']) + 5)
		elif page.status_code == 404:
			print('HTTP code 404 for no reason, waiting : 5s.')
			time.sleep(5)
		else:
			print(str(page))
			print(url)
			exit()
	return page

def getEquipUrl(url):
	page = getPage(url)
	doc = lh.fromstring(page.content)
	xPath = '//a'
	xPath.replace('/', '//')
	tr_elements = doc.xpath(xPath)
	hrefs = []
	for t in tr_elements:
		try:
			href = t.attrib['href']
			if re.search('(equipements|armes)\/\d+-', href):
				hrefs.append(href)
		except KeyError:
			pass

	return list(dict.fromkeys(hrefs))


def getEquipUrlPage(url, nbPage):

	hrefs = []
	for page in range(1, nbPage + 1):
		print('url: ' + url + str(page))
		hrefs.extend(getEquipUrl(url + str(page)))

	return hrefs


def getRessources(url):

	page = getPage('https://www.dofus.com' + url)

	doc = lh.fromstring(page.content)
	xPath = '//html/body/div[2]/div[2]/div/div/div/main/div[2]/div/div[4]/div[2]/div[2]/div/div'
	ingredients_divs = doc.xpath(xPath)
	res = []
	try:
		titre = doc.xpath('//html/body/div[2]/div[2]/div/div/div/main/div[2]/div/div[2]/h1/text()')[1]
		res.append(titre.strip())
	except Exception:
		res.append('Inconnu')

	try:
		type = doc.xpath('//html/body/div[2]/div[2]/div/div/div/main/div[2]/div/div[3]/div/div/div[2]/div/div[1]/div/div[1]/span/text()')[0]
		res.append(type.strip())
	except Exception:
		res.append('Inconnu')

	try:
		textPage = etree.tostring(doc, encoding='UTF-8').decode(encoding='UTF-8')
		niveau = re.findall('(?<=Niveau : )\d+', textPage)[0]
		res.append(niveau)
	except Exception:
		res.append('Inconnu')

	for ingredients_div in ingredients_divs:
		try:
			if ('ak-column ak-container' in ingredients_div.attrib['class']):
				text = etree.tostring(ingredients_div, encoding='UTF-8').decode(encoding='UTF-8')
				res.append(re.findall('\d+(?= x)', text)[0])
				res.append(re.findall('(?<=class="ak-linker">)[^<]+', text)[0])
		except KeyError:
			pass

	return res


def __init__():
	url_equip = 'https://www.dofus.com/fr/mmorpg/encyclopedie/equipements?size=96&page=' # 25
	url_armes = 'https://www.dofus.com/fr/mmorpg/encyclopedie/armes?size=96&page=' # 8

	hrefs = []

	hrefs.extend(getEquipUrlPage(url_equip, 25))
	hrefs.extend(getEquipUrlPage(url_armes, 8))

	equips = []

	i = 0
	t = len(hrefs)
	for href in hrefs:
		i = i + 1
		print(str(i) + " / " + str(t))

		equips.append(getRessources(href))

	import csv

	with open('equip.csv', mode='w', newline='', encoding='utf-8') as equip:
		equip_writer = csv.writer(equip, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

		for e in equips:
			equip_writer.writerow(e)


__init__()


class A:
	def __init__(self):
		dsfd = 3