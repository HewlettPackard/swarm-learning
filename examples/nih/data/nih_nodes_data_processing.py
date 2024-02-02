############################################################################
## (C)Copyright 2024 Hewlett Packard Enterprise Development LP
## Licensed under the Apache License, Version 2.0 (the "License"); you may
## not use this file except in compliance with the License. You may obtain
## a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
## WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
## License for the specific language governing permissions and limitations
## under the License.
############################################################################


# This code has been inspired from the below kaggle kernel
#https://www.kaggle.com/code/adamjgoren/nih-chest-x-ray-multi-classification


# load help packages
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt # basic plotting
import seaborn as sns # additional plotting functionality

# Input data files are available in the "input/" directory.
# For example, running the below code (by clicking run or pressing Shift+Enter) will list the files in the input directory
import os
import sys
import yaml

print("CURRENT WORKING DIRECTORY :", os.getcwd())


profdata = None
profileFile = "data_generator.yaml"
try: 
    if os.path.isfile(profileFile):  
        with open(profileFile, "r") as p: 
            # loads only the first document in the stream 
            # so prof will always be an object , not a list
            profdata = yaml.safe_load(p)
            print(" data generator yaml file loaded")

except Exception as e:
    print("exception in loading yaml" , (str(e)))
    sys.exit(1)

databasedir = profdata['inputpathofnihdata']
print("nih databasedir is :", databasedir)
print(os.listdir(databasedir))

databasedirimages = os.path.join(databasedir, "images")


from glob import glob
my_glob = glob(databasedirimages+"/*.png")
print('Number of Observations: ', len(my_glob)) # check to make sure I've captured every pathway, should equal 112,120


# load data
xray_data = pd.read_csv(databasedir + '/Data_Entry_2017.csv')
# see how many observations there are
num_obs = len(xray_data)
print('Number of observations:',num_obs)
# examine the raw data before performing pre-processing
xray_data.head(5) # view first 5 rows
#xray_data.sample(5) # view 5 randomly sampled rows


# get the information about imagesavailbale for our experiment
# because dataset here could be subset of NIH full dataset.
# Depends on how much data is downloaded.
# Get the list of all images extracted.
file_list = []
for file in os.listdir(databasedirimages):
    file_list.append(file)
    
# Drop records from main csv (Data_Entry_2017.csv) for which images are not extracted
xray_data = xray_data[xray_data['Image Index'].isin(file_list)]
print(xray_data.info())


# Explore the dataset a bit
# replacing 'No Finding' with 'No_Finding' so that class name and folder creation/accessing will be easy
xray_data['Finding Labels'] = xray_data['Finding Labels'].replace('No Finding', 'No_Finding')

# Q: how many unique labels are there? A: many (836) because of co-occurence
# Note: co-occurence will turn out to be a real pain to deal with later, but there are several techniques that help us work with it successfully
num_unique_labels = xray_data['Finding Labels'].nunique()
print('Number of unique labels:',num_unique_labels)

# let's look at the label distribution to better plan our next step
#count_per_unique_label = xray_data['Finding Labels'].value_counts() # get frequency counts per label
#df_count_per_unique_label = count_per_unique_label.to_frame() # convert series to dataframe for plotting purposes
df_count_per_unique_label = xray_data['Finding Labels'].value_counts().reset_index().rename(columns={'index': 'Finding Labels', 0: 'count'})

print(df_count_per_unique_label)

sns.barplot(x = 'Finding Labels' , y="count", data=df_count_per_unique_label[:20], color = "green"), plt.xticks(rotation = 90) # visualize results graphically


# define labels of our interest
print(type(df_count_per_unique_label))
print(df_count_per_unique_label.columns)
#Intersted_labels = df_count_per_unique_label['Finding Labels'].tolist()[ :5]
Intersted_labels = profdata['interestedlabels']
print(Intersted_labels)


# create new dataframe from xray_data to hold only intrested records
xray_df = xray_data.loc[xray_data['Finding Labels'].isin(Intersted_labels)]
print("value count after selecting few labels for exploration")
print(xray_df['Finding Labels'].value_counts())

# Map the image paths onto xray_data
# Credit: small helper code fragment adapted from Kevin Mader - Simple XRay CNN on 12/09/18
# https://www.kaggle.com/kmader/train-simple-xray-cnn
full_img_paths = {os.path.basename(x): x for x in my_glob}
xray_df['org_full_path'] = xray_df['Image Index'].map(full_img_paths.get)
print("after full_path in xray_data")
print(xray_df['org_full_path'])
#xray_df.to_csv("selected_dataset_to_explore.csv", index=False)

from sklearn.model_selection import train_test_split
train_df, test_df = train_test_split(xray_df, test_size=0.15, random_state=0, stratify=xray_df['Finding Labels'])
print(train_df.info())
print(test_df.info())


from shutil import copy

def create_dir_for_each_label(basedir):
    os.makedirs(basedir, mode = 0o777, exist_ok = True)
    for eachLabel in Intersted_labels:
        os.makedirs((os.path.join(basedir, str(eachLabel))), mode = 0o777, exist_ok = True)
        
def copy_files(basedir, labelStr, srcPath):
    #print("labelStr :", labelStr)
    #print("srcPath:", srcPath)
    destPath = os.path.join(basedir, str(labelStr))
    copy(srcPath, destPath)

#trainDir="TRAINING"
testDir="TEST"
#create_dir_for_each_label(trainDir)
create_dir_for_each_label(testDir)

#train_df.apply(lambda x: copy_files(trainDir, x['Finding Labels'], x['org_full_path']), axis=1)
test_df.apply(lambda x: copy_files(testDir, x['Finding Labels'], x['org_full_path']), axis=1)

#train_df.to_csv("train_dataset.csv", index=False)
#test_df.to_csv("test_dataset.csv", index=False)


#Further Data preparation. 
train_df["NodeInfo"] = "TBD"
grouped = train_df.groupby('Finding Labels')

# Create a dictionary of DataFrames, where keys are unique values in 'Category'
dfs_by_category = {group: group_df for group, group_df in grouped}

trainDFNodesInfo = None
# Access the DataFrames using the keys
for eachLabel in Intersted_labels:
    df_temp = dfs_by_category[str(eachLabel)]
    print("Label in process :", eachLabel)
    lengthDF = len(df_temp)
    imbList = []
    #'Atelectasis', 'Infiltration', 'Effusion'
    if('Atelectasis' == eachLabel):
        imbList = [0.65, 0.2]
    elif('Infiltration' == eachLabel):
        imbList = [0.2, 0.65]
    else:
        imbList = [0.1, 0.1]
    imbList = [int(i * lengthDF) for i in imbList]
    print( "imbList is :",imbList)
    
    df_temp.reset_index(drop=True, inplace=True)
    df_temp.loc[:imbList[0], "NodeInfo"] = "Node1"
    df_temp.loc[imbList[0] : (imbList[0]+imbList[1]), "NodeInfo"] = "Node2"
    df_temp.loc[(imbList[0]+imbList[1]) : , "NodeInfo"] = "Node3"
    if(trainDFNodesInfo is None):
        trainDFNodesInfo = df_temp
    else:
        trainDFNodesInfo = trainDFNodesInfo._append(df_temp)
#trainDFNodesInfo.to_csv("ALLNODES.csv", index=False)


#copy training files to Node specific folder
#create directories for Node1,2,3
create_dir_for_each_label("Node1")
create_dir_for_each_label("Node2")
create_dir_for_each_label("Node3")
trainDFNodesInfo.apply(lambda x: copy_files(x['NodeInfo'], x['Finding Labels'], x['org_full_path']), axis=1)

