import json
import spacy

from Janex import *

import os

class NLGTraining:
    def __init__(self):
        self.directory = None
        self.nlp = None

    def set_directory(self, directory):
        self.directory = directory

    def set_spacy_model(self, model):
        self.nlp = spacy.load("en_core_web_md")

    def extract_data_from_file(self, file_path):
        with open(file_path, 'r') as file:
            data = file.read()
            return data

    def cycle_through_files(self):

        TotalData = ""

        for root, dirs, files in os.walk(self.directory):
            for file_name in files:
                if file_name.endswith(".txt"):
                    file_path = os.path.join(root, file_name)
                    data = self.extract_data_from_file(file_path)
                    TotalData += data

        return TotalData

    def train_data(self):
        trends_dictionary = {}

        if self.directory is None:
            print("JanexNLG Error! You need to set the directory in which your .txt files are contained.")
            print("")
            print("Use NLGTraining.set_directory('directory')")
            return 404
        if self.nlp is None:
            print("JanexNLG Error! You need to set your desired spacy model. Please select from en_core_web_sm, en_core_web_md or en_core_web_lg!")
            print("")
            print("Use NLGTraining.set_spacy_model('your_desired_model')")
            return 404

        data = self.cycle_through_files()

        tokens = tokenize(data)

        for i, token in enumerate(tokens):
            if token not in trends_dictionary:
                # Get the previous and next tokens if they exist
                prev_token = tokens[i - 1] if i > 0 else None
                next_token = tokens[i + 1] if i < len(tokens) - 1 else None

                # Create a list to store the word before and word after
                context_words = []
                if prev_token:
                    context_words.append(prev_token)
                if next_token:
                    context_words.append(next_token)

                # Compute the vector arrays for context words using spaCy
                context_vectors = []
                for word in context_words:
                    word_doc = self.nlp(word)
                    context_vectors.append(word_doc.vector.tolist())

                # Append the context words and their vectors to the dictionary
                trends_dictionary[token] = {
                    "context_words": context_words,
                    "context_vectors": context_vectors
                }
                print(trends_dictionary[token])
            else:
                prev_token = tokens[i - 1] if i > 0 else None
                next_token = tokens[i + 1] if i < len(tokens) - 1 else None

                # If the token already exists, add the previous and next words
                if prev_token:
                    trends_dictionary[token]["context_words"].append(prev_token)
                if next_token:
                    trends_dictionary[token]["context_words"].append(next_token)

        # Save the trends_dictionary to a JSON file with the desired structure
        output_dictionary = {}
        for token, context_info in trends_dictionary.items():
            output_dictionary[token] = context_info

        with open("custom_janexnlg_model.bin", "wb") as bin_file:
            json_data = json.dumps(output_dictionary).encode('utf-8')
            bin_file.write(json_data)


if __name__ == "__main__":
    NLG = NLGTraining()
    NLG.set_directory("./files")
    NLG.set_spacy_model("en_core_web_md")
    NLG.train_data()
