#!/usr/bin/python
#
# Copyright 2005,2006,2011,2013 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

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


from decimal import Decimal, getcontext

from gnuradio import gr
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import time, struct, sys

from gnuradio import digital
from gnuradio import blocks

# from current dir
from transmit_path import transmit_path
from uhd_interface import uhd_transmitter


# from current dir
from receive_path import receive_path
from uhd_interface import uhd_receiver

import random
import struct, sys
import socket
from threading import Thread
import threading


import copy
import Queue

ack_l2_received = threading.Event()

ack_l4_received = threading.Event()

# this class defines the l1 transmitter

class my_top_block_tx(gr.top_block):
    def __init__(self, options):
        gr.top_block.__init__(self)


        self.sink = uhd_transmitter(options.args,
                                        options.bandwidth, options.tx_freq, 
                                        options.lo_offset, options.tx_gain,
                                        options.spec, "TX/RX",
                                        options.clock_source, options.verbose)
            
        self.txpath = transmit_path(options)
        self.connect(self.txpath, self.sink)

# this class defines the l1 receiver       
 
class my_top_block_rx(gr.top_block):
	def __init__(self, callback, options):
		gr.top_block.__init__(self)

		self.source = uhd_receiver(options.args,
				   options.bandwidth, options.rx_freq, 
				   options.lo_offset, options.rx_gain,
				   options.spec, "RX2",
				   options.clock_source, options.verbose)

		self.rxpath = receive_path(callback, options)

		self.connect(self.source, self.rxpath)        



# ////////////////////////////////////////////////////////////////////////////////////
#			NETWORK LAYER 
# ////////////////////////////////////////////////////////////////////////////////////

# this class defines the basic structure of a network layer
# it has 2 queues objects (up_queue,down_queue) and two threads (up_thread,down_thread) 
# the threads execute two functions (up_fuction,down_function)
# up_fuction continuously run. receives up_packet from pass_up and decides based on the
# 	return of pass_up whether to put the packet in upper_queue(upper layer) or down_queue (current layer)
# down_function continuously run. gets the down_packet from down_queue and passes it to pass_down 


class network_layer(object):
	
	def __init__(self, layer_name):
			self.layer_name = layer_name
			self.up_queue = Queue.Queue(1024)
			self.down_queue = Queue.Queue(1024)

	def init_upper_queue(self, upper_layer):
			self.upper_queue = upper_layer.get_up_queue()

	def init_lower_queue(self, lower_layer):
			self.lower_queue = lower_layer.get_down_queue()						
			
	def init_thread(self):	
			self.up_thread = Thread(target = self.up_fuction, args = ( ))
			self.up_thread.start()

			self.down_thread = Thread(target = self.down_function, args = ( ))
			self.down_thread.start()


	def up_fuction(self):
		while True:
			#function that assemble the packet to be sent up/to down_queue. this function will pull packets from the queue
			up_packet,passing_decision = self.pass_up()  #previous_hop_socket check
			if passing_decision == 1:
				self.upper_queue.put(up_packet, True)
			elif  passing_decision == 0:
				self.down_queue.put(up_packet,True)	
			else:
				pass #this is for mac layers not having a upper queue 	

	def down_function(self):
		while True:
			#fucntions that fragments the packet and put each of them down. the function is in charge of putting all the fragments in the queue
			down_packet = self.down_queue.get(True)	
			self.pass_down(down_packet) 


	def get_up_queue(self):
		return self.up_queue

	def get_down_queue(self):
		return self.down_queue

	#test wheter self.pass_down calls one of these functions.
	def pass_down(self,down_packet):
		print 'dummy pass_down'
		

	def pass_up(self):
		print 'dummy pass_up'
		



		
