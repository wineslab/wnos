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

##! /usr/bin/python
########################################################################################################################################################################
#               Framing
########################################################################################################################################################################
#
# layer 2 (Datalink)	 ________________________________________________________________________________________
#	STRUCTURE			|_______pktno_mac_______________|_______src_ip_usrp_____________|_______dst_ip_usrp_____|			
#	BYTES				|			2					|			13					|			13				
#
#	FIELD						WRITE								READ
#	pktno_mac					struct.pack('h', pktno_mac)			(pktno_mac,) = struct.unpack('h', down_packet[0:2]) 
#	source_ip_usrp				+ str(self.layer_2_ip_uspr)			mac_packet[2:14] 
# 	dst_ip_usrp					+ str(self.layer_2_next_hop_ip_uspr)mac_packet[14:26]
#
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# layer 4 (Transport)#   ____________________________________________________________________________________________________________	
#	STRUCTURE			|_______pktno_l4________________|_______src_ip_l4_______________|_______dst_ip_l4_______|_____timestamp_____|		
#	BYTES				|			8					|			13					|			13			|			8			
#
#	FIELD						WRITE								READ.
#	pktno_l4					struct.pack('l', pktno_l4)			(l4_ack_pktno,) = struct.unpack('l', ack_l4[:8]) 
#	source_ip_l4				+ self.ip_usrp 						l4_packet_sender = ack_l4[8:20]
# 	dst_ip_l4					+ dest_usrp 						l4_packet_receiver = ack_l4[20:32]
#	timestamp 					+  struct.pack('d', timestamp)		(timestamp,) = struct.unpack('d', ack_l4[32:40])
#
#
#--------------------------------------------------------------------------------------------------------------------------------------------------------------------
# control channel (Transport): it has a different structure according to message_code value
#																		 ------------	
#	-2: channel coding update 
#						 _______________________________________________________________________________________________________________
#	STRUCTURE			|________message_code___________|_________src_ip_usrp___________|_______dst_ip_usrp_____|__________value_______|
#	BYTES				|				2				|				13				|				13		|			4		
#
#	FIELD						WRITE								READ
#	message_kind_code			struct.pack('h', -2)		 		(pktno_mac,) = struct.unpack('h', down_packet[0:2]) 				
#	src_ip_usrp				+ str(self.ip_address_usrp)				mac_source_ip =   mac_packet[2:14]			
# 	dst_ip_usrp				+ str(self.layer_2_next_hop_ip_uspr) 	mac_destination_ip =   mac_packet[14:26]
#	value					+ struct.pack('f', ch_coding_rate)		(new_rate,) = struct.unpack('f', payload[26:30])
#
#	-1: channel coding update
#						 _______________________________________________________________________________________________________________
#	STRUCTURE			|________message_code___________|_________src_ip_usrp___________|_______dst_ip_usrp_____|__________value_______|
#	BYTES				|				2				|				13				|				13		|			4		
#
#	FIELD						WRITE								READ
#	message_kind_code			struct.pack('h', -1)		 		(pktno_mac,) = struct.unpack('h', down_packet[0:2]) 				
#	src_ip_usrp				+ str(self.ip_address_usrp)				mac_source_ip =   mac_packet[2:14]			
# 	dst_ip_usrp				+ str(self.layer_2_next_hop_ip_uspr) 	mac_destination_ip =   mac_packet[14:26]
#	value					+ struct.pack('f', ch_coding_rate)		(new_rate,) = struct.unpack('f', payload[26:30])
#					
#				
#	2: 2nd layer ack
#	 					 _______________________________________________________________________________________________________________________
#	STRUCTURE			|_______message_code____________|_______pktno_mac_______________|_______src_ip_usrp_____________|_______dst_ip_usrp_____|			
#	BYTES				|				2				|			2					|			13					|			13						
#
#	FIELD						WRITE								READ
#	message_kind_code			struct.pack('h', 2)					(pktno_mac,) = struct.unpack('h', down_packet[0:2]) 	
#	pktno_mac					struct.pack('h', pktno_mac)			(pktno_mac,) = struct.unpack('h', down_packet[0:2]) 
#	source_ip_usrp				+ str(self.layer_2_ip_uspr)			mac_packet[2:14] 
# 	dst_ip_usrp					+ str(self.layer_2_next_hop_ip_uspr)mac_packet[14:26]
#
#
#	4: 4th layer ack
#						 ___________________________________________________________________________________________________________________________________________	
#	STRUCTURE			|_______message_code____________|_______pktno_l4________________|_______src_ip_l4_______________|_______dst_ip_l4_______|_____timestamp_____|		
#	BYTES				|				2				|			8					|			13					|			13			|			8			
#
#	FIELD						WRITE								READ
#	message_kind_code			struct.pack('h', 4)			 		(pktno_mac,) = struct.unpack('h', down_packet[0:2]) 	
#	pktno_l4					struct.pack('l', pktno_l4)			(l4_ack_pktno,) = struct.unpack('l', ack_l4[:8]) 
#	source_ip_l4				+ self.ip_usrp 						l4_packet_sender = ack_l4[8:20]
# 	dst_ip_l4					+ dest_usrp 						l4_packet_receiver = ack_l4[20:32]
#	timestamp 					+  struct.pack('d', timestamp)		(timestamp,) = struct.unpack('d', ack_l4[32:40])
#
#
#	-3: general messagging
#	 					 _______________________________________________________________________________________________________________________________________________________
#	STRUCTURE			|_______message_code____________|_______src_ip_usrp_____________|_______dst_ip_usrp_____|_______message_code____________|_______message_value____________|			
#	BYTES				|				2				|			13					|			13							2				|				4				|			
#
#	FIELD						WRITE								READ
#	message_kind_code			struct.pack('h', -3)				(pktno_mac,) = struct.unpack('h', down_packet[0:2]) 	
#	source_ip_usrp				+ str(self.layer_2_ip_uspr)			mac_packet[2:14] 
# 	dst_ip_usrp					+ str(self.layer_2_next_hop_ip_uspr)mac_packet[14:26]
#	para_code					+ struct.pack('h', para_code)		(para_code,) = struct.unpack('h',sgl_msg[24:26])
#	para_val					+ struct.pack('f', para_val)		(para_value,) = struct.unpack('f',sgl_msg[26:30])
#
#


