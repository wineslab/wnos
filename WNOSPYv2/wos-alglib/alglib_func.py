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
# Module description: Template of fmincon with utility function and parameters that can be replaced 
# based on distributed network control problems resulting from decompsition. The resulting algorithm
# can be complied directly using Python.
#######################################################

import sys, os
sys.path.insert(0, './wos-network')
sys.path.insert(0, './wos-decomp')
sys.path.insert(0, './wos-algorithm')
sys.path.insert(0, './wos-alglib')
sys.path.insert(0, './wos-protocol')

# from wos-network
import net_name, net_func

# from wos-decomp
import dcp_name, dcp_xpd

# from wos-algorithm
import alg_func, alg_name

# from current folder
import alglib_name

# from wos-protocol
import ptcl_name

# from sympy
from sympy import *

# string operation 
import re

def get_next_subprob(obj_netalg):
    '''
    Func: Get netxt subproblem for which the algorithm code is generated
    
    obj_netalg: the object of problem expression, an element of network xpd (expanded control problem) object
    
    Return: a "code template object" for the subproblem, None if all subproblems have been processed
    '''
    
    # loop until finding a subproblem that hasn't been processed or all subproblems have
    # been processed
    while True:   
        ######################################################
        # get the next subproblem, loop over all subproblems
        b_last = obj_netalg.get_nexthsub()
        
        # return None if all subproblems have been processed
        if b_last == True:        
            return None
        
        ######################################################
        # At which layer is the problem?
        curhsub = obj_netalg.obj_curhsub            # current subproblem
        layer = curhsub.layer                       # layer information
  
        # if the layer has been processed, skip the subproblem
        # otherwise, record the layer as processed and proceed
        if layer in obj_netalg.lst_processed_layer:
            continue                                        # skip        
        else:
            obj_netalg.lst_processed_layer.append(layer)    # record as processed
        
        ######################################################
        # determine the name of the code template object           
        str_objname = curhsub.gen_code_name(layer)
        
               
        ######################################################
        # Create an algorithm code template object
        obj_code = crt_fmincom(obj_netalg, str_objname)
                
        # Link the code object to the subproblem
        curhsub.set_code(obj_code)          
            
        # Return the current subproblem   
        return curhsub
    

def crt_fmincom(obj_netalg, objname):
    '''
    func: create the code object for fmincon algorithm
    return: the algorithm object
    
    obj_netalg: object of network algorithm, including all subproblems and the
    corresponding code objects
    
    objname: name of the code object to be created
    '''
    
    # Check validity of the object name 
    if objname == None:
        print('Code object name cannot be None')
        exit(0)
    
    # Create object
    #---------------------------------------------------------------    
    elmt_name = objname                                             # element info    
    elmt_num = 1     
                                  
    addi_info = {'ntwk':obj_netalg.ntwk, 'parent':obj_netalg.obj_curhsub}
    info = net_func.mkinfo(elmt_name, None, elmt_num, addi_info)        

    elmt = fmincon_py(info)                                         # create element
    elmt.parent.addgroup(elmt_name, elmt)                           # add element as a subgroup 

    elmt.ping()
    #--------------------------------------------------------------- 

    return elmt  
    