# ////////////////////////////////////////////////////////////////////////////////////
#			LAYER 2
# ////////////////////////////////////////////////////////////////////////////////////		
							

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
				ip_address_pc,ip_address_usrp,ip_port,
				role, #tx / rx / relay
				layer_2_prev_hop_ip_pc='',layer_2_next_hop_ip_pc='',
				layer_2_prev_hop_ip_usrp='',layer_2_next_hop_ip_uspr='',
				
				layer_2_prev_hop_pc_port='',layer_2_next_hop_pc_port='',
				
				
				tx_options='',rx_options=''):
		
		network_layer.__init__(self, "layer_2")

		self.number_of_frames = number_of_frames #number of l2 packet that compose an upper layer packet
		self.tx_options = tx_options
		self.rx_options = rx_options


		self.ip_address_pc = ip_address_pc
		self.ip_address_usrp = ip_address_usrp		
		self.ip_port = ip_port
		self.role = role
						
		self.layer_2_prev_hop_ip_pc = layer_2_prev_hop_ip_pc		
		self.layer_2_prev_hop_ip_usrp = layer_2_prev_hop_ip_usrp
		self.layer_2_prev_hop_pc_port = layer_2_prev_hop_pc_port
				
		self.layer_2_next_hop_ip_pc = layer_2_next_hop_ip_pc
		self.layer_2_next_hop_ip_uspr = layer_2_next_hop_ip_uspr	
		self.layer_2_next_hop_pc_port = layer_2_next_hop_pc_port
		
		self.buffer_size = 20  # Normally 1024, but we want fast response
		self.packet_size = 400 #set it to 4000 since the default value

		# ack sending socket ONLY IF THE NODE RECEIVES
		if self.role == 'rx' or self.role =='relay':
			self.send_previous_hop_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		
		# transmission block ONLY IF THE NODE TRANSMITS
		if self.role == 'tx' or self.role =='relay':
			self.packet_size = tx_options.size
			self.l1_transmission_block = my_top_block_tx(self.tx_options) 		
			self.l1_transmission_block.start()




	def rx_callback(self,ok, received_pkt):		
		(pktno_mac,) = struct.unpack('!H', received_pkt[0:2])
		#print 'L1 - received'
		if ok:
			#put it in the up_queue
			self.up_queue.put(received_pkt,True)
			
			
	def start_l1_receiving_block(self):
		self.l1_receiving_block = my_top_block_rx(self.rx_callback, self.rx_options)
		self.l1_receiving_block.start()
		print 'L2 STARTED RX BLOCKthe sx freq is ', self.rx_options.rx_freq
		#time.sleep(2)
		#self.l1_receiving_block.wait() #do i need it here?


	def send_pkt(self,payload='', eof=False):
		return self.l1_transmission_block.txpath.send_pkt(payload, eof)	
	
	# Connects to the server socket present at layer_2_prev_hop_ip_pc and layer_2_prev_hop_pc_port. this must be blocked to an accept.				
	def connect_send_previous_hop_socket(self):
		while True:
			time.sleep(1)
			try:
				self.send_previous_hop_socket.connect((self.layer_2_prev_hop_ip_pc, self.layer_2_prev_hop_pc_port))	
				break
			except socket.error, exc:
				continue		
		print 'L2 connected to ', self.layer_2_prev_hop_ip_pc	

		
		
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
			#print 'L2 - POPPED PACKET ~ FLAG = ',packet_beginning_flag
			(pktno_mac,) = struct.unpack('h', mac_packet[0:2])
			#print 'L2 estracted ',pktno_mac
			

			# FRAME 0 OF A NEW PACKET
			if pktno_mac == 0 and packet_beginning_flag == 0 :
				#print 'beginning of a packet'
				packet_beginning_flag = 1

				feedback_mac = mac_packet[0:26]
				
				mac_destination_ip =   mac_packet[14:26]
				mac_source_ip =   mac_packet[2:14]			
				
				pktno_mac_old = pktno_mac
				#print 'L2 FIELDS pktno_mac ',pktno_mac,'mac_source_ip ',mac_source_ip,'mac_destination_ip ',mac_destination_ip
				up_packet += mac_packet[26:]
				mac_packet = ''

				if (self.role == 'rx' or self.role =='relay' )and (mac_destination_ip == self.ip_address_usrp):
					#print 'L2 packet for me'
					try:
						self.send_previous_hop_socket.send(feedback_mac)
						#print 'L2 SENT FEEDBACK', pktno_mac
					except socket.error, exc:
						#print 'unable to send feedback
						pass
			
			# FRAME CONTIGUOUS TO THE PREVIOUS 
			elif packet_beginning_flag == 1 and pktno_mac == (pktno_mac_old + 1) % (self.number_of_frames):
				#print 'checking' 
				#print 'fragment of the packet'
				feedback_mac = mac_packet[0:26]
				
				mac_destination_ip =   mac_packet[14:26]
				mac_source_ip =   mac_packet[2:14]			
				
				pktno_mac_old = pktno_mac
				#print 'L2 FIELDS pktno_mac ',pktno_mac,'mac_source_ip ',mac_source_ip,'mac_destination_ip ',mac_destination_ip
				up_packet += mac_packet[26:]
				mac_packet = ''

				if (self.role == 'rx' or self.role =='relay')and (mac_destination_ip == self.ip_address_usrp):
					#print 'L2 packet for me'
					try:
						self.send_previous_hop_socket.send(feedback_mac)
						#print 'L2 SENT FEEDBACK ',pktno_mac
					except socket.error, exc:
						#print 'unable to send feedback
						pass
				if pktno_mac == self.number_of_frames -1:
					break		

			
			# OUT OF ORDER FRAME
			else: 
				#print 'neglected  ',	pktno_mac
				continue 
			
		#print 'L2 PASS UP'	
		return up_packet,1 
		


	def pass_down(self,down_packet):   
         
			act_rt = 0
			rt_threshold = 5

			(pktno_mac,) = struct.unpack('h', down_packet[0:2]) 

			if self.role == 'tx' or self.role =='relay':              
				self.send_pkt(down_packet)
				self.waiting_ack_mac_pktno = pktno_mac # the ack received must be for this pktno_mac
	  			print 'L2 - sent frae ',pktno_mac
				while 1:	
					globals()["ack_l2_received"].wait(0.5) #wait at most 0.5 seconds for the ack_packet to be set
					if globals()["ack_l2_received"].isSet():
						globals()["ack_l2_received"].clear()
						break
					elif act_rt < rt_threshold:
						self.send_pkt(down_packet)
						act_rt += 1
					else:
						print "retransmission limit reached " , pktno_mac #+ str(pktno_mac)
						break  
			print 'L2 packet sent'
            

	def listening_ack_l2(self):
		try:
			 
			
			self.recv_previous_hop_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.recv_previous_hop_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #does it work?
			self.recv_previous_hop_socket.bind((self.ip_address_pc, self.ip_port))
			self.recv_previous_hop_socket.listen(1)
			self.conn, self.addr = self.recv_previous_hop_socket.accept()
			
			while (1):
				mac_ack = self.conn.recv(self.buffer_size)
				
				(mac_ack_pktno,) = struct.unpack('h', mac_ack[0:2])
				mac_source_ip =   mac_ack[2:14]					
				#print  'received ack ', pktno_mac_ack
				if mac_ack_pktno == self.waiting_ack_mac_pktno and mac_source_ip == self.ip_address_usrp: 
					#print 'ack correct for ', mac_ack_pktno
					globals()["ack_l2_received"].set() 

		except KeyboardInterrupt:
			self.recv_previous_hop_socket.close()
			self.conn.colse()
		except SystemExit:
			self.recv_previous_hop_socket.close()
		

	def start_listening_ack_l2(self):
			self.listening_ack_l2_thread = Thread(target = self.listening_ack_l2, args = ())
			self.listening_ack_l2_thread.start()

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




