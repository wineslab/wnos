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
# class my_network
#######################################################

# add external dir into search list
import sys
sys.path.insert(0, './wos-decomp')

# from current folder
import net_name, net_func, net_node, net_sess, net_protocol, net_para, net_expr
import net_fluid

# from wos-decomp
import dcp_main

def new_ntwk(ntwk_type):
    '''
    create a network of the specified network type
    '''
    elmt_name = net_name.ntwk
    elmt_type = ntwk_type
    elmt_num  = 1    
    
    # changes:
    # rngtype added to indicate the element range
    addi_info = {'ntwk':None, 'parent':None, 'rngtype': net_name.single}
    info = net_func.mkinfo(elmt_name, elmt_type, elmt_num, addi_info)    # network topology info, 1 network created

    return net_ntwk(info)                                                # create network


class net_ntwk(net_func.netelmt_group):
    def __init__(self, net_info):  

        # parameters consistence check
        if net_info['elmt_subtype'] != net_name.adhoc:
           print('Currently only ad hoc wireless networks are supported.')
           exit(0)
        
        # from base network element
        net_func.netelmt_group.__init__(self, net_info)   
        
        # a list of missing ntwk elements, whenever an element in the list is created, the ntwk will be refreshed
        # will be implemnted in future
        
        # from net_para: create an empty variables database
        net_para.new_vardb(self)
        
        # set default network fluid model
        self.set_fldmdl(net_name.dtmn)
        
        # mapping of an every-type element to non-every instances
        # updated in dcp_gn.generator.update_every2nonevery()
        # used in alglib_func.fmincon_py.find_lbd() to determine the pattern of a set of elements when generating solution algorithm
        # Note: This varible is recorded in net_ntwk for easy global access
        self.every2nonevery = None
        
                    
    def ping(self):
        '''
        disp network information, only test purpose for now
        '''
        net_func.netelmt_group.ping(self)
        
        # display additionl information
        print('\n--------------------------------------------')
        print('            Network Control Problem')
        print('--------------------------------------------')
        
        # network size
        num_rglr = self.get_netelmt(net_name.node).get_memnum()
        num_ses = self.get_netelmt(net_name.ntses).get_memnum()
        #print('Ntwk info:')
        print('   Network Type:', self.stype)
        #print('   {} nodes, {} sessions'.format(num_rglr, num_ses))
        
        
        for x in self.expr_db.subgroup:
            expr = self.get_netelmt(x).get_expr()
            self.disp_expr(expr)
                       
    def disp_expr(self, expr):
        '''
        display information of equation
        '''
        net_expr.disp_expr(self, expr)
        
    def add_node(self, num_node):
        '''
        add nodes
        '''          
        net_node.add_node(self, num_node)

    def add_sess(self, num_ses):
        '''
        add sessions
        '''   
        net_sess.add_sess(self, num_ses)

    def set_protocol(self, protocol):
        '''
        build network based on user-specified protocol
        '''
        
        # get ptcl element
        ptcl = net_protocol.get_ptcldb(self)
        
        # configure ptcl information    
        ptcl.set_ptcl(protocol)

    def mkvar(self, var_para, var_expr, *args):
        '''
        make parameters variables based on information received from other elements
        this will overwrite mkvar() in the base class defined in net_func
        
        var_para: network element (parameter) for which the variable is defined
        var_expr: the expression of the variable
        args: a list of parameters indicating the range of ntwk elements        
        '''              
        
        # we need to generate a unique name for this variable
        #varname = net_func.mkvarname(var_para)        
        
        # name variables based on the expression instead of the parameter type 
        # e.g., if expression is 'x', name the variable 'x' and register in network as '_x'
        # the expression 'x' will be recorded in the variable object
        varname = net_func.mkvarname(var_expr)                
        
        # create a new variable
        newvar = net_para.mkvar(self, varname)
        
        # specify variable information
        newvar.setinfo(var_para, var_expr, *args)
        
    def make_var(self, str_varname, lst_elmt, lst_rng):
        '''
        new version of mkvar()
        str_varname: the name string of the variable
        lst_elmt: a list of ntwk element defining the path of the variable attribute
        lst_rng: the corresponding range of the ntwk element
        '''
        # create a new variable
        newvar = net_para.mkvar(self, str_varname)
        
        # specify variable information
        newvar.setinfo2(str_varname, lst_elmt, lst_rng)    

    def set_optvar(self, varname):
        '''
        Date Created: May 22, 2017
        Func: Configure a network parameter to be optimization variable. After the long 
        expression of a subproblem has been generated, check every element in the expression
        to see if any of them is optimization variable. The found optimization variable will be
        used to configure the solution algorithm in alglib_func.gnrt_alg().
        
        Called By: wos-demo.py
        '''
        
        # get the variable object
        obj_var = self.get_netelmt(varname)
       
        # set as optimization variable
        obj_var.is_var = True
        
        #print('Debug:')
        #obj_var.ping()
        #exit(0)
    
    def set_utlt(self, expression, *args):
        '''
        add utility to the expression database (exprdb)
        1) expression: the utility expression
        2) *args: variables used in the expression, currently not used
        '''
                
        # expression database
        exprdb = net_expr.get_exprdb(self)
        
        # -----------------------------------------
        # Preprocess utility expression
        expression_new = self.pre_utlt_process(expression)
        
        # print('---')
        # print(expression_new['fmlr'])
        # print(expression['varlst'][0])
        # exit(0)                    
        # -----------------------------------------
        
        # set utility
        # Change: expression -> expression_new
        exprdb.set_utility(expression_new, *args)       
        
    def pre_utlt_process(self, expression):
        # Add this new function
            
        # Preprocess utility expression. In the utilty expression, if the variable does not appear together with
        # any predefined operations, e.g., log, exp, add a dumy operation to it, i.e., dum, meaning original variable 
        # to indicate that variable associates with the utility function. This dummy operation will be removed from the 
        # expression when generating solution algorithms in alglib_func.gnrt_alg()        
        
        # expression: a dictionary containing the expression and the variable list
        # return: expression_new, i.e., the new expression with dum operation inserted when needed
        
        # Get the list of all possible operations
        lst_oper = net_name.lst_oper
        
        # Indicate if any operation contained, 0-no, 1-yes
        b_found = 0
        
        # Check for each operation to see if any appear in the expression except  the dum operation
        for oper in lst_oper:
        
            # If dum operartion, do nothing
            if oper == 'dum':                
                continue 
                
                
            # Otherwise, see if it is in the utility expression
            if oper in expression['fmlr']:
                b_found = 1
                break
        
        # If no regular operations are found, apply dum operation to the variable
        if b_found == 0:
            expr_full = expression['fmlr']          # Full expression
            expr_old = expression['varlst'][0]      # variable without operation 
            expr_new = 'dum(' + expr_old + ')'      # variable with dummy operation
            
            # Replace and update
            expr_full_new = expr_full.replace(expr_old, expr_new)
            expression['fmlr'] = expr_full_new
            
            
        return expression
        
    
    def add_cstr(self, expression, *args):
        '''
        add constraint expression
        
        expression: constraint expression
        args: other parameters, currently not used
        '''
        
        # expression database
        exprdb = net_expr.get_exprdb(self)
        
        # add constraint expression
        exprdb.add_cstr(expression, *args)
        
    def set_fldmdl(self, fldmdl):
        '''
        set network fluid model
        '''
        
        # get fluid model of the network
        fldmdl = net_fluid.get_fldmdl(self)
        
        # set fluid model
        fldmdl.set_fldmdl(net_name.dtmn)
        
    def optm(self, operation):
        '''
        network optimization 
        call functions from wos_decomp
        '''
        
        # Convert minimization to maximization by multiplying the utility function by -1        
        
        if operation == net_name.MIN:           
            # Extract the current utility expression 
            obj_utlt = self.get_netelmt(net_name.utility)
            # print('---')
            # print(obj_utlt.expr)
            
            # Multiply the expression by -1
            obj_utlt.expr = '-1*(' + obj_utlt.expr + ')'
        

        # problem decomposition
        dcp_main.numdcp(self)
        
        
    def getcstr(self, int_cstrid):
        '''
        get a network constraint indexed by int_cstrid
        '''        
        # get the expression database
        exprdb = self.get_netelmt(net_name.expr_db)
        
        # if the maximum number of constraints have been exceeded, return None
        if int_cstrid > exprdb.expr_cnt:
            return None
        else:
            # retrieve and return the expression object         
            cstrname = net_expr.mkcstrname(int_cstrid)           # construct constraint name
            cstrobj = getattr(exprdb, cstrname)                  # get constraint object
            return cstrobj
    