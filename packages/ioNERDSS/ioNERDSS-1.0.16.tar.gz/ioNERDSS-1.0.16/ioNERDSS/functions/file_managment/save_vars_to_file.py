import os
import numpy as np


def add_empty_lists(input_list: list):
    """Will take in a list. If it has no value, it will add 'Empty List'. If it has sub lists, it will open them and do the same thing. (recursive)

    Args:
        input_list (list): list to be searched through
    """

    #check if list is empty
    if len(input_list) <= 0:
        input_list.append("Empty List")

    #check through all indexes to see if there are any lists. If there are run this function on them, else do nothing.
    input_list = [add_empty_lists(list(vars)) if (isinstance(vars,list) or isinstance(vars,np.ndarray)) else vars for vars in input_list]

    """ ^^^ equals what is below.
    for index,vars in enumerate(input_list):
        if isinstance(vars,list) or isinstance(vars,np.ndarray):
            input_list[index] = add_empty_lists(list(vars))"""

    return input_list



def save_vars_to_file(var_dict: dict):
    """This function takes a dictionary of variables and saves them to a file in the correct format.

        Parameters
            var_dict: A dictionary of variables to be saved.
        
        Explanation
            If the variable is a number or a string, it saves it to a .txt file. If the variable is a list, 
            it saves it to a .csv file. If the list is two-dimensional or deeper, it will save each sublist on a different line.
    """


    #create folder if necessary 
    file_start = "" #the starting part of the file

    #if there is a folder needed
    if len(var_dict) > 1:
        file_start = "vars/"

        #if the folder needs to be made
        if not os.path.exists("vars"):
            os.mkdir(path="vars")


    for key,value in var_dict.items():

        type = "" # what kind of file is being made
        file_end = "" # the ending part of the file
    
        #determine variable type
        if isinstance(value,int) or isinstance(value,float): #number
            file_end = f"{key}_number.txt"
            type = "txt"
        
        elif isinstance(value,str): #string
            file_end = f"{key}_string.txt"
            type = "txt"    
        
        elif isinstance(value,list) or isinstance(value,np.ndarray): #list
            file_end = f"{key}_list.csv"
            value = add_empty_lists(list(value)) #adds 'empty list' to lists that are empty 
            
            if isinstance(value[0],list) or isinstance(value[0],np.ndarray): #2dim+ deep list
                type = "2list"
            else: #1dim list
                type = "1list"
  
        else:
            file_end = f"{key}_na.txt"
            type = "txt"
        
        file_name = file_start + file_end



        #Create file name and open file 
        with open(file_name, mode = "w") as file:

            #if it is just basic text
            if type == "txt":
                file.write(str(value))
            
            #if it is a 1dim list
            elif type == "1list":
                file.write(str(value[0]))
                
                if len(value) > 1:
                    for var in value[1:]:
                        file.write(f",{var}")
            
            #if it is a 2dem list
            elif type == "2list":

                #run through each sub list
                for index,list1 in enumerate(value):
                    
                    #add \n, unless it is the first sublist
                    if index != 0:
                        file.write("\n")
                    
                    #write in entire sublist
                    file.write(f"{list1[0]}")
                    
                    if len(list1) > 1:
                        for list2 in list1[1:]:
                            file.write(f",{list2}")




            

        




