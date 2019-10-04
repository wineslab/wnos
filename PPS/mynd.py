########################################################
# mynode: single file that can run with differnt roles
########################################################
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


import os, sys, inspect
# realpath() will make your script run, even if you symlink it :)
cmd_folder = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


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

########################################
# supporting of narrowband transceiver
########################################
import transmit_path_narrow, receive_path_narrow, uhd_interface_narrow


import random
import struct, sys, string
import socket
from threading import Thread
import threading


import copy
import Queue

# from current dir
import netcfg, netlib, ntwklyr
import signalling
from lyr2 import layer_2
from lyr4 import layer_4

# control module
import ctl        
import socket

from random import randint

# import matplotlib.pyplot as plt

# Configure directory
import os, sys
p = os.getcwd()										  # Current directory
p = os.path.dirname(p)      						  # Parent directory

sys.path.insert(0, p+'/WNOSPYv2/wos-protocol')      	# Directory of testbed
sys.path.insert(0, p+'/WNOSPYv2/wos-network') 		# Network parameters 
sys.path.insert(0, p+'/wnospyv2/wos-protocol')      	# Directory of testbed
sys.path.insert(0, p+'/wnospyv2/wos-network') 		# Network parameters 


import net_name

# Mmodule defining functions for protocl parameter updating
import ptcl_func
   	
