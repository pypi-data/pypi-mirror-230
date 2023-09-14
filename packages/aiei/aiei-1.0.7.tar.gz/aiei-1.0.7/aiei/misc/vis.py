"""
(c) ZL-2020.
@author ZhaoLei
@since 2020.06.24 10:34
"""
import cv2
import numpy as np
from matplotlib import pyplot as plt


def show_coco_gt(img_origin, img_id, coco):
    plt.imshow(img_origin)
    # plt.axis('off')
    ann_ids = coco.getAnnIds(imgIds=[img_id], catIds=[], iscrowd=None)
    anns = coco.loadAnns(ann_ids)
    coco.showAnns(anns)
    plt.show()


def normalize(img):
    """
    Args:
        img (ndarray | tensor)

    Returns:
        (ndarray | tensor): same to img
    """
    img_min = float(img.min())
    img_max = float(img.max())
    img = (img + (-img_min)) / (img_max - img_min + 1e-6)
    return img


def tensor2img(img_tensor, permute=True) -> np.ndarray:
    """
    :param img_tensor: C, H, W
    :param permute: bool
    :return: H, W, C
    """
    img_tensor = img_tensor.mul(255).clamp(0, 255).byte()
    if permute:
        img_tensor = img_tensor.permute(1, 2, 0)
    return img_tensor.cpu().numpy()


def get_map(heatmap, img=None, alpha=0.5, agg_type='max'):
    """
    :param heatmap: ndarray C, H, W
    :param img: ndarray H, W, C
    :param alpha: alpha heatmap, 0-1
    :param agg_type: str max|avg
    :return: ndarray H, W, C
    """
    # from [0, 1] to [0, 255] and clip, then to uint8
    if len(heatmap.shape) == 2:
        heatmap = np.expand_dims(heatmap, 0)
    assert len(heatmap.shape) == 3, f'heatmap expects (C, H, W), currently {heatmap.shape}'
    if agg_type == 'max':
        tmp_map = np.max(heatmap, axis=0)  # H, W
    elif agg_type == 'avg':
        tmp_map = np.average(heatmap, axis=0)
    else:
        raise ValueError(f'Not support type {type}')
    tmp_map = np.array(np.clip(tmp_map * 255, 0, 255), dtype=np.uint8)
    tmp_map = cv2.applyColorMap(tmp_map, cv2.COLORMAP_JET)  # H, W, C
    if img is not None:
        tmp_map = np.array(np.clip(tmp_map * alpha + img * (1 - alpha), 0, 255), dtype=np.uint8)  # same to cv2.addWeighted
    return tmp_map


