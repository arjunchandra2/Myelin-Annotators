# Myelin-Annotators

## Overview 
This repository hosts the code to combine bounding box annotations for 3 annotators. 

## Usage 

To get started, you should first install miniconda by following the directions [here](https://www.anaconda.com/docs/getting-started/miniconda/install). Once you have miniconda set up, you can  install the necessary libraries by placing yourself in the root directory of this project and running:
```
conda env create -f environment.yml
```

This will create a conda environment called `annotation_env`. To use this environment, you should run: 
```
conda activate annotation_env
```

Once you have installed the necessary libraries and activated the environment, you can run the code in each of the files as described below. 
 
### File descriptions
- `merge_annotators.py`
    - **Description:** Combines annotations from the 3 annotators according to the  procedure below. 
        - We use a two-stage procedure to combine annotations from the three annotators:

            In the first stage, the goal is to determine all of the valid annotations made by each annotator. To do so, we go through each annotator’s annotations and attempt to find a matching bounding box annotation by either of the other two annotators. Two bounding boxes are matching if they satisfy the following criteria: 

            1. The two bounding boxes differ by at most ± `Z_PLANE_TOLERANCE` z-planes. 
            2. The two bounding boxes have an IoU > `IOU_THRESHOLD`.

            If a single matching bounding box is found, the annotation for the current annotator is marked as a valid annotation. We repeat this process for each of the annotator’s annotations so that at the end of this first stage, we have a list of valid annotations made by each annotator. 

            The goal of the second stage is to combine the three lists of valid annotations (one for each annotator) into a single list. To do so, we go through each annotator’s valid annotations. For each of these, we find all of the matching annotations made by the other two annotators. We then do the following to determine how to save the combined annotation: 

            1. To determine the class type of the annotation we will save, we check that all matching annotations and the current annotation agree on the classification. If they do not, the annotation will be saved as “Mixed” class type. 

            2. To determine the bounding box coordinates of the annotation, we choose the coordinates randomly from the current annotation plus any matching annotations that are in the same z-plane as the current annotation. Then, all of these annotations which are in the same z-plane as the current annotation are marked as processed and will be skipped over since the combined annotation we are saving is for all of the matching annotations in the same z-plane.

            Now we have the coordinates and class type of the bounding box that will be saved for the current annotation that we are iterating over. We repeat this process for all valid annotations by all three annotators (skipping over annotations marked as processed) to build the final combined version of the annotations. 
   
    - **Usage:** To run this code, you can set the `Z_PLANE_TOLERANCE` and `IOU_THRESHOLD` at the top of the script. Then at the top of the `main` function you can specify the paths to each of the 3 annotator directories. Each directory should contain `.mat` annotation files with the same name for each image. You will also need to create and specify the `save_dir` where the combined `.mat` files should be saved. 
- `table_annotations_all.py`
    - **Description:** Saves an excel file with the annotation counts by class type from each annotator (and DL model) for each image. 
    - **Usage:** To run this code, you can specify the file paths at the top of the `main` function. You will need to specify where the directories are for each annotator and a path to save the excel file. 
- `table_annotations_merged.py`
    - **Description:** Saves an excel file with the combined annotation counts by class type for each image along with metadata for each image. 
    - **Usage:** To run this code, you can specify the file paths at the top of the `main` function. You will need to specify the path to the directory which contains the combined `.mat` files and a path to save the excel file. You will also need to specify which batch the data is for so that the script can use the corresponding image metadata. 


