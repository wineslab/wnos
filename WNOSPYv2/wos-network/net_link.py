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
# class link
#######################################################

import net_name, net_func, net_para, net_sess

class net_link(net_func.netelmt_group):
    '''
    class of link
    '''
    def __init__(self, info):

        # from base network element
        net_func.netelmt_group.__init__(self, info)   
                        
        # add a dumb subgroup since link is not leaf network element
        self.addgroup(net_name.default, None)

        # link attributes
        self.new_tsmt()             # transmitter and receiver of the link       
        self.new_rcvr()             # receiver
        self.new_lkpwr()            # power 
        self.new_lkfrq()            # frequency
        self.new_sinr()             # link SINR
        self.new_lkcap()            # link capacity
        self.new_lkgain()           # link channel gain
        self.new_lknoise()          # link noise power
        self.new_lkitf()            # link interference
        self.new_itfpwr()           # power of interfering link
        
        self.new_lkses()            # session set using this link
        
        # add network link: full set of links of the network
        # the element object of netlink points to a node link
        self.new_ntlk()
                       
        # display session information
        self.ping()   
        
    def new_itfpwr(self):
        '''
        func: create power of interfering link
        '''         
        #---------------------------------------------------------------
        elmt_name = net_name.itfpwr   
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'para_type': net_name.leaf_para}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_para.net_para(info)                                        # the parent of link refer to node
        self.addgroup(elmt_name, elmt)                                        # add element to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp element information
        #---------------------------------------------------------------            
        

    def new_lkgain(self):
        '''
        func: create link channel gain 
        '''        
        #---------------------------------------------------------------
        elmt_name = net_name.lkgain   
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'para_type': net_name.leaf_para}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_para.net_para(info)                                        # the parent of link refer to node
        self.addgroup(elmt_name, elmt)                                        # add element to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp element information
        #---------------------------------------------------------------            

    def new_lknoise(self):
        '''
        func: create link noise
        '''        
        #---------------------------------------------------------------
        elmt_name = net_name.lknoise   
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'para_type': net_name.leaf_para}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_para.net_para(info)                                        # the parent of link refer to node
        self.addgroup(elmt_name, elmt)                                        # add element to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp element information
        #---------------------------------------------------------------  
        
    def new_lkitf(self):
        '''
        func: create link interference power
        '''        
        #---------------------------------------------------------------
        elmt_name = net_name.lkitf   
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'para_type': net_name.xtnl_para}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_para.net_para(info)                                        # the parent of link refer to node
        self.addgroup(elmt_name, elmt)                                        # add element to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp element information
        #---------------------------------------------------------------           
        # Add a derivative entry for this parameter. The derivative will be used in 
        # alglib_func.gnrt_pnl() to generate penalization item when generating soltion 
        # algorithm
        elmt.add_xtnl_der(net_name.lkpwr, net_name.chngain)
        
        
    def new_tsmt(self):  
        '''
        create transmitter node for a link
        '''        
        #---------------------------------------------------------------
        elmt_name = net_name.lktsmt   
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = self.parent                                                    # the parent of link refer to node
        self.addgroup(elmt_name, elmt)                                        # add element to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp element information
        #---------------------------------------------------------------     

    def new_rcvr(self):  
        '''
        create receiver node for a link
        '''        
        #---------------------------------------------------------------
        elmt_name = net_name.lkrcvr   
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = self.parent                                                    # the parent of link refer to node
        self.addgroup(elmt_name, elmt)                                        # add element to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp element information
        #---------------------------------------------------------------      

    def new_sinr(self):  
        '''
        create receiver node for a link
        currently SINR refers to a general parameter, a dedicated class may be needed
        this needs to be cosidered in algorithm generation phase
        '''        
        #---------------------------------------------------------------
        elmt_name = net_name.lksinr   
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'para_type': net_name.itmd_para}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_para.net_para(info)                                        # the parent of link refer to node
        self.addgroup(elmt_name, elmt)                                        # add element to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp element information
        #---------------------------------------------------------------          
        
    def new_lkcap(self):  
        '''
        create a link capacity element
        '''        
        #---------------------------------------------------------------
        elmt_name = net_name.lkcap   
            
        elmt_num  = 1                                                         # scalar as default 
        # add layer to indicate which layer the network element belongs to
        # hid added to indicate if the element corresponds to a horizontal network element, like src, node
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'para_type': net_name.itmd_para, 'layer': net_name.phy, 'hid': net_name.node}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_para.net_para(info)                                        # create node object
        self.addgroup(elmt_name, elmt)                                        # add nodes to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp nodes information
        #---------------------------------------------------------------          
        
    def new_lkpwr(self):
        '''
        create a new power element
        info['addi_info']['nd_lbl']: indication of node type: rin, src, dst
        '''

        # Add 'sub_type' to indicate the category of a variable. The information will be used in alglib_func.dtm_varbnd() to configure 
        # the lower and upper bounds of the variable.
        #
        #---------------------------------------------------------------
        elmt_name = net_name.lkpwr
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'para_type': net_name.leaf_para, 'is_var': True, 'layer': net_name.phy, 'sub_type': net_name.power}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_para.net_para(info)                                        # create node object
        self.addgroup(elmt_name, elmt)                                        # add nodes to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp nodes information
        #---------------------------------------------------------------           
    
    def new_lkfrq(self):    
        '''
        create a new frequency element
        info['addi_info']['nd_lbl']: indication of node type: rin, src, dst
        '''
        #---------------------------------------------------------------
        elmt_name = net_name.lkfrq                
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'para_type': net_name.leaf_para}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_para.net_para(info)                                        # create node object
        self.addgroup(elmt_name, elmt)                                        # add nodes to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp nodes information
        #---------------------------------------------------------------     

    def new_lkses(self):
        '''
        set of sessions using the link
        '''
        #---------------------------------------------------------------        
        # change ssset to lkses for naming consistence 
        # redefine the class of session set using a link 
        
        #elmt_name = net_name.ssset
        elmt_name = net_name.lkses
            
        elmt_num  = 1                                                         # scalar as default 
        
        # at this point, session has not been created, will be refreshed later
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'elmtobj': None, 'rngtype': net_name.sub}     
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # element info

        #elmt = net_sess.ssset(info)                                          # create element object
        elmt = net_sess.lkses(info)                                           # create element object
        self.addgroup(elmt_name, elmt)                                        # add element to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp element information
        #---------------------------------------------------------------   
        
    def new_ntlk(self):
        '''
        add network link to the network: full set of links of the network
        the element object of netlink points to a node link       
        '''
        #---------------------------------------------------------------
        elmt_name = net_name.ntlk                                
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self.ntwk, 'elmtobj': self, 'rngtype': net_name.all}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = ntlk(info)                                                     # create node object
        self.ntwk.addgroup(elmt_name, elmt)                                   # add nodes to network as a subgroup 
       
        x = getattr(self.ntwk, elmt_name)
        x.ping()                                                              # disp nodes information
        #---------------------------------------------------------------           
        
class lkset(net_func.netelmt_group):
    '''
    link set of a session 
    '''
    def __init__(self, info):

        # from base network element
        net_func.netelmt_group.__init__(self, info)   
                        
        # add a dumb subgroup since link is not leaf network element
        self.addgroup(net_name.default, None)
        
        # session element, refer to session of the network 
        self.lk = self.get_netelmt(net_name.ndlink)                           # return of the function can be None      
           
           
class ntlk(net_func.netelmt_group):
    '''
    link set of the whole network
    '''
    def __init__(self, info):

        # from base network element
        net_func.netelmt_group.__init__(self, info)         