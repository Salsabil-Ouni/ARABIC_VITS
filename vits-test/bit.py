
import sys
import numpy as np

def xor_f(a):
	xorbyte = 0x78
	npA = np.frombuffer(a, dtype=np.uint8)
	res = np.bitwise_xor(npA, xorbyte)
	return bytearray(res.tobytes())

def write_xor(inf, outf):
	size = 10*1024*1024
	with open(inf, mode='rb') as r:
		with open(outf, mode='wb') as w:
			while b := r.read(size):
				w.write( xor_f(b) )

if __name__ == '__main__':
	write_xor( sys.argv[1], sys.argv[2] )
