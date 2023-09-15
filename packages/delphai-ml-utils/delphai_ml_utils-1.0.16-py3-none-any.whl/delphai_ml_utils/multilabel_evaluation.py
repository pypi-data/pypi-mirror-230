import math
from mlcm import mlcm
import pandas as pd


def one_hot_encoding(data, labels_in_order):
    one_hot_encode = []
    for line in data:
        temp = []
        for label in labels_in_order:
            if label in line:
                temp.append(1)
            else:
                temp.append(0)
        one_hot_encode.append(temp)
    return one_hot_encode


def count_error_types(correct, predict, labels_in_order):
    label_error_map = {}
    for x, label in enumerate(labels_in_order):
        temp = {"TP": 0, "TN": 0, "FP": 0, "FN": 0}
        for (cor, pre) in zip(correct, predict):
            if cor[x] == pre[x]:
                if cor[x]:
                    temp["TP"] += 1
                else:
                    temp["TN"] += 1
            else:
                if cor[x]:
                    temp["FN"] += 1
                else:
                    temp["FP"] += 1

        label_error_map[label] = temp
    return label_error_map


def calculate_supports(true_labels_encoded, labels_in_order):
    supports_count = {key: 0 for key in labels_in_order}
    for item in true_labels_encoded:
        for (label_name, label) in zip(labels_in_order, item):
            if label:
                supports_count[label_name] = supports_count[label_name] + 1

    return supports_count


def calculate_metrics(
    label_error_map, supports_count
):  # include average type e.g. micro/macro/binary/weighted etc
    def accuracy(TP, TN, FP, FN):
        try:
            return (TP + TN) / (TP + TN + FP + FN)
        except:
            return 0

    def precision(TP, TN, FP, FN):
        try:
            return TP / (TP + FP)
        except:
            return 0

    def recall(TP, TN, FP, FN):
        try:
            return TP / (TP + FN)
        except:
            return 0

    def f1(precision, recall):
        try:
            return 2 * (precision * recall) / (precision + recall)
        except:
            return 0

    def f0_5(precision, recall):
        try:
            return (1.25 * precision * recall) / (0.25 * precision + recall)
        except:
            return 0

    result = {}
    for label in label_error_map.keys():
        matrics_map = {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0, "f0.5": 0}
        error_map = label_error_map[label]

        for error in matrics_map.keys():
            if error == "accuracy":
                matrics_map["accuracy"] = accuracy(
                    error_map["TP"], error_map["TN"], error_map["FP"], error_map["FN"]
                )
            if error == "precision":
                matrics_map["precision"] = precision(
                    error_map["TP"], error_map["TN"], error_map["FP"], error_map["FN"]
                )
            if error == "recall":
                matrics_map["recall"] = recall(
                    error_map["TP"], error_map["TN"], error_map["FP"], error_map["FN"]
                )
            if error == "f1":
                matrics_map["f1"] = f1(matrics_map["precision"], matrics_map["recall"])
            if error == "f0.5":
                matrics_map["f0.5"] = f0_5(
                    matrics_map["precision"], matrics_map["recall"]
                )

        # for error in matrics_map.keys():
        #     matrics_map[error] = math.floor(matrics_map[error] * 1000) / 1000

        result[label] = matrics_map

    average_map = {"accuracy": [], "precision": [], "recall": [], "f1": [], "f0.5": []}
    for key in result.keys():
        for type_ in average_map.keys():
            average_map[type_].append(result[key][type_])
    for type_ in average_map.keys():
        global_scores_ = sum(average_map[type_]) / len(average_map[type_])
        # global_scores_ = math.floor(global_scores_ * 1000) / 1000
        average_map[type_] = global_scores_
    result["average"] = average_map

    weighted_map = {"accuracy": [], "precision": [], "recall": [], "f1": [], "f0.5": []}
    for type_ in matrics_map.keys():
        scores = []
        for label in label_error_map.keys():
            scores.append(result[label][type_])
        global_scores_ = sum(
            [
                (score * support)
                for (score, support) in zip(scores, supports_count.values())
            ]
        ) / sum(supports_count.values())
        # global_scores_ = math.floor(global_scores_ * 1000) / 1000
        weighted_map[type_] = global_scores_
    result["weighted_average"] = weighted_map

    return result


# This is useful when you have annotations and classification that dont fall in to any label.
def get_conf_matrix(correct, predict, labels_in_order, normalized=False):
    conf_mat, normalized_conf_mat = mlcm.cm(correct, predict, False)
    if normalized:
        conf_mat = normalized_conf_mat
    conf_matrix_df = pd.DataFrame(
        conf_mat, columns=labels_in_order + ["NLP"], index=labels_in_order + ["NTL"]
    )
    return conf_matrix_df


def get_classification_report(correct, predict):
    conf_mat, _ = mlcm.cm(correct, predict, False)
    one_vs_rest = mlcm.stats(conf_mat, False)
    return one_vs_rest
