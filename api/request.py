import requests
import base64
import os
import json

path_pdf = "test_vids/ban_the_nao_1.mp4"
with open(path_pdf, 'rb') as pdf:
  name_pdf= os.path.basename(path_pdf)
  # print(name_pdf)
  files= {'vid': (name_pdf, pdf, 'multipart/form-data', {'Expires': '0'})}
  url = 'http://e9a7-34-73-186-215.ngrok.io/sign2text'

  # Check whether the server is on
  # res = requests.get('http://a005-104-199-224-166.ngrok.io/isAlive')

  # Send a sample request
  res = requests.post(url, files=files)

  # Print output
  res_json = res.json()
  # with open('output/tmp.json', 'w') as f:
  #   json.dump(res_json, f, indent=6)
  print(res_json)
