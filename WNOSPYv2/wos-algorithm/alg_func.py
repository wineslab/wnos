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
# common functions for algorithm generation
#######################################################

import sys
sys.path.insert(0, './wos-network')
sys.path.insert(0, './wos-decomp')

# from wos-network
import net_func

# from current directory 
import alg_name, alg_lexpr

def crt_netalg(obj_xpd):
    '''
    func: create the algorithm object
    return: the algorithm object
    obj_xpd: object of the xpanded network control problem
    '''
    #---------------------------------------------------------------    
    elmt_name = alg_name.netalg                                     # element info    
    elmt_num = 1     
                                  
    addi_info = {'ntwk':obj_xpd.ntwk, 'parent':obj_xpd.ntwk, 'xpd':obj_xpd}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = netalg(info)                                             # create element
    elmt.parent.addgroup(elmt_name, elmt)                           # add element as a subgroup 

    elmt.ping()
    #--------------------------------------------------------------- 

    return elmt
    
        
class netalg(net_func.netelmt_group):
    '''
    definition of algorithm class for the whole network control problem
    '''
    def __init__(self, info):  
        # from base network element
        net_func.netelmt_group.__init__(self, info)  
        
        # expand network control problem
        self.xpd = info['addi_info']['xpd']
        
        # list of long expressions for hsubs
        self.lst_lexp = []
        
        # current hsub, for which the lexpr will be processed
        # updated by self.get_nexthsub()
        self.id_curhsub = -1
        self.obj_curhsub = None
        
        # Current algorithm code object corresponding to current subproblem
        # Note that for all subproblems in the same layer only one algorithm
        # code objec will be created
        #
        # This variable is not needed, because the current code object can be
        # accessed via the current subproblem, i.e., hsub.code defined in dcp_hsub.py
        self.obj_curcode = None  

        # The list of layers that have been processed, i.e., for which the numerical
        # solution algorithm has been generated. Only one representative subproblem will
        # be processed at a layer.         
        # Iniatialized to empty, updated in alglib_func.get_next_subprob()
        self.lst_processed_layer = []          
        

    def reset_hsub_index(self):
        '''
        Func: Reset the index of current horizental subproblem to be processed, i.e., 
        self.id_curhsub. This function will be called before looping over all the subproblems.
        '''
        self.id_curhsub = -1
        self.obj_curhsub = None
        self.obj_curcode = None
        
    def add_lexpr(self, str_new_lexpr):
        '''
        func: add a new long expression to the list 
        return: updated list of long expressions
        str_new_lexpr: string of the new long expression
        '''
        # check if new lexpr
        if str_new_lexpr in self.lst_lexp:
            print('Error: lexpr alreay exist!')
            exit(0)
        
        # add new lexpr to the list
        self.lst_lexp += [str_new_lexpr]
        
    def get_lexpr(self, str_lexpr):
        '''
        func: get the object of lexpr with name str_lexpr
        return: the lexpr object
        str_lexpr: name of the lexpr object
        '''        
        return self.get_netelmt(str_lexpr)
    
    def get_nexthsub(self):
        '''
        func: get next hsub
        return: object of next hsub        
        '''
        self.id_curhsub += 1                                # id of next hsub
        obj_hsub = self.xpd.get_hsub(self.id_curhsub)       # get the hsub
        self.obj_curhsub = obj_hsub                         # update current hsub 
        
        if self.obj_curhsub == None:                        # if all hsubs have been processed, return True            
            return True
        else:                                               # otherwise, return False
            return False
            
    def gen_lexprname(self):
        '''
        func: generate a unique name for the new lexpr object
        return: string of the name        
        '''
        str_id = str(len(self.lst_lexp))                    # id of lexpr, if n lexpr in the current list, the id is 'n'
        return alg_name.lexpr + alg_name.suffix2 + str_id.zfill(alg_name.lenid)
        
    def new_lexpr(self):
        '''
        func: create an lexpr object for the current hsub
        return: the created lexpr object
        '''
        # generate a unique name for the lexpr
        str_lexprname = self.gen_lexprname()
        
        # record the new lexpr name in a list 
        self.add_lexpr(str_lexprname)
        
        # create lexpr object
        obj_lexpr = alg_lexpr.new_lexpr(self.obj_curhsub, str_lexprname)               
                
        return obj_lexpr