"""
contains function to extract text from image
input : image_file, coordinates file
output : list of all the text (can be made to JSON as well)
correctly_working : (jpeg)invoice4,invoice6,invoice7,
(jpg) : invoice14,
"""
import cv2
import matplotlib.pyplot as plt
import pytesseract
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from pytesseract import Output
from aims_.new_text_recog import extract_table_data
import pandas as pd
import json,math

def get_annotations_xlsx(path):
    df = pd.read_csv(path,header=None)
    annotate_dict = {}
    number_of_rows = df.shape[0]
    for r in range(1,number_of_rows):
        row1 = df.iloc[r,:]
        curr_row = row1.tolist()
        annotate_dict['page '+str(r+1)] = []
        label = curr_row[4]
        x1 = int(curr_row[2])
        x2 = x1 + int(curr_row[0])
        y1 = int(curr_row[3])
        y2 = y1 + int(curr_row[1])
        annotate_dict['page '+str(r+1)].append(
                    {
                        label:(x1,y1,x2,y2)
                    }
                )
    return annotate_dict

def plot_image(img):
    text = pytesseract.image_to_string(img)
    return text

def predict_invoice(path,excel_path):
    img = cv2.imread(path,0)
    annotations = get_annotations_xlsx(excel_path)
    # for now the text will be in list
    # further change it to json or as required
    data = []
    columns = 0
    table_img = None
    ts_first = None
    ts_second = None    
    for k in annotations.keys():
        annotations_list = annotations[k]
        for i in range(len(annotations_list)):
            
            for label in annotations_list[i]:
                x1,y1,x2,y2 = annotations_list[i][label]

                sub_image = img[y1:y2,x1:x2]
                
                if label != "Start of Table" and label!='No of Columns' and label!='End of Table':
                    temp_dict = {}
                    text = plot_image(sub_image)
                    newtext = text.strip().replace('\x0c','').replace('\n',' ')
                    temp_dict[label] = newtext
                    data.append(temp_dict)
                    
                if label == 'No of Columns':
                    columns = x1
                    
                if label == "Start of Table":
                    table_img1 = img[y1:, x1:]
                    table_img = np.stack((table_img1,)*3, axis=-1)
                    ts_first = y1
                    ts_second = x1

                # if label == "End of Table":
                #     table_img = img[ts_first:y2,ts_second:x2]
                #     # print(ts_first,y2,ts_second,x2)
    table_data = extract_table_data(table_img,columns)  
    return (data,table_data) 