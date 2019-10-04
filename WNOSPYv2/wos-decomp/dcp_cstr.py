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
# Parse constraints
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from wos-network
import net_name, net_func

# from local folder
import dcp_name, dcp_set, dcp_inst, dcp_gn

def ps_allcstrs(xpd):
    '''
    parse all constraints to generate xpd
    xpd: object of the NUM problem
    '''
    
    # retrieve the network
    ntwk = xpd.get_ntwk()
    
    # process all constraints
    cstr_id = 1
    while True:        
        # retrieve constraint object, terminate if None returned
        obj_cstr = ntwk.getcstr(cstr_id)
        if obj_cstr == None:
            break;
        else:
            cstr_id += 1
            
        # process the retrieved constraint object
        ps_cstr(xpd, obj_cstr)
        
def ps_cstr(xpd, obj_cstr):
    '''
    parse a constraint
    '''      
    
    # create the generator
    gn = dcp_gn.create_gn(obj_cstr)
    
    # generate a constraint instance every time, until None instance
    while True:
        # generate new instances until None returned
        obj_inst = gn.get_newlst()
        if obj_inst == None:                             
            break
                   
        