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
# set management functions
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from external folder
import net_name, net_func

# from local folder
import dcp_name

# from python
import random

# -------------------------------------------------------------------------
# network element operations for decomposition
# -------------------------------------------------------------------------

def newfam_xxx(dict_info):
    '''
    create a network family
    '''
    return fam(dict_info)
      
class fam_xxx:
    '''
    class of network element family
    '''
    def __init__(self, dict_info):  
        self.full_list = None                 # full list of family members, None for parameters (variables) 
        self.tmp_sublst = None                # tempory sub list
        self.allsubs = []                     # the id of all sublists
    
    def addfamset(self, fam_hldr):
        '''
        generate a new set and add to the set list
        fam_hldr: parent element of the family (fam) object
        '''      
        # create a empty subset
        self.tmp_sublst = subset(None)
               
        # generate a subset that is different from all existent subsets     
        while True:
            lst = self.genlst(fam_hldr)                       # a new sub list
            str_id = self.tmp_sublst.refresh(lst)             # refresh the sublist obj
           
            if hasattr(self, str_id):                         # if the lst is not existent, terminate; otherwise, continue iteration
                pass
            else:
                break 
                
        # take the temporary subset as the new subset, add it to the fam
        setattr(self, str_id, subset(None))                   # add a new None set with name str_id
        x = getattr(self, str_id)                             # get the new created subset
        x.lst = self.tmp_sublst.lst                           # update the lst and id
        x.id  = self.tmp_sublst.id
        self.allsubs.append(str_id)                           # add current sublist to the set of sublists
        return x
        
        #print('@@@@@@@@@@@@@@@@@', 'New subset {}: {}'.format(x.id, x.lst))
        
                    
    def get_fulfamset_xxx(self, fam_hldr):                    
        '''
        get the full familiy set from the fam holder
        '''             
        # changes
        # from: get full famset from fam_hldr
        # to: genertae famset directly 

        # return fam_hldr.get_fulfamset()
        return list(range(dcp_name.allnum))
        
        
    def genlst(self, fam_hldr):
        '''
        generate a sub list of the full list
        currently only the immediate parent elemtn of the variable can be tracked for parsing utility
        actually the depth of the element path of a varible can be larger than 1
        '''        
        # initialized to full list directly
        lst = list(range(dcp_name.allnum))
        
        # shuffle the lst 
        random.shuffle(lst)
        
        # take the first several (up to all) elements, depending on the range of the variable (which is the fam holder)
        if fam_hldr.elmt_asct_rng[-1] == net_name.all or fam_hldr.elmt_asct_rng[-1] == net_name.every:        
            first_some = dcp_name.allnum                # the full set
        else:
            first_some = dcp_name.subsum                # a subset
        
        return lst[0:first_some]
        
class subset_xxx:
    '''
    definition of a subset
    '''
    def __init__(self, lst):  
        self.lst = lst                  # list of members
        self.id = self.genid(lst)       # hash id of the list
        
    def genid(self, lst):
        '''
        generate the hash id for the list
        '''       
        # if None set, return None Id
        if lst == None:
            return None
            
        # Otherwise
        # sort the list, convert to string
        lst.sort()
        lststr = str(lst)
       
        # harsh id of the string
        return hash(lststr)
        
    def refresh(self, newlst):
        '''
        refresh the subset with new lst
        '''
        self.lst = newlst
        self.id = self.genid(newlst)
        
        return str(self.id)
        
class elmtset(net_func.netelmt_group):
    '''
    element set
    '''
    def __init__(self, info):  
        # from base network element
        net_func.netelmt_group.__init__(self, info)  

        self.lst_mb = info['addi_info']['lst_mb']      # a list of memebers; each member is an elememt name string
        
        self.elmt_cnt = 0                              # elememt counter to indicate how many elements have been used
        
        if 'mbtype' in info['addi_info'].keys():
            self.mbtype = info['addi_info']['mbtype']  # type of member: subset, or leaf element
            
        # changes:
        # add keyword and id for easy retrieve of member information
        if 'var_key' in info['addi_info'].keys():
            self.var_key = info['addi_info']['var_key']
        
        if 'var_idx' in info['addi_info'].keys():
            self.var_idx = info['addi_info']['var_idx']
        
    def reset(self):
        '''
        reset the elememt counter
        '''
        self.elmt_cnt = 0
        
    def get_next_elmt(self):
        '''
        get one element from the set
        '''

        
        # check if all elements have been used, return None if yes
        if self.elmt_cnt == len(self.lst_mb):
            return None
            
        # otherwise, return a member
        cur_mb = self.lst_mb[self.elmt_cnt]       
        
        # changes
        # use dic_info to return more information
        #return cur_mb        
        #
        # 5/23/2017: Add elmt_cnt in the returned information to indicate the index of element 
        if hasattr(self, 'var_key'):
            dic_info = {'str_elmt':cur_mb, 'var_key':self.var_key, 'var_idx':[self.var_idx[self.elmt_cnt]], 'elmt_cnt': self.elmt_cnt}
        else:
            dic_info = {'str_elmt':cur_mb, 'elmt_cnt': self.elmt_cnt}
        
        self.elmt_cnt += 1                  # count up 1 to next member
        
        return dic_info
        
    def add_mb(self, str_newmb):
        '''
        add a member to the list
        str_newmb: string name of new member
        '''
        self.lst_mb += [str_newmb]
        
    def dispmb(self):
        '''
        display the members
        '''
        print('Members:', self.lst_mb)
        
        
