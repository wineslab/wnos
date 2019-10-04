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

# ////////////////////////////////////////////////////////////////////////////////////
#			LAYER 2
# ////////////////////////////////////////////////////////////////////////////////////		
							

from ntwklyr import network_layer
from netlib import my_top_block_tx, my_top_block_rx, MyThread
import threading  
from threading import Thread
import socket, time, struct, sys

from gnuradio import digital

import netcfg, chncod, csi, signalling

import benchmark_rx_narrow, benchmark_tx_narrow
							

# define a thread used for signaling
ack_l2_received = threading.Event()
ack_l2_received_control = threading.Event()


class layer_2(network_layer):
	#defines pass_down
	#defines pass_up

	# The initialization set the previous and next hop at layer 2 (we are supposing only one previous and next)
	# the initialization opens a client tcp socket (previous_hop_socket), starts the listening_ack_l2_thread thread
	#	which executes and start the listening_ack_l2 functions.
	# 
	# pass_up defines the l2 functionality for passing a packet to upper layers.
	#	it gets packet from up_queue until number_of_mac_frames is get. it unpacks each of them and build them together sequentially
	#	(this supposes packets are queued sequentially at mac level - true). it returns the built packet,1 (send up flag)
	#	every time that gets a packet, it sends on 	previous_hop_socket an ack (feedback_mac).
	#	
	# pass_down receives the down_packet from down_function, it is in charge to send it until received.
	#	the reception is signaled by ack_l2_received signal set.
	#
	#	listening_ack_l2 function opens a socket that listens and received mac_ack_packets. check whether the received one is for
	#		self.waiting_ack_mac_pktno. in that case sets ack_l2_received



	def __init__(self,number_of_frames,
				ip_address_pc,ip_address_usrp,
				role, #tx / rx / relay
				layer_2_prev_hop_ip_pc='',layer_2_next_hop_ip_pc='',
				layer_2_prev_hop_ip_usrp='',layer_2_next_hop_ip_uspr='',
				tx_options='',rx_options='',
				window = 1,
				sock_send = '',
				udp_port = ''
				):
		
		network_layer.__init__(self, "layer_2")

		self.number_of_frames = number_of_frames #number of l2 packet that compose an upper layer packet
		self.tx_options = tx_options
		self.rx_options = rx_options		

		self.ip_address_pc = ip_address_pc
		self.ip_address_usrp = ip_address_usrp		
		self.role = role
						
		self.layer_2_prev_hop_ip_pc = layer_2_prev_hop_ip_pc		
		self.layer_2_prev_hop_ip_usrp = layer_2_prev_hop_ip_usrp
				
		self.layer_2_next_hop_ip_pc = layer_2_next_hop_ip_pc
		self.layer_2_next_hop_ip_uspr = layer_2_next_hop_ip_uspr	
		
		self.buffer_size = 1024  # Normally 1024, but we want fast response
		self.packet_size = netcfg.l2_size 
		self.block_size = netcfg.l2_size_block 

		# ack sending socket ONLY IF THE NODE RECEIVES
		if self.role == 'rx' or self.role =='relay':
			self.send_previous_hop_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		
		# transmission block ONLY IF THE NODE TRANSMITS
		if self.role == 'tx' or self.role =='relay':
			print 'txopron size ',self.packet_size
			
			if netcfg.phy == 'NARROWBAND':
				mods = digital.modulation_utils.type_1_mods()
				self.l1_transmission_block = benchmark_tx_narrow.my_top_block(mods[self.tx_options.modulation], self.tx_options)
			elif netcfg.phy == 'OFDM':
				self.l1_transmission_block = my_top_block_tx(self.tx_options) 		
			
			
			self.l1_transmission_block.start()

		self.window = window
		self.sock_send = sock_send
		self.UDP_PORT  = udp_port	
		


		#  array of corders one per frequency 
		self.ch_coding_rate = {}

		if self.role == 'tx': 
			self.ch_coding_rate[self.tx_options.tx_freq] = netcfg.ch_coding_rate[2]		
		elif self.role == 'relay':
			self.ch_coding_rate[self.tx_options.tx_freq] = netcfg.ch_coding_rate[2]
			self.ch_coding_rate[self.rx_options.rx_freq] = netcfg.ch_coding_rate[2]
		elif self.role == 'rx':	
			self.ch_coding_rate[self.rx_options.rx_freq] = netcfg.ch_coding_rate[2]




		#  array of corders one per frequency 
		self.coder = {} 

		if self.role == 'tx': 
			self.coder[self.tx_options.tx_freq] = chncod.initialize_RSCoder(self.ch_coding_rate[self.tx_options.tx_freq])		
		elif self.role == 'relay':
			self.coder[self.tx_options.tx_freq] = chncod.initialize_RSCoder(self.ch_coding_rate[self.tx_options.tx_freq])	
			self.coder[self.rx_options.rx_freq] = chncod.initialize_RSCoder(self.ch_coding_rate[self.rx_options.rx_freq])	
		elif self.role == 'rx':	
			self.coder[self.rx_options.rx_freq] = chncod.initialize_RSCoder(self.ch_coding_rate[self.rx_options.rx_freq])	


		self.transmitted_packets 				= 1
		self.successfully_transmitted_packets 	= 1
		
		self.last = time.time()
		self.A = 0	


	def send_l2_feedback(self,packet,number,ip,port):
		packet = struct.pack('h', 2) + packet
		try:
			self.sock_send.sendto(packet, (ip, port))
			#print 'UDP SENT L2 ACK ', number ,'at ', ip, ' PORT',port 
		except socket.error, exc:
			#print 'unable to send feedback'
			pass		

	def send_cc_message(self,packet,number,ip,port):
		packet = struct.pack('h', -2) + packet
		try:
			self.sock_send.sendto(packet, (ip, port))
			#print 'UDP SENT cc MSG ', number ,'at ', ip, ' PORT',port 
		except socket.error, exc:
			#print 'unable to send feedback'
			pass	
			

	def send_cc_feedback(self,packet,number,ip,port):
		packet = struct.pack('h', -1) + packet
		try:
			self.sock_send.sendto(packet, (ip, port))
			#print 'UDP  SENT cc ACK ', number ,'at ', ip, ' PORT',port 
		except socket.error, exc:
			#print 'unable to send feedback'
			pass	

	def received_cc_ack(self):
		#print 'L2 CONTROL ACK '
		globals()["ack_l2_received_control"].set() 	


	def received_l2_feedback(self,mac_ack):		

			(mac_ack_pktno,) = struct.unpack('h', mac_ack[0:2])
			mac_source_ip =   mac_ack[2:15]	#13			
			#print  'received ack ', mac_ack_pktno
			if mac_ack_pktno == self.waiting_ack_mac_pktno and mac_source_ip == self.ip_address_usrp: 
				#print 'L2 ack correct for ', mac_ack_pktno
				globals()["ack_l2_received"].set() 
			elif mac_ack_pktno == -1 :
				#print 'L2 CONTROL ACK '
				globals()["ack_l2_received_control"].set() 		


	def check_PER(self):
		#print 'PER check', 
		return 1 - float(self.successfully_transmitted_packets) /self.transmitted_packets 
		

	def check_change_rate_needed(self):
		#default no increse needed
		outcome = False
		new_rate = netcfg.ch_coding_rate[0]
		index = netcfg.ch_coding_rate.index(self.ch_coding_rate[self.tx_options.tx_freq]) # index of the channel coding rate e.g. 0 1 2 3 4  

		# check PER value
		PER = self.check_PER()
		#print 'received PER ', PER
		
		
		#check positioning between threshold
		if PER > netcfg.l2_th_PER_high:
			#print '------- above higher th'			
			#increase the rate by one step
			new_index = min(netcfg.ch_coding_rate.index(self.ch_coding_rate[self.tx_options.tx_freq]) + 1 , len(netcfg.ch_coding_rate)-1)
			#print 'previous index ', index, '------- new index = ',new_index	
			if new_index != index:
				new_rate = netcfg.ch_coding_rate[new_index]
				outcome = True
		
		elif PER < netcfg.l2_th_PER_low:
			#print '------- below lower th'
			#decrease the rate by 1 step
			new_index = max(netcfg.ch_coding_rate.index(self.ch_coding_rate[self.tx_options.tx_freq]) - 1 , 0)
			#print 'previous index ', index, '------- new index = ',new_index	
			if new_index != index:
				new_rate = netcfg.ch_coding_rate[new_index]
				outcome = True

		else: 
			#print '------- in between thresholds'
			outcome = False

		return outcome,new_rate				
		'''
		#### toy example of changing the channel coding rate
		if (pktno_mac % 5 == 0) and self.role == 'tx':
			#print 'CURRENT coding RATE ', self.ch_coding_rate[self.tx_options.tx_freq]
			#print 'current index ', netcfg.ch_coding_rate.index(self.ch_coding_rate[self.tx_options.tx_freq]) 

			new_rate = netcfg.ch_coding_rate[( netcfg.ch_coding_rate.index(self.ch_coding_rate[self.tx_options.tx_freq])  + 1) % 5]
			#print 'new rate ',new_rate
			self.coding_update(new_rate,1) #quite fast
			print 'set rate to ',new_rate
		####
		'''

		'''
		#### toy example of changing the channel coding rate

		
		if (pktno_mac % 8 == 0) and self.role == 'relay':
			new_rate = netcfg.ch_coding_rate [(netcfg.ch_coding_rate.index[self.ch_coding_rate[self.tx_options.tx_freq]] + 1) % 5]
			self.coding_update(new_rate,1) #quite fast
			print 'set rate to ',new_rate
		'''


		'''
		# adjusting rate based on act_rt
		for rate in netcfg.ch_coding_rate:
			

			if act_rt > netcfg.l2_retransmission_threshold * float(index)/len(netcfg.ch_coding_rate) and self.ch_coding_rate[self.tx_options.tx_freq] < rate:   # increase and break
				new_rate = rate
				outcome = True	
				break;	
		'''						
		

	def check_decrease_rate_needed(self,act_rt):
		#default no decrese needed				
		outcome = False
		new_rate = 	self.ch_coding_rate[self.tx_options.tx_freq]
		index = netcfg.ch_coding_rate.index(self.ch_coding_rate[self.tx_options.tx_freq])
		# index of the channel coding rate e.g. 0 1 2 3 4  

		'''
		# adjusting rate based on act_rt
		for rate in netcfg.ch_coding_rate:
			
			if act_rt < netcfg.l2_retransmission_threshold * float(index)/len(netcfg.ch_coding_rate) and self.ch_coding_rate[self.tx_options.tx_freq] > rate:# decrease and break
					new_rate = rate
					outcome = True	
					break;	
		'''							
		return outcome,new_rate	



	def rx_callback(self,ok, received_pkt):		
		(pktno_mac,) = struct.unpack('!H', received_pkt[0:2])
		#alpha 'L2 received'
	
		success = 0
		# here separate channel coding from information data
		(corrected_packet,success) = chncod.deduct_chncod(self.coder[self.rx_options.rx_freq], received_pkt, self.ch_coding_rate[self.rx_options.rx_freq])
		
		#success = ok
		#corrected_packet = received_pkt
		
		if success == 1:
			#put it in the up_queue
			self.up_queue.put(corrected_packet,True)
			#print 'R'
		else:
			print 'WRONG rassembling'	
			pass
					
			
	def start_l1_receiving_block(self):
		
		if netcfg.phy == 'NARROWBAND':			# narrow band
			demods = digital.modulation_utils.type_1_demods()
			self.l1_receiving_block = benchmark_rx_narrow.my_top_block(demods[self.rx_options.modulation], self.rx_callback, self.rx_options)
		elif netcfg.phy == 'OFDM':					# OFDM
			self.l1_receiving_block = my_top_block_rx(self.rx_callback, self.rx_options)
		
		# Update reference to this receiver block in netcfg
		netcfg.obj_rcvr_blk = self.l1_receiving_block
		
		self.l1_receiving_block.start()
		
		##############################################################
		# update SIR
		# for transmitter, do nothing
		##############################################################
		self.l1_receiving_block.wait()


	def send_pkt(self,payload='', eof=False):
	
		#######################################################
		#          add channel coding to payload
		#######################################################
	
		#print type(payload)
		# add channel coding
		payload_chncod = chncod.add_chncod(self.coder[self.tx_options.tx_freq], payload, self.ch_coding_rate[self.tx_options.tx_freq])
		
		#payload_chncod = payload

		#print 'L1 - send packet'
		return self.l1_transmission_block.txpath.send_pkt(payload_chncod, eof)	

		
	def pass_up(self):
		up_packet = ''
		pktno_mac_old = 0
		#pktno_mac = 0
		packet_beginning_flag = 0
		#print 'NUMBER OF FRAMES' ,self.number_of_frames
		#be careful here. i want to pop packets until the last mac number: assuming none is lost and they are sequential
		
		while True:
			#print 'L2  - WAITING TO POP '
			mac_packet = self.up_queue.get(True)
			if len(mac_packet) <> 128:
				print 'L2 ',len(mac_packet), 'must be 128'
				continue

			#print 'L2 - POPPED PACKET ~ FLAG = ',packet_beginning_flag
			'''
			try:
				(pktno_mac,) = struct.unpack('h', mac_packet[0:2])			
			except:
				print '!?! L2 pktno_mac ERROR - continue'
				continue
			'''
			(pktno_mac,) = struct.unpack('h', mac_packet[0:2])	
			pkto_mac_dest =  mac_packet

			
			mac_destination_ip =   mac_packet[15:28] #13
			mac_source_ip =   mac_packet[2:15]	 #13
			#print 'L2 FIELDS pktno_mac ',pktno_mac,'mac_source_ip ',mac_source_ip,'mac_destination_ip ',mac_destination_ip, 'my ip ',self.ip_address_usrp 

			
			#  if the l2 packet is for me
			if mac_packet[15:28] == self.ip_address_usrp : #13

				#print 'L2 estracted ',pktno_mac

				# FRAME 0 OF A NEW PACKET
				if pktno_mac == 1 and packet_beginning_flag == 0 :
					#print 'beginning of a packet'
					packet_beginning_flag = 1

					feedback_mac = mac_packet[0:28]		 #13
					
					mac_destination_ip =   mac_packet[15:28] #13
					mac_source_ip =   mac_packet[2:15]	 #13		
					
					pktno_mac_old = pktno_mac
					#print 'L2 FIELDS pktno_mac ',pktno_mac,'mac_source_ip ',mac_source_ip,'mac_destination_ip ',mac_destination_ip
					up_packet += mac_packet[28:] #13 
					mac_packet = ''

					if (self.role == 'rx' or self.role =='relay') :


						if mac_source_ip in netcfg.pc_usrp_dic.keys():
							#*********# FIND THE IP PC BASED ON THE IP USRP!
							pc_usrp = netcfg.pc_usrp_dic[mac_source_ip]
							port_usrp = netcfg.port_usrp_dic[mac_source_ip]
							self.send_l2_feedback(feedback_mac,pktno_mac,pc_usrp,port_usrp)
							#*********#

				# FRAME CONTIGUOUS TO THE PREVIOUS 
				elif packet_beginning_flag == 1 and pktno_mac == (pktno_mac_old + 1) % (self.number_of_frames +1): 
					#print 'fragment of the packet'
					feedback_mac = mac_packet[0:28]		#13
					
					mac_destination_ip =   mac_packet[15:28]#13
					mac_source_ip =   mac_packet[2:15]	#13		
					
					pktno_mac_old = pktno_mac
					#print 'L2 FIELDS pktno_mac ',pktno_mac,'mac_source_ip ',mac_source_ip,'mac_destination_ip ',mac_destination_ip
					up_packet += mac_packet[28:] # 13 BYTES IP
					mac_packet = ''

					if (self.role == 'rx' or self.role =='relay'):

						# The received information can be corrupted, in that case it may raise
						# errors if use the information directly
						# Add 'if' 					
						if mac_source_ip in netcfg.pc_usrp_dic.keys():
							#*********# FIND THE IP PC BASED ON THE IP USRP!
							pc_usrp = netcfg.pc_usrp_dic[mac_source_ip]
							port_usrp = netcfg.port_usrp_dic[mac_source_ip]
							self.send_l2_feedback(feedback_mac,pktno_mac,pc_usrp,port_usrp)
							#*********#

					if pktno_mac == self.number_of_frames :
						break		

				




				# CONTROL MESSAGE
				elif pktno_mac == -1: 
					print 'HANDLING code rate EXCEPTION'
					self.handle_update_rate_exceptiop(mac_packet)
					if (self.role == 'rx' or self.role =='relay'):
						
						#*********# FIND THE IP PC BASED ON THE IP USRP!
						pc_usrp = netcfg.pc_usrp_dic[mac_source_ip]
						port_usrp = netcfg.port_usrp_dic[mac_source_ip]
						self.send_cc_feedback(mac_packet,pktno_mac,pc_usrp,port_usrp)
						#*********#
					
					continue


				# OUT OF ORDER FRAME
				else: 
					#print 'L2 OUT OF ORDER'
					if (self.role == 'rx' or self.role =='relay'):
						#print 'L2 packet for me'
						feedback_mac = mac_packet[0:28]#13

					if pktno_mac == self.number_of_frames and packet_beginning_flag != 0:
						break		
					#print 'neglected  ',	pktno_mac
					continue 
				
		#print 'L2 PASS UP len ', len (up_packet)	

		return up_packet,1 


	def pass_down(self,down_packet,index):     
			act_rt = 0


			#print 'L2 PACKET SIZE IS ', len(down_packet)

			(pktno_mac,) = struct.unpack('h', down_packet[0:2]) 
			#print 'L2 recevied from l4 ',pktno_mac
			
			if self.role == 'tx' or self.role =='relay':              
				self.send_pkt(down_packet)
				self.transmitted_packets = self.transmitted_packets + 1 # counter for transmission operated

				self.waiting_ack_mac_pktno = pktno_mac # the ack received must be for this pktno_mac
				#print 'L2 - sent frame ',pktno_mac
				
				while 1:	
				
					#NEED TO DEFINE A BETTER HISTORY ERASING POLICY
					if self.transmitted_packets % 100 == 0:
						self.transmitted_packets = 1
						self.successfully_transmitted_packets = 1	
				
						
					# EVERY 10 PACKETS CHECK WHETHER THE CHANNEL CODING IS APPROPRIATE 
	
					if self.transmitted_packets % 5 == 0:
						#print '$$$ ', self.transmitted_packets
						outcome, new_rate = self.check_change_rate_needed()
						if outcome == True: #increasing the channel coding rate is needed
							#print '### RATE CHANGE YES!!!'
							pass
							self.coding_update(new_rate,1)	
						else:	
							#print '### RATE CHANGE no'	
							pass

							
					globals()["ack_l2_received"].wait(netcfg.timeout_l2) 
					if globals()["ack_l2_received"].isSet():
						globals()["ack_l2_received"].clear()
						#print 'l2 ack - variable unlocked'
						
						# If not enough packets, continue to count
						if netcfg.n_pkt_cnt < 10:
							netcfg.n_pkt_cnt = netcfg.n_pkt_cnt + 1
						else:						
							self.t1 = time.time()
							delta_t = self.t1 - self.last
							if delta_t == 0:
								a = 0
							else:	
								#a = 1/delta_t
								a = netcfg.n_pkt_cnt/delta_t
						
							# Update running average of single-link throughput
							self.A = self.A*netcfg.l2_th_coeff + (1-netcfg.l2_th_coeff)*a
							
							# Update link layer throughput in netcfg                        
							netcfg.lnk_thpt = self.A
							
							#print '+++++++A ', self.A, 'a ',a, 'delta_t ', delta_t
							self.last = self.t1
							
							#Reset packet counter						
							netcfg.n_pkt_cnt = 0
						
						self.successfully_transmitted_packets = self.successfully_transmitted_packets + 1 # counter for acks received
						break
					
					elif act_rt < netcfg.l2_retransmission_threshold:
						act_rt += 1
						
						print 'L2 try for ',act_rt,' packet ',pktno_mac
						self.send_pkt(down_packet)
						self.transmitted_packets = self.transmitted_packets + 1 # counter for transmission operated
						
					else:
						print "FATAL ERROR: L2 retransmission limit reached for l2 paktno " , pktno_mac 
						break  


					
						
					
			#print 'L2 packet sent'


	def get_number_of_frames(self):
		return self.number_of_frames
		
	def get_l2_pkt_size(self):
		return self.packet_size

	def get_layer_2_next_hop_ip_uspr(self):
		return self.layer_2_next_hop_ip_uspr

	def get_layer_2_prev_hop_ip_uspr(self):
		return self.layer_2_prev_hop_ip_usrp

	def get_layer_2_ip_uspr(self):
		return self.ip_address_usrp

	def coding_update(self,ch_coding_rate,send_update):

		if send_update == 1: 	# the update is to be sent.
			print '#### RATE UPDATE',ch_coding_rate		
			# communicate the decision
			chn_code_rate_update = struct.pack('h', -1) + str(self.ip_address_usrp) + str(self.layer_2_next_hop_ip_uspr) + struct.pack('f', ch_coding_rate)

			#*********# FIND THE IP PC BASED ON THE IP USRP!
			pc_usrp = netcfg.pc_usrp_dic[self.layer_2_next_hop_ip_uspr]
			port_usrp = netcfg.port_usrp_dic[self.layer_2_next_hop_ip_uspr]
			self.send_cc_message(chn_code_rate_update,-2,pc_usrp,port_usrp)
			#*********#


			#self.send_pkt(chn_code_rate_update)


			###	SEND THE UPDATE VIA SOCKET, WAIT FOR ACK

			act_rt = 0
			while 1:	
					globals()["ack_l2_received_control"].wait(netcfg.timeout_l2 * 2) 
					if globals()["ack_l2_received_control"].isSet():
						globals()["ack_l2_received_control"].clear()
						break
					elif act_rt < netcfg.l2_retransmission_threshold*2:	#we can incrase this threshold to make it more reliable
						act_rt += 1
						#print 'L2 try for ',act_rt,' packet ',pktno_mac

						### 	SEND IT VIA SOCKET, STILL WAIT FOR ACK.	

						#*********# FIND THE IP PC BASED ON THE IP USRP!
						pc_usrp = netcfg.pc_usrp_dic[self.layer_2_next_hop_ip_uspr]
						port_usrp = netcfg.port_usrp_dic[self.layer_2_next_hop_ip_uspr]
						self.send_cc_message(chn_code_rate_update,-2,pc_usrp,port_usrp)
						#*********#			


					else:
						print "L2 Control retransmission limit reached " 
						break  


			# update the coder
			self.ch_coding_rate[self.tx_options.tx_freq] = ch_coding_rate
			self.coder[self.tx_options.tx_freq] = chncod.initialize_RSCoder(self.ch_coding_rate[self.tx_options.tx_freq])	
			## send ack


		elif send_update == 0 :		# update has been received
			# update the coder
			self.ch_coding_rate[self.rx_options.rx_freq] = ch_coding_rate
			self.coder[self.rx_options.rx_freq] = chncod.initialize_RSCoder(self.ch_coding_rate[self.rx_options.rx_freq])
			print '#### RECEIVED RATE UPDATE',ch_coding_rate
		

	def handle_update_rate_exception(self, payload):
		(new_rate,) = struct.unpack('f', payload[28:32]) #13
		#print 'new rate ',new_rate		
		self.coding_update(new_rate,0)		
		
		#*********# FIND THE IP PC BASED ON THE IP USRP!
		mac_source_ip =  		payload[2:15]	
		pc_usrp = netcfg.pc_usrp_dic[mac_source_ip]
		port_usrp = netcfg.port_usrp_dic[mac_source_ip]
		self.send_cc_feedback(payload,-1,pc_usrp,port_usrp)
		#*********#	
