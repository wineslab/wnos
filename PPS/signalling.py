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


# signalling exchange module

# Configure directory
import os, sys
p = os.getcwd()										  # Current directory
p = os.path.dirname(p)      						  # Parent directory

sys.path.insert(0, p+'/WNOSPYv2/wos-protocol')          # Directory of protocotols
sys.path.insert(0, p+'/WNOSPYv2/wos-alglib')	        # Directory of algorithms
sys.path.insert(0, p+'/wnospyv2/wos-protocol')          # Directory of protocotols
sys.path.insert(0, p+'/wnospyv2/wos-alglib')	        # Directory of algorithms


import ptcl_func, ptcl_name
import alglib_tsptlbd

import netcfg, socket, struct,time

# Symbolic computing
from sympy import *
from mpmath import *

import math

# Power and rate control
import alglib_physol, alglib_tsptsol

# For penalization 
import alglib_phypnl

#################################################################
# signaling format
# -------------------------------------------
#|  signalling code |  node id  |   value    |
#|     (1 byte)     |  (1 byte) |  (float)   |
# -------------------------------------------
#################################################################

# signalling code, one byte
TX_GAIN = 0
SIR     = 1


def start_listening_socket(self):
	self.UDP_IP_LISTEN = self.ip_pc
	self.UDP_PORT_LISTEN = self.udp_port_listen
	print "@@@ trying to open a udop socket at ",self.UDP_IP_LISTEN,self.UDP_PORT_LISTEN

	self.sock_listen = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP

	self.sock_listen.bind((self.UDP_IP_LISTEN, self.UDP_PORT_LISTEN))

	self.l4.initialize_received_l4_feedback()

	#print 'LISTEN SCKT started at ', self.UDP_IP_LISTEN,' ',self.UDP_PORT_LISTEN
	while True:
		#print 'LISTEN UDP started cyple'
   		packet, addr = self.sock_listen.recvfrom(1024) # buffer size is 1024 bytes
 	   	#print "SOCKET LISTEN rcv"

 	   	(cc_code,) = struct.unpack('h', packet[0:2]) 
 	   	packet = packet[2:]	# removing signalling code from the received packet
 	   	if cc_code == 2 :	# layer 2 ack
 	   		#print "SOCKET rcv: L2"
 	   		self.l2.received_l2_feedback(packet)
 	   	elif cc_code == 4:	#layer 4 ack
 	   		#print "SOCKET rcv: L4" 	   		
   			self.l4.received_l4_feedback(packet)
 	   	elif cc_code == -1:	# layer 2 codig rate singalling message ack
 	   		#print "SOCKET rcv: CC ACK"
 	   		self.l2.received_cc_ack() 	
 	   	elif cc_code == -2:	# layer 2 coding rate signalling message
 	   		#print "SOCKET rcv: CC MESS"
 	   		self.l2.handle_update_rate_exception(packet)
 	   	elif cc_code == -3:	# general signaling message
 	   		#print "SOCKET rcv: SIGNALLING"
 	   		parse_sgl(self,packet)

 	   	# implement coding 2 l2 ack, 4 l4 ack -1 control
 	   	#pass it to layer functions or set globals!


# toy function to spread signalling upadates

