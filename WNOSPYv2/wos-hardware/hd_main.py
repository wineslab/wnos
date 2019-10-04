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

# from wos-network
import net_name

def ntwk_opt(ntwk, operation):
    '''
    bridge function of functions in this folder (wos-decomp) and funtions in other folders
    '''
    if operation == net_name.max:
        ntwk_max(ntwk)
    elif operation == net_name.min:
        ntwk_min(ntwk)
    else:
        print('Error: Undefined network operation!')
        exit(0)
        

def ntwk_min(ntwk):
    '''
    minimize network utility
    '''
    print('Minimization currently not supported!')
    exit(0)
    
def ntwk_max(ntwk):
    '''
    maximize network utility
    '''    
    print('Maximization currently not supported!')
    exit(0)    