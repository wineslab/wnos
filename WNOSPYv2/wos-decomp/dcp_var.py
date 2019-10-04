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
# parse variable
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from wos-network
import net_name, net_func

# from local folder
import dcp_name, dcp_cstr


def ps_var(xpd, var_name):
    '''
    parse a variable
    '''    
    print('Parsing variable {}...'.format(var_name))
    
    # variable object 
    varobj = xpd.get_netelmt(var_name)                                      
    para_name = varobj.getpara()                    # parameter name for which the variable is defined
    mbrobj = varobj.newfamset()                     # add member list for a variable    
    
    # Changes: will return the list when creating the list above
    # mbr_lst = varobj.getfamset()                  # get the member list for which the variale is defined
    
    # record the expanded varible    
    varinfo = {'var': var_name, 'para':para_name, 'lst':mbrobj.lst}
    dcp_xpd.add_xpdvar(xpd, varinfo)
          