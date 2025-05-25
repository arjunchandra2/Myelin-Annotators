"""
Build excel spreadsheet with result for defect counts from directory of .mat files

Category mapping: 
AD = 1
CTE = 2
NC = 3
"""

import os
import pandas as pd

import utils


batch1_decode = {
    11: {"Samples_ID": 10382, "Category": 1, "PMI": 6.5},
    1: {"Samples_ID": 20382, "Category": 1, "PMI": 9},
    13: {"Samples_ID": 20969, "Category": 1, "PMI": 10.5},
    14: {"Samples_ID": 21354, "Category": 1, "PMI": 3},
    9: {"Samples_ID": 21424, "Category": 1, "PMI": 6.25},
    12: {"Samples_ID": 6489, "Category": 2, "PMI": 16.5},
    17: {"Samples_ID": 6912, "Category": 2, "PMI": 7},
    7: {"Samples_ID": 7019, "Category": 2, "PMI": 18.75},
    8: {"Samples_ID": 7126, "Category": 2, "PMI": 15.75},
    4: {"Samples_ID": 8572, "Category": 2, "PMI": 17.5},
    16: {"Samples_ID": 21499, "Category": 3, "PMI": 17},
    15: {"Samples_ID": 7597, "Category": 3, "PMI": 13.5},
    2: {"Samples_ID": 8095, "Category": 3, "PMI": 13.5},
}

batch2_decode = {
    4: {"Samples_ID": 8790, "Category": 1, "PMI": 17.75},
    1: {"Samples_ID": 301181, "Category": 3, "PMI": 13.92},
    2: {"Samples_ID": 6912, "Category": 2, "PMI": 7},
    3: {"Samples_ID": 7019, "Category": 2, "PMI": 18.75},
}

batch3_decode = {5: {"Samples_ID": 34929, "Category": 3, "PMI": 4}}


def main():

    # Specify path to data dir (.mat files) and the batch
    data_dir = (
        "/projectnb/npbssmic/ac25/Myelin_paper_final/combined_annotations_0.2/3rd_batch"
    )
    save_path = "/projectnb/npbssmic/ac25/Myelin_paper_final/defect_counts_combined_3rd_batch_0.2.xlsx"
    batch = 3

    num_images = 0

    rows = []

    for file in os.listdir(data_dir):
        if file.endswith(".mat"):
            num_images += 1

            # Get fig code for current image
            fig_code = int(file[:2])

            # Now we must get the counts of each type of bbox, for this we don't really need bbox class
            annotations = utils.load_annotations(os.path.join(data_dir, file))

            class_counts = {"Defect": 0, "Swelling": 0, "Vesicle": 0, "Mixed": 0}

            for class_type in annotations["class_type"]:
                if class_type in class_counts:
                    class_counts[class_type] += 1

            if batch == 1:
                metadata = batch1_decode[fig_code]
            elif batch == 2:
                metadata = batch2_decode[fig_code]
            elif batch == 3:
                metadata = batch3_decode[fig_code]

            row_data = {
                "Samples_ID": metadata["Samples_ID"],
                "Category": metadata["Category"],
                "Defect": class_counts["Defect"],
                "Swelling": class_counts["Swelling"],
                "Vesicle": class_counts["Vesicle"],
                "Mixed": class_counts["Mixed"],
                "PMI": metadata["PMI"],
                "Filename": file,
            }

            rows.append(row_data)

    df = pd.DataFrame(rows)
    df.to_excel(save_path, index=False)
    print(f"Excel file {save_path} saved successfully.")
    print(f"Processed {num_images} images.")


main()
