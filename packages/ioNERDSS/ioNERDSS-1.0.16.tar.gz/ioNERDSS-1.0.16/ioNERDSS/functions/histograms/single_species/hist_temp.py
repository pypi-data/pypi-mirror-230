

def hist_temp(hist: list, InitialTime: float, FinalTime: float):
    """Determines the average amount of each complex type/size over this timestep

    Args:
        FileName (list): histogram data that has been read in
        InitialTime (float): The starting time. Must not be smaller / larger then times in file.
        FinalTime (float): The ending time. Must not be smaller / larger then times in file.

    Returns:
        list: a list of each complex type/size
        list: a list of the average amount of each complex type/size
    """
    
    #reads the file
   
    plot_count = [] #total count of that certain size
    plot_conv = [] #list of each complex size
    tot = 0
    
    #for each timestep
    for timestep in hist:
        if InitialTime <= timestep[0] <= FinalTime:
            tot += 1
            
            #for each complex size
            for complex_size in timestep[2]:
                
                #initilize this size + it's counting
                if complex_size not in plot_conv:
                    plot_conv.append(complex_size)
                    plot_count.append(timestep[1][timestep[2].index(complex_size)])
                
                #add size to the list
                else:
                    index = plot_conv.index(complex_size)
                    plot_count[index] += timestep[1][timestep[2].index(complex_size)]
        elif timestep[0] > FinalTime:
            break
    
    plot_count_mean = []
    
    for complex_count in plot_count:
        plot_count_mean.append(complex_count/tot)
    return plot_conv, plot_count_mean


