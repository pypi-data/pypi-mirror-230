import json
import os
from hashlib import blake2s
from pathlib import Path

from ..routes import build_default_router
from ..utils import find_zit_root
from .manager import Manager


def abspath(path):
    return os.path.abspath(path)


class DatasetBuilder:
    def __init__(self, task):
        self.task = task
        self._datasets = {}

    def __call__(self, **kwargs):
        raise NotImplementedError

    @staticmethod
    def _hash_params(params, digest_size=4):
        hasher = blake2s(digest_size=digest_size)
        hasher.update(json.dumps(params, sort_keys=True).encode("utf-8"))
        return hasher.hexdigest()


class DatasetBuilderTemplate(DatasetBuilder):
    def __call__(self, **kwargs):
        zit_root = find_zit_root(Path.cwd())

        image_source = abspath(kwargs.get("image_source", str(zit_root / "images")))
        annotation_source = abspath(kwargs.get("annotation_source", str(zit_root / "annotations.csv")))

        params = {
            "task": self.task,
            "image_source": image_source,
            "annotation_source": annotation_source,
        }

        hash_ = self._hash_params(params)

        if hash_ in self._datasets:
            dataset = self._datasets[hash_]

        else:
            manage_root = str(zit_root / ".zit" / "manager" / hash_)
            os.makedirs(manage_root, exist_ok=True)
            manager = Manager(manage_root, self.task, dataframe_serving=True)
            manager.add_metas(image_source, for_init=True)
            manager.add_annotations(annotation_source, for_init=True)

            meta_serving = kwargs.get("meta_serving", False)
            router, df, meta_df = build_default_router(
                params,
                manager,
                meta_serving=meta_serving,
            )

            dataset = {
                "params": params,
                "manager": manager,
                "router": router,
                "df": df,
                "meta_df": meta_df,
            }

            self._datasets[hash_] = dataset

        return dataset
