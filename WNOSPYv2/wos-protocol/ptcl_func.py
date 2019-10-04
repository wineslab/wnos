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

#######################################################
# Update protocol parameters in ptcl_name. Those parameters are
# used by the automatically generated solution algorithms
#######################################################

# Configure directory
import os, sys
p = os.getcwd()										  # Current directory
p = os.path.dirname(p)      						  # Parent directory
sys.path.insert(0, p+'/WNOSPY/wos-protocol')          # Directory of protocotols
sys.path.insert(0, p+'/WNOSPY/wos-network')           # Directory of network parameters
sys.path.insert(0, p+'/TBSDN')			              # Directory of testbed


import ptcl_name, net_name
import netcfg										  # Testbed configuration

import numpy as np


def updt_lnkgain():
	'''
	Update channel gain of local link by udpating ptcl_name using net_name.
	
	Called By: TBSDN -> mynd.py
	'''
	
	# Update transmit gain
	# No need to create a separtae function for just one sentence
	ptcl_name.lkpwr00 = netcfg.tx_gain_allnode[netcfg.idx_thisnode]
	ptcl_name.lkpwr00 = 10 ** (ptcl_name.lkpwr00 / 10)		# dB -> absolute 
	
	# Check if node information is ready, other reprot error
	if netcfg.idx_thisnode == None:
		print('Error: Please call this function after netcfg.idx_thisnode is configured!')
		exit(0)
	
	# Channel gain updating only for transmitters, including source and relay
	if netcfg.nd_type[netcfg.idx_thisnode] == 'rx':
		#print('Warning: Channel gain updating not supported by this node type!')
		
		# False means information not updated, False means updated
		return False

	# Determine row and column from where the channel gain shoud be taken
	row = netcfg.idx_thisnode				# row of the channel gain matrix
	col = netcfg.chn_idx_thisnode[row]		# column
		
	# Update channel gain
	ptcl_name.lkgain00 = netcfg.chn_gain[row, col]	
	return True

	
	
def updt_lnkitf():
	'''
	Update the interference measured by the receiver of this node. Currently calculated based on equation after
	receiving the transmit power of all interfering users and channel gain parameters. 
	This parameter should be sent to the corresponding transmitter.
	
	Called By: TBSDN -> signalling.periodic_update_neighbors()
	'''	
	
	# Index of node itself
	selfidx = netcfg.idx_thisnode
	
	# If this node is a source node, it doesn't need to measure local interference
	if netcfg.nd_type[selfidx] == 'tx':
		# False means information not updated, True means updated
		return False
		
	# Transmit gain of all nodes
	tsmt_gain_dB = np.array([netcfg.tx_gain_allnode])	  							# chnnel gain in dB
	tsmt_gain_abs = map(lambda elmt: np.power(10, (elmt/10)), tsmt_gain_dB[0])		# x in absolute 
	
	# Interference relationship of this node
	itf_rela = netcfg.itf_relation[selfidx, :]
	
	# Channel gain
	chn_gain = netcfg.chn_gain[selfidx, :]				
	
	# Calculate interference
	x = np.multiply(tsmt_gain_abs, [chn_gain])     			
	
	y = np.multiply(x, [itf_rela])  
	lnkitf = np.sum(y)
	
	
	# Update receiver side interference
	ptcl_name.lkitf_rcvr_side = lnkitf
	return True