def get_split_map(heatmap, img=None, alpha=0.6, column=4, ignore_first=False):
    """
    :param heatmap: ndarray C, H, W
    :param img: ndarray H, W, C
    :param alpha: alpha heatmap
    :param column: int
    :param ignore_first: ignore_first heatmap
    :return: ndarray H, W, C
    """
    vstack_map = None
    count = 0
    for index in range((heatmap.shape[0] - 1) // 4):
        hstack_map = None
        for ind in range(column):
            i = index * 4 + ind
            if ignore_first:
                i += 1  # ignore first heatmap: ind+1
            tmp_map = np.array(np.clip(heatmap[i] * 255, 0, 255), dtype=np.uint8)
            tmp_map = cv2.applyColorMap(tmp_map, cv2.COLORMAP_JET)
            if img is not None:
                tmp_map = np.array(np.clip(tmp_map * alpha + img * (1 - alpha), 0, 255), dtype=np.uint8)
            count += 1
            # cv2.putText(tmp_map, coco_kp_names[count], (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255),
            # lineType=cv2.LINE_AA)
            hstack_map = tmp_map if hstack_map is None else np.hstack((hstack_map, tmp_map))
        vstack_map = hstack_map if vstack_map is None else np.vstack((vstack_map, hstack_map))
    return vstack_map


def get_skeleton(xs, ys, vis, img, ind_person=None):
    """
    single person skeleton
    :param xs: list x coord
    :param ys: list y coord
    :param vis: list visible
    :param img: ndarray H, W, C
    :param ind_person: tuple (ind_person, total_person), one person has one color
    :return: ndarray H, W, C
    """
    # from matplotlib import cm, colors
    # color_norm = colors.Normalize(vmin=0, vmax=len(group_lines))
    # rgba = cm.get_cmap('jet')(color_norm(10))  # colormap rgba value 0-1
    group_lines = [[0, 1], [0, 2], [1, 3], [2, 4], [5, 6], [5, 7], [6, 8], [7, 9], [8, 10], [5, 11], [6, 12], [11, 13], [12, 14],
        [13, 15], [14, 16]]  # coco
    list_color = cv2.applyColorMap(np.arange(256, dtype=np.uint8), cv2.COLORMAP_HSV).reshape(256, 3).tolist()
    norm_line = lambda x: int(x * 256 / len(group_lines))
    norm_point = lambda x: int(x * 256 / len(vis))  # non-linear, distinguish with norm_line
    norm_person = lambda x: int(x * 256 / ind_person[1])  # 40: max num person
    for i, zl in enumerate(group_lines):
        if vis[zl[0]] > 0 and vis[zl[1]] > 0:  # two points all visible
            # cv2.line(image_read, (xs[zl[0]], ys[zl[0]]), (xs[zl[1]], ys[zl[1]]), list_color[norm_line(i)], thickness=2,
            #     lineType=cv2.LINE_AA)
            dis, angle = cv2.cartToPolar(xs[zl[0]] - xs[zl[1]], ys[zl[0]] - ys[zl[1]], angleInDegrees=True)  # compute with (0, 0)
            ind_color = norm_person(ind_person[0]) if ind_person is not None else norm_line(i)
            cv2.ellipse(img, ((xs[zl[0]] + xs[zl[1]]) // 2, (ys[zl[0]] + ys[zl[1]]) // 2), (int(dis[0][0] / 2), 2),
                int(angle[0][0]), 0, 360, list_color[ind_color], thickness=-1, lineType=cv2.LINE_AA)
    for i in range(len(vis)):
        if vis[i] > 0:  # draw up to line
            ind_color = norm_person(ind_person[0]) if ind_person is not None else norm_point(i)
            cv2.circle(img, (xs[i], ys[i]), 3, list_color[ind_color], thickness=-1, lineType=cv2.LINE_AA)
            # cv2.putText(image_read, f'{ind_person}', (xs[i] + 5, ys[i]), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            # list_color[norm_point(i)], lineType=cv2.LINE_AA)
    return img


def get_box(boxes, cls_ids, scores, img, thre=0.2, names=None, colors=None, is_single_cls=False, alpha=0.75):
    """
    Visual Boxes

    Args:
        boxes (ndarray, (N, 4)): (N, [x1, y1, x2, y2])
        cls_ids (ndarray | list, (N, )): e.g.: [1] * N
        scores (ndarray | list, (N, )): e.g.: [1.0] * N
        img (ndarray): [description]
        thre (float, optional): Defaults to 0.2.
        names (list, optional): Defaults to None.
        colors (list, optional): Defaults to None.
        is_single_cls (bool, optional): True will ignore names. Defaults to False.

    Returns:
        ndarray: [description]
    """
    from aiei.data.set import coco as zcoco

    if names is None:
        names = [zcoco.CLS_NAMES[cls_id.item()] for cls_id in cls_ids]
    if colors is None:
        colors = [(np.random.random((3, )) * 255).tolist() for _ in range(200)]
    img_copy = img.copy()
    centers = ((boxes[:, :2] + boxes[:, 2:]) / 2).astype(np.int)
    boxes = boxes.astype(np.int)
    for ind, (box, cls_id, score, center) in enumerate(zip(boxes, cls_ids, scores, centers)):
        if score < thre:
            continue
        if box[3] - box[1] <= 0 or box[2] - box[0] <= 0 or np.min(box) < 0:
            continue
        text = f'{names[ind]}:{score:.2f}' if not is_single_cls else f'{score:.2f}'
        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), colors[ind], thickness=1)
        pos = (box[1], box[1] + 15) if box[1] - 15 < 0 else (box[1] - 15, box[1])
        cv2.rectangle(img, (box[0], pos[0]), (box[0] + len(text) * 7 + 2, pos[1]), colors[ind], thickness=-1)
        cv2.putText(img, text, (box[0] + 2, pos[0] + 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), lineType=cv2.LINE_AA)
        cv2.circle(img, (center[0], center[1]), 3, colors[ind], thickness=-1, lineType=cv2.LINE_AA)
    img = cv2.addWeighted(img, alpha, img_copy, 1 - alpha, 0)
    return img


def get_mask(masks, img):
    img_copy = img.copy()
    for mask in masks:
        mask = (mask > 0.5).astype(np.uint8)
        if mask.sum() == 0:
            continue
        color_mask = np.random.randint(0, 256, (1, 3), dtype=np.uint8)
        mask_bool = mask.astype(bool)
        img_copy[mask_bool] = img[mask_bool] * 0.5 + color_mask * 0.5
    return img_copy
