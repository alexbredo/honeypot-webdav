# Copyright (c) 2014 Alexander Bredo
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or 
# without modification, are permitted provided that the 
# following conditions are met:
# 
# 1. Redistributions of source code must retain the above 
# copyright notice, this list of conditions and the following 
# disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above 
# copyright notice, this list of conditions and the following 
# disclaimer in the documentation and/or other materials 
# provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND 
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE 
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR 
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

from tornado import ioloop, web, autoreload, options
import logging

# Source https://www.ietf.org/rfc/rfc3648.txt

class WebdavHandler(web.RequestHandler):
	# SUPPORTED_METHODS = ("GET", "OPTIONS", "PROPFIND", "PUT", "HEAD", "PROPPATCH", "PROPFIND", "LOCK", "UNLOCK")
	SUPPORTED_METHODS = ("GET", "POST", "OPTIONS", "HEAD", "MKCOL", "PUT", "PROPFIND", "PROPPATCH", "DELETE", "MOVE", "COPY", "GETLIB", "LOCK", "UNLOCK")
	
	def options(self):
		print(self.request)
		print(len(self.request.body))
		self.set_status(200)
		self.set_header("Allow", ', '.join(WebdavHandler.SUPPORTED_METHODS))
		self.set_header("DAV", "1, 2")
		self.set_header("Content-Type", "httpd/unix-directory")
		#self.set_header("Connection", "close")
		self.request.finish()

class RootHandler(WebdavHandler):
	#SUPPORTED_METHODS = ("GET", "PROPFIND")
	
	def get(self):
		self.propfind()
		
	def propfind(self): # PROPFIND /webdav HTTP/1.1
		print(self.request)
		print(len(self.request.body))
		self.set_status(301)
		self.set_header("Location", "/webdav/")
		self.render("templates/moved.html")
		self.request.finish()
		
class RedirectHandler(WebdavHandler):
	#SUPPORTED_METHODS = ("GET", "OPTIONS", "PROPFIND")
	
	def get(self):
		self.propfind()
	
	def propfind(self): # PROPFIND /webdav HTTP/1.1
		print(self.request)
		self.set_status(301)
		self.set_header("Location", "/webdav/") # http://192.168.221.209/webdav/
		self.set_header("Connection", "close")
		self.render("templates/moved.html")
		self.request.finish()

class MainHandler(WebdavHandler):
	#SUPPORTED_METHODS = ("GET", "OPTIONS", "PROPFIND")
	
	def get(self):
		return self.propfind()
		
	def propfind(self): # PROPFIND /webdav/ HTTP/1.1
		print(self.request)
		try: 
			depth = self.request.headers['Depth']
		except: 
			depth = 0 # default
		
		self.set_status(207, 'Multi-Status')
		self.set_header("Content-Type", 'text/xml; charset="UTF-8"')
		self.set_header("Connection", "close")
		
		#self.set_header("Date", "21 Mar 2014 08:39:26 GMT")
		#self.set_header("Server", "Apache/2.4.6 (Ubuntu)")
		#self.set_header("Content-Length", "838")
		#self.set_header("Keep-Alive", "timeout=5, max=99")
		#self.set_header("Connection", "Keep-Alive")
		
		if depth == 0: # Nur eignenen Ordner
			self.render("templates/multistatus.xml")
		elif depth == 1: # Mit Unterordnern
			self.render("templates/multistatus-d1.xml")
		self.request.finish()

class FileHandler(WebdavHandler):
	def get(self, filename):
		self.propfind(filename)
		
	def put(self, filename): # PUT /webdav/neue_datei.txt
		print(self.request)
		self.set_status(201)
		self.set_header("Location", "http://192.168.221.209/webdav/neue_datei.txt")
		self.set_header("Content-Type", 'text/xml; charset="UTF-8"')
		self.request.finish() # todo
		# self.render("templates/???.html")
		
	def head(self, filename):
		print(self.request)
		self.set_status(200)
		self.set_header("Last-Modified", "Fri, 21 Mar 2014 08:40:48 GMT")
		self.set_header("ETag", "0-4f519d7b1403b")
		
		
	def proppatch(self, filename): # todo content parsen!
		print(self.request)
		self.set_status(207, 'Multi-Status')
		self.render("templates/proppatch.xml")
		self.request.finish()
	
	def lock(self, filename):
		print(self.request)
		self.set_status(200)
		self.set_header("Content-Type", 'text/xml; charset="utf-8"')
		self.set_header("Lock-Token", '<opaquelocktoken:0f8b331b-eeca-4099-93a0-8ae4af6407d8>')
		self.render("templates/lock.xml")
		self.request.finish()
		
	def unlock(self, filename):
		print(self.request)
		self.set_status(204)
		self.set_header("Content-Type", "text/plain")
		self.request.finish()
	
	def propfind(self, filename): # todo
		print('filename', filename)
		self.set_header("Content-Type", "text/xml; charset=UTF-8")
		self.request.finish()
		
		self.set_status(207, 'Multi-Status')
		self.render("templates/multistatus-file.xml")
		self.request.finish()
		
		self.set_status(404)
		self.render("templates/not-found.html")
		self.request.finish()
		
	def move(self, filename_old):
		filename_new = self.request.headers['Destination']
		self.set_header("Location", filename_new) # http://192.168.221.209/webdav/neuer-name.txt
		self.set_status(201)
		self.render("templates/empty.html")
		self.request.finish()
		
	
application = web.Application([
	(r"/", RootHandler),
	(r"/webdav", RedirectHandler),
	(r"/webdav/", MainHandler),
	(r"/webdav/(.+)", FileHandler),
])

if __name__ == "__main__":
	application.listen(80)
	try:
		options.parse_command_line() 
		logging.info('Starting up')
		print("Running on Port 80. Stop with CTRL+Pause...")
		io_loop = ioloop.IOLoop.instance()
		autoreload.start(io_loop)
		io_loop.start()
	except KeyboardInterrupt:
		ioloop.IOLoop.instance().stop()
		print("End of Service")