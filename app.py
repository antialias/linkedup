import tornado.ioloop
import tornado.web
import tornado.websocket
import os
import tornado.httpclient
import urlparse

client_id = "464d6465bc22cfca316e185e8d3bea81ba91ea8c"
client_secret = "9ddf34cda6f491a2eda403db2199600be7180cd4"
app_url = "http://thomashallock.com/linkedup/"
http_client = tornado.httpclient.HTTPClient()

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		if self.get_argument("code",False) :
			try:
				access_token_url = "https://api-ssl.bitly.com/oauth/access_token?client_id={0}&client_secret={1}&code={2}&redirect_uri={3}".format( \
					client_id, \
					client_secret, \
					self.get_argument("code"),app_url)
				# @tornado.web.asynchronous
				response = http_client.fetch(access_token_url, method="POST", body="hello")
				if response.error:
					print "Error:", response.error
				else:
					access = urlparse.parse_qs(response.body)
					self.set_cookie("oauth_access_token", access["access_token"][0])
					self.set_cookie("oauth_login", access["login"][0])
					self.set_cookie("oauth_apiKey", access["apiKey"][0])
					self.play();
				
			except tornado.httpclient.HTTPError, e:
				print "There was an Error:", e
		elif not self.get_cookie("oauth_access_token") :
			self.redirect("https://bitly.com/oauth/authorize?client_id={0}&redirect_uri={1}".format(client_id,app_url))
		else :
			self.play()

	def play(self):
		f = open("static/websocket.html")
		self.write(f.read());

class EchoWebSocket(tornado.websocket.WebSocketHandler):
	def open(self):
		url="https://api-ssl.bitly.com/v3/realtime/clickrate?access_token={0}&phrase={1}".format( \
			self.get_cookie("oauth_access_token"), \
			"obama")
		response = http_client.fetch(url, method="GET")
		print response
		print "Websocket opened"

	def on_message(self, message):
		self.write_message(u"You said: " + message)

	def on_close(self):
		print "WebSocket closed"

application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/websocket", EchoWebSocket),
])

if __name__ == "__main__":
	application.listen(11055)
	tornado.ioloop.IOLoop.instance().start()
