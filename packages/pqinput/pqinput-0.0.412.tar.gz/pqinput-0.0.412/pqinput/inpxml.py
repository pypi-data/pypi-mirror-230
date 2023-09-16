#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 15:02:59 2023

@author: lucas

New INPUTMAKER with a "dictionary to XML" structure 

"""

'''TO IMPLEMENT
comments inside xml 
'''
# %% Imports
from lxml import etree as et

# %% General functions
# def etree_to_dict(t):
#     if type(t) is et.ElementTree: return etree_to_dict(t.getroot())
#     return {
#         **t.attrib,
#         **{e.tag: etree_to_dict(e) for e in t}
#     }

def etree_to_dict(t):
    from collections import defaultdict
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update((k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d

def dict2attr(element, params, tag=None):
    """ set the attributes for the xml element using a dict
        ignores keys as head, heir and extras    """
    for key, value in params.items(): 
        if key not in ('head', 'heir', 'extra'):
            element.set(str(key), str(value))
            
    if tag: element.tag = tag
    
def subelem(supelem, params, head=None):
    """ create subelement for a lxml supelement using params dict
    Input:
        params; string - tail of subelement
                dict - tail with parameters
    Return: 
        lxml element; not mandatory
    """
    if not head:
        try: 
            params['head']
        except:
            raise SyntaxError('element head not provided')
    else: params.__setitem__('head', head)
    sub = et.SubElement(supelem, params['head'])
    dict2attr(sub, params) 
    return sub

def show(xmlelem): # works for any kind of lxml element, show is just for class
    print(et.tostring(xmlelem, pretty_print=True).decode())
    
    # %% Property methods
    
def typed_property(name): # Python Cookbook 3rd: 9.21
    storage_name = '_' + name
    
    @property
    def propriety(self): # lost in translation 
        # Get the property element 
        if not hasattr(self, storage_name): raise AttributeError(f'{name} attribute not defined.')
        # return getattr(self, storage_name)
        return etree_to_dict(getattr(self, storage_name)) # return a dict, easier to access attributes
        
    @propriety.setter
    def propriety(self, args):
        # modify key with new_value of propriedade using path 
        # args = [path, key, new_value] or "path_key_new_value"
        if isinstance(args, str): args = args.split('_') # single string format
        path = ''
        if len(args)==3: path, key, new_value = args # if path is '' is meant to set a main attribute
        elif len(args)==2: key, new_value = args

        if '_' in path: # way of differenciating between children with same name, adding index
            import re
            index = int(re.findall('\d+',re.findall('_\d+',path)[0])[0])
            path = path.replace(re.findall('_\d+',path)[0],'') 
            element = (getattr(self, storage_name).findall(path)[index] if path else getattr(self, storage_name))                        
        else:                
            element = (getattr(self, storage_name).find(path) if path else getattr(self, storage_name))
        if element is None: 
            raise AttributeError('setter path do not point to a defined attribute.')
       
        element.set(key, str(new_value))
        # show(element)
        # READ MORE ABOUT XPATH AND IF ITS USEFUL
    #
    return propriety

# %% 
'''-------------------------------------------------------------------------'''
'''                                Class                                    '''
'''-------------------------------------------------------------------------'''
class InpXML:
    """ InpXMl class for the creation of a qdng calculation input in xml format.
    requires the lxml.etree package
    
    Args:
        qdng_params (dict) parameters for the qdng calculation
        _format: {attr1:value1, attr2:value2, ... }
        * qdng [ -d output directory] [-p cpus] <input file> [var1=val1] ... [varN=valN]
        
    Attributes:
        qdng (etree._Element) root of the lxml tree
        program (etree._Element) program body: 
            either propa or eigen
        propag (etree._Element) branch of a program
        hamilt (etree._Element) branch a propagation: 
            subelement required for a Cheby propagation
        wavefunc (etree._Element) wavefunction body: 
            inclusion of initial wavefunctions for the calculations
    
    Properties:
        show: prints out the class text in readable xml format
        
        
    * comments from QDng documentation
    """
    # Attributes as properties
    qdng = typed_property('qdng')
    mainprogram = typed_property('mainprogram')    
    wavefunction = typed_property('wavefunction')
    propagator = typed_property('propagator')
    hamiltonian = typed_property('hamiltonian')
    filterpost = typed_property('filterpost')
    # Defined operations and programs so far
    
    def __init__(self, qdng_params=None): # Initiate the input layout 
        self._qdng = et.Element("qdng") 
        # Root of the XML tree: self._qdng, with the tag-headline 
        if qdng_params: dict2attr(self._qdng, qdng_params)
    
    # Import method to plot PES curves from the input info
    from pqinput.drawPES import plotPES
        
    def __str__(self): # define string format for printing
        return f'{et.tostring(self._qdng, pretty_print=True).decode()}'    
    
    @property
    def show(self): # printing property
        '''Print out the full text in readable xml format
        Useful for debugging '''
        print(self)    
        
    def clean(self, propertyname, *attributes):
        '''Remove children with nule attributes'''
        for attr in attributes: 
            [a.getparent().remove(a) for a in getattr(self, '_' + propertyname).xpath(f'//child::*[@{attr}=0.0 or @{attr}=-0.0]')] 
        
    def readInput(self, path):
        '''Read an input file to generate a InpXML class object'''
        ' reading an input file will overwrite a InpXML object with the attributes and text'
        inp = et.parse(path)
        tags = [element.tag for element in inp.iter()]
        tree = [element for element in inp.iter()]
        
        # Couldnt find a better way to direct the element to the attributes, can use string for variable name...
        self._qdng = inp.getroot()
        self._mainprogram = (tree[tags.index('propa')] if 'propa' in tags else None)
        self._propagator = (tree[tags.index('propagator')] if 'propagator' in tags else None)
        self._hamiltonian = (tree[tags.index('hamiltonian')] if 'hamiltonian' in tags else None)
        self._filterpost = (tree[tags.index('filterpost')] if 'filterpost' in tags else None)
        self._wavefunction = (tree[tags.index('wf')] if 'wf' in tags else None)
        
# %% 
    ''' METHODS '''
    ######################## Write file ########################
    def writexml(self, file_name='test_file', txt=False):
        """ Write the constructed lxml element to a XML file. """
        tree = et.ElementTree(self._qdng)
        if file_name.endswith('.txt'): 
            txt = True 
            file_name = file_name.strip('.txt')
        tree.write(file_name + ('.txt' if txt else '.xml'), pretty_print=True)
        
    def modify(self, path, key, new_value):
        self._qdng.find(path).set(key, str(new_value))
        
    def define_wavefunction(self, wfp):
        if wfp['type'] == 'file':
            wfel = et.Element('wf')
            wfel.set('file', wfp['file'])
            
        elif wfp['type'] == 'LC':
            wfel = et.Element('wf', name=wfp['type'])
            if 'normalize' in wfp.keys() and wfp['normalize']: wfel.set('normalize', 'true')
            for ind in range(wfp['states']):
                wfstate = et.SubElement(wfel, 'wf'+str(ind))
                wfstate.set('file', wfp['file'][ind])
            
        elif wfp['type'] == 'Multistate':
            wfel = et.Element('wf', name=wfp['type'])
            if 'states' in wfp.keys(): wfel.set('states', str(wfp['states']))
            # hamiltonian define states number later
            if 'normalize' in wfp.keys(): wfel.set('normalize', 'true')
            if 'label' in wfp.keys(): wfel.set('label', wfp['label'])
            
            for ii, index in enumerate(wfp['index']):
                wfstate = et.SubElement(wfel, 'wf'+str(index), file=str(wfp['file'][ii]))
                if 'coeff2' in wfp.keys(): wfstate.set('coeff2', wfp['coeff2'][ii])
        else:
            raise SyntaxError('Wavefunction type not defined.')
        self._wavefunction = wfel
        # return wfel
    
    # %% 
    """ Programs """
    def program(self, ptype, program_parameters, wf_parameters):
        """ Main program for the calculation. Either propagation or eigenfunction derivation.
                
        Args:
            ptype (string) type of program:
            _either 'propa' or 'eigen'
            program_parameters (dict) program parameters dictionary:
            _format: {'dt':num, 'steps':num, 'directory':str,'Nef':num, 'conv':num }
            wf_parameters (dict) wavefunction parameters dictionary:
            _format: {'name':str, 'states':num, 'file':[strs, ], 'normalize':True or None}
            
        """
        '''MAIN PROGRAM'''
        if not ptype in ['propa','eigen']: raise SyntaxError('Program not defined.')  
        self._mainprogram = subelem(self._qdng, program_parameters, ptype )
        # Create self._mainprogram as a lxml elem element of qdng
        '''WAVEFUNCTION'''
        self.define_wavefunction(wf_parameters)
        # define wavefunction parameters    
    
    # %% 
    """ Operators """
    def dict2ope(self, d, head=None, text_mode=False):
        """ transform a dictionary to a etree.element for an operator
        
        Args:
            d (dict) dictionary with attributes in key:value format
            _format: {'head':str, attr1:value1, ..., 'heir':[dicts, ]}   
            head (string) node for the etree.Element
            text_mode (bool) choose the output format, etree.Element or etree.tostring
            
        Return: 
            string format of the etree.Element if text_mode else the etree._Element
            
            E.g.
            
            _In: dict2ope({'head':'node', 'attr1':'value1', 'heir':[{'Op_element':'op'}]}, text_mode=True)
            
            _Out: b'<node attr1="value1"/>'
            
            # missing the operators part...
        """
        if not isinstance(d, dict):
            raise SyntaxError('Provide a dictionary to transform into a lxml element.')

        xml = et.Element(d['head']) if head==None else et.Element(head)
        # set the attributes of the lxml element removing the head and Operators part
        # [xml.set(str(key), str(value)) for key, value in d.items() if key not in ('head', 'heir')]
        dict2attr(xml, d) 
        if 'heir' in  d.keys():
            if not isinstance(d['heir'], list): d['heir'] = [d['heir']] 
            for child in d['heir']:
                # update an Multistate operator with the Hamiltonian states quantity 
                if 'Multistate' in child.values(): child['states'] = str(self.states)
                # append a child from an dictionary
                xml.append(self.dict2ope(child))
                
        return et.tostring(xml) if text_mode else xml
    
    def def_hamiltonian(self, Hp):    
        import re
        Hel = et.SubElement(self._propagator, 'hamiltonian')
        # Create a lxml element to be appended to the self.propag 
        if Hp['type'] == 'Sum': 
            Hel.set('name', Hp['type'])
            [Hel.append(self.dict2ope(elem)) for elem in Hp['heir']] # subelem(Hel, elem)
            self.states = 1
            # set hamiltonian of Sum type, creating subelements for each operator
        elif Hp['type'] == 'Multistate':
            Hel.set('name', Hp['type'])
            self.states = 0
            if None == Hp['Mels']:
                raise SyntaxError('Include states for the Multistate hamiltonian!')
            else:
                for mel in Hp['Mels'][:]:
                    # iterate through Hamiltonian matrix elements (mel)                    
                    if len(mel['head'])<3: # easy way to set Hamiltonian matrix element 'mi.i'
                        mel['head'] = (f"m{mel['head'][1]}.{mel['head'][1]}")
                    elif len(mel['head'])==3:
                        mel['head'] = (f"m{mel['head'][1]}.{mel['head'][2]}")
                    index = re.findall('\d+', mel['head'])
                    if index[0]==index[1]: self.states += 1
                    Hel.append(self.dict2ope(mel))
        self._hamiltonian = Hel            
        
    # %% 
    ''' Propagator '''
    def propagation(self, name, hamilt_params, attrib=None):
        """ Method for the wavefunction propagation. Return a etree.SubElement of previous defined program.
        
        Args:
            name (string) name of the propagation method:
                *GSPO, Cheby, *SIL, Arnoldi (*not defined yet)
            hamilt_params (dict) parameters dictionary for the required Cheby hamiltonian
            _format: {'type':hamiltonian type, 'Matrix_elems':[mij, ]} 
            _type in ('Sum', 'Multistate', )
            _matrix elements for multistate, see hamilt_elem() function for format
            
        """
        # Propagator
        if name in ['Cheby', 'Arnoldi']:# requires hamiltonian
            # create the propagator subelement of the program
            self._propagator = et.SubElement(self._mainprogram, 'propagator', name=name,
                                              attrib=attrib)
            self.def_hamiltonian(hamilt_params)
            # define hamiltonian 
            self._wavefunction.set('states', str(self.states))
            # change wavefunction states based on hamiltonian matrix
        else:
            raise SyntaxError('Propagator type not defined.')
        # others propagators
        try:
            self._mainprogram.append( self._wavefunction ) # append wavefunction after the propagation
        except:
            raise SyntaxError('Wavefunction was not properly defined for propa.')    
    
    def filter(self, filter_type, filter_list, options=None):
        # types of filter to add
        def def_filterpost(filter_list):
            # Define the filterpost operation, called after propagation
            filterpost = et.Element('filterpost')
            if not isinstance(filter_list, list): filter_list = [filter_list]
            for dic in filter_list:
                
                filterpost.append(self.dict2ope(dic))
            # add operators at the filter list with heir children through dict2ope function
            
            self._mainprogram.append(filterpost)
            return filterpost
        
        # add filter to calculation
        if filter_type == 'filterpost':
            self._filterpost = def_filterpost(filter_list)    

    
# %% Name == Main 
if __name__ == "__main__":
    
    Tf = 25 # [fs]
    dt = 0.25 # [fs]
    steps = Tf*41.34/dt
    Nfiles = 5e2
    wcycle = int(steps/Nfiles)
    mass = 1764.30
    home = '/home/lucas/mntcluster/QDng/' 
    propa_params = {'dt': dt, 'steps': int(steps), 'wcycle': wcycle, 
                'dir': 'example_directory/', 'nfile': 'norm'}

    T00 = {'head':'T', 'name':'Sum', 'mass':mass, 'key':'T'}
    V00 = {'head':'V', 'name':'Sum', 'file':home+'MgH/pots/pot_Sig0'}
    m00 = {'head':'m0', 'name':'Sum', 'heir':[T00, V00]} 
    T11 = {'head':'T', 'ref':'T'}
    V11 = {'head':'V', 'name':'Sum', 'file':home+'MgH/pots/pot_Sig1'}
    m11 = {'head':'m1', 'name':'Sum', 'heir':[T11, V11]} 
    m22 = {'head':'m2', 'name':'Sum', 'heir':[T11, V11]} 
    m10 = {'head':'m10', 'name':'GridDipole', 'file':home+'mu', 'laser':'Et', 'heir':[]} 

    H_params = {'type':'Multistate', 'Mels':[m00, m11, m10, m22]} 
    Hsum = {'type':'Sum', 'heir':[T00, V00]} 
    wf, ef, vib =   [1, ], ['Sig0',], [1, ] # args['wf'], args['ef'], , args['vib'] #
    WF_params = {'type':'Multistate', 
             'file':[home+"MgH/efs_{}/ef_{}".format(ef[i], vib[i]) for i in range(len(ef))], 
             'index':[wf[i] for i in range(len(wf))], 'normalize':True}

    # filter_elem = [{'head':'expeconly', 'name':'Multistate', 'states':WF_params['states'], 
    #                               'unity':'False', 'header':f"mu{ind}", 
    #                 'heir':{'head' : f"mu{ind}",'name':'GridPotential',
    #                         'file':home+'MgH/mu/mu_Sig0Sig1'} }
    #                         for ind in [2.1,] ]
    filter_elem = [{'head':'apply', 'name':"Jump", "seed":'seed', "max_pjump":"0.1",
                    'heir':{ 'head':'L01','name':"Multistate",'unity':"false",
                            'nonhermitian':"true",
                            'heir':{'head':'m0.1', 'name':"Scalar", 'value':"0.0155527628625"}}}]
    
    #%%
    # Initialize
    prop = InpXML()
    prop.program('propa', propa_params, WF_params)
    prop.propagation('Cheby', Hsum)
    prop.filter('filterpost', filter_elem)
    prop.show
    prop.readInput('2states-wf1.Sig0.1.xml')
    prop.show
    # Editing
    # prop.hamilt = 'name', 'something'
    # prop.hamilt = 'm0.0/T', 'name', 'something_new'
    # prop.show
    

    # prop.plotPES(showfig=True)
     
    # Writing to file
    # prop.writexml(filename='filename', txt=True)
        


# %%