def periodic_update_neighbors(self):
	value1 = 1000 
	value2 = 2000 

	# Counter to control updating frequency of physical and transport layers
	
	n_updt = 0
	n_prd  = 1			# Update transport layer once, physical layer N times
	
	while True:
		n_updt += 1
		
		time.sleep(3)
		
		# Penalization needs to be reset if having not been udpated for a while (10 second here)
		cur_time = time.time()
		if netcfg.pre_para_pnl_updt_time == -1:	# Have not received any penalization, no need to reset
			pass
		else:
			if cur_time - netcfg.pre_para_pnl_updt_time >= 15:
				ptcl_name.para_pnl = [0]
				
		
		#############################################################
		# Update Lagrangian coefficients; not needed for destinations
		if netcfg.nd_type[netcfg.idx_thisnode] != 'rx' and n_updt % n_prd == 0:	
			# Commented for debugging, should be uncommented
			# pass  
			if netcfg.b_Lag_ctl == 'on':
				updt_Lag()	
			else:
				pass

		#############################################################
		# Update transmit gain
		if netcfg.nd_type[netcfg.idx_thisnode] != 'rx':	
			updt_pwr()		

		#############################################################
		# Update transport layer transmission rate, only for source            
		if netcfg.nd_type[netcfg.idx_thisnode] == 'tx':	        
			#print '*****************************************'       
			#print '*****************************************'       
			#print '*****************************************'                   
			updt_tsptrate()				
		
		#############################################################
		# Update locally measured interference
		b_updt = ptcl_func.updt_lnkitf()
		
		#############################################################
		# Send measrued link interference to previous hop node, i.e., the 
		# corresponding transmitter
		#
		# True means information has been udpated, False not updated and no need to send
		if b_updt == True: 
			dst_addr = [netcfg.prev_hop_usrp[netcfg.idx_thisnode]]      		# The outer [] to make a list
			msg_code = ptcl_name.code_lkitf_rcvr
			msg_val = ptcl_name.lkitf_rcvr_side
			broadcast_sgl(self, self.ip_usrp, dst_addr, msg_code, msg_val)	
			# print('************************')
			# print(ptcl_name.lkitf_rcvr_side)
			# print('Itf Sent!')
				
		#############################################################
		# Send transmit power to all other nodes
		#
		# Destination nodes don't need to broadcast power message
		if netcfg.nd_type[netcfg.idx_thisnode] != 'rx':			
			dst_addr = list(netcfg.all_usrp_ip)    # Copy list		

			# No need to send message to itself	
			if self.ip_usrp in dst_addr:
				dst_addr.remove(self.ip_usrp)
			
			
			
			msg_code = ptcl_name.code_tsmt_gain
			msg_val = netcfg.tx_gain_allnode[netcfg.idx_thisnode]	

			#print 'Power Sent:', msg_val
            
			broadcast_sgl(self, self.ip_usrp, dst_addr, msg_code, msg_val)			

		#############################################################
		# Send Lagrangian coefficients to the source node of the session
		#
		# Destination doesn't send this message, since the message is updated at each transmitter (source, relay)		
		if netcfg.nd_type[netcfg.idx_thisnode] != 'rx':	
			dst_addr = [netcfg.source_usrp_session[netcfg.idx_thisnode]]
			msg_code = ptcl_name.code_Lagrangian
			msg_val = ptcl_name.link_sngl_lbd		
			broadcast_sgl(self, self.ip_usrp, dst_addr, msg_code, msg_val)	

		#############################################################
		# Send parameters for updating Lagrangian coefficients, from each source node to all the senders 
		# along the path of the session. 
		
		# Only source node needs to send
		if netcfg.nd_type[netcfg.idx_thisnode] == 'tx':	
			dst_addr = netcfg.usrp_ip_sender_of_session[self.ip_usrp]
			msg_code = ptcl_name.code_ssrate
			
			# Prepare message value
			# Loop over all keyword in the signaling expression, replace the keyword with the recorded value
			msg_expr = alglib_tsptlbd.lbd_signaling					# Message expression
			for kw in alglib_tsptlbd.keyword:
				kw_value = ptcl_name.keyword[kw]
				msg_expr = msg_expr.replace(kw, str(kw_value))
						
			msg_val = float(msg_expr)
			
			# print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
			# print(msg_val)
					
			# Send the message
			broadcast_sgl(self, self.ip_usrp, dst_addr, msg_code, msg_val)	
			
		#############################################################
		# Penalization parameters
		
		# Only transmitters (source and relay) need to send
		if netcfg.nd_type[netcfg.idx_thisnode] != 'rx':			
			msg_code = ptcl_name.code_pnl
			
			# Determine index of the receiver of this node
			idx_rcvr = netcfg.chn_idx_thisnode[netcfg.idx_thisnode]				
			
			# Loop over all interfereing nodes, prepare a message for each of them
			# and send the message 
			
			# First, take the interfereing relationship vector for the receiver of this node 
			itf_rla_vec = netcfg.itf_relation[idx_rcvr, :]
			
			# Number of possible nodes, including interfering and non-interfering
			NUM = itf_rla_vec.size
			
			# Loop over all nodes
			for n in range(NUM):
				#print('XXX', itf_rla_vec.item((0, n)))			
			
				# if the node is not interfering, skip, otherwise prepare message and send
				if  itf_rla_vec.item((0, n)) == 0:
					continue
				else:					
					# Destination address
					dst_addr = [netcfg.all_usrp_ip[n]]
					
					# Prepare message value, initialize
					msg_val = 0      				# Dummy value
					
					# Take the expression, which is a string generated automatically by WNOS					
					msg_expr = alglib_phypnl.pnl
			
					# Loop over all keywords, replace each string keyword using the corresponding value
					for kw in alglib_phypnl.keyword:
						if 'lkpwr' in kw:    	# Use transmit gain for power
							kw_value = netcfg.tx_gain_allnode[netcfg.idx_thisnode]
							msg_expr = msg_expr.replace(kw, '(' + str(kw_value) + ')')
							
						elif 'chngain' in kw:   # Recorded in netcfg
							#kw_value = netcfg.chn_gain.item((netcfg.idx_thisnode, n))
													
							# Chngain should be the channel gain from the corresponding receiver to interfereing						
							kw_value = netcfg.chn_gain.item((idx_rcvr, n))
							
							msg_expr = msg_expr.replace(kw, '(' + str(kw_value) + ')')
						
						# Now we are calculating the penalization at the transmitter side, the lkitf00 is received
						# from the receiver side, so lkitf00 can be used directly
						# elif 'itf' in kw: 		# Interference, use receiver side value
							# kw_value = ptcl_name.lkitf_rcvr_side
							# msg_expr = msg_expr.replace(kw, '(' + str(kw_value) + ')')
							
						else:					# Take from ptcl_name
							kw_value = getattr(ptcl_name, kw)
							msg_expr = msg_expr.replace(kw, '(' + str(kw_value) + ')')
							
					
					msg_val = sympify(msg_expr).evalf()			
					broadcast_sgl(self, self.ip_usrp, dst_addr, msg_code, msg_val)			
		
													
		
