import os
import imageio
import numpy as np
import tensorflow as tf
from .utils import *
import cv2


def infer_sesr(image_dir: str, output_dir: str):
    image_paths = [os.path.join(image_dir, x) for x in os.listdir(image_dir)]
    model_path = '../sesr_model/SESR_m5_f16_x2_fs256_collapsedTraining_FP32'
    model = tf.saved_model.load(model_path)

    for image_path in image_paths:
        # RGB to Y
        IMAGE = imageio.imread(image_path, pilmode="RGB")
        IMAGE = tf.convert_to_tensor(IMAGE)
        IMAGE = tf.cast(IMAGE, dtype=tf.float32)
        IMAGE_ycrcb = utils.rgb_to_ycbcr(IMAGE)
        IMAGE_y = IMAGE_ycrcb[..., 0:1] / 255
        IMAGE_cb = IMAGE_ycrcb[..., 1:2]
        IMAGE_cr = IMAGE_ycrcb[..., 2:3]

        out_cb, out_cr = tf.image.resize([IMAGE_cb, IMAGE_cr], method='nearest',
                                         size=[IMAGE_cb.shape[0] * 2, IMAGE_cb.shape[1] * 2])
        # out_cb = cv2.resize(IMAGE_cb, dsize=None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)
        # out_cr = cv2.resize(IMAGE_cr, dsize=None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST)

        IMAGE_y = tf.reshape(IMAGE_y, shape=(1, IMAGE_y.shape[0], IMAGE_y.shape[1], 1))
        # Once the file is in the desired format, just do:
        # Compute the upscaled image for a trained model
        model_out_y = model(IMAGE_y)
        # model_out_y.shape=(1, 532, 1172, 1), dtype=float32
        # print(model_out_y)
        model_out_y = model_out_y[0] * 255
        output = tf.concat([model_out_y, out_cb, out_cr], axis=2)

        IMAGE_rgb = utils.ycbcr_to_rgb(output)
        IMAGE_bgr = cv2.cvtColor(np.asarray(IMAGE_rgb), cv2.COLOR_RGB2BGR)
        sesr_img_path = 'sesr_' + os.path.basename(image_path)
        cv2.imwrite(os.path.join(output_dir, sesr_img_path), IMAGE_bgr)

        # # 这一步转换张量数据类型很重要
        # IMAGE_rgb = tf.cast(IMAGE_rgb, dtype=tf.uint8)
        #
        # # 编码回图片
        # img = tf.image.encode_png(IMAGE_rgb)
        # # 保存
        # with tf.io.gfile.GFile('HOK_SESR/result.png', 'wb') as file:
        #     file.write(img.numpy())
        #
