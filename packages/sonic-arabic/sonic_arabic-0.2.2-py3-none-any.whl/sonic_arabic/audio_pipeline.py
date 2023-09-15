from ner.ner_analysis import Ner
from sentiment.sentiment_analysis import Sentiment
from transcriber.transcribe_analysis import Transcriber
from punctuation.punctuation_analysis import Punctuation


class AudioAnalysisPipeline:

    def __init__(self):
        self.ner_model = Ner()
        self.sentiment_model = Sentiment()
        self.punctuation_model = Punctuation()
        self.transcriber_model = Transcriber()

    def predict(self, path_audio_file):
        transcriber_text = self.transcriber_model.predict(path_audio_file)
        text_list = [i['text'] for i in transcriber_text['segments']]
        sentiment_res = self.sentiment_model.predict(text_list)
        punctuation_res = self.punctuation_model.predict(text_list)
        ner_res = self.ner_model.predict(text_list)
        return {"ner": ner_res, "punctuation": punctuation_res, "sentiment": sentiment_res,
                "orig_text": transcriber_text['text']}


if __name__ == '__main__':
    _path_audio_file = 'data/arabic_1m.m4a'
    analyzer = AudioAnalysisPipeline()
    result = analyzer.predict(_path_audio_file)
    print(result)

    """
    {'ner': [[], [], [], [], [], [{'entity': 'B-PERSON', 'score': 0.8518139, 'index': 1, 'word': 'روش', 'start': 0, 'end': 3}, {'entity': 'B-PERSON', 'score': 0.85694945, 'index': 2, 'word': '##ي', 'start': 3, 'end': 4}], [], [{'entity': 'B-PERSON', 'score': 0.53922284, 'index': 4, 'word': '##د', 'start': 12, 'end': 13}], [], [], [], [], [], [{'entity': 'B-LOCATION', 'score': 0.9194007, 'index': 1, 'word': 'تاف', 'start': 0, 'end': 3}, {'entity': 'B-LOCATION', 'score': 0.963292, 'index': 2, 'word': '##ه', 'start': 3, 'end': 4}], [], [], [], [], [], [], [], [], [], [], [{'entity': 'B-PERSON', 'score': 0.94790345, 'index': 1, 'word': 'روش', 'start': 0, 'end': 3}, {'entity': 'B-PERSON', 'score': 0.9661763, 'index': 2, 'word': '##ي', 'start': 3, 'end': 4}], [], [], [], [], []], 'punctuation': ['كان ولدهم', 'أمي دوبوسي . إنه بشع', 'ما مشكلته', 'التصميم وليس من الذهب .', 'آه', 'روشي . هل تفقدت الحظار .', 'العاملون هدونا', 'ماذا أبي مؤكد هناك', 'موظف لهذه الأشياء .', 'ولما لا تفعل', 'حسناً لما أهتم بهذه الأشياء', 'تافهة ,', 'تظن أن العاملين المشتهدين شيئ', 'تافه', 'نعم آه', 'كيرو الحبوب في مزارعنا', 'هي الذهب الحقيقي .', 'والعاملون حسناً', 'هم أهم شيء', 'أمي رجاءً أهم شيء لي هو', 'آه', 'هذه دعوة عشاء الملك ,', 'أوه أحتاج ملابس جديدة', 'وكفا', 'روشي . لقد دللناك', 'كثيراً لن تأتي', 'العشاء الملك معنا', 'لماذا', 'كيرو الحبوب .', 'لقد فكرنا لبعض الوقت'], 'sentiment': [{'label': 'negative', 'score': 0.44272592663764954}, {'label': 'negative', 'score': 0.9907614588737488}, {'label': 'neutral', 'score': 0.5242040753364563}, {'label': 'positive', 'score': 0.5435761213302612}, {'label': 'negative', 'score': 0.7347790598869324}, {'label': 'neutral', 'score': 0.9290924072265625}, {'label': 'negative', 'score': 0.971164345741272}, {'label': 'neutral', 'score': 0.8854630589485168}, {'label': 'neutral', 'score': 0.6760575175285339}, {'label': 'negative', 'score': 0.5414125919342041}, {'label': 'negative', 'score': 0.6795262098312378}, {'label': 'negative', 'score': 0.9900053143501282}, {'label': 'negative', 'score': 0.7440279722213745}, {'label': 'negative', 'score': 0.9755764007568359}, {'label': 'negative', 'score': 0.413840651512146}, {'label': 'negative', 'score': 0.5336402058601379}, {'label': 'positive', 'score': 0.9709219336509705}, {'label': 'negative', 'score': 0.5461823344230652}, {'label': 'neutral', 'score': 0.6135458946228027}, {'label': 'positive', 'score': 0.6199305057525635}, {'label': 'negative', 'score': 0.7347790598869324}, {'label': 'neutral', 'score': 0.936942994594574}, {'label': 'neutral', 'score': 0.6117208003997803}, {'label': 'positive', 'score': 0.942241907119751}, {'label': 'positive', 'score': 0.9660342931747437}, {'label': 'neutral', 'score': 0.7480940222740173}, {'label': 'positive', 'score': 0.5263846516609192}, {'label': 'neutral', 'score': 0.685641884803772}, {'label': 'neutral', 'score': 0.4974607527256012}, {'label': 'negative', 'score': 0.6640478372573853}], 'orig_text': ' كان ولدهم أمي دوبوسي إنه بشع ما مشكلته التصميم وليس من الذهب آه روشي هل تفقدت الحظار العاملون هدونا ماذا أبي مؤكد هناك موظف لهذه الأشياء ولما لا تفعل حسناً لما أهتم بهذه الأشياء تافهة تظن أن العاملين المشتهدين شيئ تافه نعم آه كيرو الحبوب في مزارعنا هي الذهب الحقيقي والعاملون حسناً هم أهم شيء أمي رجاءً أهم شيء لي هو آه هذه دعوة عشاء الملك أوه أحتاج ملابس جديدة وكفا روشي لقد دللناك كثيراً لن تأتي العشاء الملك معنا لماذا كيرو الحبوب لقد فكرنا لبعض الوقت'}

    """




