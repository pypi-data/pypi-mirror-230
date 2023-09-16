#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 10:52:38 2023
Edited on Fri Aug  4 13:19:13 2023

@author: lucas

Propagation dictionaries
"""
# %% Propagation 
def propagation_parameters(dt, steps, wcycle, dir, nfile='norm'):
    propapar = {'dt': dt, 'steps': int(steps), 'wcycle': wcycle, 
                'dir': dir, 'nfile': 'norm'}
    return propapar 

'''Kinectic energy operator'''
def kinectic_operator(mass=0, pml=False, key=None, ref=None, lmap=2, thick=10):
    T = {'head':'T', 'name':"GridNablaSq"}
    if not isinstance(mass, list):
        T.update({'mass':mass})
        if pml: T.update({'name':"GridPML", 'lmap':lmap, 'thick':thick})
    else:
        T.update({'mass':','.join(str(m) for m in mass)})
        if pml: 
            if lmap==2: lmap=[2 for m in mass]
            T.update({'name':"GridPML", 'lmap':','.join(str(l) for l in lmap)})
            try: 
                len(thick)==len(mass)
                T.update({'thick':thick})
            except: pass
    if key: T.update({'key':key}) 
    if ref and not key: T = {'head':'T', 'ref':ref}
    return T

'''Potential energy surfaces'''
def potential_operator(file, offset=None, head='V', name='GridPotential', scale=None, label=None): # file MgH/pots/pot_Sig0
    V = {'head':head, 'name':name, 'file':file,}
    if not scale==None: V.update({'scale':scale})
    if offset: V.update({'offset':offset})
    if label: V.update({'label':label})
    return V

def grid_operator(file, head, scale=1, name='GridPotential', label=None): 
    G = {'head':head, 'name':name, 'file':file, 'scale':scale}
    if label: G.update({'label':label})
    return G

def scalar_operator(head, value, im=0, name='Scalar', label=None):
    S = {'head':head, 'name':name, 'value':value}
    if im!=0: S.update({'im':im})
    if label: S.update({'label':label})
    return S

'''Diagonal terms: pure states'''
def diagonal_sum(n, Opes, label=None, key=None):
    mel = {'head':f'm{n}.{n}', 'name':'Sum', 'heir':Opes}
    if label: mel.update({'label':label})
    if key: mel.update({'key':key}) 
    return mel

'''Off diagonal terms: interactions'''
def offdiagonal_mel(m,n, file, scale=None, laser=None, head=None, label=None, key=None): 
    # file MgH/mu/mu_Sig0Sig1:: relate to V
    mel = {'head':(f'm{m}.{n}' if not head else head), 'name':'GridPotential',  'file':file}
    if scale and not laser: mel.update({'scale':scale})
    if laser and not scale: mel.update({'laser':laser, 'name':'GridDipole'})
    if label: mel.update({'label':label})
    if key: mel.update({'key':key}) 
    return mel

def offdiagonal_sum(m,n, Opes, label=None, key=None): 
    mel = {'head':f'm{m}.{n}', 'name':'Sum', 'heir':Opes}
    if label: mel.update({'label':label})
    if key: mel.update({'key':key}) 
    return mel

'''Hamiltonian dictionary'''
def hamiltonian_parameters(Mels):
    Hparams = {'type':'Multistate', 'Mels':Mels} 
    return Hparams
# Hparams = {'type':'Multistate', 'Mels':[Sig0xy, Sig1y, dipx]} 

'''Wavefunction parameters'''
def wavefunction_parameters(wf, ef, vib, label=None, dim=1, folder='MgH'):
    if not isinstance(ef, list): wf, ef, vib = [wf], [ef], [vib]
    if dim==1:
        WFpar = {'type':'Multistate', 'states':'',
         'file':[f"{folder}/efs_{e}/ef_{v}" for e,v in zip(ef, vib)],
         'index':wf, 'normalize':'true'}
    if dim==2:
        WFpar = {'type':'Multistate', 'states':'',
             'file':[f"{folder}/efs_2D/{ef[i][0]}ef{vib[i][0]}_{ef[i][1]}ef{vib[i][1]}" 
                     for i, _ in enumerate(wf)], 'index':list(wf), 'normalize':True}
    if dim==3:
        WFpar = {'type':'Multistate', 'states':'',
             'file':[f"{folder}/efs_3D/{ef[i][0]}ef{vib[i][0]}_{ef[i][1]}ef{vib[i][1]}_{ef[i][2]}ef{vib[i][2]}" 
                     for i, _ in enumerate(wf)], 'index':list(wf), 'normalize':True}
    if label: WFpar.update({'label':label})
    return WFpar

'''Filter parameters'''
def filter_expeconly(mu, file, header):
    operators = {'head':'expeconly', 'name':'Multistate', 'states':'', 
                'unity':'False', 'header':header, 
                f'mu{mu}':{'name':'GridPotential', 'file':file}}
    return operators

def filter_jump(head, elements, seed, max_jump, unity="false", nonhermitian='true',
                name="Multistate"):
    operators = {'head':'apply', 'name':"Jump", "seed":seed, "max_pjump":max_jump,
                    'heir':{ 'head':head,'name':name,'unity':unity,
                            'nonhermitian':nonhermitian,
            'heir':[{'head':key, 'name':"Scalar", 'value':val}
                    for key,val in elements.items()] }}
    return operators

# %% Save parameters
def savedict2pars(dictionary, folder, fname=''):
    
    text = " Parameters for calculations \n"\
    "__________________________________________________\n"
        
    for key, value in dictionary.items():
        text += f"{key} : {value}\n"
    
    with open(folder + f'/Parameters{fname}.txt', 'w') as f:
        f.write(text)
