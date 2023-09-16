import yaml
import numpy as np


class Isotopes:
    def __init__(self):
        with open("../../isotopes.yml", "r") as f:
            dct = yaml.safe_load(f)
        
        self.isotopes = dct["Isotopes"]
        self.decay_chains = dct["Decay chains"]
        self.isotope_spectra = dct["Isotope spectra"]     
        
    def names(self):
        return [iso["Name"] for iso in self.isotopes]

    def get_spectrum(self, name):
        spectrum = list(self.isotope_spectra[name])
        for daughter, abundance in self.decay_chains.get(name, []):
            for energy, intensity in self.isotope_spectra[daughter]:
                spectrum.append([energy, intensity*abundance])
        return spectrum
    
    def get_SDEF(self, isotope):
        spectrum = np.array(self.get_spectrum(isotope))
        sorting = np.argsort(spectrum[:,0])

        energies = spectrum[sorting,0] * 1e-3
        intensities = spectrum[sorting,1]

        if len(energies) == 1:
            SDEF = f"{energies[0]} $ {isotope}"
        else:
            e_lines = np.array_split(energies, int(np.ceil(len(energies)/6)))
            i_lines = np.array_split(intensities, int(np.ceil(len(intensities)/6)))
            SDEF = f"d1 $ {isotope}\n"
            for prefix, lines in (("SI1 L  ", e_lines), ("SP1 D  ", i_lines)):
                for i, line in enumerate(lines):
                    if i == 0:
                        SDEF += prefix
                    else:
                        SDEF += " "*len(prefix)
                    SDEF += " ".join(["%9.5f"%x for x in line]) + "\n"
        return SDEF.rstrip()

class Materials:
    def __init__(self):
        with open("../../defaults.yml", "r") as f:
            dct = yaml.safe_load(f)            
        
        self.materials = [x for x in dct["Materials"] if x["Name"] != "None"]
        self.densities = {x["Name"]: x["Density"] for x in self.materials}
    
    def names(self):
        return [mat["Name"] for mat in self.materials]
    
    def get_MDEF(self, material):
        MDEF = {   
        ### WARNING: Don't just change these. Make sure the numbers 
        ### correspond to the correct materials in the templates
            "Water":           f'1  -{self.densities["Water"]}',
            "Lead":            f'2  -{self.densities["Lead"]}',
            "Concrete":        f'4  -{self.densities["Concrete"]}',
            "Concrete-Barite": f'5  -{self.densities["Concrete-Barite"]}',
            "Gypsum":          f'6  -{self.densities["Gypsum"]}',
            "Brick":           f'7  -{self.densities["Brick"]}',
            "Tungsten":        f'8  -{self.densities["Tungsten"]}',
        }[material]
        return MDEF
