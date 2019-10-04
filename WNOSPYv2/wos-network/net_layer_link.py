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
import net_name, net_func, net_layer

class ptcl_link(net_layer.net_protocol_layer):
    '''
    class of link layer protocol
    '''
    def __init__(self, info):
        net_layer.net_protocol_layer.__init__(self, info)
        
        # link layer protocol information    