import os, sys, inspect
# realpath() will make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

########################################################
#               Network Configuration 
########################################################

# Configure directory
import os, sys
p = os.getcwd()										# Current directory
p = os.path.dirname(p)      						# Parent directory
sys.path.insert(0, p+'/WNOSPYv2/wos-protocol')      	# Directory of testbed
sys.path.insert(0, p+'/WNOSPYv2/wos-network') 		# Network parameters 
sys.path.insert(0, p+'/wnospyv2/wos-protocol')      	# Directory of testbed
sys.path.insert(0, p+'/wnospyv2/wos-network') 		# Network parameters 


import time, math

import ptcl_name, net_name

import numpy as np

from random import randint

# Switch for transmission parameter optimization
# 1 - optimized; 0 - not optimized
b_optrate = 1						# switch for rate optimization 
b_optpwr = 1					    # switch for power optimization

# Point to the node object, updated in mynd.py
thisnode = None

# Node id, which will be updated in mynd.py, and will be used to construct file names in mynd.py
nodeid = None

####################################################################################
#  Constants
####################################################################################

SMALL_VALUE = 1e-20         # very small value to approximate 0 in denominator 

disp_note = 0				# change this to 0 to mute notes display 
note1 = 'Next step work: connect correlator blocks; implement CSI collection function; adaptive algorithm.'
note2 = 'In netcfg.py, set disp_note = 0 to run the program.'

####################################################################################
#  Transmission Parameters
####################################################################################

# select control algorithm
#alg = 'JOCP'                   # JOCP algorithm will not be implemented since our focus is automated algorithm generation. 
alg = 'WNOS'   

# select physical layer: 'NARROWBAND' or 'OFDM'
phy = 'NARROWBAND'
#phy = 'OFDM'

# narrowband parmeters: transmitter and reciever must be set for the same parameters
narrow_rate = ptcl_name.narrow_rate  #62500        	# transmit rate in bps
narrow_modulation =  'gmsk' 						# 'bpsk', 'gmsk'
#narrow_modulation =  'bpsk'

# Candidate schemes
# When the control objective is power minimization, scheme 6 should be used
# 1: Best Response, use the maximum power and layer-4 transmission rate
# 2: WNOS with power and rate control
# 3: WNOS with only rate control
# 4: No Control, fixed power and layer-4  transmission rate
# 5: WNOS with only power control  
# 6: For power minimization, without rate control, with power control, with Lagrangian updating

scheme = 6

# Generate the initial transmit gain randomly
tx_gain = randint(net_name.min_pwr_in_dB, net_name.max_pwr_in_dB)

tspt_rate = 256*8*1.9             # in bps
#! /usr/bin/python

# See above for information of this scheme
if scheme == 1:
	b_br = 'on'                                     # br -> best response
	b_pwr_ctl = 'off'
	b_Lag_ctl = 'off'
	b_rate_ctl = b_Lag_ctl
	
	# Use the maximum power and rate
	tx_gain = net_name.max_pwr_in_dB		    	# transmit gain of usrp
	tspt_rate = net_name.max_rate_in_bps			# Initial tansport layer rate in bps	

# See above for information of this scheme
if scheme == 2:
	b_br = 'off'
	b_pwr_ctl = 'on'
	b_Lag_ctl = 'on'
	b_rate_ctl = b_Lag_ctl	

# See above for information of this scheme
if scheme == 3:
	b_br = 'off'
	b_pwr_ctl = 'off'
	b_Lag_ctl = 'on'
	b_rate_ctl = b_Lag_ctl	

# See above for information of this scheme
if scheme == 4:
	b_br = 'off'
	b_pwr_ctl = 'off'
	b_Lag_ctl = 'off'
	b_rate_ctl = b_Lag_ctl	

# See above for information of this scheme	
if scheme == 5:
	b_br = 'off'
	b_pwr_ctl = 'on'
	b_Lag_ctl = 'off'
	b_rate_ctl = b_Lag_ctl		

# See above for information of this scheme	
if scheme == 6:
	b_br = 'off'
	b_pwr_ctl = 'on'
	b_Lag_ctl = 'on'
	b_rate_ctl = 'off'
	
	
# transmit parameters
sps = 4						# samples per symbol
tx_ampl = 0.5  				# transmit amplitude
rx_gain = 10.0				# receiver gain of usrp
# tx_gain = 15.0 		    	# transmit gain of usrp
# tspt_rate = 20000			# Initial tansport layer rate in bps

l4_control_rate_flag = 1    # 1: limited rate 0: no control, no limit on rate

# dB -> absolute 
tx_gain_abs = 10**(tx_gain/10)
rx_gain_abs = 10**(rx_gain/10)

tx_digital_gain = 1			## transmitter digital gain, default 1; seems not being used
rx_digital_gain = 1			## receiver digital gain, default 1;  seems not being used

# differential modulation or not
differential = False		# use non_differential modulation to match the preamble correlator at receiver side

# correlator-related parameters
# nfilts and eb are using the default value, do not change them 
nfilts = 32								# Number of filter taps
eb = 0.35								# Excessive bandwidth
sample_rate = narrow_rate*sps			# Sample rate of USRP	

# PN codes, must be 0 and 1 string
pn0_corr = [1,-1,1,-1,1,1,-1,-1,1,1,-1,1,1,1,-1,1,1,-1,1,-1,-1,1,-1,-1,1,1,1,-1,-1,-1,1,-1,1,1,1,1,-1,-1,1,-1,1,-1,-1,-1,1,1,-1,-1,-1,-1,1,-1,-1,-1,-1,-1,1,1,1,1,1,1,-1,-1]
pn1_corr = [-1,1,1,1,1,-1,-1,1,1,-1,-1,1,-1,-1,1,1,1,1,1,-1,-1,1,1,1,1,1,1,1,1,-1,-1,1,-1,-1,1,-1,-1,1,-1,1,-1,-1,-1,1,-1,1,-1,-1,-1,-1,1,1,1,1,-1,1,-1,1,-1,1,1,-1,1,1]
pn2_corr = [-1,-1,1,1,1,-1,-1,-1,-1,1,-1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,-1,1,1,1,1,-1,1,-1,1,1,-1,-1,-1,-1,-1,1,-1,1,-1,1,-1,1,-1,-1,-1,1,1,1,1,1,-1,-1,1,1,1,-1,1,-1,1]
pn3_corr = [-1,-1,1,-1,1,1,-1,-1,1,-1,1,-1,-1,1,-1,-1,1,-1,1,-1,1,1,1,1,1,-1,1,1,-1,-1,-1,1,-1,-1,1,1,-1,1,1,-1,1,1,-1,-1,1,1,1,1,1,1,-1,-1,-1,1,-1,1,1,-1,1,1,1,-1,-1,-1]

