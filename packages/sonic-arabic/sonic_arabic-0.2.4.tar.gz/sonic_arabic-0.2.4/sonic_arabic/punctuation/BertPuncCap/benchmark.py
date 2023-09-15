import os
import warnings
import logging
logging.getLogger()
import numpy as np
import pandas as pd
from sklearn import metrics
from collections import Counter
from transformers import BertTokenizer, BertModel
from sklearn.exceptions import UndefinedMetricWarning
warnings.filterwarnings("ignore", category=UndefinedMetricWarning)

from utils import load_file
from model import BertPuncCap
from data_handler import DataHandler


def count_true_labels(punc_true, case_true, class_to_punc, class_to_case):
    punc_counter, case_counter = Counter(), Counter()
    for punc_idx, case_idx in zip(punc_true, case_true):
        punc_counter[class_to_punc[punc_idx]] += 1
        case_counter[class_to_case[case_idx]] += 1
    # put the info in dataframe
    df = pd.DataFrame()
    puncs = list(class_to_punc.values())
    cases = list(class_to_case.values())
    df["Count"] = [punc_counter[token] for token in puncs] \
                + [case_counter[case] for case in cases]
    df.index = puncs + cases
    return df

def evaluation(y_pred, y_test, labels):
    precision, recall, f1, _ = metrics.precision_recall_fscore_support(
        y_test, y_pred, average=None)
    # overall = metrics.precision_recall_fscore_support(
    #     y_test, y_pred, average='macro')
    result = pd.DataFrame(
        np.array([precision, recall, f1]), 
        columns=labels,
        index=['Precision', 'Recall', 'F1']
    )
    # result['OVERALL'] = overall[:3]
    return result

def get_confusion_matrix(y_true, y_pred, headers):
    df = pd.DataFrame(metrics.confusion_matrix(y_true, y_pred), columns=headers)
    df.index = headers
    return df


def main(args):
    # load mBERT from huggingface's transformers package
    BERT_name = "bert-base-multilingual-cased"
    bert_tokenizer = BertTokenizer.from_pretrained(BERT_name)
    bert_model = BertModel.from_pretrained(BERT_name)

    # load trained checkpoint
    bert_punc_cap = BertPuncCap(bert_model, bert_tokenizer, args["ckpt"])
    test_sentences = load_file('data/mTEDx/fr/test.fr')

    # create data handler to handle loaded data
    data_handler = DataHandler(
        bert_tokenizer,
        bert_punc_cap.hparams["segment_size"],
        bert_punc_cap.hparams["punc_to_class"],
        bert_punc_cap.hparams["case_to_class"]
    )
    true_tokens, punc_labels, case_labels = data_handler._flatten(
        *data_handler._extract_tokens_labels(test_sentences)
    )

    # get the labels (punctuations & cases)
    tokens, punc_preds, case_preds = bert_punc_cap._get_labels(test_sentences)

    # sanity checks
    assert true_tokens == tokens
    assert (
        len(punc_labels) == len(punc_preds) \
            == len(case_labels) == len(case_preds)
    )

    # punctuations & cases
    puncs = list(bert_punc_cap.hparams["class_to_punc"].values())
    cases = list(bert_punc_cap.hparams["class_to_case"].values())

    # get F1 scores
    print(evaluation(punc_preds, punc_labels, puncs))
    print()
    print(evaluation(case_preds, case_labels, cases))



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--ckpt', type=str, required=True,
        help='The absolute/relative path where the pre-trained ' + \
            'BertPuncCap is located.')
    parser.add_argument('--in', type=str, required=True,
        help='The absolute/relative path where the ASR reference text ' + \
            'file is located.')

    # parse arguments
    args = vars(parser.parse_args())

    # benchmark
    main(args)
