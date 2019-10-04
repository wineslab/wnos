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
# vertical decomposition
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from external folder
import net_name, net_func

# from local folder
import dcp_name

# from sympy
from sympy import *

def add_dualcoef(obj_xpd):
    '''
    add Lagrangian coefficien to the network contro problem
    return: add a new attribute to each instance object to point to the coefficient object
    obj_xpd: object of the expanded network control problem
    '''

    # process all instances of the xpd        
    for str_inst in obj_xpd.lst_inst[1:]:                  # skip the first instance, which is utility
        obj_inst = obj_xpd.get_netelmt(str_inst)           # get the instance object
        
        #---------------------------------------------------------------    
        elmt_name = str_inst + '_' + dcp_name.lbd                         # element info   
        elmt_num = 1     
                                      
        # changes:
        # dcname added to represent dual coefficient name 
        addi_info = {'ntwk':obj_inst.ntwk, 'parent':obj_inst, 'dcname': elmt_name}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

        elmt = dualcoef(info)                                             # create element
        
        # changes:
        # no need to record the element name as a subgroup
        #obj_inst.addgroup(elmt_name, elmt)                               # add element as a subgroup 
        
        setattr(obj_inst, dcp_name.dualcoef, elmt)                        # add a new attribute to the parent element, i.e., the instance

        elmt.ping()
        #---------------------------------------------------------------     

        print(obj_inst.dualcoef.symexpr)    
                
class dualcoef(net_func.netelmt_group):
    '''
    definition of dual coefficient
    '''
    def __init__(self, info):  
        # from base network element
        net_func.netelmt_group.__init__(self, info)  
        
        self.expr = info['addi_info']['dcname']                          # name of the dual coefficient
        self.symexpr = Symbol(self.expr, nonnegative=True)               # symbol representation of the name, a nonnegative symbolic variable
    
        
        