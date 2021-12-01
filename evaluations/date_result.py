# -*-coding:utf-8-*-

"""
生成实验的数据的指标： acc、tpr、fpr、pre、recall、f1
"""
if __name__ == '__main__':
    tp = 45
    fn = 13
    fp = 18
    tn = 124

    acc = (tp + tn) / (tp + tn + fp + fn)
    tpr = tp / (fn + tp)
    fpr = fp / (fp + tn)

    pre = tp / (tp + fp)
    r = tp / (tp + fn)
    f1 = 2 * pre * r / (pre + r)
    print(acc, tpr, fpr, pre, f1)
