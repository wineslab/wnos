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
# functions and classes
#######################################################

# add external dir into search list
import sys
sys.path.insert(0, './wos-decomp')

# from current folder
import net_name

# from external folder
import dcp_name

# -------------------------------------------------------------------------
# network element operations
# -------------------------------------------------------------------------

def mkinfo(elmt_type, elmt_subtype, elmt_num, addi_info):
    '''
    basic information to define a network element
    '''
    net_info = {'elmt_type': elmt_type, 'elmt_subtype': elmt_subtype, 'elmt_num': elmt_num, 'addi_info': addi_info}
    return net_info   
    
# -------------------------------------------------------------------------
# network an expression
# -------------------------------------------------------------------------    
def mkexpr(fmlr, *args):
    '''
    fmlr: math expression
    varlst: variable list used in fmlr
    '''
    if len(args) == 0:                # no variable
        varlst = None
    else:
        varlst = args
            
    return {'fmlr':fmlr, 'varlst':varlst}    
    
# -------------------------------------------------------------------------
# network element operations
# -------------------------------------------------------------------------
# def mkvarname(elmt):
    # '''
    # make up a name for the new variable based on the element information
    # '''   
    # maxcnt = 999                                                # the predefined maximum number of variable index
    # if elmt.varcnt > maxcnt:
        # print('Error: Var index ({}) has reached the maximum ({})!'.format(elmt.varcnt, maxcnt))
        # exit(0)
    
    # str_cnt = str(elmt.varcnt)
    # return elmt.type + '_' + str_cnt.zfill(len(str(maxcnt)))    # example: type_001
    
def mkvarname(var_expr):
    '''
    new function to replace the old mkvarname()
    make up a variable name based on the variable expression
    '''     
    return var_expr    
    


