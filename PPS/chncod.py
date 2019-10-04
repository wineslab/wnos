# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Our Own Algorithm to determine the transmit rate of each source and transmit power of each transmitter
# Using the automatively generated solution algorithms

#####################################################################
# channel coding module
# 
# The input payload may be in binary, may need to
# be converted to ASC-II first, and then converted 
# back to binary for transmission befor return
#
# RS code can be used: https://pypi.python.org/pypi/unireedsolomon
#####################################################################

import netcfg, math, struct, time
from unireedsolomon.rs import *
from unireedsolomon.ff import *

#useless i think
def dtm_code_rate():
	'''
	func: determine channel coding rate. The channel coding rate should be determined 
	to maintain the residual packet error rate at a predefined level, say 1/10. The channel coding
	rate will increased or decreased based on the observed packet error rate. Currently
	return 0.5 as default   
	
	Define a set of possible channel coding rate in netcfg, ranging from 9/10 to 1/4
	'''
	
	# default channel coding rate


	return_rate = netcfg.ch_coding_rate[2]
	
	# get information somewhere else about observed packet error rate, (let's put it into l2 acks)
	# somewhere else there should be function to do the statistics
	
	
	# adjust channel coding rate
	return return_rate




def initialize_RSCoder(ch_coding_rate):
	'''

	initializes decoder 
	
	'''
	#l2_size_block = 128									   			# fized. at most 4096/2 = 2048
	#n = int(k * (1 + ch_coding_rate) -1	)	# variable, default half l2 packet
	#n = netcfg.l1_size

	k = netcfg.l2_size_block #this must be fixed
	n = int(k * (1 + ch_coding_rate) -1	)	# variable, default half l2 packet
	print '$$$ CODER N,K ',n,k

	generator=3
	fcr=1
	c_exp=math.ceil(math.log(netcfg.l1_size,2))
	prim=find_prime_polynomials(generator, c_exp, fast_primes=False, single=True)


	#print 'L0 pre coding', struct.unpack('h', payload[0:2])
	t1 = time.time()
	coder = RSCoder(n, k, generator, prim, fcr, c_exp)
	#print 'spent ',time.time()-t1,' in building the encoder. input ',k , 'output ',n
	return coder


def add_chncod(coder, payload, ch_coding_rate):
	'''
	func: add error protection to payload
	return: the payload with channel coding added
	parameters:
	payload_crc: payload to be protected
	chn_cod_rae: channel coding rate
	
	Notes: the payload is a string

	n = netcfg.l1_size #output bits of the encoder
	k = netcfg.l2_size #input bits of the encoder

	
	generator=3
	prim=0x11b
	fcr=1
	c_exp=math.ceil(math.log(netcfg.l1_size,2))

	#print 'L0 pre coding', struct.unpack('h', payload[0:2])



	coder = RSCoder(n, k, generator, prim, fcr, c_exp)
	


	'''

	c = ''
	c_block = ''
	d_block = ''

	# only for control messages (short)
	bloc_size = netcfg.l2_size_block
	if len(payload) < bloc_size:
		#print '@ CODING CCC'
		c_block = coder.encode(payload, poly=False, k=None, return_string=True)
		#print '@ length c ',len (c_block)
		#print 'c_block is ',i,' ' , type(c_block), 'size ',len(c_block)		
		return c_block

	else :	
		for i in range (0,netcfg.number_of_blocks):

			block_to_encode = payload[i*bloc_size:(i+1)*bloc_size]

			#print 'coding ',i,' ', len(block_to_encode)
			c_block = coder.encode(block_to_encode, poly=False, k=None, return_string=True)
			# UNCOMMENT print 'c_block is ',i,' ' , type(c_block), 'size ',len(c_block)
	#		print c_block

			#(d_block,d_block1) = coder.decode(c_block)
			#print 'DEcoding ',i,'type ',type(d_block),' ', len(d_block)
	#		print d_block		
			#print 'CHECK ',i,' ',block_to_encode == d_block

			c += c_block
			del c_block 
			#del d_block
			#del d_block1 
			del block_to_encode
			
		#print c
	#print 'L0 post coding', struct.unpack('h', c[0:2])

	#print 'c is ',len (c)
	

	return c
	
	# currently do nothing, returun the original payload directly
	
	#payload_chncod = payload
	#return payload_chncod

def deduct_chncod(coder,payload, ch_coding_rate):
	'''
	func: add error protection to payload
	return: the payload with channel coding added
	parameters:
	payload_crc: payload to be protected
	chn_cod_rae: channel coding rate
	
	Notes: the payload is a string

	#print 'L0 pre decoding',' ', struct.unpack('h', payload[0:2])
	
	'''
	d = ''
	k = netcfg.l2_size_block #this must be fixed
	bloc_size =  int(k * (1 + ch_coding_rate) -1)
	d_block = ''


	if len(payload) <=  bloc_size:
		#print '@ deCODING CCC len ',len(payload)
		try:
			(d_block,d_block1) = coder.decode(payload)
			#print '@ success'
			return d_block,1 #success
		except RSCodecError:
			#print 'unrecoverable block'	
			return d_block,0 #failure	


	else:	
		for i in range (0,netcfg.number_of_blocks):

			block_to_decode = payload[i*bloc_size:(i+1)*bloc_size]

			#print 'DEcoding ',i,' ', len(block_to_decode)
			try:
				(d_block,d_block1) = coder.decode(block_to_decode)
				#print 'd_block is ',i,' ' , type(d_block), 'size ',len(d_block)

			except RSCodecError:
				#print 'unrecoverable block'	
				return d,0 #failure


	#		print c_block

			#(d_block,d_block1) = coder.decode(c_block)
			#print 'DEcoding ',i,'type ',type(d_block),' ', len(d_block)
	#		print d_block		
			#print 'CHECK ',i,' ',block_to_encode == d_block

			d += d_block
			del d_block
			del d_block1 

	return d,1 #success

	'''	
	try:
		(m,m1) = coder.decode(payload)
		#print 'success decode'
		#print 'L0 post decoding', ' ', struct.unpack('h', m[0:2])	
		return m,1 #success
	except RSCodecError:
		#print 'failure decode'
		return payload,0 #failure
	'''

	# currently do nothing, returun the original payload directly
	
	#payload_chncod = payload
	#return payload_chncod


	
def check_phy(payload_chncod):
	'''
	func: check if length of the resulting packet exceeds phy-layer requirement
	return: 1 - OK, 0 - not OK
	'''
	
	# currently do nothing, returun OK directly
	if len(payload_chncod) <= 4096 :
		return 1
	else :
		return 0
