from fastapi import APIRouter

from ..dataset.manager import Manager
from .dataset.annotations import build_annotations_router
from .dataset.categories import build_categories_router
from .dataset.images import build_images_router
from .dataset.queries import build_queries_router


def build_default_router(params, manager: Manager, meta_serving: bool = False):
    r = APIRouter(prefix="/default")

    r.include_router(build_images_router(params, manager))
    r.include_router(build_annotations_router(params, manager))
    r.include_router(build_categories_router(params, manager))

    q_r, df, meta_df = build_queries_router(params, manager, meta_serving)
    r.include_router(q_r)

    return r, df, meta_df


__all__ = ["build_default_router"]
