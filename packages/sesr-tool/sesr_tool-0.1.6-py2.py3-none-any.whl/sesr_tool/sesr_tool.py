"""Main module."""
from .infer_sr import infer_sesr


def infer(image_dir, output_dir):
    try:
        infer_sesr(image_dir, output_dir)  # 缺少参数age
    except TypeError as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    infer('LR', 'SR')
