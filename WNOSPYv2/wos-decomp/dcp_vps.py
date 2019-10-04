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
import dcp_name, dcp_lambda, dcp_vsub

# from sympy
from sympy import *

# # print tree structure
#from sympy.printing.dot import dotprint
           
def psncp(obj_xpd):
    '''
    parse the network control problem in symbolic domain for vertical decomposition
    return the objects of sub network control problems
    obj_xpd: object of the expanded NUM
    '''
    
    # obtain the symbolic network control problem
    symncp = disp_symncp(obj_xpd)         
    symncp = symncp.expand()              # convert to expanded format
    
    print(symncp)
    #print(dotprint(symncp))
    
    net_name.outf.write('\n\n'+ str(symncp))
    
    # process every component of the symbolic expression    
    print('Parsing xpd')
    for symexpr in symncp.args:
        #print('\n')        
        #print(x)     
        sys.stdout.write('.')
        sys.stdout.flush()
        # print('Debug:', symexpr)
        # input('...')
        alloc_to_sub(obj_xpd, symexpr)    # allocate the symexpr component to a subproblem
    
    obj_xpd.dispsub()
    
    #print('dcp_vps.py, line 42')
    #exit(0)    
    
def disp_symncp(obj_xpd):
    '''
    display the dual symbolic network control problem
    return the symbolic expression of the network control problem
    '''    
    # initialize the symbolic network control problem by including only utility
    obj_utlt = obj_xpd.get_netelmt(obj_xpd.lst_inst[0])             # utility object
    obj_syminst = getattr(obj_utlt, dcp_name.inst_sym)              # symbolic instance of the utility
    symncp = obj_syminst.symexpr    
    #print(symncp)
    
    # including all constraints
    for str_inst in obj_xpd.lst_inst[1:]:
        obj_inst = obj_xpd.get_netelmt(str_inst)                    # get the instance object
        obj_syminst = getattr(obj_inst, dcp_name.inst_sym)          # symbolic instance of the constraint
        obj_symdc = getattr(obj_inst, dcp_name.dualcoef)            # symbolic dual coefficient
        symncp += obj_symdc.symexpr * obj_syminst.symexpr
        
    #print(symncp)    
    return symncp    

def alloc_to_sub(obj_xpd, symexpr):    
    '''
    allocate a component expression of the symobolic network control problem
    return: udpated subproblem with the component expression added
    '''
    # determine which layer the expression belongs to
    str_layer = dtm_layer(obj_xpd, symexpr)
    
    # get the subproblem; if the subproblem for this layer does not exist, create one
    obj_sub = dcp_vsub.get_vsub(obj_xpd, str_layer)    
    #print(obj_sub.symexpr)
    
    # add the expression to the subproblem
    obj_sub.add_expr(symexpr)

def dtm_layer(obj_xpd, symexpr):
    '''
    determine which layer the expression belongs to
    return: string of layer
    
    called by: dcp_vps.alloc_to_sub()
    '''
    # find out the name of the network element contained in the expression
    str_elmt = find_elmt(symexpr)
    #print(str_elmt)
    
    
    # get the object of the element
    obj_elmt = obj_xpd.get_netelmt(str_elmt)
    #print(obj_elmt.layer)
    
    return obj_elmt.layer   

def find_elmt_info(symexpr):
    '''
    find out the name and index of the network element contained in the expression
    return: the string name and string index of the element
    '''
    # locate '__' and '___'
    str_expr = str(symexpr)                         # convert to string
    pos_pre = str_expr.find('__')                   # position of prefix
    pos_suf = str_expr.find('___')                  # position of suffix
    
    # not found
    if pos_pre == -1 or pos_suf == -1:
        return None
    else:
        str_elmt_name = str_expr[pos_pre+2: pos_suf]    # element string
        str_elmt_id = str_expr[pos_suf+3: pos_suf+5]    # element string        
        return {'name':str_elmt_name, 'idx': str_elmt_id}    

def find_elmt(symexpr):
    '''
    find out the name of the network element contained in the expression
    return: the string name of the element
    '''
    
    dict_info = find_elmt_info(symexpr)
    
    if dict_info == None:
        return None
    else:
        return dict_info['name']

def find_elmtid(symexpr):
    '''
    func: find out the index of the network element contained in the expression
    return: the string index of the element   
    '''
    dict_info = find_elmt_info(symexpr)
    
    if dict_info == None:
        return None
    else:    
        return dict_info['idx']