def start_sending_socket(self):

	self.UDP_IP_SEND = self.ip_usrp
	self.UDP_PORT_SEND = self.udp_port_send

	self.sock_send = socket.socket(socket.AF_INET, 	# Internet
                     socket.SOCK_DGRAM) 			# UDP


def initialize_matrix(self):
	self.signalling_dic = {}
	for i in netcfg.ip_usrp:
		self.signalling_dic[i] = {}

	
def broadcast_sgl(self, idx_thisnode, rcvr_ip_list, para_code, para_val):
	'''
	func: broad signalling to all related nodes
	
	idx_thisnode: idx of transmitter node
	rcvr_ip_list: ip list of receivers to whom the message should be sent
	para_code: ID of parameters to be sent
	para_val: value of parameter to be sent
	'''
	
	# print('Debug:')
	# print(rcvr_ip_list)
	
	for i in rcvr_ip_list:
		###########################################################
		# prepare payload message
		###########################################################
		message =  struct.pack('h', -3) + str(self.ip_usrp) + str(i) + struct.pack('h', para_code) + struct.pack('f', para_val)
			
		
		###########################################################
		# send the message to all receivers one by one
		###########################################################

		#*********# FIND THE IP/PORT PC BASED ON THE IP USRP!
		ip = netcfg.pc_usrp_dic[i]
		port = netcfg.port_usrp_dic[i]
		self.sock_send.sendto(message, (ip, port))
		#print '+++ SGN node ',self.ip_usrp, 'sent update to ',i,'at ip ',ip, port, para_code,para_val
		#*********#		
	
