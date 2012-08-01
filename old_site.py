#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

class MainHandler(webapp.RequestHandler):
    def get(self):
			self.response.out.write(
				template.render("old_site/index.htm",{}))

class OLDLinkRedirectHandler(webapp.RequestHandler):
    def get(self):
			self.redirect(self.request.url+"index.html2")

class OLDLinkRedirectHandler2(webapp.RequestHandler):
    def get(self):
			new_url = self.request.url.replace("articles","Articles")
			self.redirect(new_url)

url_map = [
			('/', MainHandler),
			('/old', MainHandler),
			('/old/.*', MainHandler),
			('/Articles/.*', OLDLinkRedirectHandler),
			('/articles/.*', OLDLinkRedirectHandler2),
		]

def main():
    application = webapp.WSGIApplication(url_map,debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
