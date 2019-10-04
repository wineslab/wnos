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

class net_protocol_layer(net_func.netelmt_group):
    '''
    class of network protocol layer
    '''
    def __init__(self, info):
 
        # from base network element
        net_func.netelmt_group.__init__(self, info) 
        
        # layer parameters
        self.layer = None               # which layer
        self.ptcl  = None               # what protocol (TCP, UDP...)
        self.alg   = None               # protocol algorithm (Vegas, Reno...)
    
    def set_layer(self, info):
        '''
        configure layer information
        '''
        self.layer = info['addi_info']['layer']
        self.ptcl = info['addi_info']['protocol'] 
        self.alg = info['addi_info']['alg'] 
        
        print('Adding protocol {}:{} to {} layer'.format(self.ptcl, self.alg, self.layer))   