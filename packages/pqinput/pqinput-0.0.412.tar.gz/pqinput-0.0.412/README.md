# Python package to generate and modify QDng calculations inputs in xml format

### Module:
- `inpxml.py`: **InpXML** 
Class with methods to write and edit *xml* structures designed as input files for quantum chemistry calculations on QDng package. 
Requires *lxml*.


### Example: 

In:

    Tf = 25 # [fs]
    dt = 0.25 # [fs]
    steps = Tf*41.34/dt
    Nfiles = 5e2
    wcycle = int(steps/Nfiles)
    mass = 1764.30

    propa_params = {'dt': dt, 'steps': int(steps), 'wcycle': wcycle, 
                'dir': 'example_directory/', 'nfile': 'norm'}

    T00 = {'head':'T', 'name':'Sum', 'mass':mass, 'key':'T'}
    V00 = {'head':'V', 'name':'Sum', 'file':'MgH/pots/pot_Sig_0'}
    m00 = {'head':'m0', 'name':'Sum', 'Opes':[T00, V00]} 
    T11 = {'head':'T', 'ref':'T'}
    V11 = {'head':'V', 'name':'Sum', 'file':'MgH/pots/pot_Sig_1'}
    m11 = {'head':'m1', 'name':'Sum', 'Opes':[T11, V11]} 
    m22 = {'head':'m2', 'name':'Sum', 'Opes':[T11, V11]} 
    m10 = {'head':'m10', 'name':'GridDipole', 'file':'mu', 'laser':'Et', 'Opes':[]} 

    H_params = {'type':'Multistate', 'Mels':[m00, m11, m10, m22]} 
    Hsum = {'type':'Sum', 'Opes':[T00, V00, T00]} 
    wf, ef, vib =   [1, ], ['Sig0',], [1, ] # args['wf'], args['ef'], , args['vib'] #
    WF_params = {'type':'Multistate', 'states':'1',
             'file':["MgH/efs_{}/ef_{}".format(ef[i], vib[i]) for i in range(len(ef))], 
             'index':[wf[i] for i in range(len(wf))], 'normalize':True}
    filter_opes = [{'expeconly':{'name':'Multistate', 'states':WF_params['states'], 'unity':'False', 'header':"mu{}".format(ind)}, 
                   'm{}'.format(ind):{'name':'GridPotential', 'file':'MgH/mu/mu_Sig0Sig1'}}
                   for ind in [2.1,] ]
    #%%
    # Initialize
    prop = InpXML()
    prop.program('propa', propa_params, WF_params)
    prop.propagation('Cheby', H_params)
    prop.filter('filterpost', filter_opes)
    prop.show

    # Editing
    prop.hamilt = 'name', 'something'
    prop.hamilt = 'm0.0/T', 'name', 'something_new'
    prop.show
     
    # Writing to file
    # prop.writexml(filename='filename', txt=True)

Out:
```xml
<qdng>
  <propa dt="1" steps="1000" dir="efs_g" Nef="20" conv="1e-11">
    <propagator name="Cheby">
      <hamiltonian name="Multistate">
        <m0.0 name="Sum">
          <T name="GridNablaSq" mass="2000" key="T"/>
          <V name="GridPotential" file="pot_Vg"/>
        </m0.0>
        <m1.1 name="Sum">
          <T ref="T"/>
          <V name="GridPotential" file="pot_Vg"/>
        </m1.1>
        <m1.0 name="GridDipole" file="mu" laser="Et"/>
        <m2.2 name="Sum">
          <T ref="T"/>
          <V name="GridPotential" file="pot_Vg"/>
        </m2.2>
      </hamiltonian>
    </propagator>
    <wf name="Multistate" states="3" normalize="true">
      <wf1 file="MgH/efs_Sig0/ef_1"/>
    </wf>
    <filterpost>
      <expeconly name="Multistate" states="1" unity="False" header="mu2.1">
        <m2.1 name="GridPotential" file="MgH/mu/mu_Sig0Sig1"/>
      </expeconly>
    </filterpost>
  </propa>
</qdng>

<qdng>
  <propa dt="1" steps="1000" dir="efs_g" Nef="20" conv="1e-11">
    <propagator name="Cheby">
      <hamiltonian name="something">
        <m0.0 name="Sum">
          <T name="something_new" mass="2000" key="T"/>
          .
          .
          .
```