def create_every(obj_elmt):
    '''
    create an EVERY set for obj_elmt
    '''    
    # determine the members of the set
    # format: elmt_type#idx
    if obj_elmt.rngtype == net_name.all:               # member id
        lst_mbid = list(range(dcp_name.allnum))        # for element with ALL range, e.g., netlinks, netsessions
    elif obj_elmt.rngtype == net_name.single:
        lst_mbid = list(range(dcp_name.singlenum))     # for element with SINGLE range, e.g., network
    else:                                              # other cases will be implemented in future
        print('Error: Currently only element with {} or {} range can be set as {}!'.format(net_name.all, net_name.single, net_name.every))
        exit(0)
    print('members: {}'.format(lst_mbid))
        
    str_mbname = obj_elmt.type                         # member name
    
    # register the set in xpd    
    lst_mb = []                                        # combine name and ids
    for x in lst_mbid:
        cur_mb = 'e' +  '~' + '__' + str_mbname +  '___' + str(x)
        lst_mb.append(cur_mb)   
        
    str_id = str(hash(str(lst_mb)))                    # id of the list
    xpd = obj_elmt.get_netelmt(dcp_name.xpd)           # xpd: expanded network control problem
    b_exist = xpd.register_set(str_id)                 # register a set in xpd using the same id; if already registered, return False
    print(lst_mb, b_exist, str_id)
    
    # create the set if haven't yet
    if b_exist == True:
        obj_every = obj_elmt.get_netelmt(str_id)       # if set already registered, get it and return it    
    else:
        #---------------------------------------------------------------      
        elmt_name = str_id                                                  # element info
        elmt_num = 1     
        
        # changes:
        # var_key and var_idx added for easy retrieve of member information
        addi_info = {'ntwk':obj_elmt.ntwk, 'parent':obj_elmt, 'lst_mb': lst_mb, 'var_key': str_mbname, 'var_idx': lst_mbid}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

        elmt = elmtset(info)                                                # create element
        obj_elmt.addgroup(elmt_name, elmt)                                  # add element as a subgroup 

        elmt.ping()
        #---------------------------------------------------------------  
        obj_every = elmt
    
    # return the set object
    return obj_every

# changes
# use var_key and var_idx to indicate the element name and the set of ids    
def eachmb_every(obj_gn, dic_info):
    '''
    create an object for each member of EVERY set
    return the object
    obj_gn: the generator
    str_mb: the member
    '''
    str_mb = dic_info['str_mb']
    var_key = dic_info['var_key']
    var_idx = dic_info['var_idx']
        
    #---------------------------------------------------------------    
    #print('@@@@@@@@@@@@@@@@@@@@', obj_gn)    
    xpd = obj_gn.get_netelmt(dcp_name.xpd)                              # get the xpd object to generate a unique name for the set
    elmt_name = xpd.gen_setname()                                       # element info
    elmt_num = 1     
    
    lst_mb = [str_mb]                                                   # conver the string member to a list                                   
    #print('lst_mb:', lst_mb)  
    
    addi_info = {'ntwk':obj_gn.ntwk, 'parent':obj_gn.every_elmt, 'lst_mb':lst_mb, net_name.if_rgst:net_name.no, 'var_key': var_key, 'var_idx':var_idx}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = elmtset(info)                                                # create element
    obj_gn.addgroup(elmt_name, elmt)                                    # add element as a subgroup 

    elmt.ping()
    #---------------------------------------------------------------   

    return elmt

def empty_nonevery(obj_gn):
    '''
    create an empty NONEVERY set
    return the object
    obj_gn: object of the generator
    '''
    #---------------------------------------------------------------    
    xpd = obj_gn.get_netelmt(dcp_name.xpd)                              # get the xpd object to generate a unique name for the set
    elmt_name = xpd.gen_setname()                                       # element info
    elmt_num = 1     
    
    lst_mb = []                                                         # initialized to empty list                                  
    
    addi_info = {'ntwk':obj_gn.ntwk, 'parent':obj_gn, 'lst_mb':lst_mb, net_name.if_rgst:net_name.no, 'mbtype':dcp_name.mt_subset}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = elmtset(info)                                                # create element
    obj_gn.addgroup(elmt_name, elmt)                                    # add element as a subgroup 

    elmt.ping()
    #---------------------------------------------------------------    

    return elmt
    
