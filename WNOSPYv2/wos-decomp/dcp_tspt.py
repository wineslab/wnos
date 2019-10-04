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
# horizontal decomposition for transport layer subproblems
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from external folder
import net_name, net_func

# from local folder
import dcp_name

# from sympy
from sympy import *

def hdcp_vsub(obj_xpd, str_vsub):
    '''
    func: horizontally decmopose a vertical subproblems
    return: generate a set of subproblems, with corresponding objects created and added into xpd 
    obj_xpd: object of the expanded network control problem
    str_vsub: name string of the vertical subproblem
    '''
    
    # obtain the symbolic network control problem
    obj_vsub = obj_xpd.get_netelmt(str_vsub)   
    symncp = obj_vsub.symexpr    
    symncp = symncp.expand()              # convert to expanded format
    
    # process every component of the symbolic expression    
    print('Parsing transport layer subproblem...')
    for symexpr in symncp.args:
        #print('\n')        
        #print(x)     
        sys.stdout.write('.')
        sys.stdout.flush()
        alloc_to_sub(obj_xpd, symexpr)    # allocate the symexpr component to a subproblem