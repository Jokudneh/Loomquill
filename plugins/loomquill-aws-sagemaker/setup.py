from setuptools import setup

PLUGIN_NAME = "awssagemaker"
INFERENCE_PACKAGE = "awssagemaker_inference"
TRAINING_PACKAGE = "awssagemaker_training"
BATCH_TRANSFORM_PACKAGE = "awssagemaker_batch_transform"
INFERENCE_RECOMMENDER_PACKAGE = "awssagemaker_inference_recommender"
HYPERPARAMETER_TUNING_PACKAGE = "awssagemaker_hyperparameter_tuning"
PROCESSING_PACKAGE = "awssagemaker_processing"

microlib_name = f"flytekitplugins-{PLUGIN_NAME}"

plugin_requires = ["flytekit>1.14.6", "aioboto3>=12.3.0", "xxhash"]
