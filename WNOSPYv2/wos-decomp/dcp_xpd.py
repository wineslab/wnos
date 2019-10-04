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
# Expand a NUM problem
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from wos-network
import net_name, net_func

# from local folder
import dcp_name, dcp_cstr, dcp_utlt, dcp_hsub

def gen_xpd(ntwk):
    '''
    Parse a NUM problem to gerate the corresponding expanded version NUM
    '''    
    # initialize expanded NUM for the network
    xpd = new_xpd(ntwk)
    
    # parse utility
    dcp_utlt.ps_utlt(xpd)
    
    # parse constraints
    dcp_cstr.ps_allcstrs(xpd)
    
    print(xpd.lst_subset)
    print(xpd.lst_inst)
    
    # display instances information
    xpd.disp_inst()
    #input('Debug...')
    
    return xpd
    
def new_xpd(ntwk):
    '''
    create a new expanded NUM problem for a network
    '''   
    # if xpd has been created, do nothing; otherwise, create it
    if ntwk.hasgroup(dcp_name.xpd):
        return ntwk.get_netelmt(dcp_name.xpd)
    else:
        #---------------------------------------------------------------      
        elmt_name = dcp_name.xpd                                            # element info
        elmt_num = 1     
            
        addi_info = {'ntwk':ntwk, 'parent':ntwk}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

        elmt = xpd(info)                                                    # create element
        ntwk.vardb.addgroup(elmt_name, elmt)                                # add element as a subgroup 
                
        newobj = elmt
        newobj.ping()
        #---------------------------------------------------------------  
        
        return newobj 
       