pn0 = '0101001100100010010110110001110100001101011100111101111100000011'
pn1 = '1000011001101100000110000000011011011010111010111100001010100100'
pn2 = '1100011110100001111111100100001010011111010101011100000110001010'
pn3 = '1101001101011011010100000100111011001001001100000011101001000111'

# transmitter and receiver PN 
# Currently we have only two paths, src3 and rly3 are set with the same PNs as src2 and rly3
# If we want to establish three paths, we need two more PNs for src3 and rly3
#       src1   	src2  	src3   	
#	rly11   rly21   rly31    
#	rly12   rly22   rly32  
#	rly13   rly23   rly33 
#	rly14   rly24   rly34 
#	rly15   rly25   rly35 
#	dst1    dst2    dst3

tsmt_pn = 	[pn0,   pn1,  pn1,\
	  	pn2,	pn3,    pn3,\
		pn2,    pn3,	pn3,\
		pn2,    pn3,	pn3,\
		pn2,    pn3,	pn3,\
		pn2,    pn3,	pn3,\
	   	None,   None,   None]


rcvr_pn = 	[None,  None, None, \
 		pn0,	pn1,    pn1,\
		pn0,    pn1,    pn1,\
		pn0,    pn1,    pn1,\
		pn0,    pn1,    pn1,\
		pn0,    pn1,    pn1,\
		pn2,    pn3,    pn3]

tsmt_pn_corr = [pn0_corr,   pn1_corr,  pn1_corr,\
	   	pn2_corr,    pn3_corr,    pn3_corr,\
		pn2_corr,    pn3_corr,    pn3_corr,\
		pn2_corr,    pn3_corr,    pn3_corr,\
		pn2_corr,    pn3_corr,    pn3_corr,\
		pn2_corr,    pn3_corr,    pn3_corr,\
	 	None,   None,   None]

rcvr_pn_corr = [None,  None, None,\
		pn0_corr,    pn1_corr,    pn1_corr,\
		pn0_corr,    pn1_corr,    pn1_corr,\
		pn0_corr,    pn1_corr,    pn1_corr,\
		pn0_corr,    pn1_corr,    pn1_corr,\
		pn0_corr,    pn1_corr,    pn1_corr,\
	  	pn2_corr,    pn3_corr,    pn3_corr]

tx_pn_this_node = None		# PN code used for transmission, will be determined in mynd.py based on node role
rx_pn_this_node = None      # PN code for reception          

# corre PN sequence for correlator
# correlator uses binary sequence while the transmitter/receiver uses string 
tx_pn_this_node_corr = None
rx_pn_this_node_corr = None

####################################################################################
# channel gain information, measured offline for now
####################################################################################

# Receiver block, initialized to None, will be updated after the receiver block created in start_l1_receiving_block
# This block will be invoked to get received signal power
obj_rcvr_blk = None 

                        
# Position of nodes         
#         src1    src2    src3   rly11   rly21   rly31    rly12   rly22   rly32    rly13   rly23   rly33    rly14   rly24   rly34       rly15   rly25   rly35       dst1    dst2    dst3                                                                        dst1    dst2    dst3
nd_x = [  0,      0,      0,     2,      2,      2,       4,      4,      4,       3,      3,      3,       1,       1,     1,          0,       0,     0,          4,       4,      4] 
nd_y = [  0,      7,      10,    0,      7,      10,      0,      7,      10,      0,      7,      10,      0,       7,     10,         0,       7,     10,         0,       7,      10]  
nd_z = [  0,      0,      0,     0,      0,      0,       0,      0,      0,       1,      1,      1,       1,       1,     1,          1.5,     1.5,   1.5,        1.5,     1.5,    1.5]

# Compute distance
# loop nd1 from src1, src2 to dst3
# For each node compute the distance to all other nodes
N = 21                      # Total number of nodes
dst = np.zeros((N, N))      # Initialize distance matrix to all zero
chn_gain = np.zeros((N, N)) # Initialize channel to all zero

for nd1 in range(N):        # Compute distance and channel gain
    for nd2 in range(N):
        if nd1 != nd2:
            dst[nd1, nd2] = math.sqrt((nd_x[nd1] - nd_x[nd2])**2 + (nd_y[nd1] - nd_y[nd2])**2  + (nd_z[nd1] - nd_z[nd2])**2)
            chn_gain[nd1, nd2] = dst[nd1, nd2]**(-4)
            
                        
# Transmit gain of all transmitters, default 12.5
# This parameter is used to calculate tranmist power and interferece
# Updated in running time by signaling exchange
#   src1   	src2  	src3   	
#	rly11   rly21   rly31    
#	rly12   rly22   rly32  
#	rly13   rly23   rly33 
#	rly14   rly24   rly34 
#	rly15   rly25   rly35 
#	dst1    dst2    dst3

tx_gain_allnode = [	tx_gain, 	tx_gain, 	tx_gain,
    			tx_gain,    	tx_gain,   	tx_gain, 
	  	 	tx_gain,    	tx_gain,   	tx_gain,
	  	 	tx_gain,    	tx_gain,   	tx_gain,
	  	 	tx_gain,    	tx_gain,   	tx_gain,
	  	 	tx_gain,    	tx_gain,   	tx_gain,
			0,      	0,      	0]

# Interference relationship, this needs to be configured according to frequency used by the nodes
# Only relay and destination suffer from interference, source nodes do not
# 
# Vector name indicate the nodes that receive interference
# Elecments of each vector represent the interferer
#
# 0: no mutual interference; 1: there is mutual interference
#
#       	src1   	src2  	src3   	rly11   rly21   rly31   rly12   rly22   rly32  	rly13   rly23   rly33 	rly14   rly24   rly34 	rly15   rly25   rly35	dst1    dst2    dst3
itf_src1 	= [0,    0,    	0,     	0,      0,      0,      0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]
itf_src2 	= [0,    0,    	0,     	0,      0,      0,      0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]
itf_src3 	= [0,    0,    	0,     	0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]