class fmincon_py(net_func.netelmt_group):
    '''
    Generate python code that calls matlab function fmincon() to solve a given network control problem.
    This class defines the template of fmincon, configure the parameters according to specific problem, and 
    then generate the operational python code 
    '''
    def __init__(self, info):  
        # From base network element
        net_func.netelmt_group.__init__(self, info)  
        
        
        # Function name of the algorithm to be generated
        self.alg_name = self.get_alg_name() 
      
        # Symbolic optimization parameters, updated by self.gnrt_alg(), used for configuring
        # objective function of the solution algorithm
        self.sym_func = None                # objective function 
        self.sym_optvar = None              # optimization variable
        
        # Information about Lagrangian multiplier coefficients, updated in self.find_lbd().
        # This is used to identify the coefficient pattern when mapping instantiations back to 
        # general network elements
        self.Lagrangian = None
        
    def get_alg_name(self):
        '''
        Determine the function name of the algorithm. The name is formed by two parts:
        code template name (e.g., code_phy) and algorithm type (e.g.,itpt), connected by
        dash.
        '''                   
        return self.type + alglib_name.code_connection + alglib_name.alg_type        
                           
    def gnrt_alg(self):
        '''
        Generate python code of the optimization algorithm
        
        Called By: dcp_hsub.hsub.gnrt_alg()
        '''
		
        #################################################################
		# Determine optimization variable
        #
        # Multiple (but same) optimization variables may be returned, use only one of them
        lst_optvar = self.parent.get_optvar()              
        optvar = lst_optvar[0]  
		
        # June 13, 2017
        # Remove prefix '__' and suffix '___' to avoid treating varibles as global
        tmp_optvar = self.rmv_pre_suf(optvar)
        self.sym_optvar = sympify(optvar)                # record optimization variable  		
		
		#################################################################
        # Configure objective function
        self.sym_func = self.parent.get_lexpr()          # symbolic expression
        
        # print('---')
        # print(self.sym_func)
        # exit(0)        

        # Process the symbolic expression by collecting Lagrangian coefficients
		# self.sym_func will be updaetd in this step
        new_expr = self.analyze_Lag_pattern()
		
        #################################################################
        # Generate penalization item of the utility function based on partial linerazation decomposition (PLD)
        dict_pnl = self.gnrt_pnl()
		 
        pnl = dict_pnl['str_der']
        str_keyword = dict_pnl['str_keyword']
		
        # June 15, 2017
        # Remove prefix '__' and suffix '___' to avoid treating varibles as global		
        new_pnl = self.rmv_pre_suf(pnl)	
        # str_keyword = self.find_keyword(new_pnl)	                # Call this function in self.gnrt_pnl()	
		
        new_keyword = self.rmv_pre_suf(str_keyword)					# Remove '__' and '___'
        
        # Construct output file name        
        pnl_file = 'wos-alglib/alglib_' + self.parent.layer + 'pnl.py'
        f = open(pnl_file, 'w')
        
        # Write penalization information to file
        f.write('pnl = ' + new_pnl)
        f.write(new_keyword)
        
        f.close()
        #################################################################
		
        
        #################################################################
        # Form configuration file name
        file_cfg = 'wos-alglib/alglib_config.py'
        
        # Configure parameters for solution algorithm template        
        f = open(file_cfg, 'w')
                
        # Configure optimization variable
        #print('Debug:')
        #print(self.parent.get_optvar())
        #exit(0)
        		                                   		
        # Add penalization item to objective function if penalization is enabled
        if ptcl_name.price == 'DPL' and new_pnl != 'None':
            new_expr = new_expr + ' + (' + tmp_optvar + ' - ' + alglib_name.str_optvar  + alglib_name.tmp_optvar_suf +') * sum(para_pnl)' 		
		        
        # Not needed anymore, new expression gets returned from self.analyze_Lag_pattern()
        #str_func = str(self.sym_func)                   # convert symbolic to string
		
        # June 13, 2017
        # Remove prefix '__' and suffix '___' to avoid treating varibles as global		
        new_new_expr = self.rmv_pre_suf(new_expr)
        
        f.write('optvar = \'' + tmp_optvar + '\'\n')
        f.write('objective = \'' + new_new_expr + '\'\n') 
		
        # June 23, 2017, Guan
        # Find the keywords in utility function, then add module name (e.g., "ptcl_name.") before
        # each keyword except the optimization variable 
        obj_keyword = self.find_keyword(new_new_expr)
        f.write(obj_keyword + '\n')

        # Configure lower and upper bounds 
        dict_varbnd = self.dtm_varbnd(optvar)
        f.write('lb = \'' + dict_varbnd['lwr_bnd'] + '\'\n') 
        f.write('ub = \'' + dict_varbnd['upr_bnd'] + '\'\n')
        
        f.close()
		
        
        #################################################################
        # Form output file name for solution algorithm 
        out_file = 'wos-alglib/alglib_' + self.parent.layer + 'sol.py'
        
        #################################################################
        # Generate operational code of the solution algorithm
        os.system('python -m cogapp -d -o ' +  out_file + ' wos-alglib/alglib_template.py ')
        #exit(0)
        
        #################################################################
        # Determine signaling exchange, i.e., what information should be exchanged
        str_signling = self.dtm_lbd_xchg()
        if str_signling ==  None:
            str_signling = 'None'
                                  
        ##################################################################################
        # Update lbd configuration file alglib_xxxlbd.py         
        
        # Generate the name of signaling configuration file alglib_xxxlbd.py with xxx representing layer 
        file_cfg = 'wos-alglib/alglib_' + self.parent.layer + 'lbd.py'
        
        # Open the file and write the configuration information
        f = open(file_cfg, 'w')
		
        # June 13, 2017
        # Remove prefix '__' and suffix '___' to avoid treating varibles as global		
        new_str_signling = self.rmv_pre_suf(str_signling)	
        
        #############################################################
        # Find keywords contained in the returned singaling expression
        str_keyword = self.find_keyword(new_str_signling)
        #############################################################
		
        f.write('lbd_signaling = \'' + new_str_signling + '\'\n')
        print(str_keyword)
        f.write(str_keyword)
        f.close()
		
    def find_keyword(self, expr):
        '''
        Find all keywords contained in a string expression. 
        Return the list of all keywords in string format
		
		Parameter can be either string or symbolic. In the former case, string should be converted to symbolic first. 
		
        Called By: self.gnrt_alg()
        '''
        
        # Check if the string expression is valid
        if expr == 'None':
            return '\nkeyword = None'
   		
        # Convert the string expression to symbolic if parameter is string type
		
        if type(expr) is str:		
            sym_expr = sympify(expr)
        else:
            sym_expr = expr
			
        # print('Debug:', sym_expr)
        # input('...')
        
        # Loop over all args of the symbolic expression
        keyword = []
        for this_args in preorder_traversal(sym_expr):
            if this_args.args == () and  sum(map(lambda kw: kw in str(this_args), alglib_name.lst_flag)) != 0:    	# This is a leaf item and contains keyword at least one of the flags ('00') specified in the flag list
                keyword.append(str(this_args))                                  	                            # Find a keyword, append it to the list
				
        # Convert the keyword list to a string
        str_keyword = '\nkeyword = ['                     # Initialization
        is_first = True                                 # Indicate if this keyword the first one in the list, no: add ',' before it, yes: don't add
        for kw in keyword:
            if is_first == True:
                str_keyword = str_keyword + '\'' +  kw + '\''
                is_first = False
            else:
                if str_keyword.find(kw) == -1:
                    str_keyword = str_keyword + ',\'' +  kw + '\''
                else:
                    pass				
        str_keyword = str_keyword + ']'				
    
        return str_keyword
    
    def rmv_pre_suf(self, old_str):
        '''
        Remove prefix '__' and suffix '___' to avoid treating varibles as global
        '''
		
        new_str = old_str.replace(dcp_name.suffix, '')		# Remove '___'
        new_str = new_str.replace(dcp_name.prefix, '')      # Remove '__'
		
        return new_str
	
        
    def gnrt_pnl(self):
        '''
        Generate penalization item of the utility function based on partial linerazation decomposition
        
        Called By: self.gnrt_alg()
        '''
        
        #####################################################################
        # Find out the external parameter by looping over all variables
        
        # List of all leaf parameters contained in this expression
        lst_leaf = self.parent.lexpr.lst_leaf
        
        # Loop over all parameter to search for external parameter
        dict_xtnl_der = None
        for para_name in lst_leaf:
            para_obj = self.get_netelmt(para_name)           # Get the corresponding object 
            if para_obj.is_xtnl() == True:
                dict_xtnl_der = para_obj.der                 # Get the derivative dictionary
                break;
        
        # If there is no external parameter in the expression, so the penalization item is empty string ''
        if dict_xtnl_der == None:
            return {'str_der': 'None', 'str_keyword': '\nKeyword = None'}
        else:                                                                           # Determine the leaf parameter used in the utlity expression
            xtnl_para = dcp_name.prefix + para_name + dcp_name.suffix + '00'            # Here, '00' is hard coded
        
        
        #####################################################################
        # Derive the derivative of utility function with respect to external variable
        
        # Determine the keyword of optimization variable, e.g., if optimization variable is __lkpwr___0, then keyword is lkpwr
        xtnl_var = None
        for para_name in lst_leaf:
            if para_name in str(self.sym_optvar):
                xtnl_var = para_name

        if xtnl_var == None:
            print('Error: External variable cannot be None!')
            exit(0)

        
        xtnl_der = dict_xtnl_der[xtnl_var]
        
        
        utlt_der = diff(self.sym_func, sympify(xtnl_para))
		
		# Find keywords contained in the symbolic expression
        str_keyword = self.find_keyword(utlt_der)
        new_keyword = str_keyword.replace(']', ',\'' + xtnl_der + '\']')								# Add keyword related to external variables
		
        
        # Append the dertivative of external parameter with respect to external variable
        str_der = '\'(' + str(utlt_der) + ')*' +  xtnl_der + '\''
		
        # Record a symbolic version of str_der, because there is problem when converting string to symbolic if the string contains 'Subs'
        ptcl_name.sym_phypnl = utlt_der*sympify(xtnl_der)
        # print('Debug:')
        # print(ptcl_name.sym_phypnl)
        # input('...')
        
        # print(str_der)
        # input('...')       
        
        # The string of penalization coefficient
        return {'str_der': str_der, 'str_keyword': new_keyword}
        
    def dtm_lbd_xchg(self):
        '''
        Determine signaling exchange, i.e., at each layer what information should be passed to other layers.
        In current scheme, what is acatually determined is the coefficient of Lagrangian coefficient. If the Lagrangian
        is a local single parameter, it means the layer is receving signaling from other layers and there is no need to 
        pass any parameter to other layers. If the Lagrangian is a set-type parameter, it means the layer needs to send
        signaling to all subproblems from which it receives Lagrangian coefficients.
        
        Input of the function is self.sym_func
        Return the sigaling to be exchanged 
        
        Called By: self.gnrt_alg()
        '''
        
        ##################################################################################
        # Determine if signaling is needed by checking if Lagrangian coefficient is single or set-typle        
        
        # Feature of single-type Lagrangian coefficient
        feat_sngl = alglib_name.sngl + alglib_name.Lag_connect + alglib_name.Lag_suffix
        
        # If the feature apprears in the utility expression, then no signaling exchange is needed
        str_expr = str(self.sym_func)                   # Convert symbolic to string
        b_find = str_expr.find(feat_sngl)
        
        # A matching found, no need to exchange Lagrangian coefficient signaling
        if b_find != -1:
            signaling = None
            return None
        

        if ('+' in str_expr) and ('-' in str_expr):
            # Loop over all sub-expressions
            for expr in self.sym_func.args:
                str_expr = str(expr)
                pos_lbd = str_expr.find(alglib_name.Lag_suffix)     # Search 'lbd' in the expression
                # print(str_expr)
                # print(pos_lbd)
                if pos_lbd == -1:                                   # 'lbd' not in, do nothing            
                    pass
                else:                                               # 'lbd' is in, finish searching 'lbd'; Here, it is assumed 'lbd' is in at most one sub-expression 
                    break
        else:
            pos_lbd = str_expr.find(alglib_name.Lag_suffix)
        
        
        # Locate feature string "sum(" and ")"
        feat_str = 'sum('
        pos_left = str_expr.find(feat_str)
        if pos_left == -1:
            print('Error: Not able to find feature string \'sum\'!')
            exit(0)
            
        # Search the first ")" after "sum("
        feat_str = ')'
        pos_right = str_expr.find(feat_str, pos_left)
        if pos_right == -1:
            print('Error: Not able to find feature string \')\'')
            exit(0)
                
        
        #################################################################################
        # Extract the coefficient by replacing the located sum(Lagrangian Coefficient) using "1"
        old_str = str_expr[pos_left:pos_right+1]
        new_str = '1'
        str_expr = str_expr.replace(old_str, new_str)
        
        # Simplify string expression by converting it to symbolic domain
        sym_expr = sympify(str_expr)
        sym_expr_simp = simplify(sym_expr)
        
        
        return str(sym_expr_simp)
        
        
    def dtm_varbnd(self, var_inst):
        '''
        Determine the lower and upper bounds of optimization variable. Parameter "var_name" is a variable instiantion, this function 
        first extract the general variable name, and then indentifies the bounds. 
        
        Return a dictionary with lower and upper bounds.
        
        Called By: self.gnrt_alg()
        '''
        
        ################################################################
        # Determine general variable name
        
        # Find occurances of prefix and suffix in parent string
        pos_pre = [m.end() for m in re.finditer(dcp_name.prefix, var_inst)]
        pos_suf = [m.start() for m in re.finditer(dcp_name.suffix, var_inst)]

        if len(pos_pre) == 0 or len(pos_suf) == 0:
            print('Error: The input var_inst is not a variable instance!')
            exit(0)
        
        var_name = var_inst[pos_pre[0]:pos_suf[0]]
        
        ################################################################
        # Locate the variabe object
        var_obj = self.get_netelmt(var_name)
        # var_obj.ping()
        # exit(0)
                
        ################################################################
        # Identify the bounds
        str_lwr_bnd = 'net_name.' + var_obj.sub_type + '_lwr_default'
        str_upr_bnd = 'net_name.' + var_obj.sub_type + '_upr_default'
               
        ################################################################
        # Return
        return {'upr_bnd':str_upr_bnd, 'lwr_bnd':str_lwr_bnd}
        
        
    def analyze_Lag_pattern(self):
        '''
        Analyze the pattern of the Lagrangian coefficients of a utlity function. This is used
        to configure the objective function of solution algorithm (i.e., fmincon). 
        
        Return the new expression with instiantion Lagrangian coefficient replaced by pattern expression
        
        self.sym_func will be analyzed and updated.
        
        self.sym_optvar will be used as a parameter in the analysis. 
        
        Called By: self.gnrt_alg()
        '''
        
        # Utility function and optimization must be configured already
        if self.sym_func == None or self.sym_optvar == None:
            print('Error: Utility and optimization variable are required, at least is missing.')
            exit(0)
        
        # Collect Lagrangian coefficients
        coll_sym_func = collect(self.sym_func, self.sym_optvar)
        
       
        # Find Lagrangian coefficient pattern
        lbd = self.find_lbd(str(coll_sym_func))
        
        # Replace Lagrangian instances using the pattern string
        full_string = str(coll_sym_func)                                                      # old full string
        old_substring = full_string[lbd['start']:lbd['end']]                                  # old sub string 
        
            
        new_substring = lbd['pattern'] + alglib_name.Lag_connect + alglib_name.Lag_suffix     # new sub string
        
        # if multiple occurances, the new substring is a little more complicated. 
        if lbd['cnt'] > 1:
            new_substring = 'sum(' + new_substring + ')'
            
            # Further, if the operator is '-', the operator should be incorporated
            if lbd['operator'] == '-':
                new_substring = '(-' + new_substring + ')'
        
        
        new_string = full_string.replace(old_substring, new_substring)                        # new full string
        
        #################################################################     
        new_string = self.rmv_dum(new_string)
        self.sym_func = sympify(new_string)
        
        return new_string
        
    def rmv_dum(self, expr):
        '''
        Remove any dum operation from the expression
        
        expr: The original expression that may contain dum operation
        
        Return: The new expression without dum
        
        Called: Function above in this class
        '''
        
        new_expr = expr.replace('dum', '1*')        
        return new_expr
    
                
    def find_lbd(self, parent_str):
        '''
        Find Lagrangian coefficients contained in a string expression;
        Returned information: how many coefficients, starting and ending positions, and the
        operator (+, -) of the coefficients;        
        Used to determine the Lagrangian coefficient pattern when generating solution algorithm.
        
        Called By: self.gnrt_alg()
        '''
        
        ###################################################################
        # Initialize dictionary to be returned
        # cnt: How many Lagrangian coefficients have been found 
        # pattern: The pattern corrsponding to the Lagrangian coefficients
        # operator: Sign of the Lagrangian coefficients, '+' or '-'
        # start, end: starting and ending positions between which the text should be replaced with the Lagrangian pattern
        dict_Lag_info = {'cnt': None, 'pattern': None, 'operator': None, 'start': None, 'end': None}
        
        ###################################################################
        # Determine cnt, i.e., find the set of Lagrangian coefficients 
        
        # Construcut prefix and suffix
        pre = alglib_name.Lag_prefix
        suf = alglib_name.Lag_connect + alglib_name.Lag_suffix
        
        # Find occurances of prefix and suffix in parent string
        pos_pre = [m.end() for m in re.finditer(pre, parent_str)]
        pos_suf = [m.start() for m in re.finditer(suf, parent_str)]

                       
        # The number of occurances of prefix and suffix must be the same
        if len(pos_pre) != len(pos_suf):
            print('Error: The number of prefix and suffix must be equal for Lagrangian coefficients.')
            exit(0)

        # Find the set of indices 
        #print(parent_str[pos_pre[0]:pos_suf[0]])        
        #
        # -2 because the index here is extracted in a different way (there is a difference in base index) compared to they are generated
        set_index = [int(parent_str[pos_pre[m]:pos_suf[m]]) - 2 for m in range(len(pos_pre))]   
        set_index.sort()
        dict_Lag_info['cnt'] = len(set_index)       # Number of found Lagrangian coefficients
        
               
        ###################################################################
        # Determine sign: If there is only one Lagrangian coefficient, the sign doesn't matter
        
        if dict_Lag_info['cnt'] > 1:
            sign_pos = [m.start() for m in re.finditer(pre, parent_str)]            # Locate signs by finding the beginning of each elements
            sign = parent_str[sign_pos[1]-2]                                        # Take the second sign, '-2' gives the position of signs
            dict_Lag_info['operator'] = sign
        
        ###################################################################
        
        # Loop over all instances (each instance is a set of indeces) and compare with the current index set
        b_found = 0
        for instance in self.ntwk.every2nonevery:
            if set_index == instance:
                b_found = 1
                break
                
        # Currently we only search over pattern of sess_lnks, i.e., the set of links passed by a session. 
        # If found, it means this instance corresponds to such a pattern;
        # Otherwise, the instance is a single link 
        if b_found == 1:
            dict_Lag_info['pattern'] = alglib_name.sess_lnks
        else:
            dict_Lag_info['pattern'] = alglib_name.link_sngl
        

        ###################################################################
        # Determine start and end
        pos_pre = [m.start() for m in re.finditer(pre, parent_str)]
        pos_suf = [m.end() for m in re.finditer(suf, parent_str)]
        
             
        # If there are multiple occurances of Lagrangian coefficients, the substring to be replaced starts from "(" before the first occurance;
        # Otherwise, there is no such a "(".
        # The same consieration applies to the ending symbol ")".
        if dict_Lag_info['cnt'] > 1:        # multiple occurances
            pos_start = pos_pre[0] - 1      # -1 points to "("        
            pos_end = pos_suf[-1] + 1       # +1 points to ")"
            
            # if the operator is '-', starting position should be moved forward by 1
            if dict_Lag_info['operator'] == '-':
                pos_start = pos_start - 1
            
        else:                               # single occurance
            pos_start = pos_pre[0]
            pos_end = pos_suf[-1]           
        
        dict_Lag_info['start'] = pos_start
        dict_Lag_info['end']   = pos_end
    
        
        ###################################################################
        # Update self.Lagrangian
        self.Lagrangian = dict_Lag_info
        
        return self.Lagrangian

