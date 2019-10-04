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
# Automatically Generated Soultion Algorihtm
#------------------------------------------------------
#[[[cog
#   import cog, datetime
#   cog.outl("# Code Date: %s" % datetime.datetime.now())
#]]]
#[[[end]]]
#######################################################

# Configure directory
import os, sys
p = os.getcwd()										  # Current directory
p = os.path.dirname(p)      						  # Parent directory
sys.path.insert(0, p+'/WNOSPYv2/wos-protocol')        # Directory of protocotols
sys.path.insert(0, p+'/WNOSPYv2/wos-network')         # Directory of network parameters
sys.path.insert(0, p+'/wnospyv2/wos-protocol')        # Directory of protocotols
sys.path.insert(0, p+'/wnospyv2/wos-network')         # Directory of network parameters

# Import protoco-related parameters
import ptcl_name

# Import network-related module
import net_name

# Import optimization module
from scipy.optimize import minimize
from numpy import *

########################################################
#              Define Objective Function
########################################################
#[[[cog
#   import sys
#   sys.path.insert(0, './wos-alglib')
#   import cog, alglib_config, alglib_name
#
#   alglib_config.objective = alglib_config.objective.replace(alglib_config.optvar, alglib_name.str_optvar)
#   alglib_config.objective = alglib_config.objective.replace(alglib_name.str_optvar+alglib_name.tmp_optvar_suf, alglib_config.optvar)
#
#   for kw in alglib_config.keyword:
#       alglib_config.objective = alglib_config.objective.replace(kw, 'ptcl_name.'+kw) 
#   cog.outl("def func(%s, sign=-1.0):"% alglib_name.str_optvar)
#   cog.outl("	return sign*1000*(%s)"%alglib_config.objective)
#]]]
#[[[end]]]

########################################################
#                    Constraints
########################################################
cons = (
{'type': 'ineq',
#[[[cog
#   import sys
#   sys.path.insert(0, './wos-alglib')
#   import cog, alglib_config
#   cog.outl("\'fun\':lambda %s: %s - %s}," %(alglib_name.str_optvar, alglib_name.str_optvar, alglib_config.lb))
#]]]
#[[[end]]]
{'type': 'ineq',
#[[[cog
#   import sys
#   sys.path.insert(0, './wos-alglib')
#   import cog, alglib_config
#   cog.outl("\'fun\':lambda %s: %s - %s})" %(alglib_name.str_optvar, alglib_config.ub, alglib_name.str_optvar))
#]]]
#[[[end]]]

########################################################
#                    Optimization
########################################################
#[[[cog
#   import sys
#   sys.path.insert(0, './wos-alglib')
#   import cog, alglib_config
#   cog.outl("def wnos_optimize():")
#   cog.outl("	result = minimize(func, %s, constraints=cons, method=\'SLSQP\', options={\'disp\': False})" %(alglib_config.lb))
#]]]
#[[[end]]]
	print '-1*(' + str(ptcl_name.link_sngl_lbd) + '*log(' + str(ptcl_name.lkgain00) + '*opt_var/(' + str(ptcl_name.lkitf00) + '+' + str(ptcl_name.lknoise00) + ') + 1)/log(2) + (opt_var - ' + str(ptcl_name.lkpwr00) + ') * sum(' + str(ptcl_name.para_pnl) + '))'
	return result
