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
# expressions: network fluid model
#######################################################

import net_name, net_func

def get_fldmdl(ntwk):
    '''
    return the fluid model of the network
    '''
    if ntwk.hasgroup(net_name.fldmdl) == True:
        return ntwk.get_netelmt(net_name.fldmdl)
    else:                                                              # if does not exist, create a new one
        return new_fldmdl(ntwk)    

def new_fldmdl(ntwk):
    '''
    create a new network fluid model
    '''
    #---------------------------------------------------------------      
    elmt_name = net_name.fldmdl                                         # element info
    elmt_num = 1     
    
    addi_info = {'ntwk':ntwk, 'parent':ntwk}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = net_fldmdl(info)                                             # create element
    ntwk.addgroup(elmt_name, elmt)                                      # add element as a subgroup 
        
    x = getattr(ntwk, elmt_name)
    x.ping()        
    
    return x
    #--------------------------------------------------------------- 
              
class net_fldmdl(net_func.netelmt_group):
    '''
    class of network variable
    '''
    def __init__(self, info): 
        # from base network element
        net_func.netelmt_group.__init__(self, info)      
        
        # fluid model
        self.fldmdl = None
    
    def set_fldmdl(self, fldmdl):
        # configure fluid model
        self.fldmdl = fldmdl
        print('Network fluid model set to {}.'.format(self.fldmdl))    

        # codes to configure the network based on the new fluid model