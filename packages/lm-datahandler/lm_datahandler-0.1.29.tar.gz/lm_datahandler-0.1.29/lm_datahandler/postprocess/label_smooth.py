import numpy as np
import torch


def pp_probability_smooth(probability, padding=2):
    sample_size = probability.shape[0]
    padding_unit = [0, 0, 0, 0]
    for i in range(padding):
        probability = np.insert(probability, 0, padding_unit)
        probability = np.append(probability, padding_unit)
    # output_extend = np.append(output_extend, [[0, 0, 0, 0], [0, 0, 0, 0]])
    output_extend = probability.reshape([sample_size + padding * 2, 4])
    for j in range(2, sample_size + 2):
        output_extend[j] = (output_extend[j - 2] + output_extend[j - 1] + output_extend[j] + output_extend[
            j + 1] + output_extend[j + 2]) / 5

    predictions = torch.from_numpy(output_extend[2:sample_size + 2]).max(axis=1, keepdim=True)[1].numpy()
    return predictions


def pp_label_smooth(labels, window=10):
    if labels.shape[0] < window:
        return labels

    first_index = 0
    first_label = labels[first_index]
    for i in range(0, labels.shape[0]):
        if labels[i] != first_label:
            # first_label = labels[i]
            first_index = i
            break
        first_index += 1

    last_index = labels.shape[0] - 1
    last_label = labels[last_index]
    for i in range(labels.shape[0] - 1, -1, -1):
        if labels[i] != last_label:
            last_label = labels[i]
            last_index = i
            break
        last_index -= 1

    if last_index <= first_index:
        return labels

    count = 0
    pre_label = labels[first_index]
    pre_index = first_index
    for i in range(first_index, last_index + 2):
        if labels[i] == pre_label:
            count += 1
        else:
            if count < window:
                labels[pre_index:i] = -1
            count = 1
            pre_label = labels[i]
            pre_index = i

    pre_label = first_label
    for i in range(first_index, last_index + 1):
        if labels[i] == -1:
            j = i
            while labels[j] == -1:
                j += 1
            post_label = labels[j]
            if pre_label == post_label:
                labels[i:j] = pre_label
            else:
                labels[i:(i + j) // 2] = pre_label
                labels[(i + j) // 2: j] = post_label
        else:
            pre_label = labels[i]
    return labels


