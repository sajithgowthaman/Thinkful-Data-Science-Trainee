import re
import os
import json
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from pdt_txt import convert
from build_db import BuildingDB
from build_tfidf import buildingTFIDF
from querying import query
app = Flask(__name__)


class Training:
    def __init__(self, file_name):
        self.doc_name = file_name.strip(".pdf")
        print(self.doc_name)
        self.domain = "model"
        if not os.path.exists('./input_file'):
            print("Created directory to store the model file")
            os.makedirs('./input_file')
            os.makedirs('./db_file')
            os.makedirs('./output_model')

        self.file_name = self.doc_name + ".txt"
        self.data_path = "./input_file/" + self.domain
        self.save_path = "./db_file/" + self.domain + ".db"
        self.out_dir = "./output_model/"
        self.c = []

        self.statusContent = dict()
        self.statusContent["domainId"] = self.domain
        self.statusContent["documentId"] = self.doc_name

        try:
            self.extractedContent = convert(self.doc_name + ".pdf")
            converted = open(self.file_name, "w")
            converted.write(self.extractedContent)
            converted.close()
            print("writing content into file for training")
            print("Extracted the content for the training")

        except KeyError:
            self.statusContent["status"] = "FAILURE"
            self.statusContent["error"] = "No content found to train for the domain %s" % self.domain
            return

        if len(self.extractedContent.split()) <= 25:
            self.statusContent["status"] = "FAILURE"
            self.statusContent["error"] = "Not enough words Found to train"
            return

    def process(self, ):
        self.opening_file()
        status = self.model_creation()
        os.remove(self.file_name)
        os.remove(self.doc_name + ".pdf")
        return status

    def opening_file(self, ):
        print("Data is parsing for training")

        self.document = open(self.file_name, 'r').readlines()

        for i in self.document:
            self.d = re.sub("[^a-zA-Z0-9.,$]", " ", i)
            self.c.append(re.sub(' +', ' ', self.d.strip()))
        self.conts = list(filter(None, list(set((' '.join(self.c)).split('.')))))

        self.f2 = open('./input_file/' + self.domain, 'a')
        for i in range(len(self.conts)):
            self.f2.write('{' + '"id":"{0}"'.format(i + 1) + ', "text":"{0}"'.format(self.conts[i] + '.') + '}')
            self.f2.write('\n')
        self.f2.close()

    def model_creation(self, ):
        print("Training Process has been started")
        BuildingDB(self.data_path, self.save_path).store_contents()
        buildingTFIDF(self.save_path, self.out_dir)
        status = {"domainName": self.domain, "documentName": self.doc_name, "status": "SUCCESS"}
        return status


@app.route('/', methods=['POST', 'GET'])
def train():
    if request.method == 'GET':
        return render_template('index2.html')
    elif request.method == 'POST':
        print("..............Model training starting..............")
        fname = request.files.get('title')
        fname.save('./' + secure_filename(fname.filename))
        response = Training(fname.filename).process()
        print(response)
        return redirect(url_for('prediction'))


@app.route('/predict', methods=['POST', 'GET'])
def prediction():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        question = request.form.get('query')
        response = json.loads(query(question))
        answer = 'Sorry, I did not get that. Please rephrase your question'
        final_answer = None
        multiple_answer = []
        max_score = 0

        for ans in response['results']:
            if ans['score'] >= 35 and ans['score'] >= max_score:
                max_score = ans['score']
                final_answer = ans['answer']
            else:
                multiple_answer.append(ans['answer'])

        if final_answer:
            print(final_answer)
            kwargs = {
                'query': question,
                'answer': [final_answer],
            }
            return render_template('index.html', **kwargs)

        if multiple_answer:
            multiple_answer.insert(0, "I found top 3 answers for your question:")
            print(multiple_answer)
            kwargs = {
                'query': question,
                'answer': multiple_answer,
            }
            return render_template('index.html', **kwargs)

        print(answer)
        kwargs = {
            'query': question,
            'answer': [answer],
        }
        return render_template('index.html', **kwargs)


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8000)
