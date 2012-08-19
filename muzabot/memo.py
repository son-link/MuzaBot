# -*- coding: utf-8 -*-
import csv
import sqlite3

from time import sleep
class memo():

	def __init__(self, s):
		self.s = s
		self.db = sqlite3.connect('muzabot.db')
		self.db.row_factory = sqlite3.Row
		self.memos = None
		self.check_tables()

	def getmemos(self, username):
		"""
		Envia los mensajes al usuario destinatario cuando se conecte
		"""
		cursor = self.db.cursor()
		cursor.execute('SELECT autor, msg FROM memos WHERE dest="%s"' % username)
		memos = cursor.fetchall()
		if len(memos) > 0:
			# Si tiene mensajes se le envia
			self.s.send("PRIVMSG %s :Tienes %i mensajes nuevos\n" % (username, len(memos)))
			for m in memos:
				msg = m['autor']+': '+m['msg']
				self.s.send("PRIVMSG %s :%s\n" % (username, msg))
				sleep(0.5)
			# Borramos los mensajes
			cursor.execute('DELETE FROM memos WHERE dest="%s"' % username)
			self.db.commit()

	def sendmemos(self, dest, username, msg):
		"""
		Guarda los mensajes que se quieren enviar
		"""

		if len(msg) > 140:
			self.s.send("PRIVMSG %s :El mensaje que has querido enviar a %s tiene mas de 140 caracteres\n" % (username, dest))
		else:
			cursor = self.db.cursor()
			# Comprobamos que el destinatario no tenga 5 mensajes (buzón lleno)
			check = cursor.execute("SELECT * FROM memos WHERE dest='%s'" % dest).fetchall()
			if len(check) <= 5:
				cursor.execute("INSERT INTO memos (dest, autor, msg) VALUES ('%s', '%s', '%s')" % (dest, username, msg))
				self.db.commit()

	def check_tables(self):
		"""
		Esta función comprueba si la tabla donde guardamos los memos no existe, en cuyo caso la crea
		"""
		cursor = self.db.cursor()
		c = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memos'").fetchall()
		if len(c) == 0:
			cursor.execute("""CREATE TABLE memos(id integer primary key autoincrement,
							dest varchar(50),
							autor varchar(50),
							msg varchar(140))""")
			self.db.commit()

	def close(self):
		self.db.close()
