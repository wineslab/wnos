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


######################################################################
# Module function: get channel state information
######################################################################

# reference correlation magnitude measured at transmitter side: 
# '+1, -1' preamble modulated using bpsk with samples per symbol of 4 and excess BW 0.35
# then correlated with '+1 -1' preamble using matched filter
# no transt gain and digital gain has been considered

from gnuradio.filter import firdes
import math

import netcfg


######################################################################
# Parameters for channel gain measurement, used in 
# my_csi_est_tx.py, my_csi_est_rx.py, my_tx_withcorr.py
######################################################################

# sample rate
sps = 4
samp_rate = 250000

# PN code
pn0 = [1,-1,1,-1,1,1,-1,-1,1,1,-1,1,1,1,-1,1,1,-1,1,-1,-1,1,-1,-1,1,1,1,-1,-1,-1,1,-1,1,1,1,1,-1,-1,1,-1,1,-1,-1,-1,1,1,-1,-1,-1,-1,1,-1,-1,-1,-1,-1,1,1,1,1,1,1,-1,-1]
pn1 = [-1,1,1,1,1,-1,-1,1,1,-1,-1,1,-1,-1,1,1,1,1,1,-1,-1,1,1,1,1,1,1,1,1,-1,-1,1,-1,-1,1,-1,-1,1,-1,1,-1,-1,-1,1,-1,1,-1,-1,-1,-1,1,1,1,1,-1,1,-1,1,-1,1,1,-1,1,1]
pn2 = [-1,-1,1,1,1,-1,-1,-1,-1,1,-1,1,1,1,1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,-1,1,1,1,1,-1,1,-1,1,1,-1,-1,-1,-1,-1,1,-1,1,-1,1,-1,1,-1,-1,-1,1,1,1,1,1,-1,-1,1,1,1,-1,1,-1,1]
pn3 = [-1,-1,1,-1,1,1,-1,-1,1,-1,1,-1,-1,1,-1,-1,1,-1,1,-1,1,1,1,1,1,-1,1,1,-1,-1,-1,1,-1,-1,1,1,-1,1,1,-1,1,1,-1,-1,1,1,1,1,1,1,-1,-1,-1,1,-1,1,1,-1,1,1,1,-1,-1,-1]
pn_used = pn0

# gain
tx_gain = 13.0
rx_gain = 18.0

# dB -> absolute 
tx_gain_abs = 10**(tx_gain/10)
rx_gain_abs = 10**(rx_gain/10)

# This parameter must be 1 for channel estimation
# beause the received correlation magnitude does not change with this parameter 
digi_gain_tx = 1.0	

# This parameter can be larger than 1 
digi_gain_rx = 20.0

# usrp ip address
tx_usrp_ip = "addr=192.168.10.8"
rx_usrp_ip = "addr=192.168.10.7"

# frequency
freq = 2e9

# number of channel measurements
num_msmt = 100

# reference squared corrleation magnitude
ref_corr_mag_sqrd = 64650.0

def calc_chn_gain(corr_mag_sqrd):
	'''
	############### function ##################
	calculate channel gain 
	
	################ parameters ###############
	measured squared correlation magnitude
	
	################ return ###################
	channel gain
	'''
	
	path_gain = corr_mag_sqrd/ref_corr_mag_sqrd		# end-to-end path gain
	print 'tx_gain_abs:', tx_gain_abs
	chn_gain = path_gain/tx_gain_abs/rx_gain_abs/(digi_gain_rx**2)/(digi_gain_tx**2)
	
	return chn_gain
	

def updt_sir():
	'''
	############### function ##################
	update SIR online
	
	################ parameters ###############
	read parameters from netcfg
	
	################ return ###################
	update sir parameter in netcfg	
	'''
	#print 'in updt_sir()'
	#pass
	
	###################################################
	# Read received total signal power
	###################################################

	# check if the receier block has been created, return directly if not
	# otherwise, read the received signal power from the block
	if netcfg.obj_rcvr_blk == None:
		#print 'None receiver block!'
		return
	else:
		#print 'Receiver block detected.'
		sgl_pwr_complex = netcfg.obj_rcvr_blk.get_sgl_pwr()
		sgl_pwr = sgl_pwr_complex.imag
	#print sgl_pwr	
		
	###################################################
	# Calculate SIR
	###################################################
	
	# calculate the received useful signal power
	idx = netcfg.idx_thisnode
	chn_gain = netcfg.chn_gain[idx, netcfg.chn_idx_thisnode[idx]]
	#print chn_gain
	useful_sgl_pwr = (netcfg.tx_ampl**2) * (netcfg.tx_gain_abs) *\
					  chn_gain * (netcfg.rx_gain_abs)
					 			 
	
	# calculate interference power
	itf_pwr = max(netcfg.SMALL_VALUE, sgl_pwr - useful_sgl_pwr)
	
	# calculate SIR
	sir = useful_sgl_pwr/itf_pwr
	
	
	###################################################
	# Update SIR of this node in netcfg
	###################################################
	if netcfg.sir_thisnode == None:
		netcfg.sir_thisnode = sir
	else:
		netcfg.sir_thisnode = netcfg.sir_thisnode * netcfg.alpha + sir * (1 - netcfg.alpha)

	#print '---------------------------------------------------'
	#print 'Estimated SIR:', sir
	print sir, ' ', sgl_pwr, ' ', useful_sgl_pwr
	#print '---------------------------------------------------'

	
	
	