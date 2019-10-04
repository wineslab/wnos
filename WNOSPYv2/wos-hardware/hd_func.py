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
# decomposition functions
#######################################################

import wos_ntwk, wos_type, wos_nd, wos_par, wos_func, wos_sess


# -------------------------------------------------------------------------
# network element operations
# -------------------------------------------------------------------------

def assign_wos_id():
    '''
    count network element, increase 1 every time a new element is added    
    '''
    wos_type.cur_wos_id += 1
    return wos_type.cur_wos_id

def mkinfo(elmt_type, elmt_subtype, addi_info):
    '''
    basic information to define a network element
    '''
    net_info = {'elmt_type': elmt_type, 'elmt_subtype': elmt_subtype, 'addi_info': addi_info}
    return net_info   
 
def func_new_elmt(elmt_type):
    '''
    callback funtions to create different network elements
    '''
    func = {wos_type.ntwk:wos_ntwk.wos_ntwk,\
            wos_type.node:wos_nd.wos_nd,\
            wos_type.par :wos_par.wos_par,\
            wos_type.ses :wos_sess.wos_sess}

    return func[elmt_type]

def new_ntwk_elmt(info):
    '''
    create new network element
    '''
    #print info
    
    func = func_new_elmt(info['elmt_type'])              # find out the function to create a new element 
    return func(info)                                    # create network element

