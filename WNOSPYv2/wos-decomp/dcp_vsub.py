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
# vertical subproblem
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from external folder
import net_name, net_func

# from local folder
import dcp_name

# from sympy
from sympy import *

def get_vsub(obj_xpd, str_layer):
    '''
    get the subproblem; if the subproblem for this layer does not exist, create one
    return the object of the subproblem
    
    called from: dcp_vps.alloc_to_sub()
    '''
    
    # construct the name for the subproblem
    str_sub = dcp_name.vsub + dcp_name.prefix + str_layer
    
    # if alreay existent, return the subproblem object
    if str_sub in obj_xpd.lst_vsub:
        return obj_xpd.get_netelmt(str_sub)
        
    # otherwise, create a new subproblem and record it in the network control problem (xpd)
    #---------------------------------------------------------------      
    elmt_name = str_sub                                                 # element info
    elmt_num = 1     
        
    addi_info = {'ntwk':obj_xpd.ntwk, 'parent':obj_xpd, 'layer': str_layer}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = vsub(info)                                                   # create element
    obj_xpd.addgroup(elmt_name, elmt)                                   # add element as a subgroup 
            
    obj_vsub = elmt
    obj_vsub.ping()
    #---------------------------------------------------------------          
    
    # add the vsub to xpd
    obj_xpd.add_vsub(str_sub, obj_vsub)
    
    return obj_vsub
    
    
class vsub(net_func.netelmt_group):
    '''
    definition of vertical subproblem
    '''
    def __init__(self, info):  
        # from base network element
        net_func.netelmt_group.__init__(self, info)  
        
        self.symexpr = None               # symbol representation of the subproblem
                
    def add_expr(self, symexpr):
        '''
        add a symbolic expression component to this subproblem
        funtion: updated symbolic expression self.symexpr
        '''
        if self.symexpr == None:
            self.symexpr = symexpr
        else:
            self.symexpr += symexpr