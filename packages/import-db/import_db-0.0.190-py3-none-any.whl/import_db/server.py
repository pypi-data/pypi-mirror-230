from flask                import Flask, request
from pymetasploit3.msfrpc import MsfRpcClient, MsfRpcMethod
from tempfile             import NamedTemporaryFile
from time                 import sleep

def import_daemon(console, filename):
  console.read()
  console.write(f"db_import {filename}\n")
  out = console.read()['data']
  # TODO
  timeout = 30
  counter = 0
  while counter < timeout:
    out += console.read()['data']
    if "Nmap done" in out: break
    sleep(1)
    counter += 1
  return out

def create_app(console):
  app = Flask(__name__)

  @app.route('/upload', methods=['PUT'])
  def upload():
    file = NamedTemporaryFile()
    try:
      file.write(request.get_data())
      file.flush()
      #file.seek(0)
      out = import_daemon(console, file.name)
      return out, 200
    finally: file.close()

  return app

def start_server(password, username, upstreamh='0.0.0.0', upstreamp=55553, host="0.0.0.0", port=65432, *args, **kwargs):
  client = MsfRpcClient(password, username=username, server=upstreamh, port=upstreamp)
  c_id = client.call(MsfRpcMethod.ConsoleCreate)['id']
  console = client.consoles.console(c_id)
  app = create_app(console, **kwargs)
  app.run(debug=True, host=host, port=port, *args)

# https://www.easydevguide.com/posts/curl_upload_flask

