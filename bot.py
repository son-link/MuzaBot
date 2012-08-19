#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
#  MuzaBot
#  Bot para IRC
#  Copyright 2012 Alfonso Saavedra "Son Link" <sonlink.dourden@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
#########################################################################

import socket
import string
import datetime

from time import sleep, time
from urllib import urlopen, urlretrieve
from re import search

# Modulos del bot
from muzabot import rss
from muzabot.functions import *
from muzabot.conf import botconf
from muzabot import memo
c = botconf()

readbuffer=""
s=socket.socket( )
s.connect((c['host'], c['port']))
s.send("NICK %s\r\n" % c['nick'])
s.send("USER %s %s bla :%s\r\n" % (c['ident'], c['host'], c['realname']))
s.send("JOIN :%s\r\n" % c['channel'])
m = memo.memo(s)

class IRCBOT():

	def __init__(self):
		# Arrancamos el bot
		self.away = {}
		# Iniciamos el hilo que se encarga de ejecutar la clase encargada de publicar en el IRC los últimos artículos del blog

		# Este bucle infinito se encarga de que el bot se ejecute constantemente
		readbuffer = ""
		line = ''
		rss.RSS(s)

		try:

			while 1:
				readbuffer=readbuffer+s.recv(512)
				temp=string.split(readbuffer, "\n")
				readbuffer=temp.pop( )
				for line in temp:
					line=string.rstrip(line)
					if search('^PING :(.+)', line):
						"""
						NOTA: Este trozo es tptalmente obligatorio, de lo contrario cuando el irc pase a comprobar si el cliente aun esta conectado cerrara
						la sesión, y por lo tanto el bot dejara de ejecutarse.
						"""
						botid = search('^PING :(.+)', line).groups()[0]
						s.send("PONG %s\n" % botid)

					elif search('^\:(\S*)\!(\S*)\@(\S*)\sJOIN\s', line):
						# Damos la bienvenida al usuario que acaba de entrar
						username = line.split('!')[0].split(':')[1]
						if username != c['nick'] and username.find(c['host']) == -1:
							sleep(5)
							self.send_msg("Bienvenid@ %s ^^\n" % username)
							m.getmemos(username)

					elif search('^\:(\S*)\!(\S*)\@(\S*)\sPART\s(.+)', line):
						# Si un usuario se marcha lo mostramos y si uso el comando away lo borramos de la lista
						username = line.split('!')[0].split(':')[1]
						self.send_msg("%s se ha marchado\n" % username)
						if username in self.away:
							self.away.pop(username)

					elif search('^\:(\S*)\!(\S*)\@(\S*)\sPRIVMSG\s(\S*)\s\:(.*)', line):
						# A partir de aquí se reciben los datos enviados desde el canal
						d = search('^\:(\S*)\!(\S*)\@(\S*)\sPRIVMSG\s(\S*)\s\:(.*)', line).groups()
						username = d[0]
						channel = d[3]
						userinput = d[4]

						if userinput == 'DonaFlorinda':
							self.send_msg("Vamos hijo, no te juntes con esta chusma\n")
							sleep(2)
							self.send_msg("Si mami. Chusma, chusma prfff\n")

						# Si un usuario introdujo una URL mostramos el titulo de la pagina si es que la tiene
						elif userinput.find('http') != -1 and username != c['nick']:
							for u in userinput.split():
								try:
									d = search('(.+://)(www.)?([^/]+)(.*)', u)
									if d:
										url = urlopen(u)
										mime = url.info().gettype()
										code = url.getcode()
										if mime == 'text/html' and code == 200:
											raw = urlopen(u).read()
											title = search('<title>([\w\W]+)</title>', raw)
											if title:
												title = title.groups()[0]
												title2 = ''
												for t in title.split('\n'):
													title2 += t.lstrip()+' '
													title2 = HTMLEntitiesToUnicode(title2)
												self.send_msg("%s en %s\n" % (title2, d.groups()[2]))

								except IOError:
									pass

						elif  userinput == '$ sobre':
							# Muestra un mensaje sobre el bot
							self.send_msg("YYYYYYYYY Son Link presenta, MuzaBot, que suelta chorradas, a monton\n")

						elif  userinput == '$ version':
							# Muestra la versión del bot
							self.send_msg("CalicoBot r35 (c) 2012 Son Link\n")

						elif userinput == '$ mevoy' :
							# Con esto si un usuario se va del canal un tiempo lo guarda en un diccionario
							if not username in self.away:
								self.send_msg("%s se marcha durante un tiempo. No molestar\n" % username)
								self.away[username] = (int(time()),)

						elif search('^\$\smevoy\s(.+)', userinput):
							# Lo mismo de antes, solo que en esta ocasión el usuario deja un mensaje personalizado
							if not username in self.away:
								d = search('^\$\smevoy\s(.+)', userinput)
								print d
								if d:
									self.send_msg("%s se marcha durante un tiempo. No molestar\n" % username)
									self.away[username] = (int(time()), d.groups()[0])

						elif userinput == '$ volvi':
							# Si el usuario tras ejecutar mevoy ejecuta este comando muestra un mensaje y lo borra del diccionario
							if username in self.away:
								d = self.away.pop(username)
								self.cuantoTiempo(username, int(d[0]))

						elif search('^\$\smemo\s(.+)', userinput):
							# Permite dejar un mensaje a alguien que no esta conectado el cual lo vera al entrar al canal
							d = search('^\$\smemo\s([a-zA-Z0-9_\.\^\-]+)\s(.+)', userinput)
							if d:
								d = d.groups()
								# Comprobamos que el mensaje no va dirigido al bot
								if d[0] != c['nick']:
									m.sendmemos(d[0], username, d[1])
							else:
								s.send("PRIVMSG %s :El mensaje que ha intentado enviar es invalido. Verifique que indico el destinatario y el mensaje\n" % username)
								s.send("PRIVMSG %s :P.e: $ memo usuario El usuario MadBot esta haciendo spam. Por favor bannealo\n" % username)

						elif userinput == '$ ayuda':
							# Muestra la ayuda del bot
							self.mostrarAyuda(username)

						elif search('$\s(.+)', userinput) or userinput == "$":
							# Si introduce un comando desconocido muestra un aviso
							self.send_msg('Comando desconocido. Ejecute $ ayuda para obtener los comandos disponibles')

						for l in userinput.split():
							"""
							Si alguien nombra a un usario que este en el diccionario de los que ejecutaron mevoy, muestra un mensaje
							"""
							if l in self.away != -1 and username != c['nick']:
								d = self.away[l]
								if len(d) == 2:
									# Si dejo un mensaje personalizado se muestra
									self.send_msg("%s: %s\n" % (l, d[1]))
								else:
									self.send_msg("No molestéis a %s que no esta, cawen los mengues\n" % l)
		except:
			if line:
				log(line)
			else:
				log()

	def send_msg(self, msg):
		"""
		Envia un mensaje al canal.
		Antes de enviarlo espera 0.2 segundos para evitar que expulsen al boot por flood
		"""
		sleep(0.2)
		s.send("PRIVMSG %s :%s\n" % (c['channel'], msg))

	def cuantoTiempo(self, username, segundos):
		"""
		Calcula el tiempo que paso desde que un usuario ejecuto $ mevoy y $ volvi
		"""
		segundos = time() - segundos
		#segundos = long(segundos)

		# Comprobamos si el número introducido es menor a un millón.
		if segundos >= 1000000:
			print "El número debe de ser menor a 1000000"
		else:
			# Días.
			ndias, aux = divmod(segundos, 86400)
			# Horas.
			nhoras, aux = divmod(aux, 3600)
			# Minutos y segundos.
			nmin, nseg = divmod(aux, 60)
			# Mostramos resultado.
			self.send_msg('%s ha vuelto.' % username)
			if ndias != 0:
				self.send_msg('%s has estado ausente %i día(s), %i hora(s), %i minuto(s) y %i segundo(s).' % (username, ndias, nhoras, nmin, nseg))
			elif nhoras != 0:
				self.send_msg('%s has estado ausente %i hora(s), %i minuto(s) y %i segundo(s).' % (username, nhoras, nmin, nseg))
			else:
				self.send_msg('%s has estado ausente %i minutos y %i segundo(s)' % (username, nmin, nseg))

	def mostrarAyuda(self, username):
		"""
		Muestra la ayuda del bot
		"""
		msg = ('Comandos disponibles ($ comando):',
		'mevoy: Muestra un mensaje de que se va y avisa de su ausencia si alguien le nombra.',
		'volvi: Si ejecuto antes mevoy ejecute este para avisar de su regreso y borrarle de la lista',
		'memo <usuario> <mensaje>: Deja un mensaje a un usuario que no este en linea. Cuando se conecte se le mostrara',
		'sobre: muestra un texto sobre el bot',
		'version: nuestra la versión del bot',
		'ayuda: muestra este mensaje de ayuda')
		for m in msg:
			sleep(0.2)
			s.send("PRIVMSG %s :%s\n" % (username, m))

if __name__ == '__main__':
	bot = IRCBOT()
