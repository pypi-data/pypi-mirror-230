import tensorflow as tf
from tensorflow import keras
import os
import datetime
import random


def create_model_checkpoint(
    model_name,
    save_dir,
    monitor: str = "val_loss",
    verbose: int = 0,
    save_best_only: bool = True,
    save_weights_only: bool = False,
    mode: str = "auto",
    save_freq="epoch",
    options=None,
    initial_value_threshold=None,
    **kwargs,
):
    """
    Creates a ModelCheckpoint callback instand to store model weights.
    Stores model weights with the filepath:
    "save_dir/model_name-{str(datetime.datetime.now())}"

    Args
    ###########################################
    model_name: name of model directory (e.g. efficientnet_model_1)

    save_dir: target directory to store model weights

    monitor: metric to monitor

    verbose: verbosity mode

    save_best_only: if True, only save the model if `monitor` has improved.

    save_weights_only: if True, then only the model's weights will be saved

    mode: one of {auto, min, max}. In `min` mode, the model will be minimized
        by the quantity monitored, in `max` mode the model will be maximized
        (by the quantity monitored). In `auto` mode, the direction is
        automatically inferred from the name of the monitored quantity.

    save_freq: one of {epoch, batch}. In `epoch` mode, the callback saves the
    """
    model_name = f"{model_name}-{str(datetime.datetime.now())}"
    directory = os.path.join(save_dir, model_name)

    if not os.path.exists(directory):
        os.makedirs(directory)

    return tf.keras.callbacks.ModelCheckpoint(
        directory,
        monitor=monitor,
        verbose=verbose,
        save_best_only=save_best_only,
        save_weights_only=save_weights_only,
        mode=mode,
        save_freq=save_freq,
        options=options,
        initial_value_threshold=initial_value_threshold,
        **kwargs,
    )


def create_tensorboard_callback(dir_name, experiment_name):
    """
    Creates a TensorBoard callback instand to store log files.
    Stores log files with the filepath:
    "dir_name/experiment_name/current_datetime/"

    Args
    ###########################################
    dir_name: target directory to store TensorBoard log files
    experiment_name: name of experiment directory (e.g. efficientnet_model_1)

    Returns
    ##########################################
    A tensorboard callback
    """
    log_dir = f"{dir_name}/{experiment_name}/" + datetime.datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir)
    print(f"Saving TensorBoard log files to: {log_dir}")
    return tensorboard_callback


class DisplayCallback(tf.keras.callbacks.Callback):
    """
    Prints model prediction and true values for dataset specified

    Args
    ###########################################
    print_on_epoch:int : after how many epochs you want to print the results
    x:np.array  : input dataset (np.array)
    y:np.array  : output dataset (np.array)

    Returns
    ##########################################
    A Display callback

    """

    def __init__(self, print_on_epoch: int, x: np.array, y: np.array):
        self.print_on_epoch = print_on_epoch
        self.x = x
        self.y = y

    def predict(self):
        ypred = tf.squeeze(model.predict(self.x))
        print("ypred: ", ypred[0].numpy().astype("int"), "\nytrue: ", self.y[0])

    def on_epoch_end(self, epoch, logs=None):
        if epoch % self.print_on_epoch == 0:
            return self.predict()


def main():
    ...


if __name__ == "__main__":
    main()
