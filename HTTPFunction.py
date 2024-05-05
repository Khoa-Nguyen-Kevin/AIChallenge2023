from http.server import BaseHTTPRequestHandler
from os import curdir, sep
from urllib.parse import urlparse
import json


class myHandler(BaseHTTPRequestHandler):
	# def __init__(self, request, client_address, server) -> None:
	# 	super().__init__(request, client_address, server)
	# 	self.model = model.myModel()
	# 	print("Initialization complete.")
 
	# def _load_model(self):
	# 	if not hasattr(self, 'ready'):
	# 		print("Loading model...")
	# 		self.mymodel = model.myModel()
	# 		self.ready = True
	# 		print("Model loaded.")

	def do_GET(self):  # nhận và xử lý lệnh GET
		
		print("GET " ,end='')
		parsed_path = urlparse(self.path) # lệnh truy vấn
		self.path = self.path.split("?")[0] # đường dẫn chính
		if self.path=="/":  # đường dẫn mặc định
			self.path="/index.html"
		print(curdir + sep + self.path)   
		try:
			sendReply,data,mimetype,length = self.getcontent_toSend(self.path)
			self.send(sendReply,data,mimetype,length)
			return
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)

	def do_POST(self):
		# self._load_model()
		print("POST " ,end='')
		parsed_path = urlparse(self.path) # lệnh truy vấn
		self.path = self.path.split("?")[0] # đường dẫn chính

		reponse = {}

		if self.path=="/query":  # đường dẫn mặc định
			Text_input =  parsed_path.query.split('=')[1]
			Text_input =  Text_input.split('%20')
			Text_input = ' '.join(Text_input)


# --------------------------------------------------------------   
# --------------------------------------------------------------   
# ------------- Câu query nằm trong Text_input------------------   
# --------------------------------------------------------------   
			# TODO ....
			# results = self.mymodel.predict(Text_input, 100)
			results = self.server.myModel.predict(Text_input, 100)
			print('\n----------------------------')
			print('Text_input = ' + Text_input)
			print('----------------------------')
			# reponse = {
			# 	'url' : ['https://aichallenge2023.blob.core.windows.net/keyframes/01/keyframes/L01_V003/0003.jpg',
			# 			'https://aichallenge2023.blob.core.windows.net/keyframes/01/keyframes/L01_V003/0004.jpg',
			# 			'https://aichallenge2023.blob.core.windows.net/keyframes/01/keyframes/L01_V003/0005.jpg',
			# 			'https://aichallenge2023.blob.core.windows.net/keyframes/01/keyframes/L01_V003/0006.jpg',
			# 			'https://aichallenge2023.blob.core.windows.net/keyframes/01/keyframes/L01_V003/0007.jpg',
			# 			'https://aichallenge2023.blob.core.windows.net/keyframes/01/keyframes/L01_V003/0008.jpg',
			# 			'https://aichallenge2023.blob.core.windows.net/keyframes/01/keyframes/L01_V003/0009.jpg',
			# 			'https://aichallenge2023.blob.core.windows.net/keyframes/01/keyframes/L01_V003/0010.jpg']   
			# 	# gán mấy cái link vào đây. 
			# } 
			reponse = {
				'url' : results
			}
			#..........................
			reponse = json.dumps(reponse)
			sendReply = True
# --------------------------------------------------------------   
# --------------------------------------------------------------   
# --------------------------------------------------------------   
# --------------------------------------------------------------   
# --------------------------------------------------------------   


		if(	sendReply == True):
			#Open the static file requested and send it
			self.send_response(200)
			self.send_header('Content-type',"text/plane")
			self.end_headers()
			self.wfile.write(bytes(reponse,"utf8"))
			print("\n")
		else:
			self.send_error(404,'File Not Found: %s' % self.path)

	# ------------------------------------------------------------------
	# ------- Gởi dữ liệu đến ------------------------------------------
	# ------------------------------------------------------------------
	def getcontent_toSend(self,path): # xác đinh (trạng thái, dữ liệu, loại file, độ lớn file) gởi ngược lại browser theo yêu cầu
		sendReply = False
		data = ''
		mimetype = ''
		length = ''
		if self.path.endswith(".html"):
			mimetype='text/html'
			f = open(curdir + sep + path,"r")
			data = bytes(f.read(),'utf-8')
			length = str(len(data))
			f.close()
			sendReply = True
		if self.path.endswith(".png"):
			mimetype='image/png'
			f = open(curdir + sep + path,"rb")
			data = f.read()
			length = str(len(data))
			f.close()
			sendReply = True
		if self.path.endswith(".js"):
			mimetype='application/javascript'
			f = open(curdir + sep + path,"r")
			data = bytes(f.read(),'utf-8')
			length = str(len(data))
			sendReply = True
			f.close()
		if self.path.endswith(".json"):
			mimetype='text/json'
			f = open(curdir + sep + path,"r")
			data = bytes(f.read(),'utf-8')
			length = str(len(data))
			sendReply = True
			f.close()
		if self.path.endswith(".svg"):
			mimetype='image/svg+xml'
			f = open(curdir + sep + path,'r')
			data = bytes(f.read(),'utf-8')
			length = str(len(data))
			sendReply = True
			f.close()
		if self.path.endswith(".css"):
			mimetype='text/css'
			f = open(curdir + sep + path,"r")
			data = bytes(f.read(),'utf-8')
			length = str(len(data))
			f.close()
			sendReply = True
		if self.path.endswith(".woff"):
			mimetype='font/woff2'
			f = open(curdir + sep + path,'r',encoding="cp437")
			data = bytes(f.read(),'cp437')
			length = str(len(data))
			sendReply = True
			f.close()
		if self.path.endswith(".ttf"):
			mimetype='font/ttf'
			f = open(curdir + sep + path,'r',encoding="cp437")
			data = bytes(f.read(),'utf-8')
			length = str(len(data))
			sendReply = True
			f.close()
		if self.path.endswith(".eot"):
			mimetype='font/eot'
			f = open(curdir + sep + path,'r',encoding="cp437")
			data = bytes(f.read(),'utf-8')
			length = str(len(data))
			sendReply = True
			f.close()
		return sendReply,data,mimetype,length

	def send(self,sendReply,data,mimetype,length): # gởi dữ liệu về browser
		if sendReply == True:
			#Open the static file requested and send it
			self.send_response(200)
			self.send_header('Content-type',mimetype)
			print("file length : " + length)
			# self.send_header('Content-Length',length)
			self.end_headers()
			self.wfile.write(data)
			print("")
		else:
			self.send_error(404,'File Not Found: %s' % self.path)
	

	# ------------------------------------------------------------------
	# ------------------------------------------------------------------