class node(object):

	def main(self):
		parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
		expert_grp = parser.add_option_group("Expert")
		
		# "-i" option is added to recieve node id parameters from command
		parser.add_option("-i", "--nodeid", type="choice", choices=netcfg.nd_id,
						default='src1',
						help="Set node id from: %s [default=%%default]" 
						% (', '.join(netcfg.nd_id),))  
		
		parser.add_option("-s", "--size", type="eng_float", default=netcfg.l2_size,
							help="set packet size [default=%default]")
		parser.add_option("-M", "--megabytes", type="eng_float", default=1.0,
							help="set megabytes to transmit [default=%default]")
		parser.add_option("","--discontinuous", action="store_true", default=False,
							help="enable discontinuous mode")
		parser.add_option("","--from-file", default=None,
							help="use intput file for packet contents")
		parser.add_option("","--to-file", default=None,
							help="Output file for modulated samples")
		parser.add_option("", "--tx-gain", type="eng_float", default= netcfg.tx_gain,
							help="set tx gain [default=%default]")
		parser.add_option("", "--rx-gain", type="eng_float", default= netcfg.rx_gain,
							help="set rx gain [default=%default]")
		
		##################################################################
		# add options according to phy-layer technology, narrowband or OFDM
		##################################################################
		
		if netcfg.phy == 'NARROWBAND': 			# options for narrowband	
			mods = digital.modulation_utils.type_1_mods()
			demods = digital.modulation_utils.type_1_demods()
		
			parser.add_option("-m", "--modulation", type="choice", choices=mods.keys(),
							  default=netcfg.narrow_modulation,
							  help="Select modulation from: %s [default=%%default]"
									% (', '.join(mods.keys()),))

			for mod in mods.values():
				mod.add_options(expert_grp)	

			for mod in demods.values():
				mod.add_options(expert_grp)			

			# tx parser
			transmit_path_narrow.transmit_path.add_options(parser, expert_grp)
			uhd_interface_narrow.uhd_transmitter.add_options(parser)

			# rx parser
			receive_path_narrow.receive_path.add_options(parser, expert_grp)
			uhd_interface_narrow.uhd_receiver.add_options(parser)
			
		elif netcfg.phy == 'OFDM': 				# options for OFDM	
			# tx parser
			transmit_path.add_options(parser, expert_grp)
			digital.ofdm_mod.add_options(parser, expert_grp)
			uhd_transmitter.add_options(parser)

			# rx parser
			receive_path.add_options(parser, expert_grp)
			uhd_receiver.add_options(parser)
			digital.ofdm_demod.add_options(parser, expert_grp)	

		##################################################################
		# parse options
		##################################################################
		
		(options, args) = parser.parse_args ()
		
		#print options
		
		# get node type and id for later useport_usrp_dic
		ndinfo = netlib.get_ndinfo(options.nodeid) 
        
		# Record nodeid for later use when constructing file name 
		netcfg.nodeid = options.nodeid        
		
		# configure transmit PN sequence for this node (None if not transmitter)
		netcfg.tx_pn_this_node = netcfg.tsmt_pn[ndinfo['index']]		# Dummy parameter, not used
		netcfg.rx_pn_this_node = netcfg.rcvr_pn[ndinfo['index']]
		
		# corresponding PN code used by correlator
		netcfg.rx_pn_this_node_corr = netcfg.rcvr_pn_corr[ndinfo['index']]
			
		# configure args and other options parameters
		options.args = netcfg.args[ndinfo['index']]
		options.differential = netcfg.differential	
		
				
		self.ip_usrp = netcfg.ip_usrp[ndinfo['index']]
		self.ip_pc = netcfg.ip_pc[ndinfo['index']]


		self.udp_port_listen = netcfg.udp_port_listen[ndinfo['index']]
		self.udp_port_send = netcfg.udp_port_send[ndinfo['index']]		

		#L2 INFO
		prev_hop_usrp = netcfg.prev_hop_usrp[ndinfo['index']]	
		prev_hop_pc =  netcfg.prev_hop_pc[ndinfo['index']]

		next_hop_usrp = netcfg.next_hop_usrp[ndinfo['index']]	
		next_hop_pc =  netcfg.next_hop_pc[ndinfo['index']]


		#L4 INFO
		source_usrp = netcfg.source_usrp[ndinfo['index']]
		source_pc =  netcfg.source_pc[ndinfo['index']]

		dest_usrp = netcfg.dest_usrp[ndinfo['index']]
		dest_pc =  netcfg.dest_pc[ndinfo['index']]
		
		number_of_frames = netcfg.number_of_frames    

		options.rx_freq = netcfg.rx_freq[ndinfo['index']]
		options.tx_freq = netcfg.tx_freq[ndinfo['index']]
		
		l4_window = netcfg.l4_window[ndinfo['index']]
		l2_window = netcfg.l2_window[ndinfo['index']]


		##############################################################
		#		signalling matrix
		##############################################################
		
		signalling.initialize_matrix(self)

		##############################################################		


		##############################################################
		#		UDP sockets
		##############################################################
		
		signalling.start_sending_socket(self)
		print('--UDP SEND START')

		##############################################################		
	  
		self.l4 = layer_4(

					self.ip_pc,
					self.ip_usrp,
					number_of_frames,
					source_pc,
					source_usrp, 
					dest_pc,
					dest_usrp,
					l4_window,
					self.sock_send,
					self.UDP_PORT_SEND				
					)
					
		self.l2 = layer_2(
					number_of_frames,
					self.ip_pc,
					self.ip_usrp,
					ndinfo['type'],#role
					prev_hop_pc,
					next_hop_pc,
					prev_hop_usrp,
					next_hop_usrp,
					options,
					options,
					l2_window,
					self.sock_send,
					self.UDP_PORT_SEND
					)




		




		##############################################################
		#		UDP sockets
		##############################################################

		self.start_listening_socket_thread = Thread(target = signalling.start_listening_socket, args = (self,))
		self.start_listening_socket_thread.start()
		print('--UDP LISTEN START')
		print ' ************** I am ', self.ip_usrp,'************************', 'index',  ndinfo['index']   ,'listening on ',self.udp_port_listen		


		##############################################################
		# common to all roles
		##############################################################
		self.l2.init_upper_queue(self.l4)
		self.l4.init_lower_queue(self.l2)
		print('# linked the two layers\n')

		self.l4.get_l2_info(self.l2)
		print('# l4 got infor of l2\n')
		
		self.l2.init_thread()
		print('# l2 threads initialized\n')
		
		self.l4.init_thread()
		print('# l4 threads initialized\n')

		self.role = ndinfo['type']
		netcfg.idx_thisnode = ndinfo['index']
				
		# Update protocol parameters, which are used in the local optimization in WNOS project (wos-alglib.alglib_XXXsol.py)
		ptcl_func.updt_lnkgain()		
		
		##############################################################
		#		signalling paradigmn
		##############################################################

		self.signalling_thread = Thread(target = signalling.periodic_update_neighbors, args = (self,))
		self.signalling_thread.start()
		print('--SIGNALLING START')
		#print netcfg.port_usrp_dic


		##############################################################
		if ndinfo['type'] == 'tx' or ndinfo['type'] == 'relay':   
			ctl.start_ctl_thread()

		if ndinfo['type'] == 'relay' or ndinfo['type'] == 'rx':    	
			pass
			

		##############################################################
		# transmitter only
		##############################################################
		if ndinfo['type'] == 'tx':       
			pktno_l4 = 0

			payload = (netcfg.l4_size - netcfg.l4_header_length) * random.choice(string.digits)	# l4 
			print 'il payload e ',type(payload), 'len ', len (payload), 'l4 len must be ',(netcfg.l4_size - netcfg.l4_header_length)



			if netcfg.l4_control_rate_flag == 1 :
				print('MAX TRANSPORT RATE	l4 packet size ', netcfg.l4_size)
				print('MAX TRANSPORT RATE 	', netcfg.l4_maximum_rate) 
				print('MAX TRANSPORT RATE 	packets per second to be input ', netcfg.l4_maximum_packets_per_second) 



			while True: 	



				# to be tested

				if netcfg.l4_control_rate_flag == 1 and pktno_l4 % netcfg.l4_maximum_packets_per_second == 0:
					time.sleep(1)
					#print('WAITING ONE SECOND')
				# to be tested



				timestamp = time.time()
				packet = struct.pack('l', pktno_l4)  + self.ip_usrp + dest_usrp +  struct.pack('d', timestamp) + payload # 42 bytes added
				#print 'il packet e ',type(packet), 'len ', len (packet)
				self.l4.down_queue.put(packet)
				



				if pktno_l4 == netcfg.l4_packets_to_send:												
					break
				pktno_l4 += 1	
			
				
		if ndinfo['type'] == 'relay' or ndinfo['type'] == 'rx':        
			self.l2.start_l1_receiving_block()
			print('# started l2 rx chain\n')
					


	def run_node(self):		
		if __name__ == '__main__':
			try:
				
				
				# display next-step work
				if netcfg.disp_note == 1:
					print('#############################################################################')
					print(netcfg.note1)
					print(netcfg.note2)
					print('#############################################################################')
					exit(0)
								
				#print 'before main'
				self.main()
				while True:
					#print 'in while'					
					time.sleep(100) 		#FIX THIS 
				
			except KeyboardInterrupt:	
				print('\n\n closing all threads, this closes all the open sockets')
		  
				self.l4.up_thread._Thread__stop()
				self.l4.down_thread._Thread__stop()
				self.l2.up_thread._Thread__stop()
				self.l2.down_thread._Thread__stop()


				for i in range(self.l2.window):
					if self.l2.thread_pool[i] != None:
						self.l2.thread_pool[i]._Thread__stop()	
						 
				for i in range(self.l4.window):
					if self.l4.thread_pool[i] != None:
						self.l4.thread_pool[i]._Thread__stop()	
					
				# stop control thread
				if ctl.ctl_thread != None:
					ctl.ctl_thread._Thread__stop()

				
				# stop rcv socket thread
				if self.start_listening_socket_thread != None:
					self.start_listening_socket_thread._Thread__stop()

				# stop signaling thread
				if self.signalling_thread != None:
					self.signalling_thread._Thread__stop()	
					
				# Record throughput history
				
				#print(netcfg.thpt_history)
				                 
                    
				if netcfg.nd_type[netcfg.idx_thisnode] == 'rx':
					f_pwr_name = 'thpt_' + netcfg.nodeid + '.m'                   
					f = open(f_pwr_name, 'w')                  
					f.write('a=' + str(netcfg.thpt_history))                                    
					f.write('\n' + 'b=' + str(netcfg.time_idx))
					f.write('\n plot(b, a, \' o- \'); xlabel(\'Throughput\');') 
					f.close()
                                  
									
				# Record power history
				if netcfg.nd_type[netcfg.idx_thisnode] != 'rx':
					f_pwr_name = 'pwr_' + netcfg.nodeid + '.m'                   
					f = open(f_pwr_name, 'w')                  
					f.write('a=' + str(netcfg.pwr_history))                                    
					f.write('\n' + 'b=' + str(netcfg.pwr_time_history))
					f.write('\n plot(b, a, \' o- \'); xlabel(\'Average Power\')')                    
					f.close()		
                 	
	def set_gain(self, new_gain):
		'''
		Update transmit gain of the USRP
		
		Called By: signaling.periodic_update_neighbors()
		'''
		
		new_gain = self.l2.l1_transmission_block.sink.set_gain(new_gain)
		return new_gain
		
		


### execute program
mynode = node()

# Create a reference to the node in netcfg so the node can be accessible from other files
netcfg.thisnode = mynode

mynode.run_node()
#mynode.run_node