def parse_sgl(self,sgl_msg):
	'''
	func: pasre a received signalling message and set related parameters 
	
	sgl_msg: the received signalling message (see above for signalling format)
	'''
	###########################################################
	# get signaling code and value 
	###########################################################
	#print '+++ received a signaling message'
	source_ip_sgl = sgl_msg[0:13]
	dst_ip_sgl = sgl_msg[13:26]
	(para_code,) = struct.unpack('h',sgl_msg[26:28])
	(para_value,) = struct.unpack('f',sgl_msg[28:32])

	#print '+++ received ',source_ip_sgl, ' ',dst_ip_sgl,' ',para_code,' ',para_value

	#self.signalling_dic[self.ip_usrp][para_code] = para_value
			
	##############################################################
	# Message contains interference information from next-hop receiver
	if para_code == ptcl_name.code_lkitf_rcvr:
		ptcl_name.lkitf00 = para_value				# Record the receiver-measured interference as link interference
		
		# print('*****************************')
		# print('lkitf00:', ptcl_name.lkitf00)
	
	##############################################################
	# Message of tranmsit power of other node
	if para_code == ptcl_name.code_tsmt_gain:
		
		# Index of the node who sends the message
		idx_sender = netcfg.usrp_ip_2_ndidx[source_ip_sgl]
		
		# Record the transmit power for sender node
		netcfg.tx_gain_allnode[idx_sender] = para_value
		
		#print('********************************')
		#print 'Power Received:', para_value
				
	##############################################################
	# Lagrangian coefficients received from links belong to the path of the session
	if para_code == ptcl_name.code_Lagrangian:
		ptcl_name.sess_links_lbd_dict[source_ip_sgl] = para_value
	
		#print('*******************************')
		#print(ptcl_name.sess_links_lbd_dict)
		
		# Update sess_links_lbd based on the updated sess_links_lbd_dict
		ptcl_name.sess_links_lbd = [value for key, value in ptcl_name.sess_links_lbd_dict.items()]
		
		#print(ptcl_name.sess_links_lbd)
		
	##############################################################
	# Parameters for udpating Lagrangian coefficients		
	if para_code == ptcl_name.code_ssrate:
		ptcl_name.para_updt_Lag_dict[source_ip_sgl] = para_value
		ptcl_name.para_updt_Lag = [value for key, value in ptcl_name.para_updt_Lag_dict.items()]
			
	##############################################################
	# Parameters for penalization
	if para_code == ptcl_name.code_pnl:
		ptcl_name.para_pnl_dict[source_ip_sgl] = para_value
		ptcl_name.para_pnl = [value for key, value in ptcl_name.para_pnl_dict.items()]
		print('****:', ptcl_name.para_pnl_dict)
		
		# Record penalization updating time
		netcfg.pre_para_pnl_updt_time = time.time()
		
def updt_Lag():
	'''
	Update Lagrangian coefficient, see the following paper for theory.
	"A Tutorial on Decomposition Methods for Network Utility Maximization"
	IEEE JSAC, vol. 24, no. 8, August 2006
	
	Called By: signalling.periodic_update_neighbors()
	'''
	
	# pass
	
	# Step size
	step_size = ptcl_name.Lag_step
		
	# Parameters received from all sources using this link
	Lag_from_src = ptcl_name.para_updt_Lag
	
	# Calculate link capacity 
	#
	# First, calculate SINR
	sgl_pwr = netcfg.tx_gain_allnode[netcfg.idx_thisnode] * ptcl_name.lkgain00 		# Useful signaling
	itf = ptcl_name.lkitf00;														# Interference 	
	noise = ptcl_name.lknoise00; 													# Noise
	SINR = sgl_pwr / (itf + noise)													# SINR
	
	# Use Transmit rate to approximate the bandwidth
	bandwidth = netcfg.narrow_rate
	
	# Calculate capacity
	link_cap = bandwidth * math.log(1 + SINR, 2)
	
	#print '### Cap:', link_cap
	
	# Update Lagrangian coefficients
	# Lag_from_src is defined as negative session rate IN Kbps...
	# So, here 1000 should be multiplied
    
	# Approximate link_cap using the measrued link layer throughput,
	# which is availbe in netcfg.lnk_thpt (in lyr2 packet, needs to convert to bps)
    
	#print ptcl_name.link_sngl_lbd	
	if netcfg.scheme == 6:  # power minimization 
		link_cap = netcfg.lnk_thpt * netcfg.l2_size_block * 8   # throught in lyr2 packet * packet size * 8 bits per Byte    
		
	new_Lag = ptcl_name.link_sngl_lbd - step_size/link_cap * (link_cap + sum(Lag_from_src)*1000)
        
	#/*
	print '3333333333333' 
	print link_cap, sum(Lag_from_src)*1000, new_Lag
	# print 'itf, noise:', itf, noise
	# print ptcl_name.link_sngl_lbd, step_size, link_cap, Lag_from_src
	# print new_Lag    
	# print ptcl_name.Lag_step
	#*/
    
	ptcl_name.link_sngl_lbd = max(new_Lag, 0)

	# Dec. 13, 2017
	# Indicate zero Lagrangian coefficients have been reached    
	if ptcl_name.link_sngl_lbd == 0:
		netcfg.b_zero_lag = 1
    
	# After Lagrangian coefficients get zero, it means there is no need to update transmit rate any more,
	# but the physical layer power control still needs to continue. To enable this, the Lagrangian coefficients are set to 1e-5
	# for all nodes, but these coefficients are used only for power control at the physical layer. 
	# 
	# This is controlled using a variable b_zero_lag defined in netcfg        	
	if netcfg.b_zero_lag == 1:
		ptcl_name.link_sngl_lbd = 1e-7
		new_Lag = ptcl_name.link_sngl_lbd        
        	
	#print('111:', ptcl_name.link_sngl_lbd)
	#print('222:', new_Lag)	
	
	# print('******')
	# # print('sgl:', sgl_pwr)
	# # print('itf:', itf + noise)
	# print('Capacity:', link_cap)
	# print('Lag:', Lag_from_src)
	# print('New_lbd:', ptcl_name.link_sngl_lbd)
	

