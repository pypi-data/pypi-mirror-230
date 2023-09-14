from datetime import datetime

from fastapi import APIRouter, HTTPException

from ...dataset.manager import Manager


def build_categories_router(params, manager: Manager):
    categories_router = r = APIRouter(tags=["Dataset: Categories"])

    @r.patch("/category", summary="Rename a category")
    async def rename_category_r(
        category: str,
        rename_to: str,
        at: str = datetime.now().replace(microsecond=0).isoformat(),
    ):
        anno = manager.anno_df
        categories = anno["category"].unique()

        if category not in categories:
            raise HTTPException(status_code=404, detail=f"Category {category} not found")

        manager.rename_category(category, rename_to, at)
        anno = manager.anno_df

        return anno["category"].unique().tolist()

    return categories_router
