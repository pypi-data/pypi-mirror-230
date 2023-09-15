import glob
import tasks

list_items = glob.glob("/Users/david.lindenbaum/Downloads/detection_imgs/*.png")

for list_item in list_items:
    tasks.compute_feature_from_filepath.delay(list_item)
