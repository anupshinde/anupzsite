#!/usr/bin/python

import cherrypy
import os

class HelloWorld(object):
	
	@cherrypy.expose
	def index(self, **params):
		return "Hello World!"
config = {'/static':
                {'tools.staticdir.on': True,
                 'tools.staticdir.dir': os.path.dirname(os.path.abspath(__file__))+'/static',
                }
        }
cherrypy.quickstart(HelloWorld(), '/', config=config)