# -*- coding: utf-8 -*-

import xml.dom.minidom, hashlib
import threading

from urllib import urlopen, urlretrieve
from time import mktime, strptime, sleep
from muzabot.functions import log

CHAN="#Home"
feedurl = 'http://blog.desdelinux.net/feed/' # URL al feed que se usara en el bot para la función RSS

class RSS():
	"""
	Esta clase muestra en el canal IRC los últimos artículos publicados en el feed indicado
	"""
	def __init__(self, s):
		self.rss_md5 = ''
		self.s = s
		threading.Thread(target=self.start).start()

	def start(self):
		try:
			document = xml.dom.minidom.parse(urlopen(feedurl))
			#Almacenamos la fecha del ultimo articulo publicado para mas tarde compararlo para saber si hay artículos nuevos
			self.last_date = self.formatTime(document.getElementsByTagName('item')[0].getElementsByTagName('pubDate')[0].firstChild.data.encode('UTF8', 'replace'))
			while True:
				self.getLastNews()
				sleep(60)
		#except IOError:
			#pass
		except:
			log()

	def md5sum(self, filename):
		"""
		Esta función se encarga de crear la suma de verificación para comprobar si se modifico el feed desde la ultima vez
		"""
		md5 = hashlib.md5()
		with open(filename,'rb') as f:
			for chunk in iter(lambda: f.read(128*md5.block_size), b''):
				 md5.update(chunk)
		return md5.hexdigest()


	def getLastNews(self):
		"""
		Esta función se encarga de descargar el feed, verificar la suma de verificación y si cambio invocar a la función que se encarga de mostrar los articulos nuevos
		"""
		urlretrieve(feedurl, 'rss.xml')
		md5 = self.md5sum('rss.xml')
		if md5 != self.rss_md5:
			self.sendLastNews()
			self.rss_md5 = md5

	def formatTime(self, datetime):
		"""
		Esta función simplemente se encarga de convertir la fecha dada por el feed a segundos
		"""
		time_format = "%a, %d %b %Y %H:%M:%S +0000"
		return int(mktime(strptime(datetime, time_format)))

	def sendLastNews(self):

		"""
		Esta función se encarga de verificar si hay artículos nuevos y publicarlos en el IRC
		"""

		# Leemos el feed
		document = xml.dom.minidom.parse(open('rss.xml'))
		# Guardamos la fecha del ultimo articulo
		lastdate = document.getElementsByTagName('item')[0].getElementsByTagName('pubDate')[0].firstChild.data.encode('UTF8', 'replace')

		# Ahorra recorremos todos los elementos item del feed y almacenamos los datos que nos interesan
		for item in document.getElementsByTagName('item'):
			title = item.getElementsByTagName('title')[0].firstChild.data.encode('UTF8', 'replace')
			link = item.getElementsByTagName('link')[0].firstChild.data.encode('UTF8', 'replace')
			date = item.getElementsByTagName('pubDate')[0].firstChild.data.encode('UTF8', 'replace')
			# Si las fechas del articulo son mas actuales que la del ultimo articulo almacenado anteriormente los mostramos
			if self.formatTime(date) > self.last_date:
				msg = 'Nuevo articulo: %s -> %s' % (title, link)
				self.s.send("PRIVMSG %s :%s\n" % (CHAN, msg))
		# Ahora guardamos la fecha del articulo mas reciente
		self.last_date = self.formatTime(lastdate)