# ////////////////////////////////////////////////////////////////////////////////////
#			LAYER 4
# ////////////////////////////////////////////////////////////////////////////////////


class layer_4(network_layer):

	def __init__(self,

				ip_address_pc,ip_address_usrp,ip_port,
				
				number_of_frames='',

				layer_4_source_ip_pc='', layer_4_source_ip_usrp='', layer_4_source_pc_port='',
				
				layer_4_dest_ip_pc='', layer_4_dest_ip_uspr='', layer_4_dest_pc_port=''
				
				):
		
		network_layer.__init__(self, "layer_4")

		self.number_of_frames = number_of_frames #number of l4 packet that compose an upper layer packet

		self.ip_address_pc = ip_address_pc
		self.ip_address_usrp = ip_address_usrp	#layer 3 must not know that
		self.ip_port = ip_port			
		self.layer_4_source_ip_usrp = layer_4_source_ip_usrp #layer 3 must not know that
		self.layer_4_dest_ip_uspr = layer_4_dest_ip_uspr #layer 3 must not know that
		self.layer_4_source_ip_pc = layer_4_source_ip_pc 
		self.layer_4_dest_ip_pc = layer_4_dest_ip_pc 
		self.layer_4_source_pc_port = layer_4_source_pc_port
		self.layer_4_dest_pc_port = layer_4_dest_pc_port
				
		self.buffer_size = 20  # Normally 1024, but we want fast response

		# ack sending thread
		self.ack_send_to_source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


		
	def get_l2_info(self,l2):
		self.number_of_mac_frames = l2.get_number_of_frames()
		self.l2_pkt_size = l2.get_l2_pkt_size()
	 	self.layer_2_next_hop_ip_uspr = l2.get_layer_2_next_hop_ip_uspr()
		self.layer_2_prev_hop_ip_uspr = l2.get_layer_2_prev_hop_ip_uspr()
		self.layer_2_ip_uspr = l2.get_layer_2_ip_uspr()


	# Connects to the server socket present at layer_4_source_ip_pc and layer_4_source_pc_port. this must be blocked to an accept.				
	def connect_ack_send_to_source_socket(self)	:

		while True:
			time.sleep(1)
			try:
				self.ack_send_to_source_socket.connect((self.layer_4_source_ip_pc, self.layer_4_source_pc_port))
				break
			except socket.error, exc:
				#print 'trying to reconnect to ', self.layer_4_source_ip_pc				
				continue
		print 'L4 connected to ', self.layer_4_source_ip_pc		
		
	def pass_up(self):

		up_packet = ''
		l4_packet = ''
		
		l4_packet = self.up_queue.get(True)
		#print 'L4 / UP Q / RECEIVED'
		ack_l4 = l4_packet[0:40] #pktno + scr + dst + timestamp
		
		(pktno_l4,) = struct.unpack('l', l4_packet[:8]) 
		packet_source = l4_packet[8:20]
		packet_destination = l4_packet[20:32]
		(timestamp,) = struct.unpack('d', l4_packet[32:40])

		print 'L4 FIELDS pktno_l4 ',pktno_l4,' packet_source',packet_source,'packet_destination',packet_destination,'timestamp ', timestamp
		#print 'addresses :',packet_destination,'  ' , self.ip_address_usrp
		if packet_destination == self.ip_address_usrp:
			#print 'L4 packet for me'
			up_packet = l4_packet[40:]
			try:
				self.ack_send_to_source_socket.send(ack_l4)
				print 'L4 sent ack ',pktno_l4
			except socket.error, exc:
				pass	
			#print 'L4 PASSING UP ',pktno_l4	
			#return up_packet,1	
			return up_packet,2			
		else: 		
			#print 'passed beside'
			return l4_packet,0



	def pass_down(self,down_packet):         
		    
			act_rt = 0
			rt_threshold = 5

			(pktno_l4,) = struct.unpack('L', down_packet[:8])
			packet_source = down_packet[8:20]

			#do not touch the header. we dont know whether is our packet or a forward. tagging and timestamp must be done at l5
   			#print 'L4 / UP D / RECEIVED'

			# IF I SENT THE PACKET WAIT FOR A L4 ACK	
			if packet_source == self.ip_address_usrp : 
				down_packet = down_packet[:32] + struct.pack('d', time.time()) + down_packet[40:]	   			

			pktno_mac = 0
			while pktno_mac < self.number_of_mac_frames  :

				l2_packet = struct.pack('h', pktno_mac & 0xffff) + str(self.layer_2_ip_uspr) + str(self.layer_2_next_hop_ip_uspr) + down_packet[pktno_mac*self.l2_pkt_size : min((pktno_mac+1)*self.l2_pkt_size,down_packet) ]
				self.lower_queue.put(l2_packet)
				#print 'put packet down #',pktno_mac
				pktno_mac += 1
				l2_packet = ''
            
            
        	
			self.waiting_ack_pktno_l4 = pktno_l4 # the ack received must be for this pktno_mac

			# IF I SENT THE PACKET WAIT FOR A L4 ACK	
			if packet_source == self.ip_address_usrp : 
				#here is implemented a window of 1
				while 1:
					globals()["ack_l4_received"].wait(5) #wait at most 3 seconds for the ack_packet to be set
					if globals()["ack_l4_received"].isSet():
						globals()["ack_l4_received"].clear()
						break
					elif act_rt < rt_threshold:
						#self.lower_queue.put(l2_packet)

						# send the l4 packet again down 
						print 'L4 trying for the  ',act_rt, ' packet ',pktno_l4
						pktno_mac = 0
						while pktno_mac < self.number_of_mac_frames  :

							l2_packet = struct.pack('h', pktno_mac & 0xffff) + str(self.layer_2_ip_uspr) + str(self.layer_2_next_hop_ip_uspr) + down_packet[pktno_mac*self.l2_pkt_size : min((pktno_mac+1)*self.l2_pkt_size,down_packet) ]
							self.lower_queue.put(l2_packet)
							print 'put packet down #',pktno_mac
							pktno_mac += 1
							l2_packet = ''					
						


						act_rt += 1
					else:
						print "L4 - retransmission limit reached " + str(pktno_l4)
						break
	                
			return         

	def listening_ack_l4(self ):
		try:
			 
			self.recv_destination_socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.recv_destination_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #does it work?
			self.recv_destination_socket.bind((self.ip_address_pc, self.ip_port))
			self.recv_destination_socket.listen(1)
			self.conn, self.addr = self.recv_destination_socket.accept()
			
			while (1):
				ack_l4 = self.conn.recv(self.buffer_size) 
				
				(l4_ack_pktno,) = struct.unpack('l', ack_l4[:8]) 
				l4_packet_sender = ack_l4[8:20]
				l4_packet_receiver = ack_l4[20:32]
				timestamp = ack_l4[32:40]
				print  'received ack for', l4_ack_pktno, ' ',l4_packet_sender, ' ' , l4_packet_receiver, ' ',timestamp
				if l4_ack_pktno == self.waiting_l4_ack_pktno and l4_packet_sender == self.ip_address_usrp: 
					print 'ack correct for l4 ', l4_ack_pktno
					globals()["ack_l4_received"].set() 

		except KeyboardInterrupt:
			self.recv_destination_socket.close().close()
			self.conn.colse()
		except SystemExit:
			self.recv_destination_socket.close().close()	

	def start_ack_from_destination_thread(self)	:
		# ack receiving thread
		self.ack_from_destination_thread = Thread(target = self.listening_ack_l4, args = ( ))
		self.ack_from_destination_thread.start()


