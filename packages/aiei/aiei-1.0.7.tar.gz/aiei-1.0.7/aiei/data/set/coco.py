import itertools
import os
from collections import OrderedDict, defaultdict
import time
import json_tricks as json
import numpy as np
from tabulate import tabulate
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval
from aiei.core.base_config import cfg


def _create_table_with_header(header_dict, headers=['category', 'AP'], min_cols=10):
    assert min_cols % len(headers) == 0, 'bad table format'
    num_cols = min(min_cols, len(header_dict) * len(headers))
    result_pair = [x for pair in header_dict.items() for x in pair]
    row_pair = itertools.zip_longest(*[result_pair[i::num_cols] for i in range(num_cols)])
    table = 'Per-category AP:\n'
    table += tabulate(row_pair, tablefmt='pipe', floatfmt='.3f', headers=headers * (num_cols // len(headers)), numalign='left')
    return table


def _ms_coco_eval(det_file, gt_file, eval_type='keypoints', stats_names=None, cat_ids=None, is_show_per_category=False):
    coco = COCO(gt_file)
    coco_dt = coco.loadRes(det_file)
    coco_eval = COCOeval(coco, coco_dt, eval_type)
    coco_eval.params.useSegm = None
    if cat_ids is not None:
        coco_eval.params.catIds = cat_ids
    # coco_eval.params.imgIds = imgIds
    # coco_eval.params.maxDets = [1, 10, 20]
    coco_eval.evaluate()
    coco_eval.accumulate()
    coco_eval.summarize()

    order_dict = OrderedDict()
    for ind, name in enumerate(stats_names):
        order_dict[name] = round(coco_eval.stats[ind], 5)
    if is_show_per_category:
        precisions = coco_eval.eval['precision']  # precision has dims (iou, recall, cls, area range, max dets)
        results_per_category = {}
        for idx, name in enumerate(CLS_NAMES):
            # area range index 0: all area ranges
            # max dets index -1: typically 100 per image
            precision = precisions[:, :, idx, 0, -1]
            precision = precision[precision > -1]
            ap = np.mean(precision) if precision.size else float('nan')
            results_per_category[name] = float(ap * 100)
        cfg.LOG.INS.info(_create_table_with_header(results_per_category))
    return order_dict


def metric_box(results, output_dir, gt_file='', cat_ids=None):
    """
    :param results: {'image_id': (int), 'category_id': (int), 'bbox': (list), 'score': float}
         e.g.:  boxes {ndarray, shape(N, 4)(x, y, w, h)}; cls_ids {ndarray, shape(N,)}; det_scores {ndarray, shape(N,)}
         ```
         for box, cls_id, score in zip(boxes, cls_ids, scores):
            batch_results.append({'image_id': meta['img_id'][0].item(), 'bbox': box.tolist(),
                    'category_id': zcoco.REVERSE_CLS_IDS[cls_id.item()], 'score': score.item()})
         ```
    :param output_dir:
    :param gt_file:
    :param cat_ids: [1] is only eval person. None is all category
    :return:
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    res_file = f'{output_dir}/box_{"val" if gt_file != "" else "test"}_results.json'
    print('start pre eval...')
    t1 = time.time()
    # To avoid [WARNING:root:json-tricks: numpy scalar serial..], use .item(): numpy scalar -> python scalar
    with open(res_file, 'w') as fp:
        json.dump(results, fp)
    print(f'end pre eval...{time.time() - t1}')
    if gt_file != '':
        stats_names = [
            'AP', 'Ap .5', 'AP .75', 'AP (S)', 'AP (M)', 'AP (L)', 'AR', 'AR .5', 'AR .75', 'AR (S)', 'AR (M)', 'AR (L)'
        ]
        order_results = _ms_coco_eval(res_file, gt_file, 'bbox', stats_names=stats_names, cat_ids=cat_ids,
            is_show_per_category=(cfg.ZL != 0 and cat_ids is None))
        return order_results, order_results['AP']
    else:
        return {'test_mode_null': 0}, 0


def metric_segm(results, output_dir, gt_file='', cat_ids=None):
    """
    :param results: [{'image_id': (int), 'category_id': (int), 'segmentation': (RLE){'counts': str, 'size': list}, 'score'(det): (float)}]
        e.g.: pred_mask {ndarray, shape(N, H, W), dtype(np.uint8)}, cls_ids {ndarray, shape(N,)}; det_scores {ndarray, shape(N,)}
        ```
        for mask, cls_id, det_score in zip(pred_mask, cls_ids, det_scores):  # per box
            seg = mask_util.encode(np.array(mask[:, :, None], order='F'))[0]  # {'size': [427, 640], 'counts': b''}
            seg['counts'] = seg['counts'].decode()
            batch_results.append({'image_id': meta['img_id'][0].item(), 'segmentation': seg,
                                  'category_id': zcoco.REVERSE_CLS_IDS[cls_id.item()], 'score': det_score.item()})
        ```
    :param output_dir: str
    :param gt_file: str
    :param cat_ids: [1] is only eval person. None is all category
    :return:
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    res_file = f'{output_dir}/segm_{"val" if gt_file != "" else "test"}_results.json'
    print('start pre eval...')
    t1 = time.time()
    # To avoid [WARNING:root:json-tricks: numpy scalar serial..], use .item(): numpy scalar -> python scalar
    with open(res_file, 'w') as fp:
        json.dump(results, fp)
    print(f'end pre eval...{time.time() - t1}')
    if gt_file != '':
        stats_names = [
            'AP', 'Ap .5', 'AP .75', 'AP (S)', 'AP (M)', 'AP (L)', 'AR', 'AR .5', 'AR .75', 'AR (S)', 'AR (M)', 'AR (L)'
        ]
        order_results = _ms_coco_eval(res_file, gt_file, 'segm', stats_names=stats_names, cat_ids=cat_ids,
            is_show_per_category=(cfg.ZL != 0 and cat_ids is None))
        return order_results, order_results['AP']
    else:
        return {'test_mode_null': 0}, 0


def metric_keypoint(results, output_dir, gt_file=''):
    """
    :param results: {'image_id': (int), 'category_id': (int)1, 'keypoints': (list)[x, y, score, ...], 'score'(det): (float)}
            e.g.:  preds {ndarray, shape(N, 17 * 3)}; det_scores {ndarray, shape(N,)}
            ```
            batch_results.append({'image_id': meta['img_id'][0].item(), 'keypoints': pred.tolist(),
                    'category_id': 1, 'score': det_scores[i].item()})
            ```
    :param output_dir: str
    :param gt_file: str
    :return:
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    res_file = f'{output_dir}/keypoint_{"val" if gt_file != "" else "test"}_results.json'
    print('start pre eval...')
    t1 = time.time()
    with open(res_file, 'w') as fp:
        json.dump(results, fp)
    print(f'end pre eval...{time.time() - t1}')
    if gt_file != '':
        stats_names = ['AP', 'Ap .5', 'AP .75', 'AP (M)', 'AP (L)', 'AR', 'AR .5', 'AR .75', 'AR (M)', 'AR (L)']
        order_results = _ms_coco_eval(res_file, gt_file, 'keypoints', stats_names=stats_names)
        return order_results, order_results['AP']
    else:
        return {'test_mode_null': 0}, 0


KEYPOINT_HFLIP_INDEX = [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15]
coco_kp_names = [
    '0:nose', '1:l_eye', '2:r_eye', '3:l_ear', '4:r_ear', '5:l_shoulder', '6:r_shoulder', '7:l_elbow', '8:r_elbow', '9:l_wrist',
    '10:r_wrist', '11:l_hip', '12:r_hip', '13:l_knee', '14:r_knee', '15:l_ankle', '16:r_ankle'
]

# All coco categories, together with their nice-looking visualization colors
# It's from https://github.com/cocodataset/panopticapi/blob/master/panoptic_coco_categories.json
COCO_CATEGORIES = [
    {"color": [220, 20, 60], "isthing": 1, "id": 1, "name": "person"},
    {"color": [119, 11, 32], "isthing": 1, "id": 2, "name": "bicycle"},
    {"color": [0, 0, 142], "isthing": 1, "id": 3, "name": "car"},
    {"color": [0, 0, 230], "isthing": 1, "id": 4, "name": "motorcycle"},
    {"color": [106, 0, 228], "isthing": 1, "id": 5, "name": "airplane"},
    {"color": [0, 60, 100], "isthing": 1, "id": 6, "name": "bus"},
    {"color": [0, 80, 100], "isthing": 1, "id": 7, "name": "train"},
    {"color": [0, 0, 70], "isthing": 1, "id": 8, "name": "truck"},
    {"color": [0, 0, 192], "isthing": 1, "id": 9, "name": "boat"},
    {"color": [250, 170, 30], "isthing": 1, "id": 10, "name": "traffic light"},
    {"color": [100, 170, 30], "isthing": 1, "id": 11, "name": "fire hydrant"},
    {"color": [220, 220, 0], "isthing": 1, "id": 13, "name": "stop sign"},
    {"color": [175, 116, 175], "isthing": 1, "id": 14, "name": "parking meter"},
    {"color": [250, 0, 30], "isthing": 1, "id": 15, "name": "bench"},
    {"color": [165, 42, 42], "isthing": 1, "id": 16, "name": "bird"},
    {"color": [255, 77, 255], "isthing": 1, "id": 17, "name": "cat"},
    {"color": [0, 226, 252], "isthing": 1, "id": 18, "name": "dog"},
    {"color": [182, 182, 255], "isthing": 1, "id": 19, "name": "horse"},
    {"color": [0, 82, 0], "isthing": 1, "id": 20, "name": "sheep"},
    {"color": [120, 166, 157], "isthing": 1, "id": 21, "name": "cow"},
    {"color": [110, 76, 0], "isthing": 1, "id": 22, "name": "elephant"},
    {"color": [174, 57, 255], "isthing": 1, "id": 23, "name": "bear"},
    {"color": [199, 100, 0], "isthing": 1, "id": 24, "name": "zebra"},
    {"color": [72, 0, 118], "isthing": 1, "id": 25, "name": "giraffe"},
    {"color": [255, 179, 240], "isthing": 1, "id": 27, "name": "backpack"},
    {"color": [0, 125, 92], "isthing": 1, "id": 28, "name": "umbrella"},
    {"color": [209, 0, 151], "isthing": 1, "id": 31, "name": "handbag"},
    {"color": [188, 208, 182], "isthing": 1, "id": 32, "name": "tie"},
    {"color": [0, 220, 176], "isthing": 1, "id": 33, "name": "suitcase"},
    {"color": [255, 99, 164], "isthing": 1, "id": 34, "name": "frisbee"},
    {"color": [92, 0, 73], "isthing": 1, "id": 35, "name": "skis"},
    {"color": [133, 129, 255], "isthing": 1, "id": 36, "name": "snowboard"},
    {"color": [78, 180, 255], "isthing": 1, "id": 37, "name": "sports ball"},
    {"color": [0, 228, 0], "isthing": 1, "id": 38, "name": "kite"},
    {"color": [174, 255, 243], "isthing": 1, "id": 39, "name": "baseball bat"},
    {"color": [45, 89, 255], "isthing": 1, "id": 40, "name": "baseball glove"},
    {"color": [134, 134, 103], "isthing": 1, "id": 41, "name": "skateboard"},
    {"color": [145, 148, 174], "isthing": 1, "id": 42, "name": "surfboard"},
    {"color": [255, 208, 186], "isthing": 1, "id": 43, "name": "tennis racket"},
    {"color": [197, 226, 255], "isthing": 1, "id": 44, "name": "bottle"},
    {"color": [171, 134, 1], "isthing": 1, "id": 46, "name": "wine glass"},
    {"color": [109, 63, 54], "isthing": 1, "id": 47, "name": "cup"},
    {"color": [207, 138, 255], "isthing": 1, "id": 48, "name": "fork"},
    {"color": [151, 0, 95], "isthing": 1, "id": 49, "name": "knife"},
    {"color": [9, 80, 61], "isthing": 1, "id": 50, "name": "spoon"},
    {"color": [84, 105, 51], "isthing": 1, "id": 51, "name": "bowl"},
    {"color": [74, 65, 105], "isthing": 1, "id": 52, "name": "banana"},
    {"color": [166, 196, 102], "isthing": 1, "id": 53, "name": "apple"},
    {"color": [208, 195, 210], "isthing": 1, "id": 54, "name": "sandwich"},
    {"color": [255, 109, 65], "isthing": 1, "id": 55, "name": "orange"},
    {"color": [0, 143, 149], "isthing": 1, "id": 56, "name": "broccoli"},
    {"color": [179, 0, 194], "isthing": 1, "id": 57, "name": "carrot"},
    {"color": [209, 99, 106], "isthing": 1, "id": 58, "name": "hot dog"},
    {"color": [5, 121, 0], "isthing": 1, "id": 59, "name": "pizza"},
    {"color": [227, 255, 205], "isthing": 1, "id": 60, "name": "donut"},
    {"color": [147, 186, 208], "isthing": 1, "id": 61, "name": "cake"},
    {"color": [153, 69, 1], "isthing": 1, "id": 62, "name": "chair"},
    {"color": [3, 95, 161], "isthing": 1, "id": 63, "name": "couch"},
    {"color": [163, 255, 0], "isthing": 1, "id": 64, "name": "potted plant"},
    {"color": [119, 0, 170], "isthing": 1, "id": 65, "name": "bed"},
    {"color": [0, 182, 199], "isthing": 1, "id": 67, "name": "dining table"},
    {"color": [0, 165, 120], "isthing": 1, "id": 70, "name": "toilet"},
    {"color": [183, 130, 88], "isthing": 1, "id": 72, "name": "tv"},
    {"color": [95, 32, 0], "isthing": 1, "id": 73, "name": "laptop"},
    {"color": [130, 114, 135], "isthing": 1, "id": 74, "name": "mouse"},
    {"color": [110, 129, 133], "isthing": 1, "id": 75, "name": "remote"},
    {"color": [166, 74, 118], "isthing": 1, "id": 76, "name": "keyboard"},
    {"color": [219, 142, 185], "isthing": 1, "id": 77, "name": "cell phone"},
    {"color": [79, 210, 114], "isthing": 1, "id": 78, "name": "microwave"},
    {"color": [178, 90, 62], "isthing": 1, "id": 79, "name": "oven"},
    {"color": [65, 70, 15], "isthing": 1, "id": 80, "name": "toaster"},
    {"color": [127, 167, 115], "isthing": 1, "id": 81, "name": "sink"},
    {"color": [59, 105, 106], "isthing": 1, "id": 82, "name": "refrigerator"},
    {"color": [142, 108, 45], "isthing": 1, "id": 84, "name": "book"},
    {"color": [196, 172, 0], "isthing": 1, "id": 85, "name": "clock"},
    {"color": [95, 54, 80], "isthing": 1, "id": 86, "name": "vase"},
    {"color": [128, 76, 255], "isthing": 1, "id": 87, "name": "scissors"},
    {"color": [201, 57, 1], "isthing": 1, "id": 88, "name": "teddy bear"},
    {"color": [246, 0, 122], "isthing": 1, "id": 89, "name": "hair drier"},
    {"color": [191, 162, 208], "isthing": 1, "id": 90, "name": "toothbrush"},
    {"color": [255, 255, 128], "isthing": 0, "id": 92, "name": "banner"},
    {"color": [147, 211, 203], "isthing": 0, "id": 93, "name": "blanket"},
    {"color": [150, 100, 100], "isthing": 0, "id": 95, "name": "bridge"},
    {"color": [168, 171, 172], "isthing": 0, "id": 100, "name": "cardboard"},
    {"color": [146, 112, 198], "isthing": 0, "id": 107, "name": "counter"},
    {"color": [210, 170, 100], "isthing": 0, "id": 109, "name": "curtain"},
    {"color": [92, 136, 89], "isthing": 0, "id": 112, "name": "door-stuff"},
    {"color": [218, 88, 184], "isthing": 0, "id": 118, "name": "floor-wood"},
    {"color": [241, 129, 0], "isthing": 0, "id": 119, "name": "flower"},
    {"color": [217, 17, 255], "isthing": 0, "id": 122, "name": "fruit"},
    {"color": [124, 74, 181], "isthing": 0, "id": 125, "name": "gravel"},
    {"color": [70, 70, 70], "isthing": 0, "id": 128, "name": "house"},
    {"color": [255, 228, 255], "isthing": 0, "id": 130, "name": "light"},
    {"color": [154, 208, 0], "isthing": 0, "id": 133, "name": "mirror-stuff"},
    {"color": [193, 0, 92], "isthing": 0, "id": 138, "name": "net"},
    {"color": [76, 91, 113], "isthing": 0, "id": 141, "name": "pillow"},
    {"color": [255, 180, 195], "isthing": 0, "id": 144, "name": "platform"},
    {"color": [106, 154, 176], "isthing": 0, "id": 145, "name": "playingfield"},
    {"color": [230, 150, 140], "isthing": 0, "id": 147, "name": "railroad"},
    {"color": [60, 143, 255], "isthing": 0, "id": 148, "name": "river"},
    {"color": [128, 64, 128], "isthing": 0, "id": 149, "name": "road"},
    {"color": [92, 82, 55], "isthing": 0, "id": 151, "name": "roof"},
    {"color": [254, 212, 124], "isthing": 0, "id": 154, "name": "sand"},
    {"color": [73, 77, 174], "isthing": 0, "id": 155, "name": "sea"},
    {"color": [255, 160, 98], "isthing": 0, "id": 156, "name": "shelf"},
    {"color": [255, 255, 255], "isthing": 0, "id": 159, "name": "snow"},
    {"color": [104, 84, 109], "isthing": 0, "id": 161, "name": "stairs"},
    {"color": [169, 164, 131], "isthing": 0, "id": 166, "name": "tent"},
    {"color": [225, 199, 255], "isthing": 0, "id": 168, "name": "towel"},
    {"color": [137, 54, 74], "isthing": 0, "id": 171, "name": "wall-brick"},
    {"color": [135, 158, 223], "isthing": 0, "id": 175, "name": "wall-stone"},
    {"color": [7, 246, 231], "isthing": 0, "id": 176, "name": "wall-tile"},
    {"color": [107, 255, 200], "isthing": 0, "id": 177, "name": "wall-wood"},
    {"color": [58, 41, 149], "isthing": 0, "id": 178, "name": "water-other"},
    {"color": [183, 121, 142], "isthing": 0, "id": 180, "name": "window-blind"},
    {"color": [255, 73, 97], "isthing": 0, "id": 181, "name": "window-other"},
    {"color": [107, 142, 35], "isthing": 0, "id": 184, "name": "tree-merged"},
    {"color": [190, 153, 153], "isthing": 0, "id": 185, "name": "fence-merged"},
    {"color": [146, 139, 141], "isthing": 0, "id": 186, "name": "ceiling-merged"},
    {"color": [70, 130, 180], "isthing": 0, "id": 187, "name": "sky-other-merged"},
    {"color": [134, 199, 156], "isthing": 0, "id": 188, "name": "cabinet-merged"},
    {"color": [209, 226, 140], "isthing": 0, "id": 189, "name": "table-merged"},
    {"color": [96, 36, 108], "isthing": 0, "id": 190, "name": "floor-other-merged"},
    {"color": [96, 96, 96], "isthing": 0, "id": 191, "name": "pavement-merged"},
    {"color": [64, 170, 64], "isthing": 0, "id": 192, "name": "mountain-merged"},
    {"color": [152, 251, 152], "isthing": 0, "id": 193, "name": "grass-merged"},
    {"color": [208, 229, 228], "isthing": 0, "id": 194, "name": "dirt-merged"},
    {"color": [206, 186, 171], "isthing": 0, "id": 195, "name": "paper-merged"},
    {"color": [152, 161, 64], "isthing": 0, "id": 196, "name": "food-other-merged"},
    {"color": [116, 112, 0], "isthing": 0, "id": 197, "name": "building-other-merged"},
    {"color": [0, 114, 143], "isthing": 0, "id": 198, "name": "rock-merged"},
    {"color": [102, 102, 156], "isthing": 0, "id": 199, "name": "wall-other-merged"},
    {"color": [250, 141, 255], "isthing": 0, "id": 200, "name": "rug-merged"},
]


def _get_coco_instances_meta():
    thing_ids = [k["id"] for k in COCO_CATEGORIES if k["isthing"] == 1]
    thing_colors = [k["color"] for k in COCO_CATEGORIES if k["isthing"] == 1]
    assert len(thing_ids) == 80, len(thing_ids)
    # Mapping from the incontiguous COCO category id to an contiguous id in [0, 79]
    thing_dataset_id_to_contiguous_id = {k: i for i, k in enumerate(thing_ids)}
    thing_classes = [k["name"] for k in COCO_CATEGORIES if k["isthing"] == 1]
    ret = {
        "thing_contiguous_id": thing_dataset_id_to_contiguous_id,
        "thing_classes": thing_classes,
        "thing_colors": thing_colors,
    }
    return ret


# colors = [(np.random.random((3, )) * 255).tolist() for i in range(1000)]
_coco_meta = _get_coco_instances_meta()
CLS_CGS_IDS, CLS_NAMES, CLS_COLORS = _coco_meta['thing_contiguous_id'], _coco_meta['thing_classes'], _coco_meta['thing_colors']
REVERSE_CLS_IDS = {v: k for k, v in CLS_CGS_IDS.items()}  # same to self.cat_ids = self.coco.getCatIds()
# print(_coco_meta, REVERSE_CLS_IDS)

if __name__ == '__main__':
    test_res_file = 'zlogs/z03130005/results/box_val_results.json'
    test_gt_file = 'coco/annotations/instances_val2017.json'
    test_stats_names = [
        'AP', 'Ap .5', 'AP .75', 'AP (S)', 'AP (M)', 'AP (L)', 'AR', 'AR .5', 'AR .75', 'AR (S)', 'AR (M)', 'AR (L)'
    ]
    test_order_results = _ms_coco_eval(test_res_file, test_gt_file, 'bbox', cat_ids=None, stats_names=test_stats_names,
        is_show_per_category=False)
    print(test_order_results)
