"""
pred_batch = <tf.Tensor 'pred_batch:0' shape=(None,) dtype=string>
sim = <tf.Tensor 'while/StatefulPartitionedCall:0' shape=<unknown> dtype=float32>
pred_batch[i] = <tf.Tensor 'while/strided_slice_3:0' shape=() dtype=string>

"""

import unicodedata

import numpy as np


COST = {
    "DELETE": 1,
    "INSERT": 1,
    "SUBSTITUTE": 2,
}

def lev(pred:str, gt:str, cost:dict=COST) -> float:
    """
    Levenshtein distance
    """
    m = len(pred)
    n = len(gt)
    # Think of distance_matrix as a (m+1, n+1)-matrix
    distance_matrix = dict()

    distance_matrix[0,0] = 0
    for i in range(1,m+1):
        distance_matrix[i,0] = distance_matrix[i-1,0] + cost["DELETE"]
    for j in range(1,n+1):
        distance_matrix[0,j] = distance_matrix[0,j-1] + cost["INSERT"]

    for i in range(1,m+1):
        for j in range(1,n+1):
            candidates = (
                distance_matrix[i-1, j-1] + (0 if pred[i-1] == gt[j-1] else cost["SUBSTITUTE"]),
                distance_matrix[i-1, j] + cost["DELETE"],
                distance_matrix[i, j-1] + cost["INSERT"],
            )
            distance_matrix[i,j] = min(candidates)

    return distance_matrix[m, n]


def norm_lev(
    pred:str,
    gt:str,
    *,
    form:str="NFD",
    cost:dict=COST,
):
    pred = unicodedata.normalize(form, pred)
    gt = unicodedata.normalize(form, gt)
    return lev(pred, gt, cost)


Batch = list[str]

def batch_lev(
    pred_batch: Batch,
    gt_batch: Batch,
    *,
    form:str="NFD",
    cost:dict=COST,
):
    somme = 0
    for pred, gt in zip(pred_batch, gt_batch):
        somme += norm_lev(pred, gt, form=form, cost=cost)
    avg = somme / len(pred_batch)
    return avg


def sim(
    pred:str,
    gt:str,
    *,
    alpha:float=1/3,
    soft:bool=True,
    proportional:bool=True,
) -> float:
    """
    The idea is that we need this function to return an
    accuracy-like score, in the range of [0, 1],
    to measure the similarity between two strings.

    We have provided two distinct definition for soft similarity,
    controlled by the boolean `proportional`
    """
    if soft:
        dist = lev(pred, gt)
        if proportional:
            proportion = dist / (COST["SUBSTITUTE"]*max(len(gt), 1))
            similarity = 1 - min(1, proportion)
        else:
            if dist > len(gt)*COST["SUBSTITUTE"]:
                # That is, when they are completely different strings
                similarity = 0
            else:
                similarity = 1 / (alpha*dist + 1)
    else:
        # hard similarity is binary: same string or not
        similarity = float(pred == gt)
    return similarity


def norm_sim(
    pred:str,
    gt:str,
    *,
    alpha:float=1/3,
    soft:bool=True,
    proportional:bool=True,
    form:str="NFD",
) -> float:
    pred = unicodedata.normalize(form, pred)
    gt = unicodedata.normalize(form, gt)
    return sim(pred, gt, alpha=alpha, soft=soft, proportional=proportional)


def batch_sim(
    pred_batch: Batch,
    gt_batch: Batch,
    *,
    alpha:float=1/3,
    soft:bool=True,
    proportional:bool=True,
    form:str="NFD",
) -> float:
    somme = 0
    for pred, gt in zip(pred_batch, gt_batch):
        somme += norm_sim(pred, gt, alpha=alpha, soft=soft, proportional=proportional, form=form)
    avg = somme / len(pred_batch)
    return avg


def stdout_batch_sim(
    pred_batch: Batch,
    gt_batch: Batch,
    *,
    alpha:float=1/3,
    soft:bool=True,
    proportional:bool=True,
    form:str="NFD",
    verbose:bool=False,
) -> float:
    if verbose:
        for i, (pred, gt) in enumerate(zip(pred_batch, gt_batch)):
            sim_score = norm_sim(pred, gt)
            print(f"({i = })")
            print(f"{sim_score = :.2f}")
            print(f"{pred = }")
            print(f"{gt = }")
            print()
    avg_sim_score = batch_sim(pred_batch, gt_batch)
    print(f"{avg_sim_score = :.2f}")


if __name__ == "__main__":
    #pred = "Tôi ở Sài Gòn được 6 năm rồi."
    ##gt = "Tôi ở Sài Gòn được 7 năm."
    #gt = "Tôi ở đây chưa lâu."
    #print(f"{pred = }")
    #print(f"{gt = }")
    #d = norm_lev(pred, gt, form="NFKD")
    #print(f"(Python land) {d = }")
    #pred = tf.constant(pred)
    #gt = tf.constant(gt)
    #d = tf_byte_lev(pred, gt)
    #print(f"(TF land)     {d = }")
    #print()
    #proportional_similarity = tf_byte_sim(pred, gt)
    #print(f"(TF land)     {proportional_similarity = }")
    #unproportional_similarity = tf_byte_sim(pred, gt, proportional=tf.constant(False))
    #print(f"(TF land)     {unproportional_similarity = }")
    pred_batch = [
        "Tôi ở Sài Gòn được 6 năm rồi.",
        "Em chưa đi Đà Lạt bao giờ.",
        "Tối nay anh có đi year end party không?",
    ]
    gt_batch = [
        "Toi o Sái Gòn dưoc 6 nam rồi.",
        "Em chua di Dà Lát bao giờ!",
        "Tối nay anh có đi xear ant party không?",
    ]
    stdout_batch_sim(pred_batch, gt_batch, verbose=True)
