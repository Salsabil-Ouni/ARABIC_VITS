import sys
sys.path.append("./vits")

import vits.utils as utils
import infer

import flask
import threading
import argparse
import time
import os
import logging
import json

inferer = None
synthLock = threading.Lock()
app = flask.Flask(__name__)
model_changable = True
aliveAt = time.time()
logging.getLogger('werkzeug').disabled = True

@app.route('/', methods=['GET'])
def ping():
	global aliveAt
	aliveAt = time.time()
	return 'pong'

import subprocess
from text.symbols import symbols

def postprocess_ipa(ipa: str) -> str:
	# Only keep characters present in the model's symbols
	ipa = ipa.replace("̪", "↘")
	return ''.join(c for c in ipa if c in symbols)

@app.route('/synthesize', methods=['POST'])
def synthesize():
	try:
		synthLock.acquire()
		# Get text from JSON body
		req_json = flask.request.get_json(force=True)
		text = req_json.get('text', '').strip()
		if not text:
			return flask.jsonify({'error': 'No text provided'}), 400

		# Convert text to IPA using espeak-ng
		try:
			ipa = subprocess.check_output([
				'espeak-ng',
				'-q',
				'--ipa',
				'-v', 'ar',  # Arabic voice
				text
			], universal_newlines=True)
		except Exception as e:
			return flask.jsonify({'error': f'espeak-ng failed: {str(e)}'}), 500

		ipa = postprocess_ipa(ipa)

		# Synthesize audio from IPA
		data, synthDur, wavDur = inferer.infer(ipa, flask.request.args.get('seed', 1234, type=int))

		# Encode audio as base64 for JSON response
		import base64
		audio_b64 = base64.b64encode(data).decode('utf-8')

		return flask.jsonify({
			'ipa': ipa,
			'audio_data': audio_b64,
			'synth_duration': synthDur,
			'wav_duration': wavDur
		})
	finally:
		synthLock.release()

@app.route('/set-model', methods=['GET'])
def load_model_req():
	if (model_changable == False):
		return 'set-model is not allowed'
	args = flask.request.args
	noxorFlag = args.get('noxor') == 'true'
	return load_model(args.get('hps_path'), args.get('model_path'), noxorFlag)

@app.route('/', methods=['POST'])
def synth():
	try:
		synthLock.acquire()
		args = flask.request.args
		data, synthDur, wavDur = inferer.infer(flask.request.get_data(as_text=True), args.get('seed', 1234, type=int))
		return flask.Response(
			data,
			status=200,
			mimetype='audio/wav',
			headers={
				'X-Synth-Duration': synthDur,
				'X-Wav-Duration': wavDur
			}
		)
	finally:
		synthLock.release()

def load_model(hps_path, model_path, noxor: bool):
	try:
		synthLock.acquire(blocking=True)
		global inferer
		inferer = infer.tts(utils.get_hparams_from_file(hps_path), noxor)
		inferer.load_model(model_path)
		return model_path
	except Exception as e:
		inferer = None
		raise e
	finally:
		synthLock.release()

def flags():
	parser = argparse.ArgumentParser(description='vits tts http server or onetime synthesizer')
	parser.add_argument('--host', default='0.0.0.0') # used by server
	parser.add_argument('--port', default=17500, type=int) # used by server
	parser.add_argument('--model_path', default='./archives/G_vits_x_x.pth')
	parser.add_argument('--hps_path', default='./archives/inference.json')
	parser.add_argument('--seed', default=1234, type=int) # used by onetime
	parser.add_argument('--onetime', action='store_true')
	parser.add_argument('--alive_for', default=-1, type=int)
	parser.add_argument('--disable_set_model', action='store_false')
	parser.add_argument('--noxor', action='store_true')
	return parser.parse_args()

def healthcheck(d):
	if (d < 0):
		return
	print( f'healthcheck with alive_for {d}s' )
	while True:
		time.sleep(1)
		now = time.time()
		if now - aliveAt > d:
			print( f'got no healthcheck in {d}s, shuting down...' )
			os._exit(0)

def main():
	args = flags()

	print(json.dumps(args.__dict__), flush=True, file=sys.stderr)
	try:
		load_model(args.hps_path, args.model_path, args.noxor)
	except Exception as e:
		print(str(e), flush=True, file=sys.stderr)
		return
	if args.onetime:
		data, _, _ = inferer.infer(sys.stdin.read().strip(), args.seed)
		return sys.stdout.buffer.write(data)

	global model_changable
	model_changable = args.disable_set_model
	threading.Thread(target=healthcheck, args={args.alive_for}).start()
	print('HTTP server started...', args.host, args.port, flush=True)
	app.run(host=args.host, port=args.port, debug=False, load_dotenv=False)

if __name__ == '__main__':
	main()
