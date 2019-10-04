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


########################################################
#        Those common functions in other modules
########################################################

from gnuradio import gr
from gnuradio import eng_notation
from gnuradio.eng_option import eng_option
from optparse import OptionParser
import time, struct, sys

from gnuradio import digital
from gnuradio import blocks
from gnuradio.filter import firdes

# from current dir
from transmit_path import transmit_path
from uhd_interface import uhd_transmitter


# from current dir
from receive_path import receive_path
from uhd_interface import uhd_receiver
from threading import Thread

import netcfg

# June 12, 2017
# Commented since we won't estimate channel states online, instead fixed channel state (measured offline) will be used  
# import mycorr		# Our own correlator

class MyThread(Thread):
	def __init__(self, target, args):
		Thread.__init__(self, target=target, args=args)
		self.stop_condition = False


class my_top_block_tx(gr.top_block):
	'''
	# this class defines the l1 transmitter
	transmit block
	'''
	def __init__(self, options):			
		gr.top_block.__init__(self)


		self.sink = uhd_transmitter(options.args,
										options.bandwidth, options.tx_freq, 
										options.lo_offset, options.tx_gain,
										options.spec, "TX/RX",
										options.clock_source, options.verbose)
			
		self.txpath = transmit_path(options)
		self.connect(self.txpath, self.sink)
			 
class my_top_block_rx(gr.top_block):
	'''
	# this class defines the l1 receiver 
	receiver block
	'''
	def __init__(self, callback, options):
		gr.top_block.__init__(self)

		self.source = uhd_receiver(options.args,
				   options.bandwidth, options.rx_freq, 
				   options.lo_offset, options.rx_gain,
				   options.spec, "RX2",
				   options.clock_source, options.verbose)

		self.rxpath = receive_path(callback, options)

		self.connect(self.source, self.rxpath)   
		


def get_ndinfo(node_name):
	'''
	identify node type and index with give node name
	'''    
	# get node name
	node_index = netcfg.nd_id.index(node_name)
	print '$$$ NODE IDNEX IS' ,node_index
	
	# get the corresponding node type
	node_type = netcfg.nd_type[node_index] 
	
	ndinfo = {'index': node_index, 'type': node_type}
	return ndinfo
	
