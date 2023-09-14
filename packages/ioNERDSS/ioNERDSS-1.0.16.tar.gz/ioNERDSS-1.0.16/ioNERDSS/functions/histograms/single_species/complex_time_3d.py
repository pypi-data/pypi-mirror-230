import numpy as np
import matplotlib.pyplot as plt
from .hist_temp import hist_temp
from ...file_managment.save_vars_to_file import save_vars_to_file


def complex_time_3d(GraphType: int, GraphedData: int, full_hist: list, FileNum: int, InitialTime: float, FinalTime: float,
                               SpeciesName: str, TimeBins: int, xBarSize: int = 1, ShowFig: bool = True,
                               ShowMean: bool = False, ShowStd: bool = False, SaveFig: bool = False, SaveVars: bool = False):
    """Creates all kinds of 3d time graphs. For info on each type look at main funcs for each type

    Args:
        GraphType (int): what type of graph is being shown. (1: heatmap, 2: 3D histogram)
        GraphedData (int): what type of data is being shown. (1: "complex_count", 2: "monomer_count", 3: "monomer_fraction")
        full_hist (list): list that holds all of that data from histogram.dat
        FileNum (int): Number of the total input files (file names should be [fileName]_1,[fileName]_2,...)
        InitialTime (float): The starting time. Must not be smaller / larger then times in file.
        FinalTime (float): The ending time. Must not be smaller / larger then times in file.
        SpeciesName (str): The name of the species you want to examine. Should be in the .dat file.        
        TimeBins (int): The number of bins that the selected time period is divided into.
        xBarSize (int, optional): The size of each data bar in the x-dimension. Defaults to 1.
        ShowFig (bool, optional): If the plot is shown. Defaults to True.
        ShowMean (bool, optional): If means will be shown in each box. Defaults to False.
        ShowStd (bool, optional): If std values will be shown in each box. Defaults to False.
        SaveFig (bool, optional): If the plot is saved. Defaults to False.
        SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

    """
    
    #creates equal time chunks b/w initial and final based on # of timebins
    t_arr = np.arange(InitialTime, FinalTime, (FinalTime-InitialTime)/TimeBins)
    t_arr = np.append(t_arr, FinalTime)
    
    z_list_tot = [] #list of list of each complex type/size. Each sublist = file. Subsublist = timebin.
    x_list_tot = [] #list of list of average count of each complex type/size. Each sublist = file. Subsublist = timebin.
    
    #write name of the plot / y label (if applicable)
    if GraphedData == 1:
        graphTitle = "Size Distribution with Changing of Time"
        zLabel = "Number of complexes"
    elif GraphedData == 2:
        graphTitle = "Total Number of Monomers in Complexes with Changing of Time"
        zLabel = "Number of monomers"
    elif GraphedData == 3:
        graphTitle = "Fraction of Monomers in Complexes with Changing of Time"
        zLabel = "Fraction of monomers"
    else:
        raise Exception("Invalid data type")



    for hist in full_hist:

        #find total number of monomers (ONLY FOR MONO FRACTION)
        if GraphedData == 3: 
            n_tot = hist[0][1][0]
        else:
            n_tot = 1

        max_num = 0 #size of the largest species type
        x_lst = [] #list of list of each species type in a time bin
        z_lst = [] #list of list of average count of each species type in a time bin
        t_plt = [] #time plot

        for time_bin in range(0, len(t_arr)-1):
            
            #creates time plot (different for 3d graphs and heatmaps)
            if GraphType == 1:
                t_plt.append(str(round(t_arr[time_bin], 2)) +
                            's ~ ' + str(round(t_arr[time_bin+1], 2)) + 's')
            elif GraphType == 2:
                t_plt.append((t_arr[time_bin]+t_arr[time_bin+1])/2)
            else: 
                raise Exception("Invalid graph type enterred")
            
            #finds each species type and average number of them during this timebin
            x, z = hist_temp(hist, t_arr[time_bin], t_arr[time_bin+1])
            x_lst.append(x)
            z_lst.append(z)
            
            #find largest species type
            if max(x) > max_num:
                max_num = max(x)
        
        #initilize main plot
        z_plt = np.zeros(shape=(max_num, TimeBins))
        
        #puts values into main plot (also tranposes?)
        for timebin_index,timebin in enumerate(x_lst):
            for protein_index,protein_complex in enumerate(timebin):
                z_plt[protein_complex-1, timebin_index] = z_lst[timebin_index][protein_index]
        
        

        #determines number of monomers in each complex size (ONLY FOR MONO COUNT) or their fraction of the whole (ONLY FOR MONO FRAC)
        if GraphedData >= 2:
            z_plt_mod = []
            for complex_size,protein_complex in enumerate(z_plt):
                z_plt_mod_temp = []
                for time_bin in protein_complex:
                    z_plt_mod_temp.append(time_bin * (complex_size+1) / n_tot)
                z_plt_mod.append(z_plt_mod_temp)
            z_plt = z_plt_mod

       
        z_plt = np.array(z_plt).T #tranpose back

        
        z_plt_ = []
        for i in range(len(z_plt)):
            z_plt_temp = []
            x_count = 0
            sum_ = 0.0
            
            #for each complex species type, if the barsize is >1 then add together different time bins 
            for j in range(len(z_plt[i])):
                x_count += 1
                sum_ += z_plt[i][j]
                if j == len(z_plt) - 1:
                    z_plt_temp.append(sum_)
                    x_count = 0
                    sum_ = 0
                elif x_count == xBarSize:
                    z_plt_temp.append(sum_)
                    x_count = 0
                    sum_ = 0
            z_plt_.append(z_plt_temp)
        z_plt_ = np.array(z_plt_)
        x_plt = np.arange(0, max_num, xBarSize)+1 #creates x_plt that holds each species tyoe
       
        #append to main, cross file lists 
        x_list_tot.append(x_plt)
        z_list_tot.append(list(z_plt_))
    
    #determine largest complex species
    max_x_num = 0
    for file in x_list_tot:
        if len(file) > max_x_num:
            max_x_num = len(file)
            n_list = file
    
    #ensure that the % of og monomers in a certain species size list has equal length to the other ... lists
    for file_index,file in enumerate(z_list_tot):
        for time_index,time_bin in enumerate(file):
            if len(time_bin) < len(n_list):
                for na in range(0, 1 + len(n_list) - len(time_bin)):
                    z_list_tot[file_index][time_index] = time_bin.tolist()
                    z_list_tot[file_index][time_index].append(0.0)
    
    #determine mean count / std of monomers in a each complex species in a time bin over each file
    count_list_mean = np.zeros([TimeBins, len(n_list)])
    count_list_std = np.zeros([TimeBins, len(n_list)])
    for i in range(len(z_list_tot[0])):
        for j in range(len(z_list_tot[0][0])):
            temp_list = []
            for k in range(len(z_list_tot)):
                temp_list.append(z_list_tot[k][i][j])
            count_list_mean[i][j] += np.mean(temp_list)
            count_list_std[i][j] += np.std(temp_list)
    
    #save vars
    if SaveVars:
        if GraphedData == 1:
            save_vars_to_file({"cmplx_sizes":n_list, "time_bins":t_plt, "cmplx_count":count_list_mean, "std":count_list_std})
        if GraphedData == 2:
            save_vars_to_file({"cmplx_sizes":n_list, "time_bins":t_plt, "mono_count":count_list_mean, "std":count_list_std}) 
        if GraphedData == 3:
            save_vars_to_file({"cmplx_sizes":n_list, "time_bins":t_plt, "mono_fraction":count_list_mean, "std":count_list_std})         
    
    if ShowFig:
        
        if GraphType == 1:
            fig, ax = plt.subplots()
            im = ax.imshow(count_list_mean)
            ax.set_xticks(np.arange(len(n_list)))
            ax.set_yticks(np.arange(len(t_plt)))
            ax.set_xticklabels(n_list)
            ax.set_yticklabels(t_plt)
            if ShowMean and ShowStd:
                print('Cannot show both mean and Std!')
                return 0
            if ShowMean:
                for i in range(len(t_plt)):
                    for j in range(len(n_list)):
                        text = ax.text(j, i, round(
                            count_list_mean[i, j], 1), ha='center', va='center', color='w')
            elif ShowStd and FileNum != 1:
                for i in range(len(t_plt)):
                    for j in range(len(n_list)):
                        text = ax.text(j, i, round(
                            count_list_std[i, j], 1), ha='center', va='center', color='w')
            ax.set_title(graphTitle)
            fig.tight_layout()
            plt.colorbar(im)
            plt.xlabel('Size of Complex')
            plt.ylabel('Time (s)')
            if SaveFig:
                plt.savefig('hist_heatmap_fraction.png',
                            dpi=500, bbox_inches='tight')
            plt.show()
        else:
            xx, yy = np.meshgrid(n_list, t_plt)
            X, Y = xx.ravel(), yy.ravel()
            Z = np.array(count_list_mean.ravel())
            bottom = np.zeros_like(Z)
            width = xBarSize
            depth = 1/TimeBins
            fig = plt.figure()
            ax = fig.add_subplot(2,2,1,projection="3d")
            ax.bar3d(X, Y, bottom, width, depth, Z, shade=True)
            ax.set_xlabel('Number of ' + SpeciesName + ' in sigle complex')
            ax.set_ylabel('Time (s)')
            ax.set_zlabel(zLabel)
            if SaveFig:
                plt.savefig('histogram_3D.png', dpi=500)
            plt.show()         
        
    
    return n_list, t_plt, count_list_mean, count_list_std


# Analysing tools for 'transition_matrix_time.dat'

