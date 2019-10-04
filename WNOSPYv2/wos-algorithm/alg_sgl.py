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
# Function: signaling among network elements
#######################################################

import sys
sys.path.insert(0, './wos-network')
sys.path.insert(0, './wos-decomp')

# from wos-network
import net_func

# from wos-decomp
import dcp_vps, dcp_name

# from current directory 
import alg_name, alg_lexpr, alg_extnl

# from sympy
from sympy import *

def pnl(obj_lexpr):
    '''
    obj_lexpr: object of the expression
    
    func: add penalization to the utility expression
    return: updated utility function
    '''
    
    # get the next external sub-expression
    # current version assumes only one external sub-expression
    dict_xtnl = alg_extnl.get_xtnl(obj_lexpr)
    
    #print(type(sympify(dict_xtnl['fullname'])))
    print('dict_xtnl', dict_xtnl)
    
    # if no external element found, do nothing; otherwise, update the penalization expression
    if dict_xtnl == None:
        obj_lexpr.idi_pnl = None
    else:
        sym_expr = obj_lexpr.expr                                  # original utility function 
        sym_var = sympify(dict_xtnl['fullname'])
        
        print(alg_name.stars)
        #print(sym_expr)
        obj_lexpr.idi_pnl = diff(sym_expr, sym_var)                # penalization with respect to individual rival session
        print(pretty(obj_lexpr.idi_pnl))
        
    
    