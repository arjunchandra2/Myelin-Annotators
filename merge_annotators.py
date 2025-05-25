"""
- Merge annotations by 3 annotators into a single .mat file for each image
- For full explanation see README.md 
"""

import random 
import os
from scipy.io import savemat

import utils
from bbox import Bbox

#IOU threshold to remove bboxes 
IOU_THRESHOLD = 0.2
#Z plane tolerance for matching bboxes
Z_PLANE_TOLERANCE = 1

#Color for each class in annotation software (Mixed Class is orange)
COLOR_ENCODING = {'Defect': [1,0,0], 'Swelling': [0,1,0], 'Vesicle': [0,0,1], 'Mixed': [1.0, 0.647, 0.0]}


def add_bboxes(annotations):
    """
    - Add bboxes to Bbox class for tracking
    """
    for i in range(len(annotations['class_type'])):
        class_name = annotations['class_type'][i]
        z_plane = annotations['z_plane'][i]
        coords = annotations['bbox_coord'][i]
        
        bbox = Bbox(coords[0], coords[1], coords[2], coords[3], z_plane, class_name)


def save_cleaned_annotations(clean_annotations, im_path, save_path):
    """
    - Save the cleaned .mat file 
    """
    mat_annotations = {"annotations": [im_path, "YOLOv8", [], [], [], [], []]}

    for bbox in clean_annotations:
        mat_annotations['annotations'][2].append(bbox.class_name)
        mat_annotations['annotations'][3].append(list(map(float, COLOR_ENCODING[bbox.class_name])))
        mat_annotations['annotations'][4].append([bbox.z_plane])
        mat_annotations['annotations'][5].append(list(bbox.get_coords()))
        mat_annotations['annotations'][6].append([bbox.conf])
        
    savemat(save_path, mat_annotations)


def get_valid(annotator1, annotator2, annotator3):
    """
    Input: List of bboxes for each annotator. 
    Output: Will return the valid bboxes for annotator 1 (identified by at least one other annotator, +/- 1 z-plane)
    """
    valid = []

    for bbox_1 in annotator1:
        found_match = False
        for bbox_2 in annotator2:
            if abs(int(bbox_2.z_plane) - int(bbox_1.z_plane)) <= Z_PLANE_TOLERANCE:
                iou = utils.compute_iou(bbox_2.get_coords(), bbox_1.get_coords())
                
                if iou > IOU_THRESHOLD:
                    if not found_match: 
                        found_match = True
            if found_match:
                break
        
        if not found_match:
            for bbox_3 in annotator3:
                if abs(int(bbox_3.z_plane) - int(bbox_1.z_plane)) <= Z_PLANE_TOLERANCE:
                    iou = utils.compute_iou(bbox_3.get_coords(), bbox_1.get_coords())
                    
                    if iou > IOU_THRESHOLD:
                        if not found_match: 
                            found_match = True
                if found_match:
                    break
        
        if found_match:
            valid.append(bbox_1)

    return valid

def get_matches(bbox, annotator2, annotator3):
    """
    Input: A valid bbox (from annotator 1) and the list of all valid bboxes for annotators 2 and 3
    Output: Returns all the bboxes from annotators 2 and 3 that match with the valid bbox from annotator 1, and a separate list containing all the ones in the same z-plane too

    *There could be multiple from a single annotator (2 or 3) that match with bbox but its a rare edge case
    """
    matches_all = []
    matches_same_z = []
    
    for bbox_2 in annotator2:
        if abs(int(bbox_2.z_plane) - int(bbox.z_plane)) <= Z_PLANE_TOLERANCE:
            iou = utils.compute_iou(bbox_2.get_coords(), bbox.get_coords())
            
            if iou > IOU_THRESHOLD:
                matches_all.append(bbox_2)
                if bbox_2.z_plane == bbox.z_plane: 
                    matches_same_z.append(bbox_2)

    for bbox_3 in annotator3:
        if abs(int(bbox_3.z_plane) - int(bbox.z_plane)) <= Z_PLANE_TOLERANCE:
            iou = utils.compute_iou(bbox_3.get_coords(), bbox.get_coords())
            
            if iou > IOU_THRESHOLD:
                matches_all.append(bbox_3)
                if bbox_3.z_plane == bbox.z_plane: 
                    matches_same_z.append(bbox_3)
                    
    return matches_all, matches_same_z
    

