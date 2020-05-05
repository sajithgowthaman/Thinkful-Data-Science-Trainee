import json
import warnings
import pipeline

warnings.simplefilter('ignore')


class serializer:
    def __init__(self, ques, results, error_text):
        self.query = ques
        self.results = results
        self.errorText = error_text

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class answerSerializer:
    def __init__(self, score, answer):
        self.score = score
        self.answer = answer


class Querying(object):
    def __init__(self, ques):
        self.domain = "model"
        self.ques = ques
        self.n = 3

        self.basePath = self.domain
        self.doc_db = './db_file/' + self.basePath + '.db'
        self.retriever_model = './output_model/' + self.basePath + '-tfidf-ngram=2-hash=16777216-tokenizer=corenlp.npz'

        self.DrQA = pipeline.DrQA(
            cuda=None,
            fixed_candidates=None,
            reader_model=None,
            ranker_config={'options': {'tfidf_path': self.retriever_model}},
            db_config={'options': {'db_path': self.doc_db}},
            tokenizer='corenlp'
        )

    def main_function(self, ):

        print('Initializing pipeline...')
        results = []

        try:
            context, scores = self.process(self.ques, top_n=self.n, n_docs=self.n)
            for answer, score in zip(context, scores):
                results.append(answerSerializer(score, answer))
            response = serializer(self.ques, results, "")

        except Exception as e:
            response = serializer(self.ques, results, str(e))

        response = response.to_json()
        return response

    def process(self, question, candidates=None, top_n=1, n_docs=1):
        try:
            predictions = self.DrQA.process(question, candidates, top_n, n_docs, return_context=True)
        except Exception as e:
            response = serializer(question, [], str(e))
            return response.to_json()

        scores = []
        context = []
        for p in predictions:
            scores.append(p['doc_score'])
            context.append(p['context']['text'])
        return context, scores


def query(ques):
    response = Querying(ques).main_function()
    return response

