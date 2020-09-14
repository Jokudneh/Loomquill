from typing import Dict, Tuple

import numpy as np
import tensorflow as tf
from tensorflow.python.data.ops.readers import TFRecordDatasetV2
from typing_extensions import Annotated

from flytekit import task, workflow
from flytekit.extras.tensorflow.record import TFRecordDatasetConfig
from flytekit.types.directory import TFRecordsDirectory
from flytekit.types.file import TFRecordFile

a = tf.train.Feature(bytes_list=tf.train.BytesList(value=[b"foo", b"bar"]))
b = tf.train.Feature(float_list=tf.train.FloatList(value=[1.0, 2.0]))
c = tf.train.Feature(int64_list=tf.train.Int64List(value=[3, 4]))
d = tf.train.Feature(bytes_list=tf.train.BytesList(value=[b"ham", b"spam"]))
e = tf.train.Feature(float_list=tf.train.FloatList(value=[8.0, 9.0]))
f = tf.train.Feature(int64_list=tf.train.Int64List(value=[22, 23]))
features1 = tf.train.Features(feature=dict(a=a, b=b, c=c))
features2 = tf.train.Features(feature=dict(a=d, b=e, c=f))


def decode_fn(dataset: TFRecordDatasetV2) -> Dict[str, np.ndarray]:
    examples_list = []
    # parse serialised tensors https://www.tensorflow.org/tutorials/load_data/tfrecord#reading_a_tfrecord_file_2
    for batch in list(dataset.as_numpy_iterator()):
