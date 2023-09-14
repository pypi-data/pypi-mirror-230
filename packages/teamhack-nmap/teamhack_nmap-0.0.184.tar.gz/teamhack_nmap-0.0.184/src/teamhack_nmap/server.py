from tempfile import NamedTemporaryFile
from flask import Flask, request
from subprocess import run, PIPE

def portscan_daemon(filename):
  p = run(['nmap', '-A', '-sV', '--script=vulners/vulners.nse -p- -iL - -oX -'], stdin=file, stdout=PIPE)
  p.check_returncode()
  return p.stdout

def create_app():
  app = Flask(__name__)

  @app.route('/upload', methods=['PUT'])
  def upload():
    try:
      file = NamedTemporaryFile()
      file.write(request.get_data())
      return portscan_daemon(file), 200
    finally: file.delete()

  return app

def start_server(host="0.0.0.0", port=55432, *args, **kwargs):
  app = create_app(**kwargs)
  app.run(debug=True, host=host, port=port, *args)

# https://www.easydevguide.com/posts/curl_upload_flask

