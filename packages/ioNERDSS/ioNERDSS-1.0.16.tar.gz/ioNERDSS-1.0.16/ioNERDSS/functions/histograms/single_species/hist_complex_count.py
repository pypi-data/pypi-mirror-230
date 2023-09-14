import numpy as np
import matplotlib.pyplot as plt
from ...file_managment.save_vars_to_file import save_vars_to_file


def hist_complex_count(full_hist: list, FileNum: int, InitialTime: float, FinalTime: float, SpeciesName: str,
         BarSize: int = 1, ShowFig: bool = True, SaveFig: bool = False, SaveVars: bool = False):
    """Creates histogram of the average number of complex species that have a certain number of species.

    Args:
        full_hist (list): List that holds all of the data from the histogram.dat file
        FileNum (int): Number of the total input files (file names should be [fileName]_1,[fileName]_2,...)
        InitialTime (float): The starting time. Must not be smaller / larger then times in file.
        FinalTime (float): The ending time. Must not be smaller / larger then times in file.
        SpeciesName (str): The name of the species you want to examine. Should be in the .dat file.
        BarSize (int, optional): The size of each data bar in the x-dimension. Defaults to 1.
        ShowFig (bool, optional): If the plot is shown. Defaults to True.
        SaveFig (bool, optional): If the plot is saved. Defaults to False.
        SaveVars (bool, optional): If the variables are saved to a file. Defaults to false.

    Returns:
        Histogram. X-axis = # of species in a complexes. Y-axis = relative count of each complex over the whole timeframe
    """

    
    #main lists, each sublist = 1 folder
    count_list = []
    size_list = []
    
    #runs through each file
    for hist in full_hist:

        #lists for this file
        total_size_list = [] #list of each size
        total_count_list = [] #list of lists that hold the counts of eachsize

        data_count = 0
        for timestep in hist:
            if InitialTime <= timestep[0] <= FinalTime:
                data_count += 1
                
                #runs through each size of complex in this timestep
                for complex_index,complex_size in enumerate(timestep[2]):
                    
                    #if it is not in the total size list, add it
                    if complex_size not in total_size_list:
                        total_size_list.append(complex_size)
                        total_count_list.append(timestep[1][complex_index])
                    
                    #if it is, only add the number of this size to the list
                    else:
                        index = total_size_list.index(complex_size)
                        total_count_list[index] += timestep[1][complex_index]
        
        #entire array devided by datacount to determine % of the complexes that are that size
        total_count_list = np.array(total_count_list)/data_count
        
        #sort the size list
        if len(total_size_list) != 0:
            total_size_list_sorted = np.arange(1, max(total_size_list)+1, 1)
        else:
            total_size_list_sorted = np.array([])
        
        #sort the count list
        total_count_list_sorted = []
        for size in total_size_list_sorted:
            if size in total_size_list:
                index = total_size_list.index(size)
                total_count_list_sorted.append(total_count_list[index])
            else:
                total_count_list_sorted.append(0.0)
        
        #append sizes/counts to the main list
        size_list.append(total_size_list_sorted)
        count_list.append(total_count_list_sorted)
    
    #determine the biggest possible complex sizes, and make an empty array of that size
    max_size = 0
    for size_file in size_list:
        if max_size < len(size_file):
            max_size = len(size_file)
            n_list = size_file
    count_list_filled = np.zeros([max_size, FileNum])
    
    #add counts to the 0.0 list and make it so each sublist = 1 size across all files, instead of each sublist being 1 file with all sizes
    for i in range(len(count_list)):
        for j in range(len(count_list[i])):
            count_list_filled[j][i] += count_list[i][j]

    mean_ = []
    std_ = []
    n_list_ = []
    mean_temp = 0
    std_temp = 0
    bar_size_count = 0
    #run through each count list, find mean/stddev and add it to main list based on bar size
    for index,count_list in enumerate(count_list_filled):
        
        #determine mean / std for this count_list
        if FileNum != 1:
            mean_temp += np.nanmean(count_list)
            std_temp += np.nanstd(count_list)  
        else:
            mean_temp += count_list[0]

        #determine whether or not to add it based on bar size
        bar_size_count += 1
        
        #if it is the last run
        if index+1 == len(count_list_filled):
            mean_.append(mean_temp)
            std_.append(std_temp)
            n_list_.append(n_list[index])
        
        #if enough sizes have been gone through to create a new bar
        elif bar_size_count >= BarSize:
            mean_.append(mean_temp)
            std_.append(std_temp)
            n_list_.append(n_list[index])
            mean_temp = 0
            std_temp = 0
            bar_size_count = 0    
    
    mean_ = np.array(mean_)
    std_ = np.array(std_)
    n_list_ = np.array(n_list_)
    
    #save vars
    if SaveVars:
        save_vars_to_file({"cmplx_sizes":n_list_, "mean":mean_, "std":std_})


    #show figure!
    if ShowFig:
        if FileNum != 1:
            plt.bar(n_list_, mean_, width=BarSize, color='C0',
                    yerr=std_, ecolor='C1', capsize=2)
        else:
            plt.bar(n_list_, mean_, width=BarSize)
        plt.title('Histogram of ' + str(SpeciesName))
        plt.xlabel('Number of ' + SpeciesName + ' in sigle complex')
        plt.ylabel('Count')
        if SaveFig:
            plt.savefig('Histogram.png', dpi=500)
        plt.show()
    return n_list_, mean_, std_


