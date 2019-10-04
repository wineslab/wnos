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
# class my_node
#######################################################

import net_name, net_func, net_para, net_link

def add_node(ntwk, num_node):
    '''
    add nodes
    ntwk: to which the nodes are added
    num_node: number of nodes to be added
    '''  
    #---------------------------------------------------------------
    elmt_name = net_name.node 
    elmt_num  = num_node    
    addi_info = {'ntwk':ntwk, 'parent':ntwk}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)     # node info

    elmt = net_node(info)                                            # create node object
    ntwk.addgroup(elmt_name, elmt)                                   # add nodes to network as a subgroup 
        
    x = getattr(ntwk, elmt_name)
    x.ping()                                                         # disp nodes information
    #---------------------------------------------------------------

class net_node(net_func.netelmt_group):
    '''
    define node
    '''
    def __init__(self, info):

        # from base network element
        net_func.netelmt_group.__init__(self, info) 

        # Links associated to this node
        self.new_link(info)                     # create links           
        
        # Attributes of regular relay node       
        self.new_pwr(info)                      # create power
        self.new_frq(info)                      # create frequency

        # make all node members as regular intermediate nodes by adding a sub group
        # self.make_regular()   
        
        # Rate was moved to link class in net_link.py
        # self.new_rate(info)                   # create outgoing rate
           

    def new_link(self, info):
        '''
        create links for a node
        ''' 
        #---------------------------------------------------------------
        elmt_name = net_name.ndlink
            
        elmt_num  = 1                                                         # initialized to single link per node
        addi_info = {'ntwk':self.ntwk, 'parent':self}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # link info

        elmt = net_link.net_link(info)                                        # create link object
        self.addgroup(elmt_name, elmt)                                        # add links to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp links information
        #---------------------------------------------------------------    
        
    def new_pwr(self, info):
        '''
        create a new power element
        info['addi_info']['nd_lbl']: indication of node type: rin, src, dst
        '''
        #---------------------------------------------------------------
        elmt_name = net_name.ndpwr
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'para_type': net_name.leaf_para}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_para.net_para(info)                                        # create node object
        self.addgroup(elmt_name, elmt)                                        # add nodes to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp nodes information
        #---------------------------------------------------------------           
    
    def new_frq(self, info):    
        '''
        create a new frequency element
        info['addi_info']['nd_lbl']: indication of node type: rin, src, dst
        '''
        #---------------------------------------------------------------
        elmt_name = net_name.ndfreq                
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'para_type': net_name.leaf_para}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_para.net_para(info)                                        # create node object
        self.addgroup(elmt_name, elmt)                                        # add nodes to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp nodes information
        #---------------------------------------------------------------          
              
    def ping(self):
        '''
        disp network information, only test purpose for now
        '''
        net_func.netelmt_group.ping(self)
        
class src(net_func.netelmt_group):
    '''
    class of source of session
    '''
    def __init__(self, info):

        # from base network element
        net_func.netelmt_group.__init__(self, info)   

        # associated to a node
        self.node = self.get_netelmt(net_name.node)
        
        # display information
        self.ping()  
            
          
class dst(net_func.netelmt_group):
    '''
    class of destination of session
    '''
    def __init__(self, info):

        # from base network element
        net_func.netelmt_group.__init__(self, info)   
                                 
        # display information
        self.ping()             