itf_rly11	= [0,    1,    	1,     	0,      0,      0,      0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]
itf_rly21	= [1,    0,    	1,     	0,      0,      0,      0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]
itf_rly31 	= [1,    1,    	0,		0,      0,      0,      0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]

itf_rly12	= [0,    0,    	0,    	0,      1,      1,      0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]
itf_rly22	= [0,    0,    	0,    	1,      0,      1,      0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]
itf_rly32 	= [0,    0,    	0,		1,      1,      0,      0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]
	
itf_rly13	= [0,    0,    	0,    	0,      0,      0,      0,      1,      1,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]
itf_rly23	= [0,    0,    	0,    	0,      0,      0,      1,      0,      1,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]
itf_rly33 	= [0,    0,    	0,		0,      0,      0,      1,      1,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]
	
itf_rly14	= [0,    0,    	0,    	0,      0,      0,      0,      0,      0,		0,      1,      1,		0,      0,      0,		0,      0,      0,		0,      0,      0]
itf_rly24	= [0,    0,    	0,    	0,      0,      0,      0,      0,      0,		1,      0,     	1,		0,      0,      0,		0,      0,      0,		0,      0,      0]
itf_rly34 	= [0,    0,    	0,		0,      0,      0,      0,      0,      0,		1,      1,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0]

itf_rly15	= [0,    0,    	0,    	0,      0,      0,      0,      0,      0,		0,      0,      0,		0,      1,      1,		0,      0,      0,		0,      0,      0]
itf_rly25	= [0,    0,    	0,    	0,      0,      0,      0,      0,      0,		0,      0,      0,		1,      0,      1,		0,      0,      0,		0,      0,      0]
itf_rly35 	= [0,    0,    	0,		0,      0,      0,      0,      0,      0,		0,      0,      0,		1,      1,      0,		0,      0,      0,		0,      0,      0]

itf_dst1 	= [0,    0,    	0,     	0,      0,      0,     	0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      1,      1,		0,      0,      0]
itf_dst2 	= [0,    0,    	0,     	0,      0,      0,     	0,      0,      0,		0,      0,      0,		0,      0,      0,		1,      0,      1,		0,      0,      0]
itf_dst3 	= [0,    0,    	0,     	0,      0,      0,		0,      0,      0,		0,      0,      0,		0,      0,      0,		1,      1,      0,		0,      0,      0]

itf_relation = np.matrix([	itf_src1, 	itf_src2, 	itf_src3, 
                          	itf_rly11, 	itf_rly21, 	itf_rly31, 
				            itf_rly12, 	itf_rly22, 	itf_rly32, 
				            itf_rly13, 	itf_rly23, 	itf_rly33, 
				            itf_rly14, 	itf_rly24, 	itf_rly34, 
				            itf_rly15, 	itf_rly25, 	itf_rly35, 
                          	itf_dst1, 	itf_dst2, 	itf_dst3])
					  
#print chn_gain[1,1]

# index of this node, updated in mynd.py
idx_thisnode     = None

# Which channel gain should be used for the session with this node as transmitter, i.e., the column of chn_gain?
# idx_thisnode determines the row of chn_gain matrix to be used
#       src1   	src2  	src3   	
#	rly11   rly21   rly31    
#	rly12   rly22   rly32  
#	rly13   rly23   rly33 
#	rly14   rly24   rly34 
#	rly15   rly25   rly35 
#	dst1    dst2    dst3    
chn_idx_thisnode = [	3,     	4,    	5,\
		     	        6,      7,      8,\
	     		        9,      10,     11,\
	     		        12,     13,     14,\
	     		        15,     16,     17,\
	     		        18,     19,     20,\
			            None,   None,   None]

sir_thisnode     = None   	# SIR information measured online, initialized to None
sgl_pwr_thisnode = None	 	# average received signal power of this node, updated in csi.py
alpha = 0.5	     			# coefficient of running average
					  
####################################################################################
# Node role and IP configuration
####################################################################################

# available node id, the corresponding node typle
nd_id   = [	'src1', 	'src2', 	'src3',\
 		    'rly11',	'rly21', 	'rly31',\
	 	    'rly12', 	'rly22', 	'rly32',\
	 	    'rly13', 	'rly23', 	'rly33',\
	 	    'rly14', 	'rly24', 	'rly34',\
	 	    'rly15', 	'rly25', 	'rly35',\
		    'dst1', 	'dst2', 	'dst3']


nd_type = [	'tx',  		'tx',  		'tx',\
	  	'relay',  	'relay',  	'relay',\
	  	'relay',  	'relay',  	'relay',\
	  	'relay',  	'relay',  	'relay',\
	  	'relay',  	'relay',  	'relay',\
	  	'relay',  	'relay',  	'relay',\
		'rx',  		'rx',  		'rx']
        
# IP of PCs
IP_PC1 = '192.168.10.50'
IP_PC2 = '192.168.10.51'
IP_PC3 = '192.168.10.52'
IP_PC4 = '192.168.10.53'
IP_PC5 = '192.168.10.54'

# Session 1 IP address
ip_pc_src1 		= 	IP_PC3
ip_pc_rly11 	= 	IP_PC3
ip_pc_rly12 	= 	IP_PC1
ip_pc_rly13 	= 	IP_PC1
ip_pc_rly14 	= 	IP_PC1
ip_pc_rly15 	= 	IP_PC1
ip_pc_dst1 		= 	IP_PC1


# Specify which set of parameters to use for chain-1 usrps
chain1_usrp_cfg = 1

if chain1_usrp_cfg == 1:# high chain
	ip_usrp_src1 	= 	'192.168.10.16'
	ip_usrp_rly11 	= 	'192.168.10.26' 
	ip_usrp_rly12 	= 	'192.168.10.27' 
	ip_usrp_rly13 	= 	'192.168.10.22' 
	ip_usrp_rly14 	= 	'192.168.10.20' 
	ip_usrp_rly15 	= 	'192.168.10.23' 
	ip_usrp_dst1 	= 	'192.168.10.32'


