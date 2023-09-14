import pandas as pd


def coco_to_zity(coco: dict, project_type: str):
    if project_type == "instance_segmentation":
        return coco_to_zity_instance_segmentation(coco)
    elif project_type == "keypoints_detection":
        return coco_to_zity_keypoints_detection(coco)
    else:
        raise ValueError(f"Unsupported project type: {project_type}")


def coco_to_zity_instance_segmentation(coco: dict, ignore_is_crowd: bool = True):
    cid_to_category = {category_info["id"]: category_info["name"] for i, category_info in enumerate(coco["categories"])}

    imgid_to_hash = {}
    for img in coco["images"]:
        imgid_to_hash[img["id"]] = img["file_name"]

    zity = []

    for anno in coco["annotations"]:
        if anno["iscrowd"] and ignore_is_crowd:
            continue

        zity.append(
            {
                "image_hash": imgid_to_hash[anno["image_id"]],
                "mask": [{"closed": True, "hole": False, "points": points} for points in anno["segmentation"]],
                "category": cid_to_category[anno["category_id"]],
                "format": "rle" if anno["iscrowd"] else "polygon",
            }
        )

    return pd.DataFrame(zity), None


def coco_to_zity_keypoints_detection(coco: dict, must_have_keypoints: bool = True):
    cid_to_category = {category_info["id"]: category_info["name"] for i, category_info in enumerate(coco["categories"])}

    imgid_to_hash = {}
    for img in coco["images"]:
        imgid_to_hash[img["id"]] = img["file_name"]

    zity = []

    for anno in coco["annotations"]:
        if anno["num_keypoints"] == 0 and must_have_keypoints:
            continue

        zity.append(
            {
                "image_hash": imgid_to_hash[anno["image_id"]],
                "keypoints": anno["keypoints"],
                "category": cid_to_category[anno["category_id"]],
            }
        )

    return pd.DataFrame(zity), {"structure": coco["categories"][0]["skeleton"]}
