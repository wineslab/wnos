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
# Demonstration of WNOS 
#######################################################

import sys
sys.path.insert(0, './wos-network')
from net_ntwk import new_ntwk 
from net_func import mkexpr
from net_name import *

from sympy import *

'''
create an ad hoc network
'''
nt = new_ntwk(adhoc)
nt.add_node(10)                                                # add some nodes, 10 here
nt.add_sess(3)                                                 # add sessions   
nt.set_protocol(CDMA)                                          # use cdma at physical layer and mac layer
nt.set_protocol(TCP_VEGAS)                                     # use TCP:VEGAS at transportr layer    

'''
define network utility
'''

# 1: sum log rate maximization
# 2: sum power minimization 
ctl_obj = 1  

if ctl_obj == 1:
    nt.make_var('wos_x', [ntses, ssrate], [all, None])
    expr = mkexpr('sum(log(wos_x))', 'wos_x')
elif ctl_obj == 2:
    nt.make_var('wos_x', [ntlk, lkpwr], [all, None])
    expr = mkexpr('sum(wos_x)', 'wos_x')

# Set utility in the network object    
nt.set_utlt(expr)

'''
define network constraintsc
'''
nt.make_var('wos_y', [ntlk, lkses, ssrate], [every, all, None])
nt.make_var('wos_z', [ntlk, lkcap], [every, None])
cstr = mkexpr('sum(wos_y) <= wos_z', 'wos_y', 'wos_z')
nt.add_cstr(cstr)

##############################################################
# Sepcify optimization variables
nt.set_optvar(ssrate)               # source node transmission rate
nt.set_optvar(lkpwr)                # link transmission power

'''
optimize network
'''
if ctl_obj == 1:
    nt.optm(MAX)
elif ctl_obj == 2:
    nt.optm(MIN)
