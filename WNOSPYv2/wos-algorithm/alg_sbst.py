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
# Function: expand an symbolic expression by substituing its component with specific expressions
#######################################################

import sys
sys.path.insert(0, './wos-network')
sys.path.insert(0, './wos-decomp')

# from wos-network
import net_func

# from wos-decomp
import dcp_vps, dcp_name

# from current directory 
import alg_name

# from sympy
from sympy import *

def expd_expr(obj_lexpr):
    '''
    obj_lexpr: object of the expression
    
    func: generate the long expression of a symbolic expression by substituing its component expressions
    return: the generated long symbolic expression
    '''           
    # repeat to process all non-leaf sub-expressions
    while True:
        # get the next non-leaf sub-expression, and terminate if none        
        dict_nonleaf = get_nonleaf(obj_lexpr)
        if dict_nonleaf == None:
            print('No more nonleaf element!')
            break
        else:
            print('dict_nonleaf:', dict_nonleaf)
                        
        # construct the long expression for the leaf sub-expression            
        str_lexpr = cstr_lexpr(obj_lexpr, dict_nonleaf)
        
        
        # substitute the non-leaf sub-expression with the constructed long expression
        sbst(obj_lexpr, dict_nonleaf, str_lexpr)
        #print('Debug:', obj_lexpr.expr)
    
    #exit(0)
               
def get_nonleaf(obj_lexpr):
    '''
    obj_lexpr: object of the complete expression
    
    func: get the first non-leaf sub-expression of obj_lexpr
    return: symbolic non-leaf sub-expression, or None
    
    Called By: expd_expr() in this file
    '''        
    # get the string expression
    str_expr = str(obj_lexpr.expr)
    
    # find out all key elements
    dict_elmt = find_elmt(str_expr)
    
    # name and index of nonleaf element 
    nonleaf_name = None
    nonleaf_idx = None
    
    # check every element
    num_elmt = len(dict_elmt['lst_name'])           # total number of elements
    for nm in range(num_elmt):
        if not is_leaf(obj_lexpr, dict_elmt['lst_name'][nm]):
            nonleaf_name = dict_elmt['lst_name'][nm]
            nonleaf_idx = dict_elmt['lst_idx'][nm]
            break       
    
    if nonleaf_name == None:        # no nonleaf element was found      
        # Record the list of leaf elements for future use
        # See definition of lexpr.lst_leaf for more information
        obj_lexpr.lst_leaf = dict_elmt['lst_name']
        obj_lexpr.lst_leaf_fn = dict_elmt['lst_fullname']
        return None
    else:                           # found, return name and index 
        return {'name':nonleaf_name, 'idx':nonleaf_idx}

def is_leaf(obj_any, str_elmtname):
    '''
    obj_any: object of any network element, via which other elements can be accessed
    str_elmtname: element name in string
    
    func: check if the element is leaf or not
    return: True or False
    '''  
    obj_elmt = obj_any.get_netelmt(str_elmtname)       # object with name str_elmtname    
    b_isleaf = obj_elmt.is_leaf()    
    print('{} is leaf: {}'.format(str_elmtname, b_isleaf))
    return b_isleaf
        
def cstr_lexpr(obj_any, dict_elmt):
    '''
    obj_any: object of any network element, via which other elements can be accessed
    dict_elmt: dictionary of element {'name', 'index'}
    
    func: construct the long expression of the element
    return: constructed long expression in string
    '''    
    
    # extract object for the element
    obj_elmt = obj_any.get_netelmt(dict_elmt['name'])
    
    # extract formular
    dict_fmlr = obj_elmt.get_expr()
    
    # include index into the formula
    str_lexpr = attach_id(dict_fmlr, dict_elmt['idx'])
    
    return str_lexpr
    
    
def sbst(obj_lexpr, dic_nonleaf, str_lexpr):
    '''
    obj_lexpr: object of expression
    sym_nonleaf: current nonleaf sub-expression
    str_lexpr: new string long expression
    
    func: substitue sym_nonleaf with str_lexpr for obj_lexpr
    return: updated expression in obj_lexpr    
    '''
   
    str_expr = str(obj_lexpr.expr)                                                              # old complete expression        
    old_str  = dcp_name.prefix + dic_nonleaf['name'] + dcp_name.suffix + dic_nonleaf['idx']     # sub-expression to be replaced    
    new_str  = str_lexpr                                                                        # the sbustitution
    
    print(alg_name.sep)
    print('str_expr:', str_expr)
    print('old_str', old_str)
    print('new_str', new_str)
    
    # replace
    new_str_expr = str_expr.replace(old_str, new_str)
       
    # convert to symbolic and update the object
    obj_lexpr.expr = sympify(new_str_expr)
       
def find_elmt(str_expr):
    '''
    str_expr: string expresssion
    
    func: find all elements in str_expr
    return: dictionary of list of element name and index
    
    Called By: alg_sbst.get_nonleaf()
    '''
    # find all element names and corresponding index, and full name (name and index)
    lst_name = []         
    lst_idx = []
    lst_fulname = []
   
    # loop over the whole expression string 
    cur_start = 0           
    while True:  
        # starting position of prefix
        start_pre = str_expr.find(dcp_name.prefix, cur_start)   
        if start_pre == -1:                                     # not found
            break
        
        # search the matching suffix after current prefix
        start_suf = str_expr.find(dcp_name.suffix, start_pre + len(dcp_name.prefix))      
        if start_suf == -1:                                     # no matching suffix found
            print('Error: No matching suffix {} found for current prefix {}!'.format(dcp_name.prefix, dcp_name.suffix))    
            exit(0)
        
        # both prefix and suffix are found, extract the element name and index and append them to the list
        cur_name = str_expr[start_pre + len(dcp_name.prefix) : start_suf]
        cur_idx = str_expr[start_suf + len(dcp_name.suffix): start_suf + len(dcp_name.suffix) + dcp_name.zflen]
        lst_name += [cur_name] 
        lst_idx += [cur_idx]
        lst_fulname += [dcp_name.prefix + cur_name + dcp_name.suffix + cur_idx]
        
        # update current starting posisition
        cur_start = start_suf + len(dcp_name.suffix)
    
    # return
    if len(lst_name) == 0:
        return None
    else:
        # changes: 
        dict_elmt = {'lst_name':lst_name, 'lst_idx':lst_idx, 'lst_fullname': lst_fulname}
        print(alg_name.sep)
        print('str_expr:', str_expr)
        print('dict_elmt:', dict_elmt)
        
        return dict_elmt
    
def attach_id(dict_fmlr, str_id):
    '''
    dict_fmlr: dictionary of expression infomation
    str_id: index 
    
    func: add index information to element
    return: (new formular)
    '''  
    str_expr = dict_fmlr['fmlr']                    # original expression 
    lst_var = dict_fmlr['varlst']                   # list of variables
     
    # # attach the id to every variable in the list
    # for str_var in lst_var:
        # var_withid = dcp_name.prefix + str_var + dcp_name.suffix + str_id         # forming the variable with id
        # new_expr = str_expr.replace(str_var, var_withid)                          # replace the corresponding variable
        
    # new substitution method
    new_expr = str_expr.replace(dcp_name.suffix, dcp_name.suffix + str_id)

    print('new_expr:', new_expr)
    return new_expr