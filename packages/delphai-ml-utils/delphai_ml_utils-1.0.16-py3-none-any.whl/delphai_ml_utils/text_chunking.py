import numpy as np
import torch


"""
For tokenizing long texts into the chunks (function tokenize_with_chunks)
tutorial used - https://www.kaggle.com/code/datajameson/long-text-sentiment-classification-bert-windowing/notebook

Example how to get predicted labels from probabilities of every text chunk 
in case of multilabel classification - function get_predictions
"""


def make_chunks(tokens: dict, chunksize=512, bos=0, eos=2, pad=1):
    """
    Make chunks of tokenized and encoded text
       input:
            tokens - dictionary, which is output of the tokenizer with no max_length limits
            chunksize - length of the chunk in tokens
            bos, eos, pad - special tokens encodings

       output: chunks of token ids and attention masks
    """

    # split into chunks of 510 tokens, we also convert to list (default is tuple which is immutable)
    input_id_chunks = list(tokens["input_ids"][0].split(chunksize - 2))
    mask_chunks = list(tokens["attention_mask"][0].split(chunksize - 2))

    # loop through each chunk
    for i in range(len(input_id_chunks)):
        # add BOS and EOS tokens to input IDs
        input_id_chunks[i] = torch.cat(
            [
                torch.tensor([bos], dtype=torch.long),
                input_id_chunks[i],
                torch.tensor([eos], dtype=torch.long),
            ]
        )
        # add attention for special tokens to the attention mask
        mask_chunks[i] = torch.cat(
            [torch.tensor([1]), mask_chunks[i], torch.tensor([1])]
        )
        # get required padding length
        pad_len = chunksize - input_id_chunks[i].shape[0]

        # check if tensor length satisfies required chunk size
        if pad_len > 0:
            # check if tensor length is more than 0, we must add padding
            input_id_chunks[i] = torch.cat(
                [input_id_chunks[i], torch.tensor([pad] * pad_len, dtype=torch.long)]
            )
            mask_chunks[i] = torch.cat(
                [mask_chunks[i], torch.tensor([0] * pad_len, dtype=torch.long)]
            )
    return torch.stack(input_id_chunks), torch.stack(mask_chunks)


def tokenize_with_chunks(tokenizer, texts, chunksize=512):
    """Tokenizing long texts into the chunks"""

    # IDs of special tokens
    if tokenizer.bos_token_id:
        bos = tokenizer.bos_token_id
    else:
        bos = tokenizer.cls_token_id  # bert-like models use CLS and SEP tokens
    if tokenizer.eos_token_id:
        eos = tokenizer.eos_token_id
    else:
        eos = tokenizer.sep_token_id
    pad = tokenizer.pad_token_id

    texts_indices = list()
    input_ids = list()
    attention_mask = list()

    for ind, text in enumerate(texts):
        # tokenize the text. No max_length limits, no special tokens
        tokens = tokenizer.encode_plus(
            text, add_special_tokens=False, return_tensors="pt"
        )
        # make chunks
        input_ids_, attention_mask_ = make_chunks(tokens, chunksize, bos, eos, pad)
        # save index of the text
        texts_indices.extend([ind] * input_ids_.shape[0])
        # append chunks to the list
        input_ids.append(input_ids_)
        attention_mask.append(attention_mask_)

    # stack token IDs and attention masks into tensors with the shape (number_of_chunks, chunksize)
    input_ids = torch.vstack(input_ids)
    attention_mask = torch.vstack(attention_mask)

    return input_ids, attention_mask, texts_indices


def get_text_labels(probs, idx2label, threshold):
    """
    Convert probabilities into labels for every chunk of the single news article's text.

    input:
        probs - 2D numpy array or list of lists with probabilties;
        idx2label - dictionary, index to label map;
        threshold - float, threshold for cutting the probabilities.

    output: list of lists of labels.
    """

    # make list of lists of booleans from probablities using threshold
    # we may consider the list of booleans as a one-hot vector (True=1 and False=0)
    bool_predictions = [[p >= threshold for p in prob] for prob in probs]

    # list with text predictions
    str_predictions = list()

    # loop over one-hot vectors in the list
    for pred in bool_predictions:
        # list with chunk predictions
        str_pred = list()
        # get indices where value in one-hot vector is not zero
        inds = np.argwhere(pred)
        # for every index (this is an idx of a label)...
        for ind in inds:
            # ... map it into a label and append string to the list of chunk predictions
            str_pred.append(idx2label[ind[0]])
        # store predicted labels of a chunk in a list
        str_predictions.append(str_pred)

    return str_predictions


def get_predictions(
    probabilities, idx2label, texts_indices, unique=False, threshold=0.5
):
    """
    Agregate predictions from probabilities into either list of lists of labels
    or list of unique labels.
    If argument `unique` is True only unique labels for the whole text are returned.
    If argument `unique` is False labels for every chunk of the text are returned.

    idx2label - dictionary, mapping of label's IDs into strings
    texts_indices - list, indicates index of the text in the dataset for every it's chunk
    """

    predictions = list()
    # get start indices and counts of chunks for texts
    _, indx, counts = np.unique(texts_indices, return_index=True, return_counts=True)

    end = 0

    for start, count in zip(indx, counts):
        end += count
        # slice probabilites so we get all chunks of the text together
        probs = probabilities[start:end]
        str_preds = get_text_labels(probs, idx2label, threshold)

        if unique:
            # flatten the list of lists
            str_preds = [lbl for lst in str_preds for lbl in lst]
            # get unique labels for the whole text
            str_preds = np.unique(str_preds).tolist()

        predictions.append(str_preds)

    return predictions