def updt_pwr():
	'''
	Update transmit power (which is transmit gain for USRP) by solving the optimization problem
	automated generated in alglib_physol.py.

	Called By: signalling.periodic_update_neighbors()
	'''
	
	optval = alglib_physol.wnos_optimize()	
	
	# Update transmit gain by applying step size
	old_gain_dB = netcfg.tx_gain_allnode[netcfg.idx_thisnode]
	old_gain = 10 ** (old_gain_dB / 10)			# dB -> absolute
    
	# Setting new to power to the optimal solution directly		
	if optval.success == True: 
		if netcfg.scheme == 6:   				# Only for power minimization
			new_gain = optval.x[0]
		else: 
			new_gain = old_gain + ptcl_name.gamma * (optval.x[0] - old_gain)     # For other control schemes
	else:
		new_gain = old_gain    					# Do not update power
	
	print('1111', optval.x[0], optval.success, optval.message)
	
	new_gain_dB = 10 * math.log10(new_gain)   # absolute -> dB
    
	# Record power history
	cur_time = time.time()
	run_time = cur_time - netcfg.time_start   # Ellisped time in second    
    
	netcfg.pwr_history.append(new_gain_dB)
	netcfg.pwr_time_history.append(run_time)
    	
	# Update transmit gain of USRP
	if new_gain_dB != netcfg.tx_gain_allnode[netcfg.idx_thisnode]:
		if netcfg.b_pwr_ctl == 'ON' or netcfg.b_pwr_ctl == 'on':
			new_gain_dB = netcfg.thisnode.set_gain(new_gain_dB) 					            # Set usrp gain
			netcfg.tx_gain_allnode[netcfg.idx_thisnode]	= new_gain_dB  							# Update configuration
			ptcl_name.lkpwr00 = new_gain
			#print('Tx gain set to:', new_gain_dB, new_gain)
		else:
			pass
			# UNCOMMENT print('Power Control OFF!')
		
	# Update step size
	ptcl_name.phy_idx = ptcl_name.phy_idx + 1
    
	if netcfg.scheme != 7:			# 7 does not exist, so applies to all schemes; updating step should be adapted automatically; For power minimization, no need to update this parameter
		ptcl_name.gamma = ptcl_name.gamma * (1 - ptcl_name.epsilon * ptcl_name.gamma)
	
def updt_tsptrate():
	'''
	Update transport layer transmission rate 
	
	Called By: signaling.periodic_update_neighbors()
	'''
	
	# Update iteration parameters
	ptcl_name.gamma_tspt = ptcl_name.gamma_tspt * (1 - ptcl_name.epsilon_tspt * ptcl_name.gamma_tspt)
	
	
	optval = alglib_tsptsol.wnos_optimize()

	
	# Update for new rate
	new_rate = ptcl_name.tspt_rate + ptcl_name.gamma_tspt * (optval.x[0] - ptcl_name.tspt_rate)
	
	# If rate control is off, ptcl_name should stay at the rate specified in netcfg   
	if netcfg.b_rate_ctl == 'on':    	
		# Record new transmission rate
		ptcl_name.tspt_rate = new_rate
		ptcl_name.keyword['ssrate00'] = new_rate
	else:
		# Stay at the rate specified in netcfg    
		ptcl_name.tspt_rate = netcfg.tspt_rate/1000
		ptcl_name.keyword['ssrate00'] = netcfg.tspt_rate/1000        
	
	# Update transport layer transmission rate
	if netcfg.b_rate_ctl == 'on':
		netcfg.l4_maximum_rate = new_rate * 1000 / 8 		# Kbps -> Bps
		netcfg.l4_maximum_packets_per_second = max(1,math.ceil(netcfg.l4_maximum_rate/netcfg.l4_size))
	
