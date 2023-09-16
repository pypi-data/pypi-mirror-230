#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  3 14:57:01 2023

@author: lucas

Draw Input file system
"""
import re

import matplotlib.pyplot as plt
import numpy as np
from unitscvt.aunits import HartreeEnergy as HE
from unitscvt.aunits import HEeV
from unitscvt.aunits import autime as sec2au
from unitscvt.aunits import redPlanck as hP

# from unitscvt.siconst import electronVolt as eV
f2En = hP/HE
from qdio.qd_file_op import FileOP
from qdio.qd_file_wf import FileWF

fwf, fop = FileWF(), FileOP()

# import os
# home = '/'+ '/'.join(os.getcwd().split('/')[1:3]) + '/'
# pwdd = home + 'mntcluster/QDng/'

""" pwd = os.getcwd()
pwdd = pwd.removesuffix('Propagation_MgH')
pwdd = pwdd + ('/' if not pwdd.endswith('/') else '') """

#%%
def lighter(color, amount=0.5):
    #https://gist.github.com/ihincks/6a420b599f43fcd7dbd79d56798c4e5a
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.
    
    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """
    import colorsys

    import matplotlib.colors as mc
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = np.array(colorsys.rgb_to_hls(*mc.to_rgb(c)))
    return colorsys.hls_to_rgb(c[0],1-amount * (1-c[1]),c[2])

def plotPES(inxstc, savename=None, SIunits=True, yrange=None, xrange=None, 
legend=None, showfig=None, showWF=True, offset_overlap=0.5, sizex=12/2.54, sizey=8/2.54,
title=None, offsetlabel=None, drawpure=True): # inx structure
    
    
    fig, ax = plt.subplots(layout='constrained', figsize=(sizex, sizey))
    plt.rcParams.update({'font.size': 10})
    
    cmap = plt.get_cmap("tab10")
    potmin = 0
    x = []
    jorder = []
    previousannot = []
    off = 0
    
    iwave = inxstc._wavefunction.getchildren()[0].get('file')
    wf, _ = fwf.read(iwave + '.wf')
    windx = int(re.findall('([\d]+)', inxstc._wavefunction.getchildren()[0].tag)[0])

    children = inxstc._hamiltonian.getchildren()

    for element in children:
        jj = re.findall('([\d]+)', element.tag)
        if jj[0] == jj[1]:
            j = int(jj[0])
            pot = inxstc._hamiltonian.find(element.tag+'/V')
            filepot, offset = pot.get('file'), pot.get('offset')
            offset = (None if offset==0 else offset)
            Pot, _ = fop.read(filepot + '.op') 
            potmin = (Pot.min() if Pot.min() < potmin else potmin)
            Pot = Pot - potmin
            
            if not element.get('label'): element.set('label', element.tag)
            
            try: x.size # check if x was defined before
            except:
                _, meta = fop.read(filepot + '.op') 
                dim = meta['dim'][0]
                x = np.linspace(dim.xmin, dim.xmax, dim.size)
                
            '''PES plotting, if there is a offset (photon energy) the line is dashed'''
            ################# main plot #################
            ax.plot(x, Pot*(HEeV if SIunits else 1), 
                    color=(cmap(j) if not offset else lighter(cmap(j),.5) ), 
                    linestyle=('-' if not offset else ' ' if not drawpure else '--') ,
            # label=(re.findall('([\d]+)', element.tag)[0] if not offset else '_nolegend_') )
            label=(element.get('label') if not offset else '_nolegend_') )
    
            '''If the state PES has a photonic contribution'''
            if offset: 
                homega = float(offset)*HEeV/sec2au*f2En
                
                '''photon energy in eV'''
                xytxt = (x[Pot.argmin()], Pot.min()*HEeV)
                ax.annotate((f'{homega:.3}eV' if not offsetlabel else offsetlabel[off]),
                         xy=(x[Pot.argmin()]+.05, 
                             Pot.min()*HEeV+(0 if not xytxt in previousannot else offset_overlap)),
                         xytext=(2, 2), color=lighter(cmap(j),.8), weight=600,
                         textcoords='offset points',  bbox=dict(facecolor='w',edgecolor='none', 
                                                                pad=0, alpha=.75) )
                                
                '''add a arrow to represent the photon energy'''

                ax.arrow(x[Pot.argmin()], #+(0 if not xytxt in previousannot else offset_overlap)
                         Pot.min()*HEeV, 0 ,
                         homega, color=lighter(cmap(j),.3), linestyle='-',
                         label='_nolegend_', width=.02, head_length=.3,
                         length_includes_head=True)
                
                previousannot.append(xytxt)
                
                '''plot the shifted PES'''
                ax.plot(x, Pot*(HEeV if SIunits else 1) + homega, color=cmap(j), 
                        linestyle='-',
                        # label=re.findall('([\d]+)', element.tag)[0])
                        label=element.get('label'))
                off += 1
                
            '''Adding the initial wavefunction to the state PES'''
            if windx == j and showWF:
                ax.plot(x, abs(wf)**2 + Pot*(HEeV if SIunits else 1) + 
                        (homega if offset else 0),
                        color=cmap(j), linestyle=':',
                        alpha=.75,label='_nolabel_') # inxstc._wavefunction.get('label')
                ## if want to put label on wavefunction, need to change legend labels order
                
            jorder.append(j)
        else: 
            pass
               
        
    plt.ylabel(('Energy [eV]' if SIunits else 'Energy [au]'))
    plt.xlabel('Internuclear distance [au]')
    # Make the minor ticks and gridlines show.
    if yrange: plt.ylim( *yrange)
    if xrange: plt.xlim( *xrange)
    plt.title(title)
    [ax.legend(loc='upper right') if not legend else ax.legend([legend[idx] for idx in jorder], 
                                                               loc='upper right') ]
    ax.grid(which='major', color='#DDDDDD', linewidth=0.8)
    # Show the minor grid as well. Style it in very light gray as a thin,
    # dotted line.
    ax.minorticks_on
    ax.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
    if savename: plt.savefig(savename) 
    [plt.close() if not showfig else plt.show()]
    
    
    return fig, ax
# %%
if __name__=='__main__':
    import inpxml as inx   
    prop = inx.InpXML()   
    prop.readInput('2states-wf1.Sig0.1.xml')
    #%%
    prop.show
    #legend=['G','E','Gl','Gr',],
    plotPES(prop, yrange=(0,10), xrange=(1.1,4.5), 
            offsetlabel=['wx', 'wy'], showfig=True)