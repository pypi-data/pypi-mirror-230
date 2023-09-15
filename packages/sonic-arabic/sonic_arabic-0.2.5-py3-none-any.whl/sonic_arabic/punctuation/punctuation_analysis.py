import sys
import os
import pathlib

cur_dir = pathlib.Path(__file__).parent.resolve()
sys.path.append(os.path.join(cur_dir, 'BertPuncCap'))


from transformers import BertTokenizer, BertModel
from sonic_arabic.punctuation.BertPuncCap.model import BertPuncCap
from sonic_arabic.utils_arabic.utils import get_text, save_res


class Punctuation:

    def __init__(self):
        bert_name = "bert-base-multilingual-cased"
        bert_tokenizer = BertTokenizer.from_pretrained(bert_name)
        bert_model = BertModel.from_pretrained(bert_name)
        checkpoint_path = os.path.join(cur_dir, "BertPuncCap/models/mbert_base_cased_8langs")
        self.model = BertPuncCap(bert_model, bert_tokenizer, checkpoint_path)

    def predict(self, text_list: list[str]):
        result = self.model.predict(text_list)
        return result


if __name__ == '__main__':
    _text = get_text(one_line=False)
    _result = Punctuation().predict(_text)
    print(_result)
    # save_res("./punctuation/output.txt", '\n'.join(_result))


