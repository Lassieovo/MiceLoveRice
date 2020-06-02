import matplotlib.pyplot as plt

from helpers.util import DEBUG, INFO, WARN, ERROR

__all__ = [
    "plot_history_mae_mse",
    "plot_history_by_metrics",
    "plot_image_mat",
    "plot_images",
    "load_image_mat",
    "save_image_mat",
]


_default_cell_size = (200, 200)
_default_facecolor = "#999999"


# origin: TF_1x_to_2x_7
def plot_history_mae_mse(history):
    import pandas as pd

    hist = pd.DataFrame(history.history)
    hist['epoch'] = history.epoch

    plt.figure('MAE --- MSE', figsize=(8, 4))

    plt.subplot(1, 2, 1)
    plt.xlabel('Epoch')
    plt.ylabel('Mean Abs Error [MPG]')
    plt.plot(
        hist['epoch'], hist['mae'],
        label='Train Error')
    plt.plot(
        hist['epoch'], hist['val_mae'],
        label='Val Error')
    plt.ylim([0, 5])
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.xlabel('Epoch')
    plt.ylabel('Mean Square Error [$MPG^2$]')
    plt.plot(
        hist['epoch'], hist['mse'],
        label='Train Error')
    plt.plot(
        hist['epoch'], hist['val_mse'],
        label='Val Error')
    plt.ylim([0, 20])
    plt.legend()

    plt.show()


# origin: tensorflow.org/tutorials/structured_data/imbalanced_data#check_training_history
def plot_history_by_metrics(history, metrics=None):
    if metrics is None:
        metrics = ['loss', 'acc', 'precision', 'recall']
    for n, metric in enumerate(metrics):
        if history.history.get(metric, None) is None:
            continue
        name = metric.replace("_", " ").capitalize()
        plt.subplot(2, 2, n + 1)
        plt.plot(history.epoch, history.history[metric], label='Train')  # 原文:color=colors[0]?
        if history.history.get('val_' + metric, None) is not None:
            plt.plot(history.epoch, history.history['val_' + metric], linestyle="--",
                     label='Val')  # 原文:color=colors[0]?
        plt.xlabel('Epoch')
        plt.ylabel(name)
        if metric == 'loss':
            plt.ylim([0, plt.ylim()[1]])
        elif metric == 'auc':
            plt.ylim([0.8, 1])
        else:
            plt.ylim([0, 1])

        plt.legend()
    plt.show()


def plot_image_mat(image_mat, text=None, title=None, cell_size: tuple = None, block=None):
    import numpy as np
    if not isinstance(image_mat, np.ndarray):
        raise TypeError(f"image must be a numpy array, instead of a {type(image_mat).__name__}")

    # NOTE: matplot can only deal with channel=3, 4 or n/a(grayscale). TF-styled image_mats need to be reshaped
    if image_mat.ndim == 3 and image_mat.shape[-1] == 1:
        image_mat = np.reshape(image_mat, image_mat.shape[:-1])

    dpi = 100  # IMPROVE: get default value from `figure.dpi`
    if cell_size is None:
        cell_size = _default_cell_size
    plt.figure(title, figsize=(int(cell_size[0]/dpi), int(cell_size[1]/dpi)),
               facecolor=_default_facecolor)
    # -- plot a single image ---------------
    plt.grid(False)
    plt.xticks([])
    plt.yticks([])
    plt.imshow(image_mat)
    if text is not None:
        plt.xlabel(text)
    # TODO: try interactive mode of matplot
    plt.show(block=block)

def plot_images(images, texts=None, title=None, num_rows=None, num_cols=None, cell_size: tuple = None, block=None):
    """
    :param images: list of ndarrays. dtype is int, 0-255, can be directly rendered
    :param texts:
    :param title: title of the figure, if omitted an auto-inc number will be used
    :param num_rows: if None, will be auto calculated
    :param num_cols: if None, will be auto calculated
    :param cell_size: (w, h) of each cell, in pixel
    :param block: experimental, block or not
    :return:
    """
    import numpy as np
    if not any([isinstance(images, _) for _ in (list, np.ndarray)]):
        raise TypeError(f"images must be a list or numpy array")
    if len(images) == 0:
        raise ValueError(f"images cannot be blank")
    if texts is not None and not any([isinstance(texts, _) for _ in (list, np.ndarray)]):
        raise TypeError(f"texts must be a list or numpy array")
    if texts is not None and len(texts) != len(images):
        raise ValueError(f"texts(len={len(texts)}) ought to have the same size of images(len={len(images)})")

    num_images = len(images)
    if num_rows is None and num_cols is None:
        num_cols = int(np.sqrt(num_images * 16 / 9))
        num_rows = int(np.ceil(num_images / num_cols))
        # NOTE: assume (h, w) are same across the images
        h, w = images[0].shape[:2]
    elif num_rows is None or num_cols is None:
        raise NotImplementedError("num_rows is None or num_cols is None")

    # NOTE: matplot can only deal with channel=3, 4 or n/a(grayscale). TF-styled image_mats need to be reshaped
    if images[0].ndim == 3 and images[0].shape[-1] == 1:
        images = np.reshape(images, (-1, *images[0].shape[:-1]))

    dpi = 100  # IMPROVE: get default value from `figure.dpi`
    if cell_size is None:
        cell_size = _default_cell_size
    plt.figure(title, figsize=(num_cols * int(cell_size[0]/dpi), num_rows * int(cell_size[1]/dpi)),
               facecolor=_default_facecolor)
    for i in range(min(num_images, num_rows*num_cols)):
        plt.subplot(num_rows, num_cols, i + 1)
        # -- plot a single image ---------------
        plt.grid(False)
        plt.xticks([])
        plt.yticks([])
        plt.imshow(images[i])
        if texts is not None:
            plt.xlabel(texts[i])
    # TODO: try interactive mode of matplot
    plt.show(block=block)

def load_image_mat(image_path, format_=None):
    import numpy as np
    image_mat = plt.imread(image_path, format_)
    if isinstance(image_mat, np.ndarray) and image_mat.shape.__len__() == 2:
        image_mat = np.expand_dims(image_mat, axis=-1)
    return image_mat

def save_image_mat(image_mat, image_path, **kwargs):
    """
    :param image_mat: array-alike. shape can be one of MxN, MxNx1 (luminance), MxNx3 (RGB) or MxNx4 (RGBA).
    :param image_path: file extension determines imagee format to be saved
    :param kwargs: compatible with plt.imsave()
    :return:
    """
    import numpy as np
    if isinstance(image_mat, np.ndarray) and image_mat.shape.__len__() == 3 and image_mat.shape[-1] == 1:
        image_mat = np.reshape(image_mat, image_mat.shape[:-1])
    plt.imsave(image_path, image_mat, **kwargs)
