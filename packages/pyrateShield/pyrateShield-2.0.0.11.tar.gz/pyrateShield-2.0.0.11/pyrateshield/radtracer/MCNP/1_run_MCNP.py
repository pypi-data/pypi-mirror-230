import subprocess
import random
import os
import time
import numpy as np
import itertools
import multiprocessing
from datetime import timedelta

from constants import Isotopes, Materials


NR_OF_PHOTONS = "1E7"   #Keep this a string
REPEATS = 4
BASE_FOLDER = os.path.join("Simulations", NR_OF_PHOTONS)
CPUS_PER_TASK = multiprocessing.cpu_count()//2 

THICKNESS = np.concatenate([
    np.arange( 0,   2, 0.5),  # 4
    np.arange( 2,  10, 1),    # 8
    np.arange(10,  30, 2),    # 10
    np.arange(30, 181, 5),    # 31
])
THICKNESS_LEAD = THICKNESS * 0.1

SKIP_ISOTOPE = ["Ge-68"] # Skip simulation for these isotopes: Ge-68 is identical to Ga-68

isotopes = Isotopes()
materials = Materials()


SIM_TIME = []

def simulate(isotope, self_shielding, material, repeat_idx, todo):
    global SIM_TIME
    
    print(isotope, self_shielding, material)
    
    with open(f"Templates/{self_shielding}.i") as f:
        template_orig = f.read()
        
    folder = os.path.join(f"{BASE_FOLDER}_{repeat_idx+1}", f"{isotope}_{self_shielding}_{material}")
    if not os.path.isdir(folder):
        os.makedirs(folder)
        
    if material in ("Lead", "Tungsten"):
        thickness = THICKNESS_LEAD
    else:
        thickness = THICKNESS
    
    for th in thickness:
        start_time = time.time()
        
        thickness_str = "%.2f"%float(th)
        
        inpf = thickness_str+".i"
        inpf_path = os.path.join(folder, inpf)
        if os.path.exists(inpf_path):
            print(f"Already done {inpf_path}")
            continue

        if os.path.exists("./stop"):
            print("Got stop command...")
            exit()

        open(inpf_path, 'a').close()
        print(f"Run {inpf_path}")

        seed = random.getrandbits(44)
        if not seed % 2:
            seed += 1
            
        template = template_orig.replace('<THICKNESS>', thickness_str)
        template = template.replace('<OUTFILE>', inpf[:-2])
        template = template.replace('<MATERIAL>', materials.get_MDEF(material))
        template = template.replace('<SDEF>', isotopes.get_SDEF(isotope))        
        template = template.replace('<NPS>', NR_OF_PHOTONS)
        template = template.replace('<RAND_SEED>', str(seed))
        
        with open(inpf_path, 'w') as f:
            f.write(template)
        
        n_cpu = max(1, CPUS_PER_TASK)
        subprocess.call(['mcnp6', f'I={inpf}', "TASKS", str(n_cpu)], cwd=folder)    
        
        if os.path.exists(inpf_path[:-2]+".r"):
            os.remove(inpf_path[:-2]+".r")
        
        #### Estimate remaining time ###        
        SIM_TIME.append(time.time()-start_time)
        if len(SIM_TIME) > len(THICKNESS):
            SIM_TIME.pop(0)
        average_time = np.mean(SIM_TIME)
        todo[0] -= 1
        
        print("\nRemaining nr of simulations:", todo[0])
        print("Average time per simulation:", round(average_time,1), "sec")
        print("Estimated time left:", timedelta(seconds=todo[0]*average_time), "\n\n")


def get_todo(isotope_list, material_list, self_shieldings):
    total = 0
    todo = 0
    for repeat_idx in range(REPEATS):        
        for isotope, material, self_shielding in itertools.product(isotope_list, material_list, self_shieldings):
            if isotope in SKIP_ISOTOPE:
                continue
                        
            folder = os.path.join(f"{BASE_FOLDER}_{repeat_idx+1}", f"{isotope}_{self_shielding}_{material}")            
            if material in ("Lead", "Tungsten"):
                thickness = THICKNESS_LEAD
            else:
                thickness = THICKNESS            
            for th in thickness:
                thickness_str = "%.2f"%float(th)                
                inpf = thickness_str+".i"
                inpf_path = os.path.join(folder, inpf)
                
                total += 1
                if not os.path.exists(inpf_path):
                    todo += 1
    print("Total:", total, "Todo:", todo)
    return [todo]

if __name__ == "__main__":        
    isotope_list = isotopes.names()
    material_list = materials.names()
    self_shieldings = ("None", "Body")
    
    todo = get_todo(isotope_list, material_list, self_shieldings)
    
    for repeat_idx in range(REPEATS):        
        for isotope, material, self_shielding in itertools.product(isotope_list, material_list, self_shieldings):
            if isotope in SKIP_ISOTOPE:
                continue
                     
            simulate(isotope, self_shielding, material, repeat_idx, todo)            
            

