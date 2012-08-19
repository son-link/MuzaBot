# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulStoneSoup
from os import getpid, popen
from sys import exc_info
from traceback import format_tb

def log(line=None):
	t1 = getpid()

	"""
	Si ocurrió un error lo guardamos en un log
	"""

	f = open('log.txt', 'w')
	tb = exc_info()[2]
	tbinfo = format_tb(tb)[0]
	if line:
		f.write(line+'\n')
	f.write("PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(exc_info()[1]))
	f.close()
	popen('kill -9 '+str(t1))

def HTMLEntitiesToUnicode(text):
    """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
    text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
    pars = HTMLParser.HTMLParser()
    text = pars.unescape(text)
    return text.encode('utf-8')
