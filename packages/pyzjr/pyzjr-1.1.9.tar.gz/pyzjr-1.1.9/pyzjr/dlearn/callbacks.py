import os
import csv
import matplotlib
import torch
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import scipy.signal
from torch.utils.tensorboard import SummaryWriter
import numpy as np
import pandas as pd

from collections import defaultdict, deque
import torch.distributed as dist
import time
import datetime

class LossHistory():
    def __init__(self, log_dir, model, input_shape):
        self.log_dir = log_dir
        self.losses = []
        self.val_loss = []

        os.makedirs(self.log_dir,exist_ok=True)
        self.writer = SummaryWriter(self.log_dir)
        try:
            dummy_input = torch.randn(2, 3, input_shape[0], input_shape[1])
            self.writer.add_graph(model, dummy_input)
        except:
            pass

    def append_loss(self, epoch, loss, val_loss):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.losses.append(loss)
        self.val_loss.append(val_loss)

        with open(os.path.join(self.log_dir, "epoch_loss.txt"), 'a') as f:
            f.write(str(loss))
            f.write("\n")
        with open(os.path.join(self.log_dir, "epoch_val_loss.txt"), 'a') as f:
            f.write(str(val_loss))
            f.write("\n")

        self.writer.add_scalar('loss', loss, epoch)
        self.writer.add_scalar('val_loss', val_loss, epoch)
        self.loss_plot()

    def loss_plot(self):
        iters = range(len(self.losses))

        plt.figure()
        plt.plot(iters, self.losses, 'red', linewidth = 2, label='train loss')
        plt.plot(iters, self.val_loss, 'coral', linewidth = 2, label='val loss')
        # plt.plot(iters, [loss.item() for loss in self.losses], 'red', linewidth=2, label='train loss')
        # plt.plot(iters, [loss.item() for loss in self.val_loss], 'coral', linewidth=2, label='val loss')
        try:
            if len(self.losses) < 25:
                num = 5
            else:
                num = 15

            plt.plot(iters, scipy.signal.savgol_filter(self.losses, num, 3), 'green', linestyle = '--', linewidth = 2, label='smooth train loss')
            plt.plot(iters, scipy.signal.savgol_filter(self.val_loss, num, 3), '#8B4513', linestyle = '--', linewidth = 2, label='smooth val loss')
        except:
            pass

        plt.grid(True)
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend(loc="upper right")

        plt.savefig(os.path.join(self.log_dir, "epoch_loss.png"))

        plt.cla()
        plt.close("all")


def CsvHistory(header, value, log_dir, savefile_name):
    """Export data to CSV format
    Args:
        header (list): 列的标题,例如：['epoch', 'train loss', 'train acc', 'val loss', 'val acc']
        value (list): 对应列的值
        log_dir (str): 文件夹路径
        savefile_name (str): 文件名（包括路径）
    """
    os.makedirs(log_dir,exist_ok=True)
    file_existence = os.path.isfile(savefile_name)

    if not file_existence:
        with open(savefile_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerow(value)
    else:
        with open(savefile_name, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(value)

def plotloss(csvfile):
    '''
    Args
        csvfile: name of the csv file
    Returns
        graph_loss: trend of loss values over epoch
    '''
    loss_values = pd.read_csv(csvfile)

    # Initiation
    epoch = loss_values.iloc[:, 0]
    tr_loss = loss_values.iloc[:, 1]
    tr_acc = loss_values.iloc[:, 2]
    val_loss = np.asarray(loss_values.iloc[:, 3])
    val_acc = np.asarray(loss_values.iloc[:, 4])

    # Reduce the volume of data
    epoch_skip = epoch[::5]
    tr_loss_skip = tr_loss[::5]
    tr_acc_skip = tr_acc[::5]
    val_loss_skip = val_loss[::5]
    val_acc_skip = val_acc[::5]

    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax2 = ax1.twinx()

    # Label and color the axes
    ax1.set_xlabel('Epoch', fontsize=16)
    ax1.set_ylabel('Loss', fontsize=16, color='black')
    ax2.set_ylabel('Accuracy', fontsize=16, color='black')

    # Plot valid/train losses
    ax1.plot(epoch_skip, tr_loss_skip, linewidth=2,
             ls='--', color='#c92508', label='Train loss')
    ax1.plot(epoch_skip, val_loss_skip, linewidth=2,
             color='#c92508', label='Validation loss')
    ax1.spines['left'].set_color('#f23d1d')
    # Coloring the ticks
    for label in ax1.get_yticklabels():
        label.set_color('#c92508')
        label.set_size(12)

    # Plot valid/trian accuracy
    ax2.plot(epoch_skip, tr_acc_skip, linewidth=2, ls='--',
             color='#2348ff', label='Train Accuracy')
    ax2.plot(epoch_skip, val_acc_skip, linewidth=2,
             color='#2348ff', label='Validation Accuracy')
    ax2.spines['right'].set_color('#2348ff')
    # Coloring the ticks
    for label in ax2.get_yticklabels():
        label.set_color('#2348ff')
        label.set_size(12)

    # Manually setting the y-axis ticks
    yticks = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    ax1.set_yticks(yticks)
    ax2.set_yticks(yticks)

    for label in ax1.get_xticklabels():
        label.set_size(12)

    # Modification of the overall graph
    fig.legend(ncol=4, loc=9, fontsize=12)
    plt.xlim(xmin=0)
    ax2.set_ylim(ymax=1, ymin=0)
    ax1.set_ylim(ymax=1, ymin=0)
    plt.xlabel('epochs')
    plt.title("Adam optimizer", weight="bold")
    plt.grid(True, axis='y')

    # return train_loss, valid_loss

class SmoothedValue(object):
    """Track a series of values and provide access to smoothed values over a
    window or the global series average.
    """
    def __init__(self, window_size=20, fmt=None):
        if fmt is None:
            fmt = "{value:.4f} ({global_avg:.4f})"
        self.deque = deque(maxlen=window_size)
        self.total = 0.0
        self.count = 0
        self.fmt = fmt

    def update(self, value, n=1):
        self.deque.append(value)
        self.count += n
        self.total += value * n

    @property
    def median(self):
        d = torch.tensor(list(self.deque))
        return d.median().item()

    @property
    def avg(self):
        d = torch.tensor(list(self.deque), dtype=torch.float32)
        return d.mean().item()

    @property
    def global_avg(self):
        return self.total / self.count

    @property
    def max(self):
        return max(self.deque)

    @property
    def value(self):
        return self.deque[-1]

    def __str__(self):
        return self.fmt.format(
            median=self.median,
            avg=self.avg,
            global_avg=self.global_avg,
            max=self.max,
            value=self.value)


def save_models(model, epoch, save_dir, save_period = 10):
    """Save model to given path
    Args:
        model: model to be saved
        save_dir: path that the model would be saved
        epoch: the epoch the model finished training
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    if epoch % save_period == 0:
        torch.save(model.state_dict(),os.path.join(save_dir, f"model_epoch_{epoch}.pth"))
