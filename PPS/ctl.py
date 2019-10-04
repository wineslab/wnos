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

# control module

import netcfg, jocp, wnosalg, signalling

import threading, time
from threading import Thread

# control thread
global ctl_thread, dict_tick

ctl_thread = None

# current transmit rate and power; check these parameters to see if there are any changes
cur_rate = 0
cur_tx_gain = netcfg.tx_gain

# update period of power and rate
period_tick = 1			# period of a tick in second
pwr_tick = 1			# period of power udpate in tick
rate_tick = 5			# period of rate update in tick
tick_cnt = None			# current tick count, updated in ctl_main
dict_tick = {'period_tick':period_tick, 'pwr_tick': pwr_tick, 'rate_tick': rate_tick, 'tick_cnt': tick_cnt}

def start_ctl_thread():
	'''
	start control thread
    
    Called By: mynd.node()
	'''	
	global ctl_thread
	
	ctl_thread = Thread(target = ctl_main, args = ( ))
	ctl_thread.start()	
	print 'Control thread started.'
	
	
def ctl_main():
	'''
	main progroam of control thread
    
    Calle By: start_ctl_thread() in this file
	'''
	
	tick = 0
	
	while True:
		########################################################
		# tick is used to control the update period of rate and power
		# if tick % cnt_updt_pwr == 0, power is updated
		# if tick % cnt_updt_rate == 0, rate is updated
		########################################################
		tick += 1
		dict_tick['tick_cnt'] = tick
		
		# Determine which transmission paramter should be optimzied, according 
		# to tick count and the optimziation switch defined in netcfg		
		b_optrate = 0					# Initizlie to not being optimzied (0)
		b_optpwr = 0
		
		# Whether to optimize power?
		if dict_tick['tick_cnt'] % (period_tick * pwr_tick) == 0 and netcfg.b_optpwr == 1:
			b_optpwr = 1
			
		# Whether to optimize transport layer rate?
		if dict_tick['tick_cnt'] % (period_tick * rate_tick) == 0 and netcfg.b_optrate == 1:
			b_optrate = 1	

		dict_opt_switch = {'b_optpwr': b_optpwr, 'b_optrate': b_optrate}
		
		########################################################
		# network control algorithm here
		########################################################
		if netcfg.alg == 'JOCP':                                                    # As configured in netcfg, JOCP is not implemented
			#dict_para = jocp.jocp()
			print('Error: Currently JOCP is not supported!')
			exit(0)
		else:
			dict_para = wnosalg.wnosalg(dict_opt_switch)
		
		########################################################
		# update transmit parameters
		########################################################
		new_tx_gain = dict_para['tx_gain']
		new_rate = dict_para['rate']		
		updt_para(new_tx_gain, new_rate)
		
		########################################################
		# broad new parameters to neighbors
		########################################################
		idx_thisnode = netcfg.idx_thisnode											# index of transmitter
		rcvr_ip_list = None															# ip list of receivers
		
		para_code = None															# type of parameter to be sent
		para_val = None																# value of parameter to be sent
		#signalling.broadcast_sgl(idx_thisnode, rcvr_ip_list, para_code, para_val)	# broad the parameter
		
		########################################################
		# if tick reaches its maximum, reset it and count from 0
		########################################################
		if tick >= 100000:
			tick = 0
		
		# wait for a tick period
		time.sleep(period_tick)
		print '*'


def updt_para(new_tx_gain, new_rate):
	'''
	func: update transmit parameters
	
	new_tx_gain: new transmit gain
	new_rate: new layer-4 transmit rate 
    
    Called By: ctl_main() in this file
	'''
	pass
	


def get_rcvr_ip_list(idx_thisnode):
	'''
	determine the ip of list for control message broadcasting
	'''
	
	pass