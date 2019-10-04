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
# parameters, variables
#######################################################

import net_name, net_func, net_expr

######################################################################################################
# for parameters
######################################################################################################

class net_para(net_func.netelmt_group):
    '''
    class of network parametes and variables
    '''
    def __init__(self, info):
 
        # from base network element
        net_func.netelmt_group.__init__(self, info) 

        # properties of parameter
        self.expr_hldr  =  None                             # Symbolic expression of the element; There should be an expression management module
        self.expr_hldr_xtnl = None                          # external expression
        
        self.para_type  =  info['addi_info']['para_type']   # parameter type
        
        # protocol code: the code will be used to identify which function should be called to express a variable
        self.ptcl_code  = None
        
        # June 3, 2017
        # Lower and upper bounds of the parameter. APIs should be provided to set these bounds, hard coded for now.
        self.lwr_bnd = 'default'
        self.upr_bnd = 'default'      
        
                
    def set_expr(self, expr):
        '''
        set the expression to expr
        '''                     
        if self.expr_hldr == None:                                                                          # expression holder has not been created, create one
        

            self.expr_hldr = self.new_expr_hldr(expr)
            
        else:
            self.expr_hldr.set_expr(expr)
            
    def set_expr_xtnl(self, expr):
        '''
        expr: expression to initialize the holder
        
        func: set external expression for a network parameter
        '''
        if self.expr_hldr_xtnl == None:                   # expression holder has not been created, create one
            self.expr_hldr_xtnl = self.new_expr_hldr(expr)
            
        else:
            self.expr_hldr_xtnl.set_expr(expr)        
        
            
    def new_expr_hldr(self, expr):
        '''
        expr: expression to initialize the holder
        
        func: create a new expresssion holder object
        return: the created object
        '''
        #---------------------------------------------------------------      
        elmt_name = net_name.expr_hldr                                                                  # element info
        elmt_num = 1     
        
        addi_info = {'ntwk':self.ntwk, 'parent':self, 'expr': expr, net_name.if_rgst: net_name.no}      # no need to register element in ntwk
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

        obj_expr_hldr = net_expr.net_expr_hldr(info)                                                    # create element
        #self.addgroup(elmt_name, elmt)                                                                 # no need to record expression holder as subgroup 

        obj_expr_hldr.ping()
        #---------------------------------------------------------------          
        
        return obj_expr_hldr
        
    def get_expr(self):
        '''
        get parameer expression
        '''
        
        if self.expr_hldr == None:                          # expression holder has not been created
            print('Error: None expression holder!')
            exit(0)
        else:
            return self.expr_hldr.get_expr()        

######################################################################################################
# for variables       
######################################################################################################
 
def new_vardb(ntwk):
    '''
    create an empty vraiable database
    '''
    if hasattr(ntwk, net_name.vardb) == False:      
        #---------------------------------------------------------------      
        elmt_name = net_name.vardb
        elmt_num = 1     
        addi_info = {'ntwk':ntwk, 'parent':ntwk, net_name.if_rgst:net_name.yes}
        info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)  # element info

        elmt = net_vardb(info)                                        # create element
        ntwk.addgroup(elmt_name, elmt)                                # add element as a subgroup 
        
        x = getattr(ntwk, elmt_name)
        x.ping()
        #---------------------------------------------------------------          

class net_vardb(net_func.netelmt_group):
    '''
    class of network variable database, just a normal network element structure
    '''
    def __init__(self, info):
 
        # from base network element
        net_func.netelmt_group.__init__(self, info)         
        
        
def mkvar(ntwk, varname):
    '''
    create a new optimization variable
    '''
    #---------------------------------------------------------------      
    elmt_name = varname                                                 # element info
    elmt_num = 1     
        
    addi_info = {'ntwk':ntwk, 'parent':ntwk.vardb}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = net_var(info)                                                # create element
    ntwk.vardb.addgroup(elmt_name, elmt)                                # add element as a subgroup 
            
    newvar = elmt
    newvar.ping()
    #---------------------------------------------------------------     
        
    return newvar
        
