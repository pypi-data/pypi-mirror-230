from .platonic_solids import *
from .transition_matrix import *
from .histograms import *
from .database_PDB import *
from .locate_pos import *
from .xyz import *
from .acf import *
from .pdb import *
from .file_managment import *
from .sphere_reg import *


"""Welcome to the main ioNERDSS function library folder! Here I will give a brief description of each folder and sub folder!
    *Note: Each main folder is named after the file it reads in, except platonic solids since it reads in no files.

    multi_species_hist: reads in multi-species histograms (from NERDSS sim) and then outputs many different graphs
    
    pdb: reads in .pdb files (which is the final position of each atom in a protein complex from a NERDSS sim)
        - database: These take in database .pdb files, allow you to edit them in many ways and then output them in many ways
            - gen: these are general files called by the main files. These will rarely be used by a user of ioNERDSS
        - nerdss_op: This takes in a .pdb file that comes from a nerdss output, then removes all protein complexes that are too small
            - gen: same as before
    
    platonic_solids: creates different types of platonic solids that can be inputted into NERDSS sim
        - cube/dode/icos/octa/tetra: create that shape
        - gen_platonic: code used by all shapes
    
    restart: reads in the .restart file
    single_species_hist:reads in single-species histograms (from NERDSS sim) and then outputs many different graphs
    transition_matrix: reads in a transition matrix
    xyz: reads in the .xyz file

    """

import os
import importlib

# Get the directory of the current __init__.py file
current_directory = os.path.dirname(__file__)

# Iterate through all files in the current_directory
for filename in os.listdir(current_directory):
    # Check if the file is a Python file (ends with .py) and is not the current __init__.py
    if filename.endswith(".py") and not filename.startswith("__init__"):
        # Remove the .py extension from the filename to get the module name
        module_name = filename[:-3]

        # Import the module using importlib.import_module and add it to the globals dictionary
        module = importlib.import_module(f".{module_name}", package=__name__)
        globals().update({n: getattr(module, n) for n in module.__all__} if hasattr(module, '__all__') else {k: v for k, v in module.__dict__.items() if not k.startswith('_')})
