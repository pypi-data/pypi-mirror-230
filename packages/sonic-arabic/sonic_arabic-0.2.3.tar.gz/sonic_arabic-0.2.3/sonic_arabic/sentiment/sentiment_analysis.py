from transformers import pipeline
from sonic_arabic.utils_arabic.utils import get_text, save_res


class Sentiment:
    def __init__(self):
        self.model = pipeline('text-classification', model='CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment')

    def predict(self, text_list: list[str]):
        return self.model(text_list)


if __name__ == '__main__':
    text = get_text(one_line=False)
    result = Sentiment().predict(text)
    result = [f"label: {res['label']}, text: {txt.strip()}, score: {res['score']}" for res, txt in zip(result, text)]
    print(result)
    # save_res("./sentiment/output.txt", result)
