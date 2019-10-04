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
# horizontal subproblem of a vertical subproblem
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from external folder
import net_name, net_func, alglib_name

# from local folder
import dcp_name

# from sympy
from sympy import *

def get_hsubclsname(str_vsub):
    '''
    func: form the name for a class of hsubs
    return: the name string
    str_vsub: name of the corresponding vsub, from which the hsubs are decomposed 
    '''
    return dcp_name.hcls + dcp_name.suffix + str_vsub

def get_hsubname(sym_expr, obj_xpd):
    '''
    func: form the name for a hsub
    return: the formed name string
    sym_expr: symbolic expression based which the hsub name is constructed
    
    Dec 5, 2017:
    Use parameter obj_xpd as a link to other network elements, e.g., to get parent element with given element name
    '''
    
    # convert from symbolic domain to string
    str_expr = str(sym_expr)
    
    # find the key network element that identifies horizontal subproblems
    # key element format: __XXX___XX
    pos_pfx = str_expr.find(dcp_name.prefix)                                     # starting position of prefix, i.e., __
    pos_sfx = str_expr.find(dcp_name.suffix)                                     # starting position of suffix, i.e., ___

    
    # Get the name of the key element, e.g., lkcap, lkpwr
    str_keyelmt = str_expr[(pos_pfx+len(dcp_name.prefix)): pos_sfx]
    
    # Find the associated physical element, i.e., link
    phy_elmt = obj_xpd.get_netelmt(str_keyelmt)
    
    # Use the type information of the physical element as the name of the horizontal subproblem
    str_type_elmt = phy_elmt.parent.type
    
    # Add the prefix, suffix and element index to the name
    str_keyelmt = str_expr[pos_pfx: pos_pfx + len(dcp_name.prefix)] + str_type_elmt + str_expr[pos_sfx: + pos_sfx + len(dcp_name.suffix)+dcp_name.zflen]

    # construct hsub name
    str_hsub = dcp_name.hsub + str_keyelmt
    
    return str_hsub
    

def get_hsub(obj_xpd, str_hsubcls, symexpr):
    '''
    func: get the horizontal subproblem; if does not exist, create one
    return: the object of the horizontal subproblem
    str_hsubcls: the class which the hsub belongs to
    symexpr: expression to be added to the hsub
    '''
    
    # construct the name for the horizontal subproblem
    str_hsub = get_hsubname(symexpr, obj_xpd)
    #print(str_hsub)
    
    # if alreay exists, return the subproblem object
    lst_hsubcls = getattr(obj_xpd, str_hsubcls)                         # get the list of hsubs
    #print(lst_hsubcls)
    if str_hsub in lst_hsubcls:
        return obj_xpd.get_netelmt(str_hsub)
        
    # otherwise, create a new subproblem and record it in the network control problem (xpd)
    #---------------------------------------------------------------      
    elmt_name = str_hsub                                                # element info
    elmt_num = 1     
        
    addi_info = {'ntwk':obj_xpd.ntwk, 'parent':obj_xpd, 'hsubcls':str_hsubcls}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = hsub(info)                                                   # create element
    obj_xpd.addgroup(elmt_name, elmt)                                   # add element as a subgroup 
            
    obj_hsub = elmt
    obj_hsub.ping()
    #---------------------------------------------------------------          
    
    # add the vsub to xpd, and update the corresponding list of hsubs 
    obj_xpd.add_hsub(str_hsub, obj_hsub)
    
    return obj_hsub
    
    
