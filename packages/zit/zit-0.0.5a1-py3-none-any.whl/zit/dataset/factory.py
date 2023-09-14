from .build import DatasetBuilderTemplate


class DatasetFactory:
    _REGISTERED = {}

    @staticmethod
    def register(dataset_type, builder):
        DatasetFactory._REGISTERED[dataset_type] = builder

    @staticmethod
    def get(dataset_type, **kwargs):
        builder = DatasetFactory._REGISTERED.get(dataset_type)
        if not builder:
            raise KeyError(f"dataset type {dataset_type} not supported or registered!")

        return builder(**kwargs)


DatasetFactory.register("detection", DatasetBuilderTemplate("detection"))
DatasetFactory.register("classification", DatasetBuilderTemplate("classification"))
DatasetFactory.register("box_classification", DatasetBuilderTemplate("box_classification"))
DatasetFactory.register("multilabel_classification", DatasetBuilderTemplate("multilabel_classification"))
DatasetFactory.register("box_multilabel_classification", DatasetBuilderTemplate("box_multilabel_classification"))
DatasetFactory.register("instance_segmentation", DatasetBuilderTemplate("instance_segmentation"))
DatasetFactory.register("keypoints_detection", DatasetBuilderTemplate("keypoints_detection"))
