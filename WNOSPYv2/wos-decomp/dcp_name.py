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
# Name space of c2d decomposition
#######################################################

#------------------------------------------
#             general
#------------------------------------------
prefix  =   '__'                        # prefix
suffix  =   '___'                       # suffix

zflen   =   2                           # the fixed length of string index

#------------------------------------------
#             set of members
#------------------------------------------

# Selecting 10 from 20 yields 184756 different combinations
# with around 97% probability, a unique combination can be generated with shuffle()
allnum = 20                             # the maximum number of members in set
subnum = 10                             # number of member in a subset
singlenum = 1                           # number of single element (e.g., network)  

#------------------------------------------
#             NUM
#------------------------------------------
xpd     =       'xpd'                   # expanded NUM problem
cstr    =       'cstr'                  # constraint
xpdutlt =       'xpdutlt'               # expanded utility
inst    =       'inst'                  # instance
generator =     'generator'             # generator
set     =       'set'                   # set

#------------------------------------------
#             member type (mt)
#------------------------------------------
mt_subset  = 'mt_subset'                # member type: subset

#------------------------------------------
#             vertical decomposition
#------------------------------------------
sym             =   'sym'                       # indication of symbolic domain
inst_sym        =   'inst_sym'                  # instance in symbolic domain
dualcoef        =   'dualcoef'                  # dual coefficient
lbd             =   'lbd'                       # labmda
vsub            =   'vsub'                      # vertical subproblem
hsub            =   'hsub'                      # horizontal subproblem
hcls            =   'hcls'                      # suffix of hsub class name

#------------------------------------------
#             protocol layer
#------------------------------------------
phy             =   'phy'                       # physical layer
tspt            =   'tspt'                      # transport layer

