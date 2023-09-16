import os
import numpy as np
from scipy.optimize import curve_fit
from scipy import interpolate
import matplotlib.pyplot as plt
import pickle
from constants import Isotopes, Materials


PICKLE_FILE = "MCNP.pickle"
BASE_FOLDER = os.path.join("Simulations","1E7")

DUPLICATE_RESULTS = [("Ga-68", "Ge-68"),] # Duplicate results for these isotopes: Ga-68 will also be stored as Ge-68 

mu_rho = np.array([
    (1.00000E-03, 3.606E+03, 3.599E+03),
    (1.50000E-03, 1.191E+03, 1.188E+03),
    (2.00000E-03, 5.279E+02, 5.262E+02),
    (3.00000E-03, 1.625E+02, 1.614E+02),
    (3.20290E-03, 1.340E+02, 1.330E+02),
    (3.20290E-03, 1.485E+02, 1.460E+02),
    (4.00000E-03, 7.788E+01, 7.636E+01),
    (5.00000E-03, 4.027E+01, 3.931E+01),
    (6.00000E-03, 2.341E+01, 2.270E+01),
    (8.00000E-03, 9.921E+00, 9.446E+00),
    (1.00000E-02, 5.120E+00, 4.742E+00),
    (1.50000E-02, 1.614E+00, 1.334E+00),
    (2.00000E-02, 7.779E-01, 5.389E-01),
    (3.00000E-02, 3.538E-01, 1.537E-01),
    (4.00000E-02, 2.485E-01, 6.833E-02),
    (5.00000E-02, 2.080E-01, 4.098E-02),
    (6.00000E-02, 1.875E-01, 3.041E-02),
    (8.00000E-02, 1.662E-01, 2.407E-02),
    (1.00000E-01, 1.541E-01, 2.325E-02),
    (1.50000E-01, 1.356E-01, 2.496E-02),
    (2.00000E-01, 1.233E-01, 2.672E-02),
    (3.00000E-01, 1.067E-01, 2.872E-02),
    (4.00000E-01, 9.549E-02, 2.949E-02),
    (5.00000E-01, 8.712E-02, 2.966E-02),
    (6.00000E-01, 8.055E-02, 2.953E-02),
    (8.00000E-01, 7.074E-02, 2.882E-02),
    (1.00000E+00, 6.358E-02, 2.789E-02),
    (1.25000E+00, 5.687E-02, 2.666E-02),
    (1.50000E+00, 5.175E-02, 2.547E-02),
    (2.00000E+00, 4.447E-02, 2.345E-02),
    (3.00000E+00, 3.581E-02, 2.057E-02),
    (4.00000E+00, 3.079E-02, 1.870E-02),
    (5.00000E+00, 2.751E-02, 1.740E-02),
    (6.00000E+00, 2.522E-02, 1.647E-02),
    (8.00000E+00, 2.225E-02, 1.525E-02),
    (1.00000E+01, 2.045E-02, 1.450E-02),
    (1.50000E+01, 1.810E-02, 1.353E-02),
    (2.00000E+01, 1.705E-02, 1.311E-02),
])
_log_interp = interpolate.interp1d(np.log(mu_rho[:,0]*1e3), np.log(mu_rho[:,2]), fill_value="extrapolate")

def linear_energy_absorption_coeff_air(energy_kev):
    return np.exp(_log_interp(np.log(energy_kev))) / 10 # cm^2/g --> m^2/kg

def ratio_H10_air_kerma(energy_keV):
    # source https://nucleonica.com/wiki/index.php?title=Help:Dose_Rate_Constants%2B%2B
    E0 = 9.85
    xi = np.log(energy_keV / E0)
    r = xi / (1.465 * xi**2 - 4.414 * xi + 4.789) \
        + 0.7006 * np.arctan(0.6519 * xi)
    return np.maximum(r, 0)

def flux_to_h10(energy_kev, flux):
    energy_J = energy_kev * 1.60217662e-16    
    kerma_air_rate = flux * energy_J * linear_energy_absorption_coeff_air(energy_kev)
    return np.dot(ratio_H10_air_kerma(energy_kev), kerma_air_rate)


