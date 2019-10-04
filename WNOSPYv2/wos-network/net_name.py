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
# Name space of network elements and attributes
#######################################################

import sys
outf = open('output.txt','w')

#------------------------------------------
#                 network
#------------------------------------------
ntwk       = 'ntwk'                          # network element
adhoc      = 'Ad Hoc'                        # --- ad hoc network
cell       = 'Cellular'                      # --- cellular network

#------------------------------------------
#                 general
#------------------------------------------
para       = 'para'                          # parameter element: pwr, rate...
default    = '_default'                      # default parameter
vardb      = 'vardb'                         # refer to the database of variables

if_rgst    = 'if_rgst'                       # whether to register an element in ntwk
yes        = 'yes'                           # yes
no         = 'no'                            # no

all        = 'ALL'                           # to indicate the range of variables: all sessions, all src nodes
mltp       = 'MLTP'                          # >= 1, used when exact number is not known
every      = 'EVERY'                         # keyword: each, representing each network element 
sub        = 'SUB'                           # a subset
single     = 'SINGLE'                        # single network element

#------------------------------------------
#                 node
#------------------------------------------
node       = 'node'                          # node element

# src        = 'src'                           # source node
# dst        = 'dst'                           # destination node
# rin        = 'rin'                           # regular intermediate node
node_type  = [node]                          # node type list

ndpwr      = 'ndpwr'                         # trans power
ndlink     = 'ndlink'                        # the links associated to a node

spwr       = 'spwr'                          # src node power

rate       = 'rate'                          # node outgoing rate
srate      = 'srate'                         # src node rate
          
ndfreq     = 'ndfreq'                        # operating frequency (bandwdith)
sfreq      = 'sfreq'                         # src operating frequency (bandwdith)

rin_lbl    = ''                              # label for regular node: empty string
src_lbl    = 's'                             # label for source node    
dst_lbl    = 'd'                             # label for destination node    

#------------------------------------------
#                 link
#------------------------------------------       
lkrcvr     = 'lkrcvr'                        # reciever node of a link
lkcap      = 'lkcap'                         # capacity of link   
lkpwr      = 'lkpwr'                         # link power
lkfrq      = 'lkfrq'                         # frequency used by a link
lksinr     = 'lksinr'                        # link SINR
lktsmt     = 'lktsmt'                        # transmitter of link
lkrcvr     = 'lkrcvr'                        # receiver of link
lkgain     = 'lkgain'                        # link channel gain
lknoise    = 'lknoise'                       # link noise power
lkitf      = 'lkitf'                         # link interference power

lkset      = 'lkset'                         # set of links used by a session

ntlk       = 'ntlk'                          # the set of all links in the network

itfpwr     = 'itfpwr'                        # power of interference link

#------------------------------------------
#                 session
#------------------------------------------
#ses        = 'ses'                           # session element, replaced by ntses
ntses      = 'ntses'                         # set of sessions in the network 

ssrate     = 'ssrate'                        # session rate

src        = 'src'                           # src of sessions
dst        = 'dst'                           # dst of sessions

sslink     = 'sslink'                        # set of links of a session

ssset      = 'ssset'                         # set of sessions using a link

lkses      = 'lkses'                         # session set associated to a link  


#------------------------------------------
#                 protocol and layer 
#------------------------------------------
# general protocol
ptcl       = 'protocol'

# physical layer
CDMA       = {'name':'cdma', 'layer':'physical', 'alg': None}
phy_list   = [CDMA['name']]                 # list of physical-layer protocols currently supported

# transport layer
TCP_VEGAS  = {'name':'tcp_vgs', 'layer':'transport', 'alg': 'vegas'}                          
tspt_list  = [TCP_VEGAS['name']]            # list of transport-layer protocols currently supported

#------------------------------------------
#                 network expressions
#------------------------------------------
expr_db    = 'expr_db'                      # expression data base
expr_hldr  = 'expr_hldr'                    # expression holder
utility    = 'utlt'                         # utility expression
constraint = 'cstr'                         # constraint expression

fmlr       = 'fmlr'                         # formula of expression
varlst     = 'varlst'                       # variable list of expression


#------------------------------------------
#                 network operation
#------------------------------------------
MAX        = 'max'                          # network utility maximization
MIN        = 'min'                          # network utility minimization


#------------------------------------------
#                 fluid model
#------------------------------------------
fldmdl     = 'fldmdl'                       # network fluid model
dtmn       = 'determinstic'                 # determinstic fluid model


#------------------------------------------
#         parameter and variables
#------------------------------------------
leaf_para  = 'leaf_para'                    # leaf parameter, cannot be represented using other parameters
itmd_para  = 'itmd_para'                    # intermediate parameter, needs to be represented by other parameters
xtnl_para  = 'xtnl_para'                    # external parameter

# variables can be defined for these network elements; the variable definition function can be generalized
var_hldr_list  = [node, ntses, ndlink]        


#------------------------------------------
#         element relationship
#------------------------------------------         
elmt_asct = 'elmt_asct'                     # network element to which a parameter is associated

#------------------------------------------
#         numbers
#------------------------------------------  
max_exprcnt = 999


#------------------------------------------
#         protocol layer
#------------------------------------------ 
tspt    =   'tspt'                          # transport layer
phy     =   'phy'                           # physical layer

# list of all layers, used in dcp_hsub to determine the layer for a subproblem
lst_layer = [tspt, phy]


#------------------------------------------
#         external variable
#------------------------------------------ 
isxtnl     =       'isextnl'                # to mark if an element is external
pre_xtnl   =       '_pxnl_'                 # prefix for external element
suf_xtnl   =       '_sxnl_'                 # suffix for external element


#------------------------------------------
#         variable subtype
#------------------------------------------ 
power = 'power'                             # transmit power. variables belonging to this category include lkpwr, spwr...
rate = 'rate'                               # transmission rate. variables belonging to this category include ssrate...


#------------------------------------------
# variable default lower and upper bounds
#------------------------------------------ 
max_pwr_in_dB = 25.0
min_pwr_in_dB = 5.0
power_lwr_default = 10 ** (min_pwr_in_dB/10)          		# USRP Transmit Gain ), absolute value
power_upr_default = 10 ** (max_pwr_in_dB/10)      	        # 2, 15 are in dB

# Dec. 13, 2017; Guan; Change 10000 to 100000
max_rate_in_bps = 20000
min_rate_in_bps = 1000
rate_lwr_default = min_rate_in_bps/1000                        		# in kbit/seek
rate_upr_default = max_rate_in_bps/1000
                  

#--------------------------------------------------
# parameters used for defining signaling exchange
#--------------------------------------------------
chngain = 'chngain00'

#--------------------------------------------------
# Support operations
#-------------------------------------------------
# Operation 'dum' does nothing to the optimization variable rather than
# indicating that the variable comes from utility function; 
# Operation 'dum' is inserted when updating utility function and then removed when generating solution algorithm
lst_oper = ['log', 'exp', 'sqrt', 'sin', 'cos', 'dum']