if chain1_usrp_cfg == 2:# middle chain
	ip_usrp_src1 	= 	'192.168.10.13'
	ip_usrp_rly11 	= 	'192.168.10.24' 
	ip_usrp_rly12 	= 	'192.168.10.17' 
	ip_usrp_rly13 	= 	'192.168.10.10' 
	ip_usrp_rly14 	= 	'192.168.10.19' 
	ip_usrp_rly15 	= 	'192.168.10.14' 
	ip_usrp_dst1 	= 	'192.168.10.31'	
	
	
if chain1_usrp_cfg == 3:#low chain 
	ip_usrp_src1 	= 	'192.168.10.15'
	ip_usrp_rly11 	= 	'192.168.10.12' 
	ip_usrp_rly12 	= 	'192.168.10.11' 
	ip_usrp_rly13 	= 	'192.168.10.18' 
	ip_usrp_rly14 	= 	'192.168.10.21' 
	ip_usrp_rly15 	= 	'192.168.10.25' 
	ip_usrp_dst1 	= 	'192.168.10.30'	
	
#Session 2
ip_pc_src2 		= 	IP_PC3
ip_pc_rly21 	= 	IP_PC3
ip_pc_rly22 	= 	IP_PC2
ip_pc_rly23 	= 	IP_PC2
ip_pc_rly24 	= 	IP_PC2
ip_pc_rly25 	= 	IP_PC2
ip_pc_dst2 		= 	IP_PC2


ip_usrp_src2 	= 	'192.168.10.13'
ip_usrp_rly21 	= 	'192.168.10.24' 
ip_usrp_rly22 	= 	'192.168.10.17' 
ip_usrp_rly23 	= 	'192.168.10.10' 
ip_usrp_rly24 	= 	'192.168.10.19' #
ip_usrp_rly25 	= 	'192.168.10.14' #
ip_usrp_dst2 	= 	'192.168.10.31' #

# Session 3 IP address
ip_pc_src3 		= 	IP_PC5
ip_pc_rly31 	= 	IP_PC5
ip_pc_rly32 	= 	IP_PC5
ip_pc_rly33 	= 	IP_PC4
ip_pc_rly34 	= 	IP_PC4
ip_pc_rly35 	= 	IP_PC4
ip_pc_dst3 		= 	IP_PC4

ip_usrp_src3 	= 	'192.168.10.15'
ip_usrp_rly31 	= 	'192.168.10.12' 
ip_usrp_rly32 	= 	'192.168.10.11' #
ip_usrp_rly33 	= 	'192.168.10.18' 
ip_usrp_rly34 	= 	'192.168.10.21' 
ip_usrp_rly35 	= 	'192.168.10.25' 
ip_usrp_dst3 	= 	'192.168.10.30'#
	
# map usrp ip to index of the node
usrp_ip_2_ndidx = {}
usrp_ip_2_ndidx[ip_usrp_src1] 	= 	0
usrp_ip_2_ndidx[ip_usrp_src2] 	= 	1
usrp_ip_2_ndidx[ip_usrp_src3] 	=	2
usrp_ip_2_ndidx[ip_usrp_rly11] 	= 	3
usrp_ip_2_ndidx[ip_usrp_rly21] 	= 	4
usrp_ip_2_ndidx[ip_usrp_rly31] 	= 	5
usrp_ip_2_ndidx[ip_usrp_rly12] 	= 	6
usrp_ip_2_ndidx[ip_usrp_rly22] 	= 	7
usrp_ip_2_ndidx[ip_usrp_rly32] 	= 	8
usrp_ip_2_ndidx[ip_usrp_rly13] 	= 	9
usrp_ip_2_ndidx[ip_usrp_rly23] 	= 	10
usrp_ip_2_ndidx[ip_usrp_rly33] 	= 	11
usrp_ip_2_ndidx[ip_usrp_rly14] 	= 	12
usrp_ip_2_ndidx[ip_usrp_rly24] 	= 	13
usrp_ip_2_ndidx[ip_usrp_rly34] 	= 	14
usrp_ip_2_ndidx[ip_usrp_rly15] 	= 	15
usrp_ip_2_ndidx[ip_usrp_rly25] 	= 	16
usrp_ip_2_ndidx[ip_usrp_rly35] 	= 	17
usrp_ip_2_ndidx[ip_usrp_dst1] 	= 	18
usrp_ip_2_ndidx[ip_usrp_dst2] 	= 	19
usrp_ip_2_ndidx[ip_usrp_dst3] 	= 	20

# USRP IPs of sender-type nodes of a session, including the source but not destination
usrp_ip_sender_of_session = {}
usrp_ip_sender_of_session[ip_usrp_src1] = [ip_usrp_src1, ip_usrp_rly11, ip_usrp_rly12, ip_usrp_rly13, ip_usrp_rly14, ip_usrp_rly15]
usrp_ip_sender_of_session[ip_usrp_src2] = [ip_usrp_src2, ip_usrp_rly21, ip_usrp_rly22, ip_usrp_rly23, ip_usrp_rly24, ip_usrp_rly25]
usrp_ip_sender_of_session[ip_usrp_src3] = [ip_usrp_src3, ip_usrp_rly31, ip_usrp_rly32, ip_usrp_rly33, ip_usrp_rly34, ip_usrp_rly35]

# All usrp IPs	
all_usrp_ip = [	ip_usrp_src1, 	ip_usrp_src2, 	ip_usrp_src3,\
		        ip_usrp_rly11, 	ip_usrp_rly21, 	ip_usrp_rly31,\
		        ip_usrp_rly12, 	ip_usrp_rly22, 	ip_usrp_rly32,\
		        ip_usrp_rly13, 	ip_usrp_rly23, 	ip_usrp_rly33,\
		        ip_usrp_rly14, 	ip_usrp_rly24, 	ip_usrp_rly34,\
		        ip_usrp_rly15, 	ip_usrp_rly25, 	ip_usrp_rly35,\
		        ip_usrp_dst1, 	ip_usrp_dst2, 	ip_usrp_dst3]
# print(all_usrp_ip)
# input('...')

