import json

from fastapi import APIRouter, Form

from ...dataset.manager import Manager


def build_annotations_router(params, manager: Manager):
    annotations_router = r = APIRouter(tags=["Dataset: Annotations"])

    @r.put("/annotations", summary="Update/insert new annotation records")
    async def upsert_annotations_r(
        annotation_records: str = Form(...),
    ):
        manager.upsert_annotations(json.loads(annotation_records))
        return {"status": "200 Succeed"}

    return annotations_router