#test classes general network 

class class_network_test_up(network_layer):

	def __init__(self):
		network_layer.__init__(self, "up")

	def pass_up(self):	
		#time.sleep(1)	
		packet = self.up_queue.get(True)
		print self.layer_name, '- up_queue. received one packet'		
		return packet,0 #pass beside


	def pass_down(self,down_packet):
		#time.sleep(1)		
		print self.layer_name, '- down_queue. received one packet'
		down_packet = struct.pack('h', 0 & 0xffff) 	+ down_packet	
		self.lower_queue.put(down_packet)
		pass




class class_network_test_down(network_layer):

	def __init__(self):
		network_layer.__init__(self, "down")

	def pass_up(self):			
		packet = self.up_queue.get(True)
		#time.sleep(1)		
		#print self.layer_name, '- up_queue. got one packet'			
		return packet,2 #basically discard


	def pass_down(self,down_packet):
		#time.sleep(1)
		#print self.layer_name, '- down_queue. got one packet'
		pktno_mac = 0
		packet = struct.pack('h', pktno_mac & 0xffff) 
		pass




def main():

	#l_down = class_network_test_down()
	f1 = 2000000000
	f2 = 1300000000

	ip_usrp = '192.168.10.4'
	ip_pc = '192.168.10.1'
	port_pc_l2_services = 7012
	port_pc_l4_services = 7004


	#L2 INFO
	prev_hop_usrp = '192.168.10.3'	
	prev_hop_pc =  '192.168.10.1'
	prev_hop_port_pc_l2_services = 6012



	#next_hop_usrp = '192.168.10.3'	
	#next_hop_pc =  '192.168.10.1'	
	#next_hop_port_pc_l2_services = 


	#L4 INFO
	source_usrp = '192.168.10.2'	
	source_pc =  '192.168.10.1'
	source_port_pc_l4_services = 5004 	


	#dest_usrp = '192.168.10.3'	
	#dest_pc =  '192.168.10.1'	
	#dest_port_pc_l4_eervices = 
	

	number_of_frames = 3

	parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
	expert_grp = parser.add_option_group("Expert")
	parser.add_option("-s", "--size", type="eng_float", default=400,
						help="set packet size [default=%default]")
	parser.add_option("-M", "--megabytes", type="eng_float", default=1.0,
						help="set megabytes to transmit [default=%default]")
	parser.add_option("","--discontinuous", action="store_true", default=False,
						help="enable discontinuous mode")
	parser.add_option("","--from-file", default=None,
						help="use intput file for packet contents")
	parser.add_option("","--to-file", default=None,
						help="Output file for modulated samples")
	parser.add_option("", "--tx-gain", type="eng_float", default=15.750000,
						help="set tx gain [default=%default]")
  	parser.add_option("", "--rx-gain", type="eng_float", default=19,
						help="set rx gain [default=%default]")


  	# tx parser
	transmit_path.add_options(parser, expert_grp)
	digital.ofdm_mod.add_options(parser, expert_grp)
	uhd_transmitter.add_options(parser)



	# rx parser
	receive_path.add_options(parser, expert_grp)
	uhd_receiver.add_options(parser)
	digital.ofdm_demod.add_options(parser, expert_grp)

	(rx_options, args) = parser.parse_args ()
	#rx_options = tx_options

	rx_options.rx_freq = f2
	#rx_options.rx_freq = rx_freq




	#main.l_mac = layer_2(1,'192.168.10.1',5005,'rx','192.168.10.1','','' ,'' ,5006 ,'' , tx_options,rx_options)


	main.l4 = layer_4(

				ip_pc,#ip_address_pc,
				ip_usrp,#ip_address_usrp,
				port_pc_l4_services,#ip_port,
				'',#number_of_frames='',
				source_pc,#layer_4_source_ip_pc='', 
				source_usrp,#layer_4_source_ip_usrp='', 
				source_port_pc_l4_services,#layer_4_source_pc_port='',
				'',# layer_4_dest_ip_pc='', 
				'',# layer_4_dest_ip_uspr='', 
				'',# layer_4_dest_pc_port=''

				)

	main.l2 = layer_2(
				number_of_frames,#number_of_frames,
				ip_pc,#ip_address_pc,
				ip_usrp,#ip_address_usrp,
				port_pc_l2_services,#,ip_port,
				'rx',#role, #tx / rx / relay
				prev_hop_pc,#layer_2_prev_hop_ip_pc='',
				'',#layer_2_next_hop_ip_pc='',
				prev_hop_usrp,#layer_2_prev_hop_ip_usrp='',
				'',#layer_2_next_hop_ip_uspr='',
				prev_hop_port_pc_l2_services,#layer_2_prev_hop_pc_port='',
				'',#layer_2_next_hop_pc_port='',
				'',#tx_options='',
				rx_options#rx_options=''
				)



	print '#created the two blocks\n'



 
 	main.l2.init_upper_queue(main.l4)
 	main.l4.init_lower_queue(main.l2)
 	print '# linked the two layers\n'

 	main.l4.get_l2_info(main.l2)
	print '# l4 got info of l2\n'



	pktno_mac = 0
	pktno_l4 = 0

	#packet = (1000) * chr(pktno_l4  & 0xff) 



 	#print main.l2.up_queue.qsize()
 	#print main.l2.down_queue.qsize()
 	#print main.l4.up_queue.qsize()
 	#print main.l4.up_queue.qsize()




 	main.l4.init_thread()
 	print '# started l4 threads\n'
 	main.l2.init_thread()
 	print '# started l2 threads\n'


	main.l2.start_listening_ack_l2()
 	main.l4.start_ack_from_destination_thread()

 	main.l2.start_l1_receiving_block()
 	print '# started l2 rx chain\n'

 	
	 	

 	main.l2.connect_send_previous_hop_socket()
 	print 'created socket to listen acks l2'
 	main.l4.connect_ack_send_to_source_socket()
 	print 'created socket to listen acks l4'

	#pktno_mac = 0

	#while True: 	

	#	time.sleep(0.05)
	#	pktno_mac += 1
	#timestamp = time.time()
	#packet = struct.pack('l', pktno_l4)  + ip_usrp + dest_usrp +  struct.pack('d', timestamp) + packet
 	#main.l4.up_queue.put(packet)
	

	#wait at the end of all

	time.sleep(2)
	main.l2.l1_receiving_block.wait() 



if __name__ == '__main__':
	try:
		print 'before main'
		main()
		print 'after main'
		while True:
			time.sleep(100) #FIX THIS SH**
		
	except KeyboardInterrupt:		#WHY IS NOT WORKING 
		print '\n\n closing all threads, this closes all the open sockets'
		main.l4.up_thread._Thread__stop()
		main.l4.down_thread._Thread__stop()
		main.l4.ack_from_destination_thread._Thread__stop()
		main.l2.up_thread._Thread__stop()
		main.l2.down_thread._Thread__stop()
		main.l2.listening_ack_l2_thread._Thread__stop()
		main.l2.l1_receiving_block.stop()
		pass    

