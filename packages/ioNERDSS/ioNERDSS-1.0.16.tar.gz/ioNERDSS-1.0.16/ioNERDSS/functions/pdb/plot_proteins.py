from ..locate_pos.nerdss_PDB.read_PDB import read_PDB
import matplotlib.pyplot as plt

def plot_proteins(FileName: str):
    """Create a 3D plot that shows loation of each protein section
    """

    #reads in the PDB file. 
    # site_array: list that holds information about every protein site. 
    # site_dict: dictionary so you can index for site_array for specific attributes.
    # num_name_dict: holds the protein type for every protein number
    # main_pdb_list: literally the pdb file read in. Every line = pdb file
    site_array,site_dict,num_name_dict,main_pdb_list = read_PDB(file_name=FileName,drop_COM=False)
    
    #create plot
    fig = plt.figure(figsize=[12.8,9.6])
    ax = fig.add_subplot(projection="3d")

    for site in site_array:
        if site[site_dict["Site_Name"]] == "COM":
            #get x,y,z
            x = site[site_dict["x_coord"]]
            y = site[site_dict["y_coord"]]
            z = site[site_dict["z_coord"]]
        
            if site[site_dict["Protein_Name"]] == "cla":
                ax.scatter(x,y,z,marker="o")
            elif site[site_dict["Protein_Name"]] == "ap2":
                ax.scatter(x,y,z,marker="X")
            else:
                ax.scatter(x,y,z,marker="H")

    
    ax.set_xlabel("x_coord")
    ax.set_ylabel("y_coord")
    ax.set_zlabel("z_coord")

    plt.show()
