import genanki
import random
from os.path import split
from os.path import join

class GoodNote(genanki.Note):
  @property
  def guid(self):
    return genanki.guid_for(self.fields[2])


def anki_from_file_list(questions, answers, question_ids, id_number, title, folder):
    random.seed(id_number)
    deck = genanki.Deck(
        id_number,
        title
    )
    model_id = random.randrange(1 << 30, 1 << 31)
    model = genanki.Model(
        model_id,
        "Card from GoodNotes",
        fields = [
                {"name": "QuestionMedium"},
                {"name": "AnswerMedium"},
                {"name": "GUID"},
        ],
        templates=[
            {
                "name": "Imported Flashcard",
                "qfmt": "{{QuestionMedium}}",
                "afmt": "{{FrontSide}}<hr id=\"answer\">{{AnswerMedium}}",
            }
        ]
    )
    deck.add_model(model)

    for i in range(len(questions)):
        note = GoodNote(
            model = model,
            fields=["<img src=\"" + split(questions[i])[-1] + "\">", "<img src=\"" + split(answers[i])[-1] + "\">", question_ids[i]]
        )
        deck.add_note(note)
    
    package = genanki.Package(deck)
    package.media_files = questions + answers
    package.write_to_file(join(folder, "deck.apkg"))