def combine_valid_bboxes(annotator1, annotator2, annotator3):
    """
    Input: List of valid bboxes for each annotator 
    Output: Combined list of valid bboxes for final image annotations
    """

    processed = []
    valid_bboxes_final = []

    for bbox1 in annotator1:
        #This check shouldn't be needed for the first annotator but just keeping it for symmetry 
        if bbox1 not in processed:
            matches, matches_same_z = get_matches(bbox1, annotator2, annotator3)

            #Now all the matches must agree on the class type, otherwise its "Mixed"
            final_class_name = bbox1.class_name
            for bbox in matches:
                if bbox.class_name != final_class_name:
                    final_class_name = "Mixed"
                    break
            #Now pick a random bbox amongst same z-plane ones and use its coordinates
            all_bboxes_same_z = [bbox1] + matches_same_z
            final_bbox_c = random.choice(all_bboxes_same_z)

            #Create a new object since we might be changing the class name 
            final_bbox = Bbox(*final_bbox_c.get_coords(), final_bbox_c.z_plane, final_class_name)

            valid_bboxes_final.append(final_bbox)

            #Mark all the same z-plane ones as processed 
            for bbox in all_bboxes_same_z:
                processed.append(bbox)

    for bbox2 in annotator2:
        if bbox2 not in processed:
            matches, matches_same_z = get_matches(bbox2, annotator1, annotator3)

            #Now all the matches must agree on the class type, otherwise its "Mixed"
            final_class_name = bbox2.class_name
            for bbox in matches:
                if bbox.class_name != final_class_name:
                    final_class_name = "Mixed"
                    break
            #Now pick a random bbox amongst same z-plane ones and use its coordinates 
            all_bboxes_same_z = [bbox2] + matches_same_z
            final_bbox_c = random.choice(all_bboxes_same_z)

            #Create a new object since we are changing the class name 
            final_bbox = Bbox(*final_bbox_c.get_coords(), final_bbox_c.z_plane, final_class_name)

            valid_bboxes_final.append(final_bbox)

            #Mark all the same z-plane ones as processed 
            for bbox in all_bboxes_same_z:
                processed.append(bbox)

    for bbox3 in annotator3: 
        if bbox3 not in processed:
            matches, matches_same_z = get_matches(bbox3, annotator1, annotator2)

            #Now all the matches must agree on the class type, otherwise its "Mixed"
            final_class_name = bbox3.class_name
            for bbox in matches:
                if bbox.class_name != final_class_name:
                    final_class_name = "Mixed"
                    break
            #Now pick a random bbox amongst same z-plane ones and use its coordinates
            all_bboxes_same_z = [bbox3] + matches_same_z
            final_bbox_c = random.choice(all_bboxes_same_z)

            #Create a new object since we are changing the class name 
            final_bbox = Bbox(*final_bbox_c.get_coords(), final_bbox_c.z_plane, final_class_name)

            valid_bboxes_final.append(final_bbox)

            #Mark all the same z-plane ones as processed 
            for bbox in all_bboxes_same_z:
                processed.append(bbox)

    return valid_bboxes_final


def main():

    arjun_dir = '/projectnb/npbssmic/ac25/Myelin_paper_CCP_dataset_arjun/3rd_batch'
    anna_dir = '/projectnb/npbssmic/annanov/Myelin_paper_CCP_dataset/Anna_annotated_final/3rd_batch'
    samer_dir = '/projectnb/npbssmic/ac25/Myelin_paper_CCP_dataset_samer/3rd_batch_annotations'

    save_dir = '/projectnb/npbssmic/ac25/Myelin_paper_final/combined_annotations_0.2/3rd_batch'

    num_arjun = 0
    num_anna = 0
    num_samer = 0

    num_arjun_valid = 0
    num_anna_valid = 0
    num_samer_valid = 0

    num_total = 0
    num_images = 0

    for arjun_file in os.listdir(arjun_dir):
        if arjun_file.endswith('.mat'):
            num_images += 1

            #Get .mat file paths for all three annotators for the current image
            arjun_annotation_fp = os.path.join(arjun_dir, arjun_file)

            for anna_file in os.listdir(anna_dir):
                if anna_file == arjun_file:
                    anna_annotation_fp = os.path.join(anna_dir, anna_file)

            for samer_file in os.listdir(samer_dir):
                if samer_file == arjun_file:
                    samer_annotation_fp = os.path.join(samer_dir, samer_file)

            #Load annotations for all three annotators for the current image
            Bbox.bboxes_unseen = {}
            arjun_annotations = utils.load_annotations(arjun_annotation_fp)
            add_bboxes(arjun_annotations)
            arjun_annotations = [item for sublist in Bbox.bboxes_unseen.values() for item in sublist]
            Bbox.bboxes_unseen = {}

            anna_annotations = utils.load_annotations(anna_annotation_fp)
            add_bboxes(anna_annotations)
            anna_annotations = [item for sublist in Bbox.bboxes_unseen.values() for item in sublist]
            Bbox.bboxes_unseen = {}

            samer_annotations = utils.load_annotations(samer_annotation_fp)
            add_bboxes(samer_annotations)
            samer_annotations = [item for sublist in Bbox.bboxes_unseen.values() for item in sublist]
            Bbox.bboxes_unseen = {}

            num_arjun += len(arjun_annotations)
            num_anna += len(anna_annotations)
            num_samer += len(samer_annotations)

            #Now step 1: Get all valid annotations by each annotator. They can differ by at most one z-plane as long as they have IoU > threshold
            anna_valid = get_valid(anna_annotations, arjun_annotations, samer_annotations)
            arjun_valid = get_valid(arjun_annotations, anna_annotations, samer_annotations)
            samer_valid = get_valid(samer_annotations, anna_annotations, arjun_annotations)

            num_anna_valid += len(anna_valid)
            num_arjun_valid += len(arjun_valid)
            num_samer_valid += len(samer_valid)

            #Now step 2: Combine all the valid bboxes (which coordinates to save and which class) *This creates new Bboxes which get tracked by Bbox class, so 
            #we clear them in the next iteration
            final_bboxes = combine_valid_bboxes(anna_valid, arjun_valid, samer_valid)

            num_total += len(final_bboxes)


            save_cleaned_annotations(final_bboxes, '', save_path=save_dir + "/" + arjun_file)

    print("{:<10} {:>10} {:>10}".format("Annotator", "Total", "Valid"))
    print("-" * 32)
    print("{:<10} {:>10} {:>10}".format("Anna", num_anna, num_anna_valid))
    print("{:<10} {:>10} {:>10}".format("Arjun", num_arjun, num_arjun_valid))
    print("{:<10} {:>10} {:>10}".format("Samer", num_samer, num_samer_valid))


    print()
    print(f"Total number of images: {num_images}")
    print(f"Total number of bboxes saved: {num_total}")


main()
