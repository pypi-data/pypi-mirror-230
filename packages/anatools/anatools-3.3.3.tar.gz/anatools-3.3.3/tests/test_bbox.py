import unittest
from anatools import annotations
import os

class Test2dBBoxAnnotation(unittest.TestCase):

    def test_template_bbox(self): #update with the file paths as downloaded to do tests. Example included.
        anns = annotations()

        mappings_file_name = '/Users/samruddhi/resources/3_anatools_for_ML/default.yml'
        data_dir = "/Users/samruddhi/resources/1_getting_started/6e396ea6-e394-4566-8259-76bcadc16ab7"

        kitti_dir = os.path.join(data_dir, 'kitti_labels')
        anns.dump_kitti(data_dir, kitti_dir, mappings_file_name)

        # annotations = annotations()
        
        # annotations.bounding_box_2d(image_path='', 
        #                         out_dir='', object_types=['YoYo'])  


if __name__ == '__main__':
    unittest.main()