def ini_nonevery(obj_gn, lst_nonevery):
    '''
    initialize the list of NONEVERY elements
    return the list object
    obj_gn: object of the generator
    lst_nonevery: the list of names of NONEVERY elements
    '''
    #---------------------------------------------------------------    
    xpd = obj_gn.get_netelmt(dcp_name.xpd)                              # get the xpd object to generate a unique name for the set
    elmt_name = xpd.gen_setname()                                       # element info
    elmt_num = 1     
                                  
    addi_info = {'ntwk':obj_gn.ntwk, 'parent':obj_gn, 'lst_mb':lst_nonevery, net_name.if_rgst:net_name.no}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = elmtset(info)                                                # create element
    obj_gn.addgroup(elmt_name, elmt)                                    # add element as a subgroup 

    elmt.ping()
    #---------------------------------------------------------------    

    return elmt    
 
def gen_nonevery(obj_gn, str_elmt):
    '''
    generate the object for a sample set of the element
    return name of the object of the set
    obj_gn: object of the generator
    str_elmt: name of the element, for which the object is generated
    '''       
    

    
    # generate the sample set of the element
    dic_elmt = gen_elmtset(obj_gn, str_elmt)

    
    # create an object for the sample set
    #---------------------------------------------------------------    
    elmt_name = dic_elmt['str_id']                                      # element info
    elmt_num = 1     
    
    # var_key and var_idx for easy information retrieve
    var_key = dic_elmt['var_key']
    var_idx = dic_elmt['var_idx']
    
    lst_mb = dic_elmt['lst_elmt']                                       # initialized to empty list                                  
    obj_elmt = obj_gn.get_netelmt(str_elmt)
    addi_info = {'ntwk':obj_gn.ntwk, 'parent':obj_elmt, 'lst_mb':lst_mb, net_name.if_rgst:net_name.yes, 'var_key': var_key, 'var_idx': var_idx}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = elmtset(info)                                                # create element
    obj_elmt.addgroup(elmt_name, elmt)                                  # add element as a subgroup 

    elmt.ping()
    #---------------------------------------------------------------       
    
    # register the set in xpd
    xpd = obj_gn.get_netelmt(dcp_name.xpd)
    xpd.register_set(elmt_name)
    
    # return the name of the object    
    print('elmt_name:', elmt_name)
    return elmt_name
    
def gen_elmtset(obj_gn, str_elmt):
    '''
    generate the sample set for the elememnt
    return the list of element
    obj_gn: object of the generator
    str_elmt: name of the element, for which the sample set is generated    
    '''
    
    # get the element range type
    obj_elmt = obj_gn.get_netelmt(str_elmt)                           # get the element object
    rngtype = obj_elmt.rngtype                                        # range type
    str_name = obj_elmt.type                                          # element type 
    
    #print('Debug:')
    #obj_elmt.ping()
    #input('...')
    
    # generate subset according to the range type
    if rngtype == net_name.all:                                       # if ALL range
        # changes: add .zfill(dcp_name.zflen) for fixed length index
        lst_elmt = ['__' + str_name + '___' + str(id).zfill(dcp_name.zflen) for id in range(dcp_name.allnum)] # generate set
        str_id = str(hash(str(lst_elmt)))                                      # generate hash id 
        # changes: var_id added for easy information retrieve
        var_idx = list(range(dcp_name.allnum))   

        
        # Create an empty list for each of the every-type elements, each empty list will be updated when generating non-every elements.
        # This information is used to map every-type elememnt to non-every elememnts. See dcp_gn.generator for more information. 
        obj_gn.ini_every2nonevery(var_idx)
        
    elif rngtype == net_name.sub:                                     # if SUB range
        # iterate until a subset with unique id is generated
        while True:
            lst_fullidset = list(range(dcp_name.allnum))                        # full id set
            random.shuffle(lst_fullidset)                                       # shuffle the full set
            subidset = lst_fullidset[0:dcp_name.subnum]                         # take a subset of the shuffled ids
            subidset.sort()                                                     # sort the subset
            # changes: add .zfill(dcp_name.zflen) for fixed length index
            lst_elmt = ['__' + str_name + '___' + str(id).zfill(dcp_name.zflen) for id in subidset]            # form the set
            str_id = str(hash(str(lst_elmt)))                                   # get the hash id as string
            
            # changes: var_id added for easy information retrieve
            var_idx = subidset 
            
            # check if the id has been existent in the xpd, break if no
            xpd = obj_gn.get_netelmt(dcp_name.xpd)                              # get the xpd object
            if xpd.have_subset(str_id) == False:                                # already exist
                break   

        # Record the generated instance set of non-every element and map it to the current every-type element
        obj_gn.update_every2nonevery(var_idx)
                
    else:                                                             # all other cases, currently not supported
        print('Error: Only {} and {} range types are supported.'.format(net_name.all, net_name.sub))
        exit(0)

    
    print('lst_elmt:', lst_elmt, 'id', str_id)
    net_name.outf.write('\n\n'+str(lst_elmt))
    #input("Press Enter to continue...")
    return {'lst_elmt':lst_elmt, 'str_id':str_id, 'var_key': str_name, 'var_idx': var_idx}