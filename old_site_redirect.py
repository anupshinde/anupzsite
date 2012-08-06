#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template

red_map = [
			('/Articles/GMan/index.html', '/microsoft-agent-based-gmail-reader'),
			('/Articles/WordInDotnet/index.html', '/microsoft-word-in-dotnet'),
			('/Articles/OnionRouting/index.html', '/tunneling-and-onion-routing'),
			('/Articles/Hacking-The-World/Geo-locate-Emails/index.html', '/geo-locate-emails'),
			('/Articles/Hacking-The-World/Forcing-Mail-Receipts/index.html', '/forcing-email-read-receipts'),
			('/Articles/quaked/index.html', '/modifying-quake3'),
			('/Articles/LatentSemanticIndexing/Part1/index.html', '/latent-semantic-indexing')
		]
class MainHandler(webapp.RequestHandler):
    def get(self):
			u = self.request.url
			for (k,v) in red_map:
				if k in u:
					self.redirect(v)					
			#self.redirect("http://www.google.com?dr="+self.request.url)

class OLDLinkRedirectHandler(webapp.RequestHandler):
    def get(self):
			self.redirect(self.request.url+"index.html")

class OLDLinkRedirectHandler2(webapp.RequestHandler):
    def get(self):
			new_url = self.request.url.replace("articles","Articles")
			self.redirect(new_url)

url_map = [
			('.*', MainHandler)
		]

def main():
    application = webapp.WSGIApplication(url_map,debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
