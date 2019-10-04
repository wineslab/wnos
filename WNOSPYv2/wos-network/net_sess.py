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
# class session
#######################################################

import net_name, net_func, net_node, net_para, net_link

def add_sess(ntwk, num_ses):
    '''
    add sessions
    '''
    #---------------------------------------------------------------      
    elmt_name = net_name.ntses
    elmt_num = num_ses      
    
    # changes:
    # rngtype added to indicate the range of the element
    addi_info = {'ntwk':ntwk, 'parent':ntwk, 'rngtype': net_name.all}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)     # session info

    elmt = net_sess(info)                                            # create session object
    ntwk.addgroup(elmt_name, elmt)                                   # add sessions to network as a subgroup 
        
    x = getattr(ntwk, elmt_name)
    x.ping()                                                         # disp sessions information
    #---------------------------------------------------------------   

    # At this point, the link session set has been created when creating links, but the link session was initialized to None
    # The session set of links need to be refreshed
    lkses = x.get_netelmt(net_name.lkses)
    lkses.refresh_ses(x)

class net_sess(net_func.netelmt_group):
    '''
    class of session
    '''
    def __init__(self, info):

        # from base network element
        net_func.netelmt_group.__init__(self, info)   

        # add a dumb subgroup since sess is not leaf network element
        self.addgroup(net_name.default, None)
                       
        # session rate
        self.add_rate()
        
        # source and destination nodes
        self.add_src()
        self.add_dst()
        
        # the set of links of a session
        self.add_links()
               
        # display session information
        self.ping()  

    def ping(self):
        '''
        disp network information, only test purpose for now
        '''
        net_func.netelmt_group.ping(self)            

    def add_rate(self):  
        '''
        create element: end-to-end session rate
        '''        
        #---------------------------------------------------------------
        elmt_name = net_name.ssrate   
            
        elmt_num  = 1                                                         # scalar as default 
        
        # Changes:
        # add layer to indicate which layer the element belongs to
        # hid added to indicate if the element corresponds to a horizontal network element, like src, node
        # Add 'sub_type' to indicate the category of a variable. The information will be used in alglib_func.dtm_varbnd() to configure 
        # the lower and upper bounds of the variable.
        #
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'para_type': net_name.leaf_para, 'layer': net_name.tspt, 'hid': net_name.src, 'sub_type': net_name.rate}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_para.net_para(info)                                        # create node object
        self.addgroup(elmt_name, elmt)                                        # add nodes to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp nodes information
        #---------------------------------------------------------------          
          
    def add_src(self):  
        '''
        create element: source of session
        '''        
        #---------------------------------------------------------------
        elmt_name = net_name.src   
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_node.src(info)                                             # create node object
        self.addgroup(elmt_name, elmt)                                        # add nodes to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp nodes information
        #---------------------------------------------------------------    
        
    def add_dst(self):  
        '''
        create element: destination of session
        '''        
        #---------------------------------------------------------------
        elmt_name = net_name.dst   
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # node info

        elmt = net_node.dst(info)                                             # create node object
        self.addgroup(elmt_name, elmt)                                        # add nodes to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp nodes information
        #---------------------------------------------------------------    

    def add_links(self):
        '''
        define the link set for a session
        '''
        #---------------------------------------------------------------
        elmt_name = net_name.lkset
            
        elmt_num  = 1                                                         # scalar as default 
        addi_info = {'ntwk':self.ntwk, 'parent':self}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)          # link info

        elmt = net_link.lkset(info)                                           # create link object
        self.addgroup(elmt_name, elmt)                                        # add links to network as a subgroup 
       
        x = getattr(self, elmt_name)
        x.ping()                                                              # disp link set information
        #---------------------------------------------------------------   

class lkses(net_func.netelmt_group):
    '''
    session set sharing the same link
    '''
    def __init__(self, info):

        # from base network element
        net_func.netelmt_group.__init__(self, info)   
                        
        # add a dumb subgroup since link is not leaf network element
        self.addgroup(net_name.default, None)
        
        # session element, refer to session of the network 
        self.ses = self.get_netelmt(net_name.ntses)                            # return of the function can be None
             
    def refresh_ses(self, ssobj):
        '''
        refer the session set to a session object
        '''
        self.elmtobj = ssobj        
                     
        

