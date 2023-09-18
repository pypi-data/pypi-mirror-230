import tensorflow as tf
import infer_sr


def test_sesr():
    model_path = 'SESR_m5_f16_x2_fs256_collapsedTraining_FP32'
    model = tf.saved_model.load(model_path)
    infer.infer_sesr(model)

