
# Breakhis

The dataset used can be obtained [here]() 

This dataset consists of microscopic images of breast cancer tumors, both benign and malignant. Under benign, there are four subtypes namely - Adenosis, Fibroadenoma, Phyllodes, and Tubular adenoma. And under Malignant, there are four subtypes namely - Ductal, Lobular, Mucinous and Papillary. 

The various subtypes mentioned above were the lines along which the data was split among the two nodes under consideration. For example one of the SL nodes is trained on images of Ductal and Lobular carcinoma (under malignant), while the second SL node is trained on images of Mucinous and Papillary carcinoma. 

For ease of training and study, the images were converted to NPZ file format. 
To convert an image to a numpy array : 
np.asarray(Image.open(imname).convert("RGB"))

To convert into NPZ format, the image and its label is required and can be done as shown below : 
np.savez('destination_path/train.npz', X_train, Y_train)


The model being used here is the DenseNet201 from keras.applications.densenet.
The test set was kept common for both the SL nodes.