# usrp address 
# Currently exactly 12 character IP address is supported
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3    
args     = [	'addr='+ip_usrp_src1, 	'addr='+ip_usrp_src2,  	'addr='+ip_usrp_src3,\
		'addr='+ip_usrp_rly11, 	'addr='+ip_usrp_rly21,  'addr='+ip_usrp_rly31,\
		'addr='+ip_usrp_rly12, 	'addr='+ip_usrp_rly22,  'addr='+ip_usrp_rly32,\
		'addr='+ip_usrp_rly13, 	'addr='+ip_usrp_rly23,  'addr='+ip_usrp_rly33,\
		'addr='+ip_usrp_rly14, 	'addr='+ip_usrp_rly24,  'addr='+ip_usrp_rly34,\
		'addr='+ip_usrp_rly15, 	'addr='+ip_usrp_rly25,  'addr='+ip_usrp_rly35,\
		'addr='+ip_usrp_dst1, 	'addr='+ip_usrp_dst2,  	'addr='+ip_usrp_dst3]

# transmit/receive frequency
######################################################################################
#   !!!!!! When freq is changed, itf_relation needs to be udpated accordingly
######################################################################################
f1 = 2.0e9
f2 = 2.2e9
f3 = 2.4e9
f4 = 2.6e9
f5 = 2.8e9
f6 = 3.0e9

#   src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 9001
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
tx_freq   =   [	f1,  		f1, 		f1,\
  		        f2,  		f2,  		f2,\
  		        f3,  		f3,  		f3,\
  		        f4,  		f4,  		f4,\
  		        f5,  		f5,  		f5,\
  		        f6,  		f6,  		f6,\
		        None,   	None,   	None]
    
rx_freq   =   [	None,   	None,   	None,\
		        f1,  		f1, 		f1,\
  		        f2,  		f2,  		f2,\
  		        f3,  		f3,  		f3,\
  		        f4,  		f4,  		f4,\
  		        f5,  		f5,  		f5,\
  		        f6,  		f6,  		f6]
        
           

# ip_usrp
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
ip_usrp = [ 	ip_usrp_src1,   	ip_usrp_src2,   	ip_usrp_src3,\
		ip_usrp_rly11,   	ip_usrp_rly21,  	ip_usrp_rly31,\
		ip_usrp_rly12,   	ip_usrp_rly22, 		ip_usrp_rly32,\
		ip_usrp_rly13,   	ip_usrp_rly23, 		ip_usrp_rly33,\
		ip_usrp_rly14,   	ip_usrp_rly24, 		ip_usrp_rly34,\
		ip_usrp_rly15,   	ip_usrp_rly25, 		ip_usrp_rly35,\
		ip_usrp_dst1,  		ip_usrp_dst2,  		ip_usrp_dst3]

					 
# ip_pc
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
ip_pc = [ip_pc_src1,         ip_pc_src2,   ip_pc_src3,\
		 ip_pc_rly11,         ip_pc_rly21,   ip_pc_rly31,\
		 ip_pc_rly12,         ip_pc_rly22,   ip_pc_rly32,\
		 ip_pc_rly13,         ip_pc_rly23,   ip_pc_rly33,\
		 ip_pc_rly14,         ip_pc_rly24,   ip_pc_rly34,\
		 ip_pc_rly15,         ip_pc_rly25,   ip_pc_rly35,\
		 ip_pc_dst1,         ip_pc_dst2,   ip_pc_dst3]    


# prev_hop_usrp
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
prev_hop_usrp = [None,             None,             None,\
				 ip_usrp_src1,     ip_usrp_src2,	 ip_usrp_src3,\
				 ip_usrp_rly11,     ip_usrp_rly21,  	 ip_usrp_rly31,\
				 ip_usrp_rly12,     ip_usrp_rly22,  	 ip_usrp_rly32,\
				 ip_usrp_rly13,     ip_usrp_rly23,  	 ip_usrp_rly33,\
				 ip_usrp_rly14,     ip_usrp_rly24,  	 ip_usrp_rly34,\
				ip_usrp_rly15,     ip_usrp_rly25,  	 ip_usrp_rly35]   


# prev_hop_pc
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
prev_hop_pc =  [None,               None,               None,\
	ip_pc_src1,         ip_pc_src2,  		ip_pc_src3,\
 ip_pc_rly11,         ip_pc_rly21, 		ip_pc_rly31,\
 ip_pc_rly12,         ip_pc_rly22, 		ip_pc_rly32,\
 ip_pc_rly13,         ip_pc_rly23, 		ip_pc_rly33,\
 ip_pc_rly14,         ip_pc_rly24, 		ip_pc_rly34,\
 ip_pc_rly15,         ip_pc_rly25, 		ip_pc_rly35]								
								
# next_hop_usrp
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
next_hop_usrp = [ip_usrp_rly11,   	ip_usrp_rly21, 	ip_usrp_rly31,\
		ip_usrp_rly12,   	ip_usrp_rly22, 	ip_usrp_rly32,\
		ip_usrp_rly13,   	ip_usrp_rly23, 	ip_usrp_rly33,\
		ip_usrp_rly14,   	ip_usrp_rly24, 	ip_usrp_rly34,\
		ip_usrp_rly15,   	ip_usrp_rly25, 	ip_usrp_rly35,\
				 ip_usrp_dst1,   	ip_usrp_dst2,   ip_usrp_dst3,\
				 None,              None,          		None]    

# next_hop_pc
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
next_hop_pc =  [ip_pc_rly11,          ip_pc_rly21, 		ip_pc_rly31,\
		ip_pc_rly12,          ip_pc_rly22, 		ip_pc_rly32,\
		ip_pc_rly13,          ip_pc_rly23, 		ip_pc_rly33,\
		ip_pc_rly14,          ip_pc_rly24, 		ip_pc_rly34,\
		ip_pc_rly15,          ip_pc_rly25, 		ip_pc_rly35,\
				ip_pc_dst1,          ip_pc_dst2,  		ip_pc_dst3,\
				None,                None,              None]                  

# source_usrp
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
source_usrp =  [None,             None,            None,\
				None,             None,            None,\
				None,             None,            None,\
				None,             None,            None,\
				None,             None,            None,\
				None,             None,            None,\
				ip_usrp_src1,     ip_usrp_src2,    ip_usrp_src3]    
								
# source_pc
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
source_pc   =  [None,             None,             None,\
				None,             None,             None,\
				None,             None,            None,\
				None,             None,            None,\
				None,             None,            None,\
				None,             None,            None,\
				ip_pc_src1,   ip_pc_src2,	  ip_pc_src3]  
								
