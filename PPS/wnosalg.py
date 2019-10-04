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


def wnosalg(dict_opt_switch):
	'''
	Joint rate and power control algorithm designed based on NLPD framework
	
	dict_opt_switch: optimization switch dictionary, 1-the corresponding parameter is optimized, 0-not optimized
	
	Called By: ctl.ctl_main()
	'''
	dict_para = {'tx_gain': None, 'rate': None}
	
	# my code here
	if dict_opt_switch['b_optpwr'] == 1:			# Optimize transmission power
		dict_para['tx_gain'] = opt_pwr()									
		
	if dict_opt_switch['b_optrate'] == 1:			# Optimize transmission rate
		dict_para['rate'] = opt_rate()
	
	return dict_para
	
	
def opt_pwr():
	'''
	Optimize transmission power based on automatically generated solution algorithm (see WNOS project for details)
	
	Called By: wnosalg() in the same file
	'''
	return None



def opt_rate():
	'''
	Optimize transmission rate based on automatically generated solution algorithm (see WNOS project for details)
	
	Called By: wnosalg() in the same file
	'''
	return None