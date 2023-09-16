import matplotlib as mpl
import tensorflow as tf


def create_bert(trainable=False):
    import tensorflow_hub as hub

    text_input = tf.keras.layers.Input(shape=(), dtype=tf.string)
    preprocessor = hub.KerasLayer(
        "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3"
    )
    encoder_inputs = preprocessor(text_input)
    encoder = hub.KerasLayer(
        "https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-12_H-128_A-2/2",
        trainable=trainable,
    )
    outputs = encoder(encoder_inputs)
    pooled_output = outputs["pooled_output"]
    sequence_output = outputs["sequence_output"]
    embedding_model = tf.keras.Model(text_input, pooled_output)
    return embedding_model


if __name__ == "__main__":
    print("hello")