class net_var(net_func.netelmt_group):
    '''
    class of network variable
    '''
    def __init__(self, info): 
        # from base network element
        net_func.netelmt_group.__init__(self, info)      
        
        # variable information
        # (1) currently a variable is associated to only nodes
        # (2) in future, a variable can also be associated to frequencies, among others, not considered for now
        self.para_asct      = None                      # the leaf parameter to which the variable is associated 
        self.elmt_asct      = None                      # for which kind of network elements the variable is defined? rin, src, dst
        self.elmt_asct_rng  = None                      # the range of the network element 
                
        self.var_expr       = None                      # variable expression
        
    def getfamset_xxx(self):                            # _xxx: discarded function
        '''
        get the set of family memebers
        '''
        
        # error check
        if len(self.fam.allsubs) == 0:
            print('Error: No subset created for variable!')
            exit(0)
        
        str_id = self.fam.allsubs[0]                    # default: only one subset for each variable
        subobj = getattr(self.fam, str_id)              # object of the subset
        return subobj.lst                               # a list of members in the subset
        
    def newfamset(self):
        '''
        generate a subset for this variable
        '''
        return self.fam.addfamset(self)
        
    def getname(self):
        '''
        expression of the variable
        '''
        return self.var_expr
        
    def getpara(self):
        '''
        for which parameter?
        '''
        return self.para_asct.type
        
    def getrng_xxx(self):                                           # _xxx indicates a disabled function
        '''
        range in which the variable is defined
        '''
        return self.elmt_asct_rng
        
    def getelmt(self):
        '''
        path of ntwk elements is defined
        '''
        
        # construct a string in the form of elmt(rng)->elmt(rng)...
        elmtinfo = ''
        
        # process every elemnt in the path of the variable
        num_elmt = len(self.elmt_asct)                              # how many elememnts along the path?
        for idx in range(num_elmt):
            elmtinfo = elmtinfo + self.elmt_asct[idx] + '(' + self.elmt_asct_rng[idx] + ')'
            
            if idx < num_elmt - 1:                  # does not add '->' after the last element
                elmtinfo = elmtinfo + ' -> '
        
        return elmtinfo
        
    def getvarinfo(self):
        '''
        get variable information
        '''
        return self.getname() + ': ' + self.getpara() + ' {' + self.getelmt() + '}'
        
    def setinfo_xxx(self, var_para, var_expr, *args):              # _xxx indicates a discarded function; to avoid mistakenly calling
        '''
        specify variable information
        
        var_para: network element (parameter) for which the variable is defined
        var_expr: the expression of the variable
        args: a list of parameters indicating the range of ntwk elements             
        
        Changes (05/28/2016): _xxx indicates that this function will be replaced by setinfo2()
        '''
        self.para_asct = var_para
       
        # identify the element type
        elmt = self.para_asct
        depth = 0                                                        # to identify the range of the element
        while elmt.parent != net_name.ntwk and elmt.parent != None:      # check the parent element (ntwk's parent is None)
            depth += 1
            if elmt.parent.type in net_name.var_hldr_list:               # if in the variable holder list
                self.elmt_asct = elmt.parent                             # it is the element for which the variable is defined 
                break
            elmt = elmt.parent                                           # otherwise, go the its parent
        
        # specify the range of the holding element (for which the variable is defined)
        self.elmt_asct_rng = args[-(depth+1)]
        
        # variable expression
        self.var_expr = var_expr      
        
        # configure the set of members for network control problem decomposition
        self.fam.add_famset(self)                                        # self (the variable) as the fam_hldr (family holder)
        
        self.ping()                                                      # display the updated variable information
        
    def setinfo2(self, str_varname, lst_elmt, lst_rng):
        '''
        specify variable information
        
        str_varname: the name string of the variable
        lst_elmt: a list of ntwk element defining the path of the variable attribute
        lst_rng: the corresponding range of the ntwk element           
        '''
        self.para_asct = self.get_netelmt(lst_elmt[-1])                  # variable parameter: pwr, rate, etc
       
        # identify the element type
        # Since the same network parameter can be reached via differnt paths, the path needs to be recorded
        self.elmt_asct = lst_elmt[:-1]                                   # path ntwk elements for which the variable is defined
        
        # specify the range of the holding element (for which the variable is defined)
        self.elmt_asct_rng = lst_rng[:-1]
        
        # variable expression
        self.var_expr = str_varname      
        
        
        #self.ping()                                                      # display the updated variable information        
        
    def ping(self):
        '''
        display variable information
        '''
        net_func.netelmt_group.ping(self)                                # ping from base class
        
        if self.para_asct != None:                                       # if information has been specified 
            print('target elmt: {}'.format(self.para_asct.type))
            print('holder elmt: {}'.format(self.elmt_asct.type))
            print('holder rng: {}'.format(self.elmt_asct_rng))