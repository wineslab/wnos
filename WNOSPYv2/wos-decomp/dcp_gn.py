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
# instance generator
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from wos-network
import net_name, net_func

# from local folder
import dcp_name, dcp_set, dcp_inst

def create_gn(obj_expr):
    '''
    create a intance generator
    obj_expr: the expression object, for which the generator is created
    '''
    
    #--------------------------------------------------------------- 
    xpd = obj_expr.get_netelmt(dcp_name.xpd)    
    elmt_name = xpd.gen_gnname()                                        # element info
    elmt_num = 1     
       
    addi_info = {'ntwk':obj_expr.ntwk, 'parent':obj_expr, 'obj_expr': obj_expr}  
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        
 
    elmt = generator(info)                                              # create element
    #---------------------------------------------------------------      
    
    # configure the generator for the expression object
    obj_expr.set_gn(elmt)
    
    return elmt
    
class generator(net_func.netelmt_group):
    '''
    instance generator
    '''
    def __init__(self, info):  
        # from base network element
        net_func.netelmt_group.__init__(self, info)    
        
        # for which expression the generator is created?
        self.obj_expr = info['addi_info']['obj_expr']
        
        # EVERY element
        self.every_elmt = None               # every element to control how many instances will be generated
        
        # object of list of nonvery elements
        self.lst_nonevery = None      

        # Information about mapping from each every-type element to non-every-type elements, e.g., each session
        # passes which links. Each element corresponds to an every-type element (e.g., session rate), and is represented
        # using a list (i.e., the set of associated non-every elements).
        #
        # Updated in self.update_every2nonevery()
        self.every2nonevery = []
             
        # Index of current every-type element for which the non-every instance is generated. 
        # Updated in self.get_every_elmt(), used in self.update_every2nonevery() to record the generated non-every instance.
        self.idx_cur_every = None
        
        # Initialize slef.every2nonevery, see the definition of this function for details, including why None is passed.
        self.ini_every2nonevery(None)
        
    def ini_every2nonevery(self, lst_every):
        '''
        Initialize self.every2nonevery, see above for definition of this variable. For each index of every-type element, create an emtpy list.
        
        every: information about every element, a list of index of every-type elements
        
        Called By: dcp_set.gen_elmtset(), self.__init__()
        '''
        
        # This function was initially called from outside of this class, now we want to call it upon class initialization
        # In this case, the calling of this funciton from somewhere else will be bypassed. The length of lst_every is also
        # hard coded as dcp_name.allnum and None will be passed by self.__init__().
        if self.every2nonevery != []:
            return
        
        for idx in range(dcp_name.allnum):
            self.every2nonevery.append([]) 
            
        #print(self.every2nonevery)
        #input('Debug...')
        
    def update_every2nonevery(self, lst_nonevery):
        '''
        Update self.every2nonevery, see above for definition of this variable. 
        The information about every element is taken from self.idx_cur_every
        
        lst_nonevery: information about associated non-every elements, a list
        
        Called By: dcp_set.gen_elmtset()
        '''
        
        # Current every element must be set before being used
        if self.idx_cur_every == None:
            print('Current every-type element cannot be None!')
            exit(0)                   
        
        # Record current every-type element for each of the non-every element 
        for idx in lst_nonevery:
            self.every2nonevery[idx].append(self.idx_cur_every)
            
        # Update ntwk.every2nonevery - see net_ntwk.__init__() for definition of that variable
        self.ntwk.every2nonevery = self.every2nonevery
                
            
    def get_newlst(self):
        '''
        generate a new list of variable strings       
        '''
     
        # if EVERY element has not been created, create it
        if self.every_elmt == None:
            self.dtm_every_elmt()
            
        # get one instance for every elemnt, if None returned, it means all instances have been generated, return None
        obj_every_elmt = self.get_every_elmt()        
        if obj_every_elmt == None:
            return None
        
        # generate instances for non-every elements
        obj_nonevery_elmt = self.get_nonevery_elmt()
        obj_nonevery_elmt.dispmb()
        
        # construct the instance and return 
        obj_inst = self.form_inst(obj_every_elmt, obj_nonevery_elmt)       
        return obj_inst
        
    def set_every_elmt(self, obj_every_elmt):
        '''
        set the every element
        '''
        self.every_elmt = obj_every_elmt
    
    def dtm_every_elmt(self):
        '''
        determine every element
        return the object with information of the every element
        '''
        # if every element has not been configured, configure it
        # otherwise, do nothing
        if self.every_elmt == None:
            self.obj_expr.dtm_every_elmt(self)
            print('Every:', self.every_elmt.lst_mb)
        else:
            pass
         
        # reset the EVERY element set in case the element counter has been changed somewhere else
        self.every_elmt.reset()
                 
    def get_every_elmt(self):  
        '''
        generate a new instance for element with EVERY range
        return the element object
        '''
        
        # return a dictionary to obtain more information
        # get an element string from the EVERY set
        dic_every = self.every_elmt.get_next_elmt()
       
        # if None, return None
        if dic_every == None:
            return None
        else:
            str_elmt = dic_every['str_elmt']
            var_key = dic_every['var_key']
            var_idx = dic_every['var_idx']
        
        # otherwise, create an object for the element string
        print('Creating an object for current member: ', str_elmt)  

        # changes parameters of the function to pass more information with dictionary dic_info
        dic_info = {'str_mb': str_elmt, 'var_key':var_key, 'var_idx': var_idx}
        obj_mbevery = dcp_set.eachmb_every(self, dic_info)        
        obj_mbevery.dispmb()
        
        # Record the index of the current every-type element, for which the non-every instance will be generated and recorded later 
        self.idx_cur_every = var_idx[0]        
        
        return obj_mbevery
        
    def get_nonevery_elmt(self):
        '''
        generate a new instance for element without EVERY range
        return the element object
        '''
        # create an empty NONEVERY set, with each member a subset for each element
        obj_nonevery = dcp_set.empty_nonevery(self)
        obj_nonevery.dispmb()
        
        # loop for all NONEVERY elements and update the NONEVERY set
        if self.lst_nonevery == None:                                    # initialize NONEVERY element list if needed
            self.ini_nonevery()
        else:   
            self.lst_nonevery.reset()                                    # reset the element counter
                     
        while True:            
            # if all NONEVERY element has been processed, terminate            
            str_elmt = self.get_noneveryelmtname()
            if str_elmt == None:
                break
                
            # otherwise, process the element, return the name of the new object
            str_name = dcp_set.gen_nonevery(self, str_elmt)
            obj_nonevery.add_mb(str_name)           
        
        return obj_nonevery
            
    def get_noneveryelmtname(self):
        '''
        get the name of a NONEVERY element in NONEVERY list
        return the name of the element
        '''
        # changes
        # use dic_info to return more information
        dic_info = self.lst_nonevery.get_next_elmt()
        
        
        if dic_info != None:
            str_elmt = dic_info['str_elmt']
        else:
            str_elmt = None

        
        return str_elmt
    
    def ini_nonevery(self):
        '''
        initialize the NONEVERY element list
        return the object
        '''
        # construct the list of NONEVERY element involved in the expression
        lst_nonevery = []                                     # initialized to empty list
        for varname in self.obj_expr.varlst:                  # loop for all variables
            obj_var = self.get_netelmt(varname) 
            lst_elmt = obj_var.elmt_asct                      # list of elements for this variable         
            lst_rng = obj_var.elmt_asct_rng                   # corresponding ragne
                   
            # loop for all elements
            idx = 0
            for elmtname in lst_elmt:
                if lst_rng[idx] != net_name.every and elmtname not in lst_nonevery:  # if NONEVERY element, add to the list if not yet
                    lst_nonevery = lst_nonevery + [elmtname]  
                idx += 1
        
        # create an object for the list
        self.lst_nonevery = dcp_set.ini_nonevery(self, lst_nonevery) 
        self.lst_nonevery.dispmb()
                       
    def form_inst(self, obj_every, obj_nonevery):
        '''
        construct an instantance of variable vector based on the generaed every and nonevery elements subset
        return the list of instance variables names
        '''
        #---------------------------------------------------------------    
        xpd = self.get_netelmt(dcp_name.xpd)                              # get the xpd object to generate a unique name for the set
        elmt_name = xpd.get_newinstname()                                 # element info
        
        elmt_num = 1     
                                      
        addi_info = {'ntwk':self.ntwk, 'parent':xpd, 'every':obj_every, 'nonevery':obj_nonevery}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

        elmt = dcp_inst.inst(info)                                        # create element
        xpd.addgroup(elmt_name, elmt)                                     # add element as a subgroup 

        elmt.ping()
        #---------------------------------------------------------------  
        
        # register the instance in xpd
        xpd.rgst_inst(elmt_name)
        
        # set up the expression to which the instance is related
        elmt.set_expr(self.obj_expr)
        
        return elmt
    