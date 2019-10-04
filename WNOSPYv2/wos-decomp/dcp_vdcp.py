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
import dcp_name, dcp_lambda, dcp_vps

# from sympy
from sympy import *
      
def vdcp(obj_xpd):
    '''
    vertical decomposition of an expanded NUM 
    return the object of the decomposed NUM
    obj_xpd: object of the expanded NUM
    '''
    
    # convert the network control problem from string to symbolic domain
    ncp_to_symb(obj_xpd)    
    
    # add Lagrangian coefficient
    dcp_lambda.add_dualcoef(obj_xpd)
    
    # parse the network control problem in symbolic domain for vertical decomposition
    dcp_vps.psncp(obj_xpd)
    
    return None
    

def ncp_to_symb(obj_xpd):
    '''
    convert the utility and constraints of a network control problem from string to symbolic domain
    obj_xpd: object of the expanded network control problem
    return: add new attributes in each connstraint object to record the symbolic expression
    '''    
    # process all instances of the xpd    
    for str_inst in obj_xpd.lst_inst:
        obj_inst = obj_xpd.get_netelmt(str_inst)           # get the instance object
        #print('\n', obj_inst.get_expr())
        inst_to_symb(obj_inst, str_inst)             
    
    #exit(0)
    
def inst_to_symb(obj_inst, str_instname):
    '''
    convert an expression (utility or constraint) from string to symbolic domain
    obj_inst: object of the expression instance
    return: add new attributes in the instance object to record the symbolic expression
    '''     
    #print(str_instname)
    
    # create a seprate object for the instance 
    # all processing to convert the instance to symbolic domain will be done in the new object
    # a new attribute with name 'inst_sym' will be added to the instance object to record the new object
    #---------------------------------------------------------------    
    elmt_name = str_instname + '_' + dcp_name.sym                     # element info   
    elmt_num = 1     
                                  
    addi_info = {'ntwk':obj_inst.ntwk, 'parent':obj_inst}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = inst_sym(info)                                             # create element
    
    # changes:
    # no need to record the element name as a subgroup
    #obj_inst.addgroup(elmt_name, elmt)                               # add element as a subgroup 
    
    setattr(obj_inst, dcp_name.inst_sym, elmt)                        # add a new attribute to the parent element, i.e., the instance

    #elmt.ping()
    #---------------------------------------------------------------     
    
    #print(obj_inst.inst_sym.symexpr)
   

