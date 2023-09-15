from model import BertPuncCap
from transformers import BertTokenizer, BertModel

def load_file(filename):
    """reads text file where sentences are separated by newlines."""
    with open(filename, 'r', encoding='utf-8') as f:
        data = [line.strip() for line in f.readlines()]
    return data


def main(args):
    # load mBERT from huggingface's transformers package
    BERT_name = "bert-base-multilingual-cased"
    bert_tokenizer = BertTokenizer.from_pretrained(BERT_name)
    bert_model = BertModel.from_pretrained(BERT_name)

    # load trained checkpoint
    bert_punc_cap = BertPuncCap(bert_model, bert_tokenizer, args["ckpt"])

    # read ASR output transcriptions
    with open(args["in"]) as fin:
        x = fin.readlines()
    
    # re-punctuate & re-capitalize
    results = bert_punc_cap.predict(x)

    # write results to an output file
    with open(args["out"], 'w') as fout:
        fout.writelines([res+'\n' for res in results])


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--ckpt', type=str, required=True,
        help='The absolute/relative path where the pre-trained ' + \
            'BertPuncCap is located.')
    parser.add_argument('--in', type=str, required=True,
        help='The absolute/relative path where the ASR transcription ' + \
            'file is located.')
    parser.add_argument('--out', type=str, required=True,
        help='The absolute/relative path where the output file will ' + \
            'be located.')

    # parse arguments
    args = vars(parser.parse_args())

    # re-punctuate & re-capitalize
    main(args)
