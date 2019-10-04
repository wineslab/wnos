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
# Network Protocols Information
#######################################################

# from current folder
import net_name, net_func
import net_layer_phy, net_layer_link, net_layer_ntwk, net_layer_tspt, net_layer_app

def get_ptcldb(ntwk):
    '''
    get network protocol database
    '''
    if ntwk.hasgroup(net_name.ptcl) == True:
        return ntwk.get_netelmt(net_name.ptcl)
    else:                                                              # if does not exist, create a new one
        return new_ptcl(ntwk)       
      
def new_ptcl(ntwk):
    '''
    create a new ptorotocl database
    '''
    #---------------------------------------------------------------      
    elmt_name = net_name.ptcl                                          # element info
    elmt_num = 1     
    
    addi_info = {'ntwk':ntwk, 'parent':ntwk}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = net_protocol(info)                                          # create element
    ntwk.addgroup(elmt_name, elmt)                                     # add element as a subgroup 
        
    x = getattr(ntwk, elmt_name)
    x.ping()        
    
    return x
    #--------------------------------------------------------------- 

class net_protocol(net_func.netelmt_group):
    '''
    class of network protocol
    '''
    def __init__(self, info):
 
        # from base network element
        net_func.netelmt_group.__init__(self, info) 
        
    def set_ptcl(self, protocol):
        '''
        configure network protocol
        '''
        
        # protocol information
        ptcl_layer = protocol['layer']                                   # which layer?
        ptcl_name  = protocol['name']                                    # what protocol?
        ptcl_algo  = protocol['alg']                                     # what algorithm?
        
        elmt_name = ptcl_layer
        elmt_num  = 1                   
        addi_info = {'ntwk':self.ntwk, 'parent':self,\
                     'layer': ptcl_layer, 'protocol': ptcl_name, 'alg': ptcl_algo}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)             
                   
        # get layer 
        layer_elmt = self.get_layer(ptcl_layer)
        
        # set layer information
        layer_elmt.set_layer(info)
        
    def get_layer(self, ptcl_layer):
        '''
        get layer element 
        '''
        
        if self.hasgroup(ptcl_layer) == True:
            return self.get_netelmt(ptcl_layer)
        else:                                                            # if does not exist, create a new one
            return self.new_layer(ptcl_layer)          
    
    def new_layer(self, ptcl_layer):   
        '''
        create a new layer
        '''
        #---------------------------------------------------------------      
        elmt_name = ptcl_layer                                           # element info
        elmt_num = 1     
        
        addi_info = {'ntwk':self.ntwk, 'parent':self}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

        # create layer-specific element          
        #elmt = net_protocol_layer(info)                                 # create element        
        if ptcl_layer == 'physical':                                     # physical and mac    
            elmt = net_layer_phy.ptcl_phy(info)
        elif ptcl_layer == 'link':                                       
            elmt = net_layer_link.ptcl_link(info)
        elif ptcl_layer == 'network':                                    # network layer
            elmt = net_layer_ntwk.ptcl_ntwk(info)
        elif ptcl_layer == 'transport':                                  # transport layer
            elmt = net_layer_tspt.ptcl_tspt(info)
        elif ptcl_layer == 'application':                                # application layer
            elmt = net_layer_app.ptcl_app(info)
        else:
            print('Error: Unknown protocol!')
            exit(0)
        
        
        self.addgroup(elmt_name, elmt)                                   # add element as a subgroup 
            
        x = getattr(self, elmt_name)
        x.ping()        
        
        return x
        #---------------------------------------------------------------         
