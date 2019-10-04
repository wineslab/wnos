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
# main file for network control problem decomposition
#######################################################

import sys
sys.path.insert(0, './wos-network')
sys.path.insert(0, './wos-algorithm')

# from wos-network
import net_name

# from wos-algorithm
import alg_main

# from local folder
import dcp_name, dcp_xpd, dcp_vdcp, dcp_hdcp

def numdcp(ntwk):
    '''
    NUM problem decomposition
    ntwk: network object
    '''
    print('Decomposing...')  
    print('Generating expanded NUM...')
    
    # generate an expanded NUM problem
    obj_xpd = dcp_xpd.gen_xpd(ntwk)
    
    #exit(0)

    # vertical decomposition
    print('Starting vertical decomposition...')
    print('Entering symbolic domain...')        
    dcp_vdcp.vdcp(obj_xpd)
        
    # horizontal decomposition
    print('Starting horizontal decomposition...')
    dcp_hdcp.hdcp(obj_xpd)

    #exit(0)
   
    # call algorithms generation functions
    print('Generating algorithms for horizontal subproblems')
    alg_main.alg(obj_xpd)
   