# dest_usrp
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
dest_usrp =  [ip_usrp_dst1,          ip_usrp_dst2,     ip_usrp_dst3,\
			  None,                  None,             None,\
				None,             None,            None,\
				None,             None,            None,\
				None,             None,            None,\
			  None,                  None,             None,\
			  None,                  None,             None]    
								
# dest_pc
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
dest_pc   =  [ip_pc_dst1,   	    ip_pc_dst2,		   ip_pc_dst3,\
			  None,                 None,              None,\
				None,             None,            None,\
				None,             None,            None,\
				None,             None,            None,\
			  None,                  None,             None,\
			  None,                 None,              None]                  

# source usrp ip of sessions
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
source_usrp_session   =  [ip_usrp_src1,   	    ip_usrp_src2,	   ip_usrp_src3,\
						  ip_usrp_src1,         ip_usrp_src2,      ip_usrp_src3,\
						ip_usrp_src1,         ip_usrp_src2,      ip_usrp_src3,\
						ip_usrp_src1,         ip_usrp_src2,      ip_usrp_src3,\
						ip_usrp_src1,         ip_usrp_src2,      ip_usrp_src3,\
						ip_usrp_src1,         ip_usrp_src2,      ip_usrp_src3,\
						  ip_usrp_src1,   		ip_usrp_src2,      ip_usrp_src3]   			  




# number of frames at mac layer building one layer-4 packet
number_of_blocks = 1			# number of 255B blocks composing a l2 packet
number_of_frames = 2 		    # number of layer 2 frames in one layer 4 packet
l4_packets_to_send = 10000

ch_coding_rate = [0.14, 0.16, 0.18, 0.20, 0.22, 0.24, 0.20, 0.22, 0.24, 0.26, 0.28, 0.30] 


l2_size_block = 128									    # fixed, in Byte, maximum 4096/2 = 2048
l1_size = int(l2_size_block * (1 + ch_coding_rate[2]) -1	)	# variable, default half l2 packet
l2_size = l2_size_block*number_of_blocks
l4_size = l2_size*number_of_frames
l4_header_length = 42
l2_header_length = 28
chunk_size = l2_size - l2_header_length 


timeout_l2 = 0.3*number_of_blocks		        # time in second to wait for layer 2 ack
timeout_l4 = timeout_l2*number_of_frames*number_of_blocks*2*7	        # time in second to wait for layer 4 ack


# It has been observed that the transmission
# get stuck while keep retransmitting, and gets recovered after the
# retransmission limit is reached - this will waste a lot transmission time. 
l2_retransmission_threshold = 500

l4_retransmission_threshold = 20

#p[ont to point PER thresholds 
l2_th_PER_low = 0.05	
l2_th_PER_high = 0.1

total_bytes = l4_packets_to_send*number_of_frames*l2_size

# P2P throughput parameters
l2_th_coeff = 0.75


# window size for layer 2
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 
l2_window   =  [1,   					1, 						   1,\
				1,  					1,						   1,\
				1,  					1,						   1,\
				1,  					1,						   1,\
				1,  					1,						   1,\
				1,  					1,						   1,\
				1,   					1,						   1] 

# window size for layer 4
#       src1   			src2  			src3   	
#	rly11   		rly21   		rly31    
#	rly12   		rly22   		rly32  
#	rly13  			rly23   		rly33 
#	rly14   		rly24   		rly34 
#	rly15   		rly25   		rly35 
#	dst1    		dst2    		dst3 

# 12/13/17 LB: changing the sources window size implements sliding window transport layer protocol at sources
l4_window   =  [6,   					6, 						   6,\
				1,  					1,						   1,\
				1,  					1,						   1,\
				1,  					1,						   1,\
				1,  					1,						   1,\
				1,  					1,						   1,\
				1,   					1,						   1] 


# Move the following line to the beginning of this file
#l4_control_rate_flag 				= 1      			# 1: with control 0: no control
l4_maximum_rate 					= tspt_rate/8 	    # bps -> [Bps]
l4_maximum_packets_per_second 		= max(1,int(math.ceil(l4_maximum_rate/l4_size)))


# ip computer controlling usrp

pc_usrp_dic = {}
pc_usrp_dic[ip_usrp_src2] =  ip_pc_src2    	# session2
pc_usrp_dic[ip_usrp_dst2] =  ip_pc_dst2    
pc_usrp_dic[ip_usrp_rly21] =  ip_pc_rly21   
pc_usrp_dic[ip_usrp_rly22] =  ip_pc_rly22  
pc_usrp_dic[ip_usrp_rly23] =  ip_pc_rly23  
pc_usrp_dic[ip_usrp_rly24] =  ip_pc_rly24  
pc_usrp_dic[ip_usrp_rly25] =  ip_pc_rly25   

# June 12, 2016
# Revise pc_usrp_dic to accomodate sessions 1 and 3
pc_usrp_dic[ip_usrp_src1] =  ip_pc_src1		# Session 1		    
pc_usrp_dic[ip_usrp_dst1] =  ip_pc_dst1    
pc_usrp_dic[ip_usrp_rly11] =  ip_pc_rly11   
pc_usrp_dic[ip_usrp_rly12] =  ip_pc_rly12     
pc_usrp_dic[ip_usrp_rly13] =  ip_pc_rly13     
pc_usrp_dic[ip_usrp_rly14] =  ip_pc_rly14     
pc_usrp_dic[ip_usrp_rly15] =  ip_pc_rly15  

pc_usrp_dic[ip_usrp_src3] =  ip_pc_src3		# Session 3		    
pc_usrp_dic[ip_usrp_dst3] =  ip_pc_dst3    
pc_usrp_dic[ip_usrp_rly31] =  ip_pc_rly31 
pc_usrp_dic[ip_usrp_rly32] =  ip_pc_rly32 
pc_usrp_dic[ip_usrp_rly33] =  ip_pc_rly33 
pc_usrp_dic[ip_usrp_rly34] =  ip_pc_rly34 
pc_usrp_dic[ip_usrp_rly35] =  ip_pc_rly35 


# UDP port number                
#src 1 --> dst 1
#src 2 --> dst 2
#src 2 --> dst 3

