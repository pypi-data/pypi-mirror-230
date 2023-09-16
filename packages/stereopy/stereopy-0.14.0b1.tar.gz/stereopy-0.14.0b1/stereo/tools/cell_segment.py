import imp
import os
import shutil
from ..image import cell_seg, cell_seg_deepcell
from ..log_manager import logger

class CellSegment(object):

    def __init__(self, image_path, gpu='-1', mask_out_path=None):
        self.image_path = image_path
        self.mask_out_path = "cell_seg_res" if mask_out_path is None else mask_out_path
        if not os.path.exists(self.mask_out_path):
            os.makedirs(self.mask_out_path)
        self.gpu = gpu

    def generate_mask(
            self,
            model_path,
            model_type='deep-learning',
            depp_cro_size=20000,
            overlap=100,
            tissue_seg_model_path=None,
            tissue_seg_method=None,
            post_processing_workers=10
        ):
        logger.info(f"start to generate mask,model type {model_type}.")
        self.mask_out_path = os.path.join(self.mask_out_path, model_type)
        if model_type == 'deep-learning':
            cell_seg(
                model_path,
                self.image_path,
                self.mask_out_path,
                depp_cro_size,
                overlap,
                self.gpu,
                tissue_seg_model_path=tissue_seg_model_path,
                tissue_seg_method=tissue_seg_method,
                post_processing_workers=post_processing_workers
            )
        else:
            cell_seg_deepcell(
                model_path,
                self.image_path,
                self.mask_out_path,
                depp_cro_size,
                overlap,
                self.gpu,
                tissue_seg_model_path=tissue_seg_model_path,
                tissue_seg_method=tissue_seg_method,
                post_processing_workers=post_processing_workers
            )
        logger.info(f"generate mask end, the results is saved in {self.mask_out_path}")
    
    def get_mask_files(self):
        if self.mask_out_path is None:
            raise Exception("no mask files, please run the function generate_mask first")
        return [os.path.join(self.mask_out_path, file_name) for file_name in os.listdir(self.mask_out_path) if file_name.endswith('mask.tif')]

    def remove_all_mask_files(self):
        shutil.rmtree(self.mask_out_path)