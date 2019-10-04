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
# parse utility
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from wos-network
import net_name, net_func

# from local folder
import dcp_name, dcp_cstr, dcp_var, dcp_inst, dcp_gn

def ps_utlt(xpd):
    '''
    parse the utility function for a NUM to generate its expanded version
    '''  
    # parse utility function
    print('Parsing utility function...')
    
    # generate an instance of the expression
    obj_utlt = gen_xpdutlt(xpd)
    
    # add the instance to xpd
    # xpd.add_utlt(obj_utlt)        # no need to add utlity explicitly, its name has been recorded in xpd.lst_inst


def gen_xpdutlt(xpd):
    '''
    generate expanded utility
    return the string name of the utility
    '''    
    # create the generator
    obj_utlt = xpd.get_netelmt(net_name.utility)
    gn = dcp_gn.create_gn(obj_utlt)
    
    # generate instance for utility
    obj_utlt = gn.get_newlst()
       
  
    # return the utility name
    return obj_utlt