# -------------------------------------------------------------------------
# basic network element class 
# base class of all other element classes
# -------------------------------------------------------------------------
class netelmt_group:
    def __init__(self, info):
        self.type       = info['elmt_type']                       # network element type: network, node, session, parameter (variable) ...
        self.stype      = info['elmt_subtype']                    # subtype: Parameter: power, frequency, rate ...
        self.member     = []                                      # members list in the current group
        self.subgroup   = []                                      # elements are grouped into different groups; e.g., node: source, destination, relay
        self.para_type  = None                                    # leaf element, intemediate elelemt, external element
        self.is_var     = None                                    # is this element an optimization variable?  
        self.layer      = None                                    # protocol layer 

        #// Changes:
        # this will not be included in the basic class because most elements do not need this attribute
        # instead, it will be implemented where really needed
        # self.fam        = self.newfam(None)                       # list of family members of this network element, used for NUM decomposition
        #//
        
        # if elmtobj is None, the network element is self
        # otherwise, if not None, self is just a wrapper with elmtobj referring to the actual element
        # this attribute is added later, in order to include more types of network elememts        
        self.elmtobj    = None
        
        # for some elements implemented earlier, this parameters is not passed
        if 'elmtobj' in info['addi_info'].keys():
            self.elmtobj = info['addi_info']['elmtobj']        
            

        # for back compatibility
        # rngtype means if the element is single, subset, or full set
        self.rngtype    = None

        # for some elements implemented earlier, this parameters is not passed        
        if 'rngtype' in info['addi_info'].keys():
            self.rngtype = info['addi_info']['rngtype']          
            
        # add members of current type
        print('-----------------------------------------------------------------------------')            
        #print('Creating {}...'.format(self.type))
        self.addmember(info['elmt_num'])


        # pointer to network, parent, and itself
        self.ntwk       = info['addi_info']['ntwk']                 # to network
        if self.ntwk == None:                                       # when creating a network, None 
            self.ntwk = self 

        self.parent     = info['addi_info']['parent']               # to parent

        # register the elelemt according to addi_info
        if net_name.if_rgst in info['addi_info'].keys():
            if info['addi_info'][net_name.if_rgst] == net_name.no:  # no need to register
                b_rgst = 0
            else:
                b_rgst = 1
        else:             
            b_rgst = 1
                      
        if b_rgst == 1:                                             # need to register, or not specified    
            ptr_name = '_'+self.type                                # to itself; pointer name format: node: _node
            if hasattr(self.ntwk, ptr_name):
                print('Error: Duplicated network element!')           
                exit(0)
            else:
                setattr(self.ntwk, ptr_name, self)
        else:
            pass
            
        self.varcnt = 0                                             # recodring the number of variables this parameter has been made as
        
        # changes:
        # add layer to indicate which layer the network element belongs to
        # hid added to indicate if the element corresponds to a horizontal network element, like src, node
        if 'layer' in info['addi_info'].keys():
            self.layer = info['addi_info']['layer']      

        if 'hid' in info['addi_info'].keys():
            self.hid = info['addi_info']['hid']   

        # changes:
        # add 'para_type' to indicate type of the elements
        if 'para_type' in info['addi_info'].keys():
            self.para_type = info['addi_info']['para_type']
        
        # changes
        # add is_var to indicate if a network element 
        if 'is_var' in info['addi_info'].keys():
            self.is_var = info['addi_info']['is_var']  

        # June 3, 2017
        # Add sub_type to indicate the category of a network variable, e.g., the subtype of "lnkpwr" is "power"
        # This informaiton will be used to configure the lower and upper bounds of a variable
        if 'sub_type' in info['addi_info'].keys():
            self.sub_type = info['addi_info']['sub_type']        
        
        # June 5, 2017
        # Add an attribute for external parameter to record derivative of the paramter with respect to external variables
        # Used in alglib_func.gnrt_pnl() to generate penalization when generating solution algorithms
        # Initialized to an empty dictionary, updated in self.add_xtnl_der()
        if 'para_type' in info['addi_info'].keys() and info['addi_info']['para_type'] == net_name.xtnl_para:
            self.der = {}                 
    
    def add_xtnl_der(self, var_name, der_expr):    
        '''
        Add a derivative for external parameters
        
        var_name: variable name with respective to which the derivative is defined
        der_expr: derivative experssion 
        
        Return: -1 if error, 1 if new entry added
        
        Called By: net_link.net_link.new_lkitf()                
        '''
        
        # This element must have attribute para_type with value net_name.xtnl_para
        if hasattr(self, 'para_type') and self.para_type == net_name.xtnl_para:
            self.der.update({var_name: der_expr})
        else:
            print('Error: This element doesn\'t have attribute para_type or is not external, -1 returned!')
            return -1                                                                    
        
    
            
    def ping(self):
        '''
        disp information
        '''       
        #print('--------------Basic Information------------------')
        print('Elmt: {}, members: {}'.format(self.type, self.member))
        print('Sub-elmt: {}'.format(self.subgroup))
        for subgrp in self.subgroup:           
            if subgrp == net_name.default:                          # skip the default dumb subgroup
                pass
            else:
                x = getattr(self, subgrp)
                print('{}, members: {}'.format(x.type, x.member))
                
        #print('--------------Other Information------------------')  
        print('layer:', self.layer)
        print('is_var:', self.is_var)      
                
    def hasgroup(self, groupname):
        '''
        check if an element has a group 
        '''
        return hasattr(self, groupname)


    def addgroup(self, groupname, groupvalue):
        '''
        add a new group to an element
        '''
        if self.hasgroup(groupname):
            print('Error: group {} already exists.'.format(groupname))
            exit(0)
        elif groupname == net_name.default:
            self.subgroup.append(groupname)              # add default group (just name, a dumb group)
        else:
            setattr(self, groupname, groupvalue)         # create new subgroup
            self.subgroup.append(groupname)              # add subgroup name to the group list

    def addmember(self, mem_num):
        '''
        add new members to current group
        '''       
        self.member = range(len(self.member) + mem_num)    
           
    def delmember(self, mem_num):
        '''
        delete members from current group
        '''                   
        self.member = range(len(self.member) - mem_num)
        print('{}, members: {}'.format(self.type, self.member))

    def get_memnum(self):
        '''
        the number of members
        '''  
        return len(self.member)
        
    def set_memnum(self, mem_num):
        '''
        set the number of membes in this group
        '''        
        if mem_num < 0:
            print('Error: The number of members must be >= 0! ')
            Exit(0)
        else:
            self.member = range(mem_num)        

    def get_ntwk(self):
        '''
        return the network object
        '''         
        return self.ntwk

    def get_netelmt(self, elmt_name):
        '''
        return the network object
        '''   
       
        # get network
        ntwk = self.get_ntwk()
         
        # get network element
        _elmt_name = '_'+elmt_name                                            # construct network attribute cosrresponding to elmt_name
        
        if hasattr(ntwk, _elmt_name) == False:      
            print('Network element {} does not exist, ntwk notified.'.format(_elmt_name))    # the request network element doesn't exist
            
            # if the wanted element does not exist, notify the network
            # will be implemented in future
            
            return None
        else:
            return getattr(ntwk, _elmt_name)

    def get_depth(self):
        '''
        get the depth information of the current element in the network tree
        '''
        depth = 0                           # initialized to 03/12/2016
        elmt = self         
        while elmt.parent != None:          # not the top element
            depth += 1 
            elmt = elmt.parent
            
        return depth        
        
    def mkvar(self, var_expr, *args):
        '''
        make a (or a set) network parameters variables
        #) var_expr: the expression of the variable
        #) args: a list of parameters indicating the range of ntwk elements
        
        Changes(5/28/2016):
        This function will be discarded. Instead, variables will be created by calling ntwk.make_var() directly
        '''             
        # only enabled for leaf parameters 
        if len(self.subgroup) != 0:
            print('Error: Only leaf parameters can be made variables!')
            exit(0)
        
        # check if the number of parameters are correct
        elmt_depth = self.get_depth()                                       # depth of the network element
        num_arg = len(args)                                                 # number of parameters
        if elmt_depth != num_arg:                                           # the two should equal to each other
            print('Error: The number of argments should equal to elment depth!')
            #exit(0)                                                        # no need to exit, still works
        
        # count up the variables this parameter has been made as
        self.varcnt += 1
        
        # create variable by calling mkvar of the network
        newvar = self.ntwk.mkvar(self, var_expr, *args)
        
        #return newvar   # no need to return any value
        
    def newfam_xxx(self, dict_info):
        '''
        create a family for a network element
        '''
        #print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        return dcp_set.newfam(dict_info)

    def get_fulfamset_xxx(self):                                                        # _xxx: discarded function
        '''
        get the full familiy set
        '''
        # for a parameter (or variable), get the full set of its elmt_asct
        # for network element, get the full set of itself        
        if hasattr(self, net_name.elmt_asct): 
            return self.elmt_asct.get_fulfamset()                                       # the parameter is associated to other network element
        else:                                                                           # otherwise
            # if full list does not exist, create one
            if self.fam.full_list == None:                              
                lst = list(range(dcp_name.allnum))                                      # generate the full list, here allnum is the size of the full set
                self.fam.full_list = dcp_set.subset(lst)
                
            # return the full list    
            return self.fam.full_list
                       
    def create_every_xxx(self):
        '''
        create an EVERY subset and add the corresponding attribute in this element
        return the object of EVERY set
        '''
        return dcp_set.create_every(self)
        
    def is_leaf(self):
        '''
        func: determine if a network element is a leaf element by checking if the element has attribute 'expr_hldr'
        return: True for leaf or False non-leaf
        '''        
        if hasattr(self, net_name.expr_hldr):
            obj_expr_hldr = getattr(self, net_name.expr_hldr)
            if obj_expr_hldr == None:
                return True                             # is leaf
            else:
                return False                            # not leaf
        else:
            return True                                 # is leaf
            
    def is_xtnl(self):
        '''
        func: determine if the element is external element
        return: True or False        
        '''
        
        #print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', self.para_type)
        
        if self.para_type == net_name.xtnl_para:
            return True
        else:
            return False