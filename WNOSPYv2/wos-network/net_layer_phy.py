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

import sys
sys.path.insert(0, './wos-network/physical')

# from current folder
import net_name, net_func, net_layer
                      
class ptcl_phy(net_layer.net_protocol_layer):
    '''
    class of physical layer protocol
    '''
    def __init__(self, info):
        net_layer.net_protocol_layer.__init__(self, info)
                
    def set_layer(self, info):
        '''
        configure layer information
        '''       
        # from base class
        net_layer.net_protocol_layer.set_layer(self, info)
        
        # if the current protocol supported?
        if self.ptcl not in net_name.phy_list:
           print('Error: Currently {} not supported at {} layer!'.format(self.ptcl, self.layer))
           exit(0)
           
        # from /physical import the corresponding physical layer module
        self.phy = __import__(self.ptcl)           
        
        # additional codes for layer configuration:       
        # setup parameter vector for frequency
        self.set_freq()
        self.set_pwr()
        self.set_link_rate()
        self.set_sinr()   
                
        # configure interference, which is an external paramter because it is comprises variables of other users   
        self.set_itf()
        #self.set_itfpwr()      
        
    def set_itf(self):
        '''
        func: configure total interference, which is an external paramter because it is comprises variables of other users 
        '''
        self.phy.set_itf(self)
        
    def set_itfpwr(self):
        '''
        func: configure individual interfering power
        '''
        pass
       
    def set_sinr(self):
        '''
        func: set up sinr for link 
        '''
        # # from /physical import the corresponding physical layer module
        # phy = __import__(self.ptcl)
        
        # set sinr
        self.phy.set_sinr(self)        
        
        
    def set_freq(self):
        '''
        set the number of frequency according to physical layer protocol
        '''        
        # # from /physical import the corresponding physical layer module
        # phy = __import__(self.ptcl)
        
        # set frequency
        self.phy.set_freq(self)
               
            
    def set_pwr(self):
        '''
        set the number of power according to physical layer protocol
        '''     
        # # from /physical import the corresponding physical layer module
        # phy = __import__(self.ptcl)
        
        # set power
        self.phy.set_pwr(self)
        

    def set_link_rate(self):
        '''
        set the rate achievable by a link with given physical layer technology
        '''
        # # from /physical import the corresponding physical layer module
        # phy = __import__(self.ptcl)
        
        # set rate
        self.phy.set_link_rate(self)