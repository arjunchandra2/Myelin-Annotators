"""
Build excel spreadsheet with result for defect counts from directory of .mat files

*Here we don't combine annotations into one, we keep all results from each annotator so we can evaluate 
inter-annotator reliability
"""

import os
import pandas as pd

import utils


def main():
    
    #Specify path to data dir (.mat files) 
    arjun_dir = '/projectnb/npbssmic/ac25/Myelin_paper_CCP_dataset_arjun/1st_batch'
    anna_dir = '/projectnb/npbssmic/annanov/Myelin_paper_CCP_dataset/Anna_annotated_final/1st_batch'
    samer_dir = '/projectnb/npbssmic/ac25/Myelin_paper_CCP_dataset_samer/1st_batch_annotations'
    dl_dir = '/projectnb/npbssmic/s/Anna_DL/test/Defect-Detection-main/data/inference/CCPtune/1st_batch'
    
    save_path = '/projectnb/npbssmic/ac25/Myelin_paper_final/defect_counts_raw_1st_batch.xlsx'

    num_images = 0

    rows = [] 

    for arjun_file in os.listdir(arjun_dir):
        if arjun_file.endswith('.mat'):

            #Get .mat file paths for all three annotators for the current image
            arjun_annotation_fp = os.path.join(arjun_dir, arjun_file)

            for anna_file in os.listdir(anna_dir):
                if anna_file == arjun_file:
                    anna_annotation_fp = os.path.join(anna_dir, anna_file)

            for samer_file in os.listdir(samer_dir):
                if samer_file == arjun_file:
                    samer_annotation_fp = os.path.join(samer_dir, samer_file)

            for dl_file in os.listdir(dl_dir):
                if dl_file == arjun_file:
                    dl_annotation_fp = os.path.join(dl_dir, dl_file)

            num_images += 1

            class_counts = {
                "Arjun: Defect": 0,
                "Arjun: Swelling": 0,
                "Arjun: Vesicle": 0,
                "Anna: Defect": 0,
                "Anna: Swelling": 0,
                "Anna: Vesicle": 0,
                "Samer: Defect": 0,
                "Samer: Swelling": 0,
                "Samer: Vesicle": 0,
                "DL: Defect": 0,
                "DL: Swelling": 0,
                "DL: Vesicle": 0
            }
            
            #Now we must get the counts of each type of bbox, for this we don't really need bbox class
            arjun_annotations = utils.load_annotations(arjun_annotation_fp)

            for class_type in arjun_annotations['class_type']:
                key = "Arjun: " + class_type
                class_counts[key] += 1       

            anna_annotations = utils.load_annotations(anna_annotation_fp)

            for class_type in anna_annotations['class_type']:
                key = "Anna: " + class_type
                class_counts[key] += 1      

            samer_annotations = utils.load_annotations(samer_annotation_fp) 

            for class_type in samer_annotations['class_type']:
                key = "Samer: " + class_type
                class_counts[key] += 1   

            dl_annotations =  utils.load_annotations(dl_annotation_fp) 

            for class_type in dl_annotations['class_type']:
                key = "DL: " + class_type
                class_counts[key] += 1   
            

            row_data = {
                "Image Name": arjun_file[:-4],
                "Arjun Defect": class_counts["Arjun: Defect"],
                "Arjun Swelling": class_counts["Arjun: Swelling"],
                "Arjun Vesicle": class_counts["Arjun: Vesicle"],
                "Anna Defect": class_counts["Anna: Defect"],
                "Anna Swelling": class_counts["Anna: Swelling"],
                "Anna Vesicle": class_counts["Anna: Vesicle"],
                "Samer Defect": class_counts["Samer: Defect"],
                "Samer Swelling": class_counts["Samer: Swelling"],
                "Samer Vesicle": class_counts["Samer: Vesicle"],
                "DL Defect": class_counts["DL: Defect"],
                "DL Swelling": class_counts["DL: Swelling"],
                "DL Vesicle": class_counts["DL: Vesicle"],

            }

            rows.append(row_data)

    df = pd.DataFrame(rows)
    df.to_excel(save_path, index=False)
    print(f"Excel file {save_path} saved successfully.")
    print(f"Processed {num_images} images.")

           

main()