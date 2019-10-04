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
# Date: 05/04/2016
# Author: Zhangyu Guan
# Project Manager: Tommaso Melodia, Zhangyu Guan
# Physical layer: CDMA
#######################################################

import sys
sys.path.insert(0, './wos-network')

# from wos-network
import net_name, net_func

# parameters
# layer: layer element of the network; one can access all other elements of the whole network via layer

def set_freq(layer):
    '''
    configure frequency for CDMA
    '''
    # with cdma, only one frequency band will be used, 
    # therefore set the number of freq to one for nodes                                       
    ndfreq  = layer.get_netelmt(net_name.ndfreq)                  # get freq element of the network            
    ndfreq.set_memnum(1)                                          # set freq number
                    
                
def set_pwr(layer):
    '''
    configure power for CDMA
    '''           
    # get the number of frequency
    freq = layer.get_netelmt(net_name.ndfreq)                     # freq element
    num_freq = freq.get_memnum()                                  # get the number
        
    # pwr number = freq number
    ndpwr = layer.get_netelmt(net_name.ndpwr)
    ndpwr.set_memnum(num_freq)                           
    
def set_link_rate(layer):
    '''
    configure link rate indexed by rin and src nodes
    '''
    
    # get link capacity element of link
    lkcap = layer.get_netelmt(net_name.lkcap)
       
    # set protocol code ('cdma') for rate
    # the code will be used to identify which function should be called to express a variable
    lkcap.ptcl_code = layer.ptcl
    
    # construct and set rate expression
    lkcap_expr = rate_cdma(layer)    
    lkcap.set_expr(lkcap_expr)
    
def rate_cdma(layer):
    '''
    construct rate expression for cdma
    layer: protocol layer
    '''    
    # all variables must be predefined for certain protocols, check this in future
    # changes: lksinr -> __lksinr___
    expr = net_func.mkexpr('log(1 + __lksinr___)/log(2)', 'lksinr')
    
    return expr
    
def set_sinr(obj_layer):
    '''
    obj_layer: object of physical layer
    
    func: set sinr for link 
    return: updated sinr information, e.g., expression
    '''
    # get lksinr object
    obj_lksinr = obj_layer.get_netelmt(net_name.lksinr)
    
    # protocol code
    obj_lksinr.ptcl_code = obj_layer.ptcl
    
    # set expression for link sinr
    dict_expr = sinr_cdma()            # construct link sinr expression             
    obj_lksinr.set_expr(dict_expr)
    
def sinr_cdma():
    '''
    func: construct SINR expression for CDMA
    return: dictionary for sinr expression
    '''
    
    # use __ and ___ to indicate a keyword
    dict_expr = net_func.mkexpr('__lkpwr___ * __lkgain___ / (__lknoise___ + __lkitf___)') 
    
    return dict_expr

def set_itf(obj_layer):
    '''
    func: configure interference, which is an external paramter because it is comprises variables of other users 
    '''
    # get lksinr object
    obj_lkitf = obj_layer.get_netelmt(net_name.lkitf)
    
    # protocol code
    obj_lkitf.ptcl_code = obj_layer.ptcl
    
    #set external expression for link sinr
    dict_expr = itf_cdma()            # construct link interference expression             
    obj_lkitf.set_expr_xtnl(dict_expr)    
    
def itf_cdma():
    '''
    notes: Itf is a time-varying network elements. It involves the parameters 
    Assume there are three intefering links 
    
    func: construct interference expression for CDMA
    return: dictionary for interference expression    
    '''
    
    # use __ and ___ to indicate a keyword
    dict_expr = net_func.mkexpr('__itfpwr___xtnl_01 + __itfpwr___xtnl_02 + __itfpwr___xtnl_03') 
    
    return dict_expr