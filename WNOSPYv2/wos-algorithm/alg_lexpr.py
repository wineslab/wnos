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
# Function: genrate long expressions by wirting out all intermedium expressions, e.g., SINR
#######################################################

import sys
sys.path.insert(0, './wos-network')
sys.path.insert(0, './wos-decomp')

# from wos-network
import net_func

# from current directory 
import alg_name, alg_sbst, alg_pnl

# from sympy
from sympy import *

def gen_longexpr(obj_netalg):
    '''
    func: genrate long expressions by wirting out all intermedium expressions, e.g., SINR
    return: object with long expressions for each horizontal subproblem
    obj_netalg: object of network algorithm
    '''    
    while True:
        # get a horizontal subproblem (hsub)
        b_lastdone = obj_netalg.get_nexthsub()

        # if the last hsub has been processed, terminate      
        if b_lastdone == True:
            break
                        
        # otherwise, create an lexpr object (long expression) for the hsub
        obj_lexpr = obj_netalg.new_lexpr()
        
        # generate the long expression for the hsub        
        obj_lexpr.expd_expr()
        

def new_lexpr(obj_hsub, str_lexprname):
    '''
    func: create a new lexpr object for the hsub
    return: new lexpr object
    obj_hsub: hsub object
    str_lexprname: name of lexpr
    '''    
    #---------------------------------------------------------------    
    elmt_name = str_lexprname                                        # element info    
    elmt_num = 1     
                                  
    addi_info = {'ntwk':obj_hsub.ntwk, 'parent':obj_hsub.ntwk, 'hsub':obj_hsub}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = lexpr(info)                                               # create element
    elmt.parent.addgroup(elmt_name, elmt)                            # add element as a subgroup 

    elmt.ping()
    #---------------------------------------------------------------      
    
    return elmt
                        
class lexpr(net_func.netelmt_group):
    '''
    definition of long subproblem expression
    '''
    def __init__(self, info):  
        # from base network element
        net_func.netelmt_group.__init__(self, info)  
        
        # the corresponding horizontal subproblem
        self.hsub = info['addi_info']['hsub']
        
        # while self.hsub (see above) points from a long expression
        # to a subproblem, we also need inverse pointing. This will be
        # used when generating solution algorithms in alglib_func.fmincon_py.gnrt_alg()
        self.hsub.lexpr = self
        
        # initialize symbolic expression of the horizontal subproblem
        self.expr = self.hsub.get_expr()                         # expressions not expanded   
        self.idi_pnl = None                                      # penalization item for individual rival session        
        self.idi_pnl_xtnl = None                                 # penalization item for individual rival session with external variables integrated    
        
        # List of leaf elements contained in this long expression; 
        # Initialized to be [], updated in alg_sbst.get_nonleaf();
        # In self.get_optvar(), optimization variables will be determined by 
        # checking every elements. 
        # The corresponding full name variable is actually used to generate algorithm 
        self.lst_leaf = []
        self.lst_leaf_fn = []      # full name version of self.lst_leaf 
        
        # list of self variables
        self.lst_selfvar = []
        
        # list of rival variables
        self.lst_rvlvar = []
        
        # list of parameters
        self.lst_par = []                                       # parameters in self.long_expr                    
        self.lst_par_forpnl = []                                # parameters in self.long_expr_forpnl
        
    def get_optvar(self):
        '''
        Func: Get the list of optimization variables, by checking each and every 
        leaf elements. The result will be used to specify the optimization variable
        when generating solution algorithm in alglib_func.gnrt_alg().
        
        Called By: alglib_func.gnrt_alg()
        '''
        
        
        # Initialize list of optimization variables to be returned
        lst_optvar = [];
        
        # loop over all leaf elements contained in this long expression
        for idx in range(len(self.lst_leaf)):
            var_name = self.lst_leaf[idx]                   # variable name
            var_obj = self.get_netelmt(var_name)            # the corresponding instance
            if var_obj.is_var == True:
                lst_optvar.append(self.lst_leaf_fn[idx])    # record the full name version of the optimization variable
                
        return lst_optvar
        
    def expd_expr(self):
        '''
        func: expand symbolic expression by substituting key elements in self.expr with their expressions
        return: updated self.expr
        '''
        alg_sbst.expd_expr(self)
            
    def expd_expr_pnl(self):
        '''
        func: expand symbolic expression for generating penalized items
        return: updated lexpr object with new self.long_expr_pnl and other parameters
        '''
        alg_pnl.pnl(self)        
    