udp_port_listen = [	9000,  	9001,	9002,\
					9003,  	9004,  	9005,\
					9005,	9007,  	9008,\
					9009,	9010,  	9011,\
					9012,	9013,  	9014,\
					9015,	9016,  	9017,\
					9019,	9020,  	9021,]

udp_port_send =   [	8000,  	8001,	8002,\
					8003,  	8004,  	8005,\
					8005,	8007,  	8008,\
					8009,	8010,  	8011,\
					8012,	8013,  	8014,\
					8015,	8016,  	8017,\
					8019,	8020,  	8021,]

# UDP listening ports associated to usrp


#		'src1', 	'src2', 	'src3',\
# 		'rly11',	'rly21', 	'rly31',\
#	 	'rly12', 	'rly22', 	'rly32',\
#	 	'rly13', 	'rly23', 	'rly33',\
#	 	'rly14', 	'rly24', 	'rly34',\
#	 	'rly15', 	'rly25', 	'rly35',\
#		'dst1', 	'dst2', 	'dst3'

port_usrp_dic = {}

port_usrp_dic[ip_usrp_src1] = udp_port_listen[0]	# Session 1
port_usrp_dic[ip_usrp_rly11] = udp_port_listen[3]
port_usrp_dic[ip_usrp_rly12] = udp_port_listen[6]
port_usrp_dic[ip_usrp_rly13] = udp_port_listen[9]
port_usrp_dic[ip_usrp_rly14] = udp_port_listen[12]
port_usrp_dic[ip_usrp_rly15] = udp_port_listen[15]
port_usrp_dic[ip_usrp_dst1] = udp_port_listen[18]


port_usrp_dic[ip_usrp_src2] = udp_port_listen[1]	# Session 2
port_usrp_dic[ip_usrp_rly21] = udp_port_listen[4]
port_usrp_dic[ip_usrp_rly22] = udp_port_listen[7]
port_usrp_dic[ip_usrp_rly23] = udp_port_listen[10]
port_usrp_dic[ip_usrp_rly24] = udp_port_listen[13]
port_usrp_dic[ip_usrp_rly25] = udp_port_listen[16]
port_usrp_dic[ip_usrp_dst2] = udp_port_listen[19]


port_usrp_dic[ip_usrp_src3] = udp_port_listen[2]	# Session 3
port_usrp_dic[ip_usrp_rly31] = udp_port_listen[5]
port_usrp_dic[ip_usrp_rly32] = udp_port_listen[8]
port_usrp_dic[ip_usrp_rly33] = udp_port_listen[11]
port_usrp_dic[ip_usrp_rly34] = udp_port_listen[14]
port_usrp_dic[ip_usrp_rly35] = udp_port_listen[17]
port_usrp_dic[ip_usrp_dst3] = udp_port_listen[20]


# dictionary of neighboring nodes. used in the periodic signalling function
# node swill send broadcast periodic updates to all the nodes in their neugboring set
# the function is to be implemented yet
 
neighbors_dic = {}

#session 1 : src has rly as neigbor, rly has src and dst, dst has rly as neigbor. the definition of neigbor can be changed 
neighbors_dic[ip_usrp_src1] = [ip_usrp_rly11]					
neighbors_dic[ip_usrp_dst1] = [ip_usrp_rly12]
neighbors_dic[ip_usrp_rly11] = [ip_usrp_src1,ip_usrp_rly12]
neighbors_dic[ip_usrp_rly12] = [ip_usrp_rly11,ip_usrp_rly13]
neighbors_dic[ip_usrp_rly13] = [ip_usrp_rly12,ip_usrp_rly14]
neighbors_dic[ip_usrp_rly14] = [ip_usrp_rly13,ip_usrp_rly15]
neighbors_dic[ip_usrp_rly15] = [ip_usrp_rly14,ip_usrp_dst1]

#session 2
neighbors_dic[ip_usrp_src2] = [ip_usrp_rly21]					
neighbors_dic[ip_usrp_dst2] = [ip_usrp_rly22]
neighbors_dic[ip_usrp_rly21] = [ip_usrp_src2,ip_usrp_rly22]
neighbors_dic[ip_usrp_rly22] = [ip_usrp_rly21,ip_usrp_rly23]
neighbors_dic[ip_usrp_rly23] = [ip_usrp_rly22,ip_usrp_rly24]
neighbors_dic[ip_usrp_rly24] = [ip_usrp_rly23,ip_usrp_rly25]
neighbors_dic[ip_usrp_rly25] = [ip_usrp_rly24,ip_usrp_dst2]

#session 3
neighbors_dic[ip_usrp_src3] = [ip_usrp_rly31]					
neighbors_dic[ip_usrp_dst3] = [ip_usrp_rly32]
neighbors_dic[ip_usrp_rly31] = [ip_usrp_src3,ip_usrp_rly32]
neighbors_dic[ip_usrp_rly32] = [ip_usrp_rly31,ip_usrp_rly33]
neighbors_dic[ip_usrp_rly33] = [ip_usrp_rly32,ip_usrp_rly34]
neighbors_dic[ip_usrp_rly34] = [ip_usrp_rly33,ip_usrp_rly35]
neighbors_dic[ip_usrp_rly35] = [ip_usrp_rly34,ip_usrp_dst3]

# Total number of received packets
n_tot = 0

# Time when node starts to run
time_start = time.time()
prev_time = time_start


# Record Throughput
thpt_history = []
time_idx = []

# Record power 
pwr_history = []
pwr_time_history = []

# Indication of whether Lagrangian has reached zero. 0: No; 1: Yes
# Updated in signaling.py
b_zero_lag = 0


# Link layer running average throughput, updated in lyr2 class, used in signaling module
# in lyr2 packet, multiply packet size to convert to bps
lnk_thpt = 0.001     # Initialized to small value rather than zero to avoid "divied by zero" error
n_pkt_cnt = 0        # Link layer packet counter, used in ly2 to count the received packets for throughput estimation

# Configure initial Lagrangane coefficent dynamically
if scheme != 6:
	ptcl_name.link_sngl_lbd = 0.01
	ptcl_name.Lag_step = 0.0005
	
	
# para_pnl needs to be reset to zero if having not been updated for a while 
pre_para_pnl_updt_time = -1		# Initialized to -1 	