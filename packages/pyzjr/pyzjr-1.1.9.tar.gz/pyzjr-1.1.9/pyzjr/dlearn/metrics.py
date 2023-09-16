# Dice系数 Dice Loss
import torch
from torch import nn

def get_onehot(labels, num_classes, dtype=torch.int64):
    """
    one-hot编码过程[b, H, W] -> [b, C, H, W]
    Args:
        label: b,h,w
        num_classes: 分类数
    Returns:
        b,num_classes,h,w
    """
    def to_onehot(label, num_classes):
        return nn.functional.one_hot(label.to(dtype), num_classes)
    N = labels.size(0)
    onehot_labels = []
    for i in range(N):
        onehot = to_onehot(labels[i], num_classes)
        onehot_labels.append(onehot)

    return torch.stack(onehot_labels).permute(0, 3, 1, 2)

def Dice_coeff(pred, true, reduce_batch_first=False, epsilon=1e-6):
    """
    计算预测和目标的Dice系数的平均值
    :param pred: Tensor，预测的分割结果
    :param true: Tensor，真实的分割标签
    :param reduce_batch_first: bool，是否在批次维度上求平均，如果希望在整个批次上获得一个总体的Dice系数，
                               可以设置为 False。如果希望获得每个样本的Dice系数，并根据需要进行进一步的
                               处理，可以设置为 True。
    :param epsilon: float，平滑因子，避免分母为零
    :return: Tensor，Dice系数的平均值
    """
    assert pred.size() == true.size()
    if pred.dim() == 2 and reduce_batch_first:
        raise ValueError(f"Request to reduce batches, but obtain tensors without batch dimensions")
    assert pred.dim() == 3 or not reduce_batch_first

    if pred.dim() == 2 or not reduce_batch_first:
        sum_dim = (-1, -2)
    else:
        sum_dim=(-1, -2, -3)

    inter = 2 * (pred * true).sum(dim=sum_dim)
    sets_sum = pred.sum(dim=sum_dim) + true.sum(dim=sum_dim)
    sets_sum = torch.where(sets_sum == 0, inter, sets_sum)

    dice = (inter + epsilon) / (sets_sum + epsilon)
    return dice.mean()


def multiclass_Dice_coeff(pred, true, reduce_batch_first=False, epsilon=1e-6):
    """
    计算多类别分割任务中所有类别的Dice系数的平均值
    [batch_size, num_classes, h, w] ——> [batch_size * num_classes, h, w]
    :param pred: Tensor，预测的分割结果
    :param true: Tensor，真实的分割标签
    :param reduce_batch_first: bool，是否在批次维度上求平均
    :param epsilon: float，平滑因子，避免分母为零
    :return: Tensor，所有类别的Dice系数的平均值
    """
    return Dice_coeff(pred.flatten(0, 1), true.flatten(0, 1), reduce_batch_first, epsilon)


def Dice_Loss(pred, true, multiclass=False):
    """
    计算Dice损失（目标是最小化），介于0和1之间
    :param pred: Tensor，预测的分割结果
    :param true: Tensor，真实的分割标签
    :param multiclass: bool，是否为多类别分割任务
    :return: Tensor，Dice损失
    """
    diceloss = multiclass_Dice_coeff if multiclass else Dice_coeff
    return 1 - diceloss(pred, true, reduce_batch_first=True)

class ConfusionMatrix(object):
    def __init__(self, num_classes):
        self.num_classes = num_classes
        self.mat = None

    def update(self, t, p):
        n = self.num_classes
        if self.mat is None:
            # 创建混淆矩阵
            self.mat = torch.zeros((n, n), dtype=torch.int64, device=t.device)
        with torch.no_grad():
            # 寻找GT中为目标的像素索引
            k = (t >= 0) & (t < n)
            # 统计像素真实类别t[k]被预测成类别p[k]的个数
            inds = n * t[k].to(torch.int64) + p[k]
            self.mat += torch.bincount(inds, minlength=n**2).reshape(n, n)

    def reset(self):
        if self.mat is not None:
            self.mat.zero_()

    def compute(self):
        """
        计算全局预测准确率(混淆矩阵的对角线为预测正确的个数)
        计算每个类别的准确率
        计算每个类别预测与真实目标的iou,IoU = TP / (TP + FP + FN)
        """
        h = self.mat.float()
        acc_global = torch.diag(h).sum() / h.sum()
        acc = torch.diag(h) / h.sum(1)
        iu = torch.diag(h) / (h.sum(1) + h.sum(0) - torch.diag(h))
        return acc_global, acc, iu

    def __str__(self):
        acc_global, acc, iu = self.compute()
        return (
            'global correct: {:.1f}\n'
            'average row correct: {}\n'
            'IoU: {}\n'
            'mean IoU: {:.1f}').format(
            acc_global.item() * 100,
            ['{:.1f}'.format(i) for i in (acc * 100).tolist()],
            ['{:.1f}'.format(i) for i in (iu * 100).tolist()],
            iu.mean().item() * 100)