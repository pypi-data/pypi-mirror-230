import math

def distance_bw_atoms_in_chains(split_position,split_resi_position,i,j):
    """Determines which atoms are bounded, and adds their position to a list

    Args:
        split_position (list): position of each atom in each chain
        split_resi_position (list): position of each residiual of each atom in each chain
        i (int): Index of the first chain
        j (int): Index of the second chain

    Returns:
        list: list of the positions of each atoms that are bounded
        int: count of how many atoms that are bounded b/w these chains
    """
    
    
    
    inner_reaction_resi_position = []
    count = 0 #if these 2 chains have any atoms binding b/w them

    
    #for each atom in chain 1 (i)
    for m,atom_coords_ch1 in enumerate(split_position[i]):
                
        #for each atom in chain 2 (j)
        for n,atom_coords_ch2 in enumerate(split_position[j]):
                    
            #calculate the distance between the two
            distance = math.sqrt((atom_coords_ch1[0]-atom_coords_ch2[0])**2 + (atom_coords_ch1[1]-atom_coords_ch2[1])**2 + (atom_coords_ch1[2]-atom_coords_ch2[2])**2)

            if distance <= 0.3:
                inner_reaction_resi_position.append([split_resi_position[i][m], split_resi_position[j][n]])
                count += 1
    return inner_reaction_resi_position,count





def real_PDB_chain_int_simple(unique_chain, split_position, split_resi_count, split_atom_count, split_resi_type, split_atom_type, split_resi_position):
    """
    This function takes a complex protein structure and determines which chains and residues are interacting
    with each other based on the distance between atoms. The output is a tuple that includes the following lists:

    Args:
        unique_chain (list): Unique chains within the protein structure
        split_position (list of list): Each sublist contains the positions of atoms in a specific chain
        split_resi_count (list of list): Each sublist contains the residue count of atoms in a specific chain
        split_atom_count (list of list): Each sublist contains the atom count in a specific chain
        split_resi_type (list of list): aEach sublist contains the residue type of atoms in a specific chain
        split_atom_type (list of list): Each sublist contains the atom type of atoms in a specific chain
        split_resi_position (list of list): Each sublist contains the residue position of atoms in a specific chain
    
    Returns:
        reaction_chain (list of list): Each sublist contains the chain IDs of two chains that are interacting with each other
        reaction_resi_position (list of list of list): Each sub-sublist contains pairs of residue positions that are interacting

    """
    
    # list of lists (each sublist will include two letters indicating these two chains have interaction)
    reaction_chain = []
    
    # list of lists of lists (Each sublist contains the residue position of atoms in a specific chain)
    reaction_resi_position = []
    
    #for each unique chain
    for i in range(len(unique_chain) - 1):
        
        #for each unique chain, not this one!
        for j in range(i+1, len(unique_chain)):
            
            #calculates distance between each atom in the chain, creating a list of their positions and overall number
            inner_reaction_resi_position,count = distance_bw_atoms_in_chains(split_position,split_resi_position,i,j)
            
            if count > 0:
                reaction_chain.append([unique_chain[i], unique_chain[j]])
                reaction_resi_position.append(inner_reaction_resi_position)
    return reaction_chain, reaction_resi_position


