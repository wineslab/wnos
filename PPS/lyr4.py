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
#			LAYER 4
# ////////////////////////////////////////////////////////////////////////////////////
							
import netlib, socket, time, struct, sys, netcfg
from ntwklyr import network_layer
import threading
from threading import Thread


l4_lower_queue_access = threading.Lock()
l4_dict_pktno_thread_access = threading.Lock()


class layer_4(network_layer):

	def __init__(self,

				ip_address_pc,ip_address_usrp,
				#ip_port,
				
				number_of_frames='',

				layer_4_source_ip_pc='', layer_4_source_ip_usrp='', #layer_4_source_pc_port='',
				
				layer_4_dest_ip_pc='', layer_4_dest_ip_uspr='', #layer_4_dest_pc_port='',

				window = 1, 

				sock_send = '', udp_port = ''
				
				):
		
		network_layer.__init__(self, "layer_4")

		self.number_of_frames = number_of_frames #number of l4 packet that compose an upper layer packet

		self.ip_address_pc = ip_address_pc
		self.ip_address_usrp = ip_address_usrp	#layer 3 must not know that
		#self.ip_port = ip_port			
		self.layer_4_source_ip_usrp = layer_4_source_ip_usrp #layer 3 must not know that
		self.layer_4_source_ip_pc = layer_4_source_ip_pc 
		self.layer_4_dest_ip_uspr = layer_4_dest_ip_uspr #layer 3 must not know that
		self.layer_4_dest_ip_pc = layer_4_dest_ip_pc 
		#self.layer_4_source_pc_port = layer_4_source_pc_port
		#self.layer_4_dest_pc_port = layer_4_dest_pc_port
				
		self.buffer_size = 1024  # Normally 1024, but we want fast response

		# ack sending thread
		self.ack_send_to_source_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		self.window = window
		self.t1 = time.time()

		self.sock_send =  sock_send
		self.UDP_PORT  = udp_port	


	def send_l4_feedback(self,packet,number,ip,port):
		packet = struct.pack('h', 4) + packet
		try:
			self.sock_send.sendto(packet, (ip, port))
			netcfg.n_tot += 1   # Total number of correct packets
							
			print 'SENT L4 ACK ', number# ,'at ', ip, ' PORT',port 
			#print netcfg.n_tot
			
			# Calculate throughput
			# First, get current time
			
			# Measure throughput every 5 packets
			if netcfg.n_tot >= 5:						
				cur_time = time.time()
				run_time = cur_time - netcfg.time_start    # Ellisped time in second			
				time_intveral = cur_time - netcfg.prev_time
				
				print('Throught [packet/s]:', netcfg.n_tot/time_intveral)
				netcfg.thpt_history.append(netcfg.n_tot/time_intveral)
				netcfg.time_idx.append(run_time)	
				
				netcfg.n_tot = 0
				netcfg.prev_time = cur_time
			
		except socket.error, exc:
			#print 'unable to send feedback'
			pass		


	def initialize_received_l4_feedback(self):
		self.waiting_l4_ack_pktno = 0


	def received_l4_feedback(self,ack_l4):	

		(l4_ack_pktno,) = struct.unpack('l', ack_l4[:8]) 
		print '## L4 RECEIVED ACK ', l4_ack_pktno
		#print 'received ' ,l4_ack_pktno,'waiting ',waiting_l4_ack_pktno
		if l4_ack_pktno >= self.waiting_l4_ack_pktno and l4_ack_pktno < (self.waiting_l4_ack_pktno + self.window) :  #check acks for the whole window
			timestamp_2 = time.time()
			self.waiting_l4_ack_pktno +=1	


			l4_packet_sender = ack_l4[8:21]#13
			l4_packet_receiver = ack_l4[21:34]#13
			(timestamp,) = struct.unpack('d', ack_l4[34:42])#13
			#print  'received ack for', l4_ack_pktno
			if l4_packet_sender == self.ip_address_usrp: 
				self.dict_thread_signal[ self.dict_pktno_thread[l4_ack_pktno] ].set() 

				l4_dict_pktno_thread_access.acquire() #ACQUIRE the dict
				if l4_ack_pktno in self.dict_pktno_thread:
					del self.dict_pktno_thread[l4_ack_pktno]
				l4_dict_pktno_thread_access.release() #RELEASE the dict_pktno_thread

				if l4_ack_pktno == netcfg.l4_packets_to_send:
					self.t2 = time.time()
					print self.t2-self.t1, ' for ',netcfg.total_bytes,'.',netcfg.total_bytes/(self.t2-self.t1)/1000, 'KB/s'			


	
	def get_l2_info(self,l2):
		self.number_of_mac_frames = l2.get_number_of_frames()
		self.l2_pkt_size = l2.get_l2_pkt_size()
		self.layer_2_next_hop_ip_uspr = l2.get_layer_2_next_hop_ip_uspr()
		self.layer_2_prev_hop_ip_uspr = l2.get_layer_2_prev_hop_ip_uspr()
		self.layer_2_ip_uspr = l2.get_layer_2_ip_uspr()




	def pass_up(self):

		up_packet = ''
		l4_packet = ''
		
		l4_packet = self.up_queue.get(True)
		#print 'L4 / UP Q / RECEIVED'
		ack_l4 = l4_packet[0:42] #pktno + scr(13) + dst(13) + timestamp 


		try:
			(pktno_l4,) = struct.unpack('l', l4_packet[:8])			
		except ValueError:
			print '!?! L2 pktno_mac ERROR - continue'
			

		
		 
		packet_source = l4_packet[8:21] #13
		packet_destination = l4_packet[21:34]#13
		(timestamp,) = struct.unpack('d', l4_packet[34:42])#13

		#print 'L4 FIELDS pktno_l4 ',pktno_l4,' packet_source',packet_source,'packet_destination',packet_destination,'timestamp ', timestamp
		#print 'addresses :',packet_destination,'  ' , self.ip_address_usrp
		if packet_destination == self.ip_address_usrp:
			#print 'L4 packet for me'
			up_packet = l4_packet[42:]


			#*********# FIND THE IP PC BASED ON THE IP USRP!
			pc_usrp = netcfg.pc_usrp_dic[packet_source]
			port_usrp = netcfg.port_usrp_dic[packet_source]
			self.send_l4_feedback(ack_l4,pktno_l4,pc_usrp,port_usrp)
			#*********#
			'''
			try:
				self.ack_send_to_source_socket.send(ack_l4)
				print 'L4 sent ack ',pktno_l4
			except socket.error, exc:
				pass	
			'''

			#print 'L4 PASSING UP ',pktno_l4	
			#return up_packet,1	
			return up_packet,2			
		else: 		
			#print 'L4 PACKET FORWARDED n ',pktno_l4
			return l4_packet,0
	


	def pass_down(self,down_packet,index):         
			
			act_rt = 0
			rt_threshold = 15

			(pktno_l4,) = struct.unpack('L', down_packet[:8])
