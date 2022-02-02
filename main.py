from multiprocessing.connection import answer_challenge
import goodnotes_fetcher
import anki_generator
import cv2   
from os.path import join
from os.path import split
from os import makedirs
import random
from flask import Flask, request, send_from_directory, redirect

def title_hash(text: str):
  hash = 0
  for ch in text:
    hash = (hash*281^ord(ch)*997) & 0xFFFFFFFF
  return hash

def make_deck_from_input(input: str):
    # TODO: Make sure input is correct
    image_files, folder, title = goodnotes_fetcher.get_goodnotes_flashcards(input)
    
    questions = []
    answers = []
    # split images
    makedirs(join(folder, "deckimages/"), exist_ok=True)
    random.seed()
    
    question_ids = []
    for i in range(len(image_files)):
        question_id = split(image_files[i][0])[-1].split(".")[0].split("@")[0]
        question_ids.append(question_id)

        image_file_name = str(random.randrange(1e10, 1e11))

        img = cv2.vconcat([cv2.imread(image) for image in image_files[i]])
        # TODO don't hardcode size
        img = img[0:2154, 0:1668]

        height = img.shape[0]
        height_cutoff = height // 2
        question = img[:height_cutoff, :]
        answer = img[height_cutoff:, :]
        question_filename = join(folder, "deckimages/", image_file_name + "_question.png")
        answer_filename = join(folder, "deckimages/", image_file_name + "_answer.png")
        cv2.imwrite(question_filename, question)
        cv2.imwrite(answer_filename, answer)
        questions.append(question_filename)
        answers.append(answer_filename)
    anki_generator.anki_from_file_list(questions, answers, question_ids, title_hash(title), title, folder)

# make_deck_from_input("https://share.goodnotes.com/s/iQyqS5wLY6ZxaZVukfNc0W")

app = Flask(__name__, static_folder="static", static_url_path="/static/")

@app.route("/", methods=["GET"])
def index():
    return send_from_directory("static", "index.html")

@app.route("/submit-job", methods=["POST"])
def submit_job():
    goodnotes_url = request.form["goodnotes-url"]
    # TODO check url is goodnotes url
    make_deck_from_input(goodnotes_url)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
