from transformers import pipeline
from transformers import AutoModelForTokenClassification, AutoTokenizer

from sonic_arabic.ner.arabic_ner.helpers import split_sentences
from sonic_arabic.utils_arabic.utils import get_text, save_res


class Ner:
    def __init__(self):
        tokenizer = AutoTokenizer.from_pretrained("hatmimoha/arabic-ner")
        base_model = AutoModelForTokenClassification.from_pretrained("hatmimoha/arabic-ner")
        self.model = pipeline("ner", model=base_model, tokenizer=tokenizer)

    def predict(self, text_list: list[str]):
        text_list = [split_sentences(text) for text in text_list]
        return self.model(text_list)


if __name__ == '__main__':
    _text = get_text(one_line=False)
    _result = Ner().predict(_text)
    print(_result)
    # save_res("./ner/output.txt", pprint.pformat(_result))



