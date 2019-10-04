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
# horizontal decomposition
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from external folder
import net_name, net_func

# from local folder
import dcp_name, dcp_phy, dcp_tspt, dcp_hsub

# from sympy
from sympy import *

def hdcp(obj_xpd):
    '''
    func: horizontal decomposition
    return: generate a set of subproblems, with corresponding objects created and added into xpd 
    obj_xpd: object of the expanded network control problem 
    '''    
    # process all vertical subproblems 
    for str_vsub in obj_xpd.lst_vsub:
       hdcp_vsub(obj_xpd, str_vsub)
       #print(str_vsub)
       
    # display horizontal subproblems
    obj_xpd.disphsub()
    
    # print('dcp_hdcp.py, line 34')
    # exit(0)        
              
def hdcp_vsub(obj_xpd, str_vsub):
    '''
    func: horizontally decmopose a vertical subproblems
    return: generate a set of subproblems, with corresponding objects created and added into xpd 
    obj_xpd: object of the expanded network control problem
    str_vsub: name string of the vertical subproblem
    '''
    
    # create a hsub class in xpd if not yet
    str_hsubcls = dcp_hsub.get_hsubclsname(str_vsub)            # form the class name first    
    obj_xpd.crt_hsubcls(str_hsubcls)
               
    # obtain the symbolic vertical sub network control problem
    obj_vsub = obj_xpd.get_netelmt(str_vsub)   
    symncp = obj_vsub.symexpr    
    symncp = symncp.expand()                                    # convert to expanded format
    
    # For debug
    #print(obj_vsub.layer)
    #exit(0)
    
    # process every component of the symbolic expression    
    print('Decomposing vsub {}...'.format(str_vsub))
    for symexpr in symncp.args:
        sys.stdout.write('.')
        sys.stdout.flush()
        alloc_to_hsub(obj_xpd, str_hsubcls, symexpr)            # allocate the symexpr component to a subproblem   
    
def alloc_to_hsub(obj_xpd, str_hsubcls, symexpr):
    '''
    func: allocate a symbolic expression to a horiziontal subproblem
    return: updated (or a new) horizontal subprobmem
    obj_xpd: object of the expanded network control problem
    str_hsubcls: the class of hsubs the current hsub belongs to
    symexpr: the symbolic expression
    '''
    
    # get the object of hsub
    #print('################', symexpr)
    obj_hsub = dcp_hsub.get_hsub(obj_xpd, str_hsubcls, symexpr)
    
    # add current expression to the subproblem
    obj_hsub.add_expr(symexpr)
    #print(obj_hsub.symexpr)