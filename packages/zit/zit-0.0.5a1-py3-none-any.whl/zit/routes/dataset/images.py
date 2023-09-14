import json
import os

from fastapi import APIRouter, Form, HTTPException
from fastapi.responses import FileResponse

from ...dataset.manager import Manager


def build_images_router(params, manager: Manager):
    images_router = r = APIRouter(tags=["Dataset: Images"])

    @r.get("/images/count", summary="Get number of images")
    async def get_images_count_r(only_annotated: bool = True):
        anno = manager.anno_df

        if only_annotated:
            size = anno["image_hash"].nunique()
        else:
            size = len(os.listdir(params["image_source"]))
        return size

    @r.get("/images/category/count", summary="Get number of images in a category")
    async def get_images_count_by_category_r(category: str):
        anno = manager.anno_df

        size = anno[anno["category"] == category]["image_hash"].nunique()
        return size

    @r.get("/images/meta", summary="Get images meta infos with annotations")
    async def get_images_meta_r(offset: int, limit: int):
        meta = manager.meta_df

        metainfos = meta[offset : offset + limit].to_dict(orient="records")
        annotations = manager.get_annotations_of_image_hashes([rec["file_name"] for rec in metainfos])
        res = [{**dict(rec), "annotations": annotations.get(rec["file_name"])} for rec in metainfos]
        return res

    @r.get("/images/category/meta", summary="Get images meta infos with annotations in a category")
    async def get_images_meta_by_category_r(category: str, offset: int, limit: int):
        anno = manager.anno_df
        meta = manager.meta_df

        image_hashes = anno[anno["category"] == category]["image_hash"].unique().tolist()[offset : offset + limit]
        annotations = manager.get_annotations_of_image_hashes(image_hashes)
        metainfos = meta[meta.file_name.isin(image_hashes)].to_dict(orient="records")

        result = []
        for rec in metainfos:
            result.append({**rec, "annotations": annotations.pop(rec.get("file_name"))})

        if len(annotations):
            raise HTTPException(status_code=404, detail="there are annotated images that don't exist")

        return result

    @r.get("/image", summary="Download image by filename")
    async def get_image_r(file_name: str):
        file_path = os.path.join(params["image_source"], file_name)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"{file_name} not found")

        return FileResponse(file_path, media_type="image/jpeg+png+bmp", filename=file_name)

    @r.post("/images", summary="Delete images by filenames")
    async def delete_images_r(
        filenames: str = Form(...),
    ):
        filenames = json.loads(filenames)
        image_fd = params["image_source"]

        # delete image files
        for filename in filenames:
            filepath = os.path.join(image_fd, filename)
            if os.path.isfile(filepath):
                os.remove(filepath)

        # delete image metas
        manager.delete_metas_of_file_names(filenames)

        # delete annotation records
        manager.delete_annotations_of_image_hashes(filenames)

        return {"status": "200 Succeed"}

    return images_router
