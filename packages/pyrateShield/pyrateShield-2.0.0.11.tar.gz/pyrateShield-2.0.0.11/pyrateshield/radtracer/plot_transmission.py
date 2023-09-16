import numpy as np
import matplotlib.pyplot as plt
from pyrateshield.constants import CONSTANTS
from pyrateshield.radtracer.radtracer import TransmissionArcher, TransmissionMCNP, MCNP_LOOKUP


if 0:
    for material in CONSTANTS.base_materials:
        if material == 'None': continue
        
        if material == "Lead":
            X = np.linspace(0,0.3,50,endpoint=True)
        else:
            X = np.linspace(0,30,50,endpoint=True)
        
        for params in CONSTANTS.ct:
            transmission = TransmissionArcher(params.archer)      
            plt.plot(X, transmission.get(material, X), '-', label="CT "+str(params.kvp))

        for params in CONSTANTS.xray:
            transmission = TransmissionArcher(params.archer)      
            plt.plot(X, transmission.get(material, X), '--', label="xray "+str(params.kvp))
        
        plt.title(material)
        plt.xlabel("Thickness [cm]")
        plt.ylabel("Transmission")
        plt.yscale("log")
        plt.ylim((1E-5,1))
        plt.legend(title="kVp")
        plt.show()

def arch(a,b,g,x):
    return ( (1 + b/a)*np.exp(a*g*x) - b/a )**(-1/g) 

cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
for material in CONSTANTS.base_materials:
    if material == 'None': continue
    
    if material == "Lead":
        X = np.arange(0,18.1,0.1)
        xlim = (-0.1, 5)
        ylim = (1E-5, 2)
    
        #a, b, g = (1.322, 148.5, 1.488)
        #plt.plot(X, arch(a,b,g,X), ":", color="k", label="I-123 Archer", lw=3)
    else:
        X = np.arange(0,181,1)
        xlim = (-0.5, 15)
        ylim = (1E-2, 1.1)
        
        #a, b, g = (0.1866, 1253, 74.93)
        #plt.plot(X, arch(a,b,g,X), ":", color="k", label="I-123 Archer", lw=3)
        
    for i, isotope in enumerate(CONSTANTS.isotopes):
        if isotope.name == "Ge-68": #Ge-68 is just a copy of Ga-68
            continue
        
        lw = 2 if i//10 else 1.2
        
        for self_shielding in ["None", "Body"]:
            transmission = TransmissionMCNP(MCNP_LOOKUP[isotope.name][self_shielding])            
            ls = "-" if self_shielding == "None" else "--"
            lbl = isotope.name if self_shielding == "None" else None
            plt.plot(X, transmission.get(material, X), ls, color=cycle[i%10], label=lbl, lw=lw)
    
    
    
    
    
    plt.title(material + " - dashed: patient self-shielding")
    plt.xlabel("Thickness [cm]")
    plt.ylabel("Transmission")
    plt.yscale("log")
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.legend()
    plt.show()