class xpd(net_func.netelmt_group):
    '''
    define expanded NUM problem
    '''
    def __init__(self, info):
        # from base network element
        net_func.netelmt_group.__init__(self, info) 
        
        self.lst_subset = []                    # the list of hash ids of all subsets generated ever during the decoposition
               
        self.inst_cnt = 0                       # the total number of instants       
        self.set_cnt = 0                        # counter of sets, used when a set does not have its own unique name
        self.gn_cnt  = 0                        # generator counter to generate a unique name for a generator        
        self.hsub_cnt = 0                       # counter of horizontal subproblems
        
        self.lst_inst = []                      # list of the names of all instances         
        self.lst_vsub = []                      # list of vertical subproblems
        
        # list of hsubs in classes, each class is a vsub in self.lst_vsub
        # the list will be created dynamically
        
    def disphsub(self):
        '''
        func: display all hsubs
        return: None
        '''
        for str_vsub in self.lst_vsub:                              # take one vsub
            str_hsubcls = dcp_hsub.get_hsubclsname(str_vsub)        # corresponding hsubclass
            lst_hsub = getattr(self, str_hsubcls)                   # corresponding list of hsubs
            for str_hsub in lst_hsub:                               # take one hsub from the list
                print('\n', str_hsub)                               # name of the hsub
                obj_hsub = getattr(self, str_hsub)                  # get hsub object
                obj_hsub.disp_expr()                                # display the expression
                
                #print('Debug:')
                #input("Press the <ENTER> key to continue...")
                
    def get_hsub(self, subid):
        '''
        func: get a hsub from the xpd; 
              currently only one hsub will be processed for each vsub category, because all hsubs in the same vsub
              category represent the same sub network control problem; 
              in future, hsubs in the same vsub may represent different subproblems, then they will be processed one by one
              
        return: the object of the hsub; if all hsubs processed already, return False
        
        subid: the integer index of the hsub to be reterived
        '''                        
        num_vsub = len(self.lst_vsub)                           # total number of vsub categories
        if subid >= num_vsub:                                   # if all categories have been processed, return None
            return None
        else:                                                   # otherwise, get a hsub from the vsub category
            str_vsub = self.lst_vsub[subid]                         # name of the vsub category
            str_hsubcls = dcp_hsub.get_hsubclsname(str_vsub)        # corresponding hsubclass
            lst_hsub = getattr(self, str_hsubcls)                   # corresponding list of hsubs  
            
            ### start debug
            #print(lst_hsub)
            #print('Exiting debug...')
            #exit(0)
            ### end debug
            
            str_hsub = lst_hsub[0]                                  # take the first hsub as example for each vsub category
            obj_hsub = getattr(self, str_hsub)                      # get hsub object            
            return obj_hsub
                     
    def crt_hsubcls(self, str_hsubcls):
        '''
        func: create a class for hsub. This class does not have a template, 
        instead it is just a list of the names of hsubs belonging to the same layer. 
        
        The list of hsubs is updated by add_hsub() in this module. 
        
        return: new attribute created
        
        str_hsubcls: name of the hsub class, a class representing a layer
        '''
        setattr(self, str_hsubcls, [])             # create a new attribute with name of the class of hsubs
                   
    def add_hsub(self, str_hsub, obj_hsub):
        '''
        func: add the name of an husb to the corresponding hsub list 
        return: updated hsub list; create an attribute for the new hsub
        str_hsub: name of hsub
        str_hsubcls: name of hsub class
        
        called by: dcp_hsub.get_hsub()
        '''
        lst_hsubcls = getattr(self, obj_hsub.hsubcls)           # get the list of husb
        lst_hsubcls += [str_hsub]                               # add current the name of current hsub to the list 
        
        setattr(self, str_hsub, obj_hsub)                       # create new attribute for the hsub
        
    def rgst_inst(self, str_name):
        '''
        func: register a new instance based on its object and name 
        str_name: name of the instance
        obj_elmt: object of the instance
        '''
        if str_name in self.lst_inst:
            print('Error: The instance has been registered before!')
            exit(0)
        
        # add the instance object to xpd
        self.lst_inst += [str_name]
        
    def gen_gnname(self):
        '''
        func: generate a unique name for generator        
        '''
        # construct the name
        gn_name = dcp_name.generator + str(self.gn_cnt)
        
        # count up for next generator
        self.gn_cnt += 1
        
        return gn_name
        
    def gen_setname(self):
        '''
        get a unique name for a set; for those sets without a unique name, e.g., each member of EVERY set
        '''
        # construct name for the set
        str_setname = dcp_name.set + str(self.set_cnt)
        
        # counter up by 1
        self.set_cnt += 1
        
        return str_setname
        
    def register_set(self, str_id):
        '''
        register a set in xpd using the harsh id of the set
        '''
        if self.have_subset(str_id):
            return True                         # there is already such a set
        else:
            self.add_subset(str_id)            
            return False                        # set registered, but still needs to be created
        
    def add_subset(self, str_id):
        '''
        add an id string to the list, in order to record all id strings
        '''
        self.lst_subset.append(str_id)
        
    def have_subset(self, str_id):
        '''
        if an id already exists
        '''
        if str_id in self.lst_subset == True:
            return True
        else:
            return False
            
    def add_vsub(self, str_vsub, obj_vsub):
        '''
        add a vertical subproblem to xpd
        return: updated list of vsubs self.lst_vsub
        '''
        self.lst_vsub += [str_vsub]         # add to the vsub list
        setattr(self, str_vsub, obj_vsub)   # create a new attribute for the vsub
    
    def dispsub(self):
        '''
        display each subproblem
        '''
        for subname in self.lst_vsub:
            obj_sub = self.get_netelmt(subname)
            print('\n', subname, ':')
            print(obj_sub.symexpr)
        
            net_name.outf.write('\n###############################################################\n')
            net_name.outf.write('\n\n'+ str(obj_sub.symexpr))
        #exit(0)

                
    def get_newinstname(self):
        '''
        generate a name for a new instance
        '''
        self.inst_cnt += 1                                  # record the new instance by couting up 1
        return dcp_name.inst + str(self.inst_cnt)   

    def ping(self):
        '''
        disp network element information
        '''
        net_func.netelmt_group.ping(self)  
                        
    def disp_inst(self):
        '''
        display information of instances
        '''
        # process every instance
        for str_inst in self.lst_inst:
            obj_inst = self.get_netelmt(str_inst)           # get the instance object
            print('\n', obj_inst.get_expr())
            obj_inst.disp_varinst()
            