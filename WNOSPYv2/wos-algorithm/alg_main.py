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
# main functions for algorithm generation
#######################################################

import sys
sys.path.insert(0, './wos-network')
sys.path.insert(0, './wos-decomp')
sys.path.insert(0, './wos-alglib')

# from wos-network
import net_name

# from wos-decomp
import dcp_name, dcp_xpd

# from wos-alglib
import alglib_main

# from local directory
import alg_func, alg_name, alg_lexpr

def alg(obj_xpd):
    '''
    func: generate numerical solution algorithms for each distributed network control problem
    return: an object containing all informaiton of the algorithms
    obj_xpd: object of the expanded network control problem, containing all horizontal distributed problems
    '''
    
    # creat an object for algorithms
    obj_netalg = alg_func.crt_netalg(obj_xpd)
        
    # Genrate long expressions by wirting out all intermediate expressions, e.g., SINR
    # In the resulting expression, all elements are leaf expression, i.e., expression that cann't 
    # be further expressed using smaller sub-expressions
    alg_lexpr.gen_longexpr(obj_netalg)
    
    # # add penalized item to each horizontal subproblem
    # alg_pnl.add_pnlitem(obj_alg)
    
    # # generate numerical solution algorithms
    # alg_nsl.gen_alg(obj_alg)
    
    # Generate solution algorithm, i.e., executable code to solve the optimization problem
    alglib_main.gnrt_alg_code(obj_netalg)
    
    
    
    
    