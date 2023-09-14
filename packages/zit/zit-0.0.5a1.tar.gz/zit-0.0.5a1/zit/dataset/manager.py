import hashlib
import io
import json
import os
from datetime import datetime
from typing import Dict, List

import duckdb
import pandas as pd
from fastapi import HTTPException
from PIL import Image, ImageOps

from .convert import coco_to_zity


def _get_all_files(folder_path):
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), folder_path)
            file_list.append(file_path)
    return file_list


def _parquet_to_csv(parquet_file_path: str):
    df = pd.read_parquet(parquet_file_path)
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False, encoding="utf-8-sig")
    csv_buf.seek(0)
    return csv_buf


class Manager:
    def __init__(self, root_path: str, task: str, dataframe_serving: bool = False):
        self.task = task
        self.anno_db = os.path.join(root_path, "anno.db")
        self.anno_df = None

        if task == "classification":
            self.required_fields = ["image_hash", "category"]
            self.unique_fields = ["image_hash"]

        elif task == "multilabel_classification":
            self.required_fields = ["image_hash", "attributes"]
            self.unique_fields = ["image_hash"]

        elif task == "box_classification":
            self.required_fields = ["image_hash", "x", "y", "w", "h", "category"]
            self.unique_fields = ["image_hash", "x", "y", "w", "h"]

        elif task == "box_multilabel_classification":
            self.required_fields = ["image_hash", "x", "y", "w", "h", "attributes"]
            self.unique_fields = ["image_hash", "x", "y", "w", "h"]

        elif task == "detection":
            self.required_fields = ["image_hash", "x", "y", "w", "h", "category"]
            self.unique_fields = ["image_hash", "x", "y", "w", "h"]

        elif task == "instance_segmentation":
            # format refers to: polygon / rle / binary
            self.required_fields = ["image_hash", "mask", "category", "format"]
            self.unique_fields = ["image_hash", "mask"]

        elif task == "keypoints_detection":
            self.required_fields = ["image_hash", "keypoints", "category"]
            self.unique_fields = ["image_hash", "keypoints"]

        self.meta_db = os.path.join(root_path, "meta.db")
        self.meta_df = None

        self.serving = dataframe_serving
        if dataframe_serving:
            self.connect_db()
            if self._table_exists("anno"):
                self.anno_df = self.cursor.execute("select * from anno").fetchdf()
            self.close_db()

            self.connect_db("meta")
            if self._table_exists("meta"):
                self.meta_df = self.cursor.execute("select * from meta").fetchdf()
            self.close_db()

    def connect_db(self, db: str = "anno"):
        self.conn = duckdb.connect(self.anno_db if db == "anno" else self.meta_db)
        self.cursor = self.conn.cursor()

    def close_db(self):
        self.cursor.close()
        self.conn.close()

    def add_metas(self, folder_path: str, for_init: bool = False):
        if for_init:
            self.connect_db("meta")
            inited = self._table_exists("meta")
            self.close_db()
            if inited:
                return

        self.connect_db("meta")
        inited = self._table_exists("meta")
        existed_names = (
            [row[0] for row in self.cursor.execute("select file_name from meta").fetchall()] if inited else []
        )
        self.close_db()

        meta = []
        todo = set(_get_all_files(folder_path)) - set(existed_names)

        for file_name in todo:
            file_path = os.path.join(folder_path, file_name)
            im = Image.open(file_path)
            im = ImageOps.exif_transpose(im)
            width, height = im.size
            area = width * height
            meta.append(
                {
                    "file_name": file_name,
                    "file_size": os.path.getsize(file_path),
                    "image_width": width,
                    "image_height": height,
                    "image_area": area,
                    "updated_at": (
                        datetime.fromtimestamp(os.path.getmtime(file_path)).replace(microsecond=0).isoformat()
                    ),
                    "upload_time": datetime.now().replace(microsecond=0).isoformat(),
                }
            )

        df = pd.DataFrame(meta)
        if df.empty:
            return

        self.connect_db("meta")

        if inited:
            self.cursor.execute("insert into meta select * from df")
        else:
            self.cursor.execute("create table meta as select * from df")

        if self.serving:
            self.meta_df = self.cursor.execute("select * from meta").fetchdf()

        self.close_db()

    def add_annotations(self, file_path: str, for_init: bool = False):
        if for_init:
            self.connect_db()
            inited = self._table_exists("anno")
            self.close_db()
            if inited:
                return

        df, extra_info = self._sanitycheck_file(file_path)

        if "timestamp_z" not in df.columns:
            now_str = datetime.now().replace(microsecond=0).isoformat()
            df["timestamp_z"] = now_str

        if "unique_hash_z" not in df.columns:
            df["unique_hash_z"] = df[self.unique_fields].apply(
                lambda row: hashlib.md5("-".join([str(v) for v in row.values]).encode()).hexdigest(),
                axis=1,
            )

        # dedup
        df = df.drop_duplicates(subset=["unique_hash_z"])

        self.connect_db()

        # merge added annotations with existed annotations
        if self._table_exists("anno"):
            df_ = self.cursor.execute("select * from anno").fetchdf()

            df = pd.concat([df_, df], ignore_index=True, sort=False)

            # dedup again
            df = df.drop_duplicates(subset=["unique_hash_z"], keep="last")

        # update anno_db
        self.cursor.execute("drop table if exists anno; create table anno as select * from df")

        if self.serving:
            self.anno_df = df

        # write extra_info, e.g. the skeleton/structure for keypoints_detection project
        if extra_info and not self._table_exists("extra_info"):
            self.cursor.execute(f"create table extra_info as select {json.dumps(extra_info)} as info")

        self.close_db()

    def upsert_annotations(self, records: List[Dict]):
        image_hashes = [rec["image_hash"] for rec in records]
        image_hashes_str = ", ".join([f"'{h}'" for h in image_hashes])
        records = self._transform_records(records)

        self.connect_db()

        if not self._table_exists("anno"):
            # create anno table here, this happens when annotate from scratch and sync annotations
            # to backend the first time
            if self.task in ["detection", "box_classification"]:
                self.cursor.execute(
                    "CREATE TABLE anno(image_hash VARCHAR, x INTEGER, y INTEGER, w INTEGER, h INTEGER, "
                    "category VARCHAR, timestamp_z VARCHAR, unique_hash_z VARCHAR)"
                )

            elif self.task == "classification":
                self.cursor.execute(
                    "CREATE TABLE anno(image_hash VARCHAR, category VARCHAR, timestamp_z VARCHAR, "
                    "unique_hash_z VARCHAR)"
                )

            elif self.task == "multilabel_classification":
                self.cursor.execute(
                    "CREATE TABLE anno(image_hash VARCHAR, attributes VARCHAR, timestamp_z VARCHAR, "
                    "unique_hash_z VARCHAR)"
                )

            elif self.task == "box_multilabel_classification":
                self.cursor.execute(
                    "CREATE TABLE anno(image_hash VARCHAR, x INTEGER, y INTEGER, w INTEGER, h INTEGER, "
                    "attributes VARCHAR, timestamp_z VARCHAR, unique_hash_z VARCHAR)"
                )

            elif self.task == "instance_segmentation":
                self.cursor.execute(
                    "CREATE TABLE anno(image_hash VARCHAR, mask STRUCT(closed BOOLEAN, hole BOOLEAN, points"
                    " DOUBLE[])[], category VARCHAR, format VARCHAR, timestamp_z VARCHAR, unique_hash_z VARCHAR)"
                )

            elif self.task == "keypoints_detection":
                self.cursor.execute(
                    "CREATE TABLE anno(image_hash VARCHAR, keypoints BIGINT[], category VARCHAR, "
                    "timestamp_z VARCHAR, unique_hash_z VARCHAR)"
                )

        # image-level overwrite:
        # 1. delete outdated annotations given an image hash
        self.cursor.execute(f"delete from anno where image_hash in ({image_hashes_str})")

        # 2. insert updated annotations
        if len(records):
            columns = records[0].keys()
            columns_str = ", ".join(columns)
            q_str = ", ".join(["?"] * len(columns))
            self.cursor.executemany(
                f"insert into anno({columns_str}) values ({q_str})",
                [rec.values() for rec in records],
            )

        if self.serving:
            self.anno_df = self.cursor.execute("select * from anno").fetchdf()

        self.close_db()

    def get_annotations_of_image_hashes(self, image_hashes: List[str], return_dict: bool = True):
        self.connect_db()

        if not self._table_exists("anno") or not len(image_hashes):
            self.close_db()
            return {} if return_dict else pd.DataFrame()

        image_hashes_str = ", ".join([f"'{h}'" for h in image_hashes])
        res = self.cursor.execute(f"select * from anno where image_hash in ({image_hashes_str})").fetchdf()

        if self.task in ["classification", "multilabel_classification"]:
            res["type"] = "image"

        elif self.task in ["detection", "box_classification", "box_multilabel_classification"]:
            res["type"] = "box"

        elif self.task == "instance_segmentation":
            res["type"] = "mask"

        elif self.task == "keypoints_detection":
            res["type"] = "keypoints"
            structure = self.cursor.execute("select info from extra_info").fetchdf()["info"][0]["structure"]
            res["structure"] = [structure] * len(res)

        self.close_db()

        if not return_dict:
            return res

        fields = [f for f in self.required_fields if f != "image_hash"] + [
            "type",
            "timestamp_z",
            "unique_hash_z",
        ]

        if self.task in ["multilabel_classification", "box_multilabel_classification"] and "category" in res.columns:
            fields.append("category")

        if self.task == "keypoints_detection":
            fields.append("structure")

        res = res.groupby("image_hash", sort=False).apply(lambda obj: obj[fields].to_dict(orient="records")).to_dict()

        return res

    def delete_annotations_of_image_hashes(self, image_hashes: List[str]):
        image_hashes_str = ", ".join([f"'{h}'" for h in image_hashes])

        self.connect_db()

        if self._table_exists("anno"):
            self.cursor.execute(f"delete from anno where image_hash in ({image_hashes_str})")

            if self.serving:
                self.anno_df = self.cursor.execute("select * from anno").fetchdf()

        self.close_db()

    def delete_metas_of_file_names(self, file_names: List[str]):
        file_names_str = ", ".join([f"'{h}'" for h in file_names])

        self.connect_db("meta")

        if self._table_exists("meta"):
            self.cursor.execute(f"delete from meta where file_name in ({file_names_str})")

            if self.serving:
                self.meta_df = self.cursor.execute("select * from meta").fetchdf()

        self.close_db()

    def rename_category(
        self, category: str, new_category: str, at: str = datetime.now().replace(microsecond=0).isoformat()
    ):
        self.connect_db()

        if not self._table_exists("anno"):
            self.close_db()
            return

        # TODO: multilabel classification

        # single label classification
        self.cursor.execute(
            "update anno set category = ?, timestamp_z = ? where category = ?", [new_category, at, category]
        )

        if self.serving:
            self.anno_df = self.cursor.execute("select * from anno").fetchdf()

        self.close_db()

    def _table_exists(self, name: str):
        tables = [tbl[0] for tbl in self.cursor.execute("show tables").fetchall()]
        return name in tables

    def _sanitycheck_fields(self, df: pd.DataFrame):
        columns = df.columns
        for field in self.required_fields:
            if field not in columns:
                raise HTTPException(
                    status_code=400,
                    detail=f"field {field} is required for task: {self.task}",
                )

    def _sanitycheck_file(self, file_path: str):
        suffix = os.path.splitext(file_path)[1][1:]

        if self.task in [
            "classification",
            "box_classification",
            "multilabel_classification",
            "box_multilabel_classification",
            "detection",
        ]:
            if suffix not in ["csv", "parquet"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"{file_path} not in one of the supported formats: csv, parquet",
                )

        elif self.task in ["instance_segmentation", "keypoints_detection"]:
            if suffix not in ["json"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"{file_path} should be in coco json format as required by {self.task} task",
                )

        extra_info = None
        if suffix == "csv":
            df = pd.read_csv(file_path)

        elif suffix == "parquet":
            df = pd.read_parquet(file_path)

        elif suffix == "json":
            # if its json file, it should be in coco format
            coco = json.load(open(file_path, "rb"))
            df, extra_info = coco_to_zity(coco, self.task)

        self._sanitycheck_fields(df)

        return df, extra_info

    def _transform_records(self, records: List[Dict]):
        """based on task, transform records send from frontend:
        for detection, records is in format:
            [{
                image_hash: * ,
                image_width: * ,
                image_height: * ,
                annotations: [{
                    x: * ,
                    y: * ,
                    w: * ,
                    h: * ,
                    category: * ,
                    unique_hash_z: * ,
                    timestamp_z: *
                }, ...]
            }, ...]

        for classification, records is in format:
            [{
                image_hash: * ,
                image_width: * ,
                image_height: * ,
                annotations: {
                    category: * ,
                    unique_hash_z: * ,
                    timestamp_z: *
                }
            }, ...]

        for instance_segmentation, records is in format:
            [{
                image_hash: * ,
                image_width: * ,
                image_height: * ,
                annotations: [{
                    mask: [{
                        closed: * ,
                        hole: * ,
                        points: *
                    }, ...] ,
                    format: * ,
                    category: * ,
                    unique_hash_z: * ,
                    timestamp_z: *
                }, ...]
            }, ...]

        for keypoints_detection, records is in format:
            [{
                image_hash: * ,
                image_width: * ,
                image_height: * ,
                annotations: [{
                    keypoints: * ,
                    category: * ,
                    unique_hash_z: * ,
                    timestamp_z: *
                }, ...]
            }, ...]

        """
        if self.task == "detection":
            records_ = []
            for rec in records:
                iw, ih = rec["image_width"], rec["image_height"]

                for anno in rec["annotations"]:
                    x0 = min(max(0, round(anno["x"])), iw)
                    y0 = min(max(0, round(anno["y"])), ih)
                    x1 = min(max(0, round(anno["x"]) + round(anno["w"]) - 1), iw)
                    y1 = min(max(0, round(anno["y"]) + round(anno["h"]) - 1), ih)
                    records_.append(
                        {
                            "image_hash": rec["image_hash"],
                            "x": x0,
                            "y": y0,
                            "w": x1 - x0 + 1,
                            "h": y1 - y0 + 1,
                            "category": anno["category"],
                            "timestamp_z": anno["timestamp_z"],
                            "unique_hash_z": anno["unique_hash_z"],
                        }
                    )

        else:
            records_ = [anno | {"image_hash": rec["image_hash"]} for rec in records for anno in rec["annotations"]]

        # TODO multilabel classification

        if records_:
            # ensure required fields are present
            for field in self.required_fields:
                if field not in records_[0]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"field {field} is missing in annotation records",
                    )

        return records_
