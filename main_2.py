import time
from http.server import HTTPServer
from HTTPFunction import myHandler
import subprocess
import sys
import pkg_resources

HOST_NAME = ''
PORT = 8008
a = 0



print("Checking required libraries...")
required = {"tensorflow","spacy","sentence_transformers", "numpy"}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    python = sys.executable
    subprocess.check_call([python, '-m', 'pip', '-q', 'install', *missing], stdout=subprocess.DEVNULL)

import spacy
if not spacy.util.is_package("en_core_web_lg"):
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_lg"])

import model_2 as model

class myServer(HTTPServer):
    def __init__(self, address, handler):
        print("Loading model...")
        self.myModel = model.myModel()
        super().__init__(address, handler)
        print("Model loaded")

if a == 0:
    httpd = myServer((HOST_NAME, PORT), myHandler)
    print(time.asctime(), "Start Server - %s:%s\n"%(HOST_NAME,PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(),'Stop Server - %s:%s' %(HOST_NAME,PORT))