class inst_sym(net_func.netelmt_group):
    '''
    instance in symbolic domain
    '''
    def __init__(self, info):  
        # from base network element
        net_func.netelmt_group.__init__(self, info)  
        
        # instance expression
        self.expr = self.parent.obj_expr.expr           
        
        # substitute variable with instances
        self.var_sub()
        
        # substitue wos functions with sympy functions
        self.func_mnp()
        
        # Replace '[]' with '' after substituting instance vector with individuals
        # to avoid error when converting to symbolic
        self.expr = self.expr.replace('[', '')
        self.expr = self.expr.replace(']', '')
        
        # print(self.expr)
        # input('Debug: Here...')        
        
        self.symexpr = sympify(self.expr)                # record the symbolic expression
        #print(self.symexpr)
        
    def var_sub(self):
        '''
        substitue variables in the expression with instances 
        return: updated self.expr
        '''                  
  
        
        # substitiute all variables
        obj_inst = self.parent                      # get the instance object
        lst_var = obj_inst.get_varlst()             # variable list
        for var in lst_var:                         # substitiute every variable 
            str_varinst = obj_inst.get_instvar(var) # list of variable instance 
            num_elmt = len(str_varinst)             # the length of the list            
            str_sub = ''                            # the substitiute string, initialized to be empty string
            for idx in range(num_elmt):
                str_sub += str_varinst[idx]
                if idx < num_elmt - 1:              # if not the last element, add a seprator ','
                    str_sub += ', '
                    
            # Add '[' and ']' to indicate a vector replacement
            new_expr = self.expr.replace(var, '[' + str_sub + ']')      # replace the variable
            self.expr = new_expr                            # update expression of the instance
            
        # print(self.expr)
        # input('...')        
   
    def func_mnp(self):
        '''
        substitiute wos functions to sympy functions 
        e.g., sum -> Add, log(vectror) -> element-wise log
        more manipulations will be added in future
        '''
        
        # substitiute sum() with Add()
        self.subs_sum()
        self.subs_log()
        self.subs_comp()
        
    def subs_sum(self):
        '''
        substitiute sum() with Add() 
        return: update the expression self.expr
        '''
        new_expr = self.expr.replace('sum', 'Add')
        self.expr = new_expr
        
    def subs_log(self):
        '''
        substitiute log(vector) with log(element-wise)
        return: update the expression self.expr
        '''  
        
        # Determine the keyword of operation, e.g., log, exp...    
        print('Debug:', self.expr)        
        oper_name = None
        for oper in net_name.lst_oper:
            # print('Debug:', oper)
            # input('...')
            if self.expr.find(oper) != -1:
                oper_name = oper
                break;
        
        # If no operation keyword found, no need to subsutitue vector parameter with individuals, return directly
        if oper_name == None:
            return
        
        # determine the position of 'log', '(' and ')'
        #int_pos1 = self.expr.find('log')
        int_pos1 = self.expr.find(oper_name)                    # Use the found operation keyword to replace hard coded 'log'
        int_pos2 = self.expr.find('(', int_pos1)
        int_pos3 = self.expr.find(')', int_pos2)
        
        # substring to be substituted
        old_str = self.expr[int_pos1:int_pos3+1]                # +1 to include ')'
        #print(substr_subd)
        
        # # string of vector elements 
        # str_vec = self.expr[int_pos2+1:int_pos3]              # string between ()
        # lst_vec = str_vec.split(', ')                         # conver to list
        # #print(lst_vec)
        #
        # use '[' and ']' to locate the instance vector
        vec_pos_left = self.expr.find('[')
        vec_pos_right = self.expr.find(']')
        str_vec = self.expr[vec_pos_left+1:vec_pos_right]       # string between ()
        lst_vec = str_vec.split(', ')                           # conver to list        
        
        # # construct the new string
        # new_str = ''
        # for x in lst_vec:
            # new_str += 'log(' + x + ')' + ', '
        # new_str = new_str[0:len(new_str)-2]                   # remove the last ' , '
        # #print(new_str)
        #
        # Replace the instance vector in [] using individual element
        # construct the new string
        new_str = ''
        for x in lst_vec:
            old_log = old_str                                                # log(XXXXX)      
            str_vec_inbracket = self.expr[vec_pos_left:vec_pos_right+1]      # [a, b]
            new_log = old_log.replace(str_vec_inbracket, x) + ', '           # log(a), log(b)
            new_str += new_log         
        new_str = new_str[0:len(new_str)-2]                                  # remove the last ', '
        
        # substitue the old string with new string
        new_expr = self.expr.replace(old_str, new_str)
        
        # update the expression
        self.expr = new_expr              

      
    def subs_comp(self):
        '''
        remove <= and >= from the expression
        return: update the instance expression
        '''
        
        # check if '>=' or '<=' is in the expression, return error if not
        b_comp = 0                          # initialized to no comparision operator        
        if '>=' in self.expr:
            b_comp = 1
            int_pos = self.expr.find('>=')
        elif '<=' in self.expr:
            b_comp = 2
            int_pos = self.expr.find('<=')
        else:
            return None                     # could be utility, do nothing 
         
        # left and right parts of the constraints
        str_left = self.expr[0:int_pos]
        str_right = self.expr[int_pos+3:]

        
        # manipulate the expression to the form of x - y (>= 0)
        if b_comp == 1:
            new_expr = '(' + str_left + ')' + '-' + '(' + str_right + ')' 
        elif b_comp == 2:
            new_expr = '(' + str_right + ')' + '-' + '(' + str_left + ')' 
            
        # update instance expression
        self.expr = new_expr