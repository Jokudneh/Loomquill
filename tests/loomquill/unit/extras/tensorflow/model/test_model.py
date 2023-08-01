import tensorflow as tf

from flytekit import task, workflow


@task
def generate_model() -> tf.keras.Model:
    inputs = tf.keras.Input(shape=(32,))
    outputs = tf.keras.layers.Dense(1)(inputs)
    model = tf.keras.Model(inputs, outputs)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss=tf.keras.losses.BinaryCrossentropy(),
        metrics=[
            tf.keras.metrics.BinaryAccuracy(),
        ],
    )
    return model


