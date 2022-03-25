import os
import json
import time
import threading
from queue import Empty, Queue
from flask import Flask, request, json
import io
from sign2text import SOSign
from keras import backend as K
from utils.io_handler import NumpyEncoder, filename_gen
import argparse
from flask_cors import CORS

# Argument parsing
# ap = argparse.ArgumentParser()
# ap.add_argument("-e", "--engine", default='easyocr', help="ocr engine")
# args = vars(ap.parse_args())

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})

# Import model here
model = SOSign(model_path='models/sign2text_v2.h5', tokenizer_path='tokenizers/tokenizer_v2.pickle')
requestQueue = Queue()
CHECK_INTERVAL = 1
BATCH_SIZE = 10
BATCH_TIMEOUT = 2

def request_handler():
    while True:
        batch = []
        while not (
                len(batch) > BATCH_SIZE or
                (len(batch) > 0 and time.time() - batch[0]['time'] > BATCH_TIMEOUT)
        ):
            try:
                batch.append(requestQueue.get(timeout=CHECK_INTERVAL))
            except Empty:
                continue
        for req in batch:
            res, out_status = model.infer(req['vid'])
            out = {'result': res, 'out_status': out_status}
            req['output'] = out


threading.Thread(target=request_handler).start()

@app.route('/isAlive', methods=['GET'])
def is_alive():
    return {'responses': "Alive"}

@app.route('/sign2text', methods=['POST'])
def extract_table():
    vid = request.files['vid'].read()
    save_name = filename_gen()[:-4]
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    save_path = os.path.join('tmp', save_name+'.mp4')
    with open(save_path, 'wb') as f:
        f.write(vid)
    data = {'vid': [save_path], 'time': time.time()}

    requestQueue.put(data)
    response = {}
    count = 10
    while 'output' not in data and count > 0:
        time.sleep(CHECK_INTERVAL)

    if data['output']['out_status'] == 0:
        response = {
            'status': 'successful',
            'result': data['output']['result']
        }
    else:
        response = {
            'status': 'failed'
        }

    # Delete tmp file
    if os.path.exists(save_path):
        os.remove(save_path)
    else:
        print("Can not delete the temporary file(s) as it doesn't exists")

    return json.dumps(response, cls=NumpyEncoder)


if __name__ == "__main__":
    app.run(debug=True, port=50051, host='0.0.0.0', threaded=True)