def getData(folder, phot_per_decay):    
    dose = []

    filenames = [fn for fn in os.listdir(folder) if fn.endswith(".o")]
    for fn in filenames:
        if "conflicted" in fn:
            continue
        
        thickness = float(fn[:-2])        
        path = os.path.join(folder, fn)   
        found = False 
        with open(path) as f:
            energy = []
            flux = []
            for line in f.readlines():
                line = line.strip().split()
                if not len(line): continue
                if line[0] == 'detector' and line[1] == 'located':
                    found = True
                if found:
                    try:
                        energy.append(float(line[0]) * 1e3)
                        flux.append(float(line[1]))
                    except ValueError:
                        if line[0] == 'total':
                            error = float(line[2])
                            break
            
            ### Note: source-detector distance is 400 cm, MCNP outputs flux as MeV/cm^2 (hence the 400**2)
            flux = np.array(flux) * phot_per_decay * 400**2  * 3600 * 1e12 # 3600 s/hr, 1e12: Sv->uSv, Bq->MBq
            
            dose.append([thickness, flux_to_h10(np.array(energy), np.array(flux)), error])
               
    return np.array(sorted(dose))


def fix_spikes(dose, material):
    dx = dose[-1,0]-dose[-2,0]
    
    ### Moving average    
    x = np.arange(dose[-1,0], 0-0.1*dx, -dx/2)[::-1]    
    y = np.interp(x, dose[:,0], np.log(dose[:,1]))

    w = 7
    ma = np.copy(y)
    ma[w//2:-(w//2)] = np.convolve(y, np.ones(w), 'valid') / w
        
    indices = np.where( (dose[1:,0]-dose[:-1,0]) >= 0.5*dx )[0] + 1
    
    newdose = np.copy(dose)
    newdose[indices,1] = np.exp( np.interp(dose[indices,0], x, ma) )
    
    
    # Recursively remove outliers
    remove = np.where(dose[:,1] / newdose[:,1] > 3)[0]
    if len(remove):
        print("Removed:", len(remove))
        plt.plot(dose[remove,0], dose[remove,1], marker='o', ms=10, c='k', fillstyle='none')    
        newdose = np.delete(newdose, remove, axis=0)  
        return fix_spikes(newdose, material)
    
    return newdose



if __name__ == "__main__":        
    try:
        results = pickle.load(open(PICKLE_FILE, "rb"))
    except FileNotFoundError:
        results = {}
    
    isotopes = Isotopes()
    materials = Materials()
    
    for material in materials.names():
        for isotope in isotopes.names():
        
            spectrum = np.array(isotopes.get_spectrum(isotope))
            phot_per_decay = spectrum[:,1].sum()/100
            print(f"\n{isotope} yield:", "%.3f"%phot_per_decay)
                
            color = next(plt.gca()._get_lines.prop_cycler)['color']
            for self_shielding in ("None", "Body"):
                
                all_doses = []
                for base_folder in [BASE_FOLDER+f"_{i}" for i in range(10)]:
                    folder = os.path.join(base_folder, f"{isotope}_{self_shielding}_{material}")
                    
                    if os.path.exists(folder):
                        all_doses.append( getData(folder, phot_per_decay) )

                if not len(all_doses):
                    continue
                
                # Get the values with the lowest statistical uncertainty
                all_doses = np.array(all_doses)
                print(all_doses.shape)
                min_arr = np.argmin(all_doses, axis=0)[:,2]                
                dose = np.empty_like(all_doses[0])                                
                for j in range(len(dose)):
                    dose[j] = all_doses[min_arr[j]][j]
                                
                h_10 = dose[0,1]
                print("h(10): %.5f"%h_10, self_shielding)
                
                dose[:,1] /= h_10                
                dose = dose[np.where(dose[:,1])[0]] # Exclude dose values of 0                
                
                ls = '-' if self_shielding == "None" else '--'
                ms = '.' if self_shielding == "None" else '+'
                
                plt.plot(dose[:,0], dose[:,1], ms, color=color, label=f"{isotope}-{self_shielding}")
                
                dose = fix_spikes(dose, material)
                
                plt.plot(dose[:,0], dose[:,1], ls, color=color)            
                
                results.setdefault(isotope, {})
                results[isotope].setdefault(self_shielding, {})
                results[isotope][self_shielding]["h(10) [uSv/h per MBq/m^2]"] = h_10
                results[isotope][self_shielding][material] = dose[:,:2]
        if 1:
            pass
            #plt.ylim([1e-9, 2])
            plt.yscale('log')
        else:
            if material == "Lead":
                plt.xlim([-0.1, 3])
            else:
                plt.xlim([-1, 40])
        #plt.xlim([-0.1, 3])
        #plt.ylim([1E-8, 2])
        plt.title(f"{material}")    
        plt.legend(loc="lower right")
        plt.show()
    
    for dupl in DUPLICATE_RESULTS:
        results[dupl[1]] = results[dupl[0]]
    
    with open(PICKLE_FILE, 'wb') as f:
        pickle.dump(results, f)