#			packet_source = down_packet[8:20]
			packet_source = down_packet[8:21]
#			print 'DOWN PACKET SRC IP:', packet_source

			#do not touch the header. we dont know whether is our packet or a forward. tagging and timestamp must be done at l5
			#print 'L4 / DOWN Q / RECEIVED'

			# IF I SENT THE PACKET WAIT FOR A L4 ACK	
			if packet_source == self.ip_address_usrp : 
				down_packet = down_packet[:34] + struct.pack('d', time.time()) + down_packet [42:]  		#updating the timestamp	(8+13+13 + 8 + ...)

			pktno_mac = 1
			l4_lower_queue_access.acquire() #ACQUIRE the lower_queue (to not mix sequential mac packets)
			#print 'L4 - sending packet ',pktno_l4
			while pktno_mac <= self.number_of_mac_frames :
				
				chunk = down_packet[(pktno_mac-1)*netcfg.chunk_size : min((pktno_mac)*netcfg.chunk_size,down_packet) ]
				l2_packet = struct.pack('h', pktno_mac & 0xffff) + str(self.layer_2_ip_uspr) + str(self.layer_2_next_hop_ip_uspr) + chunk
				#print 'PUTTING DOWN A MAC PACKET LENGTH ', len(l2_packet) , 'lenght chunk ', len(chunk	)
				self.lower_queue.put(l2_packet)
				#print 'put packet down #',pktno_mac
				pktno_mac += 1
				l2_packet = ''
			
			l4_lower_queue_access.release() #RELEASE the lower_queue
			
			
			waiting_ack_pktno_l4 = pktno_l4 # the ack received must be for this pktno_mac

			# IF I SENT THE PACKET WAIT FOR A L4 ACK	
			if packet_source == self.ip_address_usrp : 
				# update dictionary pktno - thread id 

				self.dict_thread_signal[ self.thread_pool[index].ident ] = threading.Event() # DICT thread_id | Event
				#print self.dict_thread_signal


				l4_dict_pktno_thread_access.acquire() #ACQUIRE the dict_pktno_thread

				if not waiting_ack_pktno_l4 in self.dict_pktno_thread : #if there is no entry still for this packet (in case of retransmission it might be)
					self.dict_pktno_thread[waiting_ack_pktno_l4] = self.thread_pool[index].ident # DICT pkton | thread_id
					#print 'adding ' ,waiting_ack_pktno_l4, ' dict: ' ,self.dict_pktno_thread
				
				l4_dict_pktno_thread_access.release() #RELEASE the dict_pktno_thread





				#self.dict_thread_signal[ self.thread_pool[index].ident ].clear() #not really needed?

				#print ' thread ',self.thread_pool[index].ident, 'is sending packet ',waiting_ack_pktno_l4
				#print ' sending packet ',waiting_ack_pktno_l4
				while 1:


					

					self.dict_thread_signal[ self.thread_pool[index].ident ].wait(netcfg.timeout_l4)
					if self.dict_thread_signal[ self.thread_pool[index].ident ].isSet():
						self.dict_thread_signal[ self.thread_pool[index].ident ].clear()
						break

					elif act_rt < netcfg.l4_retransmission_threshold:
						#self.lower_queue.put(l2_packet)

						# send the l4 packet again down 
						#print 'L4 trying for the  ',act_rt, ' packet ',pktno_l4
						pktno_mac = 1

						l4_lower_queue_access.acquire() #ACQUIRE the lower_queue
						while pktno_mac <= self.number_of_mac_frames  :


							chunk = down_packet[(pktno_mac-1)*netcfg.chunk_size : min((pktno_mac)*netcfg.chunk_size,down_packet) ]
							l2_packet = struct.pack('h', pktno_mac & 0xffff) + str(self.layer_2_ip_uspr) + str(self.layer_2_next_hop_ip_uspr) + chunk
 
                            #Commented the following one line, which is obsolete
							#l2_packet = struct.pack('h', pktno_mac & 0xffff) + str(self.layer_2_ip_uspr) + str(self.layer_2_next_hop_ip_uspr) + down_packet[(pktno_mac-1)*l2_interval : min((pktno_mac)*l2_interval,down_packet) ]                                                       
                            
							self.lower_queue.put(l2_packet)
							#print 'put packet down #',pktno_mac
							pktno_mac += 1
							l2_packet = ''					
						l4_lower_queue_access.release() #RELEASE the lower_queue


						act_rt += 1
					else:
						print "L4 - retransmission limit reached " + str(pktno_l4)
						break
		
						
			return           


