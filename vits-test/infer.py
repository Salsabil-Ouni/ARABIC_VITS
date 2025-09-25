
import sys
sys.path.append("./vits")

import torch
import vits.commons as commons
import vits.utils as utils
from vits.models import SynthesizerTrn
from text.symbols import symbols
from text import text_to_sequence
from scipy.io.wavfile import write
import bit

import tempfile
import time
from io import BytesIO
import logging

utils.logger.root.setLevel(logging.ERROR)

def get_text(text, hps):
	text_norm = text_to_sequence(text, hps.data.text_cleaners)
	if hps.data.add_blank:
		text_norm = commons.intersperse(text_norm, 0)
	text_norm = torch.LongTensor(text_norm)
	return text_norm

class tts:
	def __init__(self, hps, noXOR: bool):
		self.net_g = None
		self.hps = hps
		self.noXOR = True

	def load_model(self, model_path):
		t1 = time.time()
		print("vits model path: %s" % model_path, flush=True, file=sys.stderr)
		device = "cuda" if torch.cuda.is_available() else "cpu"
		self.net_g = SynthesizerTrn(
			len(symbols),
			self.hps.data.filter_length // 2 + 1,
			self.hps.train.segment_size // self.hps.data.hop_length,
			**self.hps.model).to(device)
		_ = self.net_g.eval()
		if self.noXOR:
			### normal load
			_ = utils.load_checkpoint(model_path, self.net_g, None)
		else:
			### xor load
			with tempfile.TemporaryDirectory() as temp_dir: # windows cannot open that opened file (double opening)
				# print(temp_dir, flush=True, file=sys.stderr)
				with open(f"{temp_dir}/model.pth", mode='wb') as f:
					with open(model_path, 'rb') as ff:
						while b := ff.read(1<<24): # 16 MB
							f.write( bit.xor_f(b) )
				_ = utils.load_checkpoint(f"{temp_dir}/model.pth", self.net_g, None)
		# self.net_g = torch.compile(self.net_g, mode="max-autotune")
		print("load vits model: %s seconds" % (time.time() - t1), flush=True, file=sys.stderr)

	def infer(self, text, seed):
		device = "cuda" if torch.cuda.is_available() else "cpu"
		text = text.rstrip('\n')
		stn_tst = get_text( text, self.hps )
		print('### starting synthesis... input_text <%s> [%d]' % (text, seed), flush=True, file=sys.stderr)
		t1 = time.time()
		with torch.no_grad():
			torch.manual_seed(seed)
			torch.cuda.manual_seed(seed)
			x_tst = stn_tst.to(device).unsqueeze(0)
			x_tst_lengths = torch.LongTensor([stn_tst.size(0)]).to(device)
			audio = self.net_g.infer(x_tst, x_tst_lengths, noise_scale=.667, noise_scale_w=0.8, length_scale=1)[0][0,0].data.cpu().float().numpy()
		t2 = time.time()
		with BytesIO() as b:
			write(b, rate=self.hps.data.sampling_rate, data=audio)
			data = b.getvalue()
		dur = float(audio.squeeze().shape[0]) / self.hps.data.sampling_rate
		rtf = float(t2 - t1) / dur
		print("RTF: %.4f, wav dur.: %.4f s, synth dur.: %.4f s" % ( rtf, dur, t2 - t1 ), flush=True, file=sys.stderr)
		return data, float(t2 - t1), dur