class hsub(net_func.netelmt_group):
    '''
    definition of horizontal subproblem
    '''
    def __init__(self, info):  
        # from base network element
        net_func.netelmt_group.__init__(self, info)  
        
        self.symexpr = None                                             # symbol representation of the subproblem
        
        self.hsubcls = info['addi_info']['hsubcls']                     # from which vsub this hsub is decomposed?
        
        #-- start debug
        #print('hsub subproblem class:', self.hsubcls)
        #exit(0)
        #-- end debug
        
        self.layer = self.set_layer()                                   # layer the subproblem is at
        
 
        # code object (i.e., numerical algorithm code) assocaited 
        # the subproblem, updated by method set_code() defined below
        self.code = None  

        # Long expression of the subproblem, where intermediate variables have been
        # replaced with leaf nodes. Initialized to None, and updated in 
        # alg_lexpr.lexpr.__init__(). Will be used in self.code.gnrt_alg(), with code referring
        # to alglib_func.fmincon_py.
        self.lexpr = None  

        # Symbolic long expression, will be updated when getting long expression in self.get_lexpr()
        # This is used to generate simplified version of the expression and hence to analyze the
        # patten of Lagrangian coefficients.
        self.lexpr_sym = None 

    def gnrt_alg(self):
        '''
        Generate interior point algorithm that solves this subproblem, by calling
        method of self.code
        
        Called By: alglib_main.gnrt_alg_code()
        '''        
        self.code.gnrt_alg()        
        
    def set_code(self, obj_code):
        '''
        Link a newly created code object to a subproblem.
        Called By: alglib_func.get_next_subprob()
        '''        
        self.code = obj_code

    def gen_code_name(self, layer):
        '''
        For each subproblem (actully only one representative subproblem will be considered
        at each layer), a code template will be generated. This function generates the name of the
        code template. The name has the form of code_phy for physical layer.
        
        Called by: alglib_func.get_next_subprob()
                   alglib_func.fmincon_py.gnrt_alg_name()
        '''
        
        return alglib_name.code_prefix + alglib_name.code_connection + layer
        
    def set_layer(self):
        '''
        Func: Specify layer information of subproblem. The layer is determined 
        by searching layer key word, e.g., 'phy', in self.hsubcls. The list of layer 
        keyword is specified in wos-network/net_name. The layer information will be used
        to check if a subproblem has been process in that layer - only one subproblem will
        be processed in each layer.
        
        Called By: __init__() of this class
        '''
        
        # 1 - a matching layer is found; 0 - not found
        b_found = 0
        
        # loop over all layer keywords and see if any keyword is included in self.hsubcls, 
        # which has been formed to include layer information
        for lyr in net_name.lst_layer:
            if lyr in self.hsubcls:
                b_found = 1
                break
                
        if b_found == 1:
            return lyr
        else:
            return None
                       
    def add_expr(self, symexpr):
        '''
        add a symbolic expression component to this subproblem
        funtion: updated symbolic expression self.symexpr
        '''
        if self.symexpr == None:
            self.symexpr = symexpr
        else:
            self.symexpr += symexpr
            
    def disp_expr(self):
        '''
        func: display expression
        return: None        
        '''        
        print(factor(self.symexpr))
        
    def get_expr(self):
        '''
        func: get the symbolic expression of the hsub
        return: the symbolic expression
        '''
        return self.symexpr
    
    def get_lexpr(self):
        '''
        Return the long (i.e., expanded) expression of the associated subproblem. 
        Used to generate solution algorithms in alglib_func.fmincon_py.gnrt_alg()
        
        Called By: alglib_func.fmincon_py.gnrt_alg()
        '''
        
        if self.lexpr == None:
            print('Error: Long expresson of the subproblem is None!')
            exit(0)
            
        # else, take the string expression and convert it to symbolic    
        str_expr = self.lexpr.expr
        self.lexpr_sym = sympify(str_expr)
                        
        #print('Debug:')
        #print(self.lexpr_sym)
        #input('...')
        
        return self.lexpr_sym
            
    def get_optvar(self):
        '''
        Get optimization variable of this subproblem
        
        Called By: alglib_func.fmincon_py.gnrt_alg()
        ''' 
        # Get variable list from long expression of this subproblem
        lst_var = self.lexpr.get_optvar()
        #print('Debug:', lst_var)
        #exit(0)
        
        
        return lst_var
        