# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from os.path import isfile

def botconf():
	cfg = ConfigParser()
	conf = {}
	if not isfile('bot.cfg'):
		print 'No se encuentra el archivo de configuración del bot. Asegúrese de que el fichero bot.cfg esta en la carpeta raiz del bot'
		exit(1)

	cfg.read(['bot.cfg'])
	conf['host'] = cfg.get('muzabot', 'host')
	conf['port'] = int(cfg.get('muzabot', 'port'))
	conf['nick'] = cfg.get('muzabot', 'nick')
	conf['ident'] = cfg.get('muzabot', 'ident')
	conf['realname'] = cfg.get('muzabot', 'realname')
	conf['channel'] = cfg.get('muzabot', 'channel')

	return conf
