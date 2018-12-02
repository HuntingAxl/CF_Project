#!/usr/bin/python3
import re
import os
import os.path as path
from pandas import DataFrame

def getFileData(file_path):
    file = open(file_path,'r')
    data = file.readlines()
    file.close()
    return data

def date2int(date):
    components = date.split('-')
    month_dic={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
    month=month_dic[components[1]]
    if month < 10:
        month= '0' + str(month)
    return int(components[2]+str(month)+components[0])

def getValueFromData(data,date):
    max_date = 100000000
    prev_value = 0.0
    for item in data:
        item_date = item[0]
        item_value= item[1]
        if item_value!=0.0 and item_date<date:
            prev_value = item_value
    if prev_value==0.0:
        for item in data:
            item_date = item[0]
            item_value= item[1]
            if item_value!=0.0:
                prev_value = item_value
                break
    for item in data:
        item_date = item[0]
        value = item[1]
        if date==item_date:
            return value
        elif item_date<=date and item_date>max_date and value!=0.0:
            max_date = item_date
            prev_value = value
        elif item_date > date:
            break
    return prev_value

def addData(list1,list2):
    result = []
    for i in range(len(list1)):
        result.append(list1[i] + list2[i])
    return result

def extract_data(folder_name):
    folder_names = os.listdir(folder_name)
    split_token1 = '\n'
    split_token2 = ";"
    extracted_data = []
    line_match_pattern = ".*[;]*[;]([0-9]+[.][0-9]+)[;]*[;]*[;]([0-3][0-9][-](Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dev)[-]20[0-1][0-9])"
    for j in range(8):
        folder = folder_names[j]
        print("Processing Folder '",folder,"'")
        scheme_dict = {}
        date_list = []
        
        folder_path = path.join(folder_name,folder)
        files_list = os.listdir(folder_path)

        for file_name in files_list:
            
            file_path = path.join(folder_path,file_name)    
            data_lines = getFileData(file_path)

            for line in data_lines:
                if re.match(line_match_pattern,line):
                    line_data = line.split(split_token1)[0]
                    line_data = line_data.split(split_token2)
                    
                    date = date2int(line_data[5])
                    scheme = line_data[1]
                    nav_value = line_data[2]
                    if(nav_value=='#N/A'):
                        nav_value = 0.0
                    else:
                        nav_value = float(nav_value)
                    
                    if date not in date_list:
                        date_list.append(date)
                    
                    if scheme in scheme_dict:
                        scheme_dict[scheme].append([date,nav_value])
                    else:
                        scheme_dict[scheme] = [[date,nav_value]]
                    del(line_data)
            del(data_lines)
        date_list.sort()
        # print(date_list)
        # for i in range(1,len(date_list)):
        #     if(date_list[i-1]>date_list[i]):
        #         raise Exception('Wrong Ordering.')
        
        print("Connecting Data",end=', ')

        for scheme in scheme_dict:
            data = scheme_dict[scheme]
            data.sort(key=lambda a:a[0])
            new_date_data = []
            present_dates = [data_item[0] for data_item in data]
            for date in date_list:
                new_date_data.append([date,getValueFromData(data,date)])
            scheme_dict[scheme] = new_date_data
        
        print("Data Connected","Starting Aggregation",sep=', ')
        
        schemes = list(scheme_dict.keys())
        if len(schemes)>0:
            prev_data = scheme_dict[ schemes[0] ]
            for i in range(1, len(schemes)):
                cur_data  = scheme_dict[ schemes[i] ]
                prev_data = addData(prev_data,cur_data)
        
        dates = [data[0] for data in prev_data]
        values = [data[1] for data in prev_data]
        print("Aggregation Completed.")
        extracted_data.append(dict(zip(dates,values)))
        del(scheme_dict)
        del(date_list)
        del(files_list)
        del(schemes)
        del(dates)
        del(values)
        
    # print(extracted_data)
    delete_extracted_data = []
    delete_folder_names = []

    for i in range(len(extracted_data)):
        if len(extracted_data[i].keys()) == 0:
            delete_extracted_data.append(extracted_data[i])
            delete_folder_names.append(folder_names[i])
    
    for item in delete_extracted_data:
        extracted_data.remove(item)
    
    for item in delete_folder_names:
        folder_names.remove(item)
    
    ''' create the vectors. 
        Later on change the date to [dd, mm, yyyy] or any other date format.
    '''

    final_data = []
    for data_dict in extracted_data:
        data_list = []
        dates = data_dict.keys()
        for date in dates:
            vector = [date, data_dict[date]]
            data_list.append(vector)
        final_data.append(data_list)
    return final_data,folder_names

def main():
    FOLDER_NAME = 'Data'
    NAME_MAPPING_FILE = 'name_mapping.csv'

    name_data = getFileData(NAME_MAPPING_FILE)

    ''' remove '\n' from the names. '''
    for i in range(len(name_data)):
        name_data[i] = name_data[i].split('\n')[0]
    
    final_file_names = {}
    
    for line in name_data:
        split_line = line.split(sep=',')
        mf=split_line[0]
        name = split_line[1]
        final_file_names[mf] = name

    extracted_data, folder_names = extract_data(FOLDER_NAME)
    for i in range(1,8):
        DataFrame(extracted_data[i]).to_csv(path.join("Final",final_file_names[folder_names[i]]),sep=',',index=False,header=False)
        print(final_file_names[folder_names[i]]," converted to csv.")
    
    # DataFrame(extracted_data[0]).to_csv(path.join("Final",final_file_names['3']+'.csv'),sep=',',index=False,header=False)
    # print(final_file_names['3']," converted to csv.")

if __name__ == '__main__':
    main()