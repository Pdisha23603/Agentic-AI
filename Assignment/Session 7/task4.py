# ============================================
# Task 4: Restaurant Name Detection using spaCy
# ============================================

import spacy
from spacy.pipeline import EntityRuler

# Load English spaCy model
nlp = spacy.load("en_core_web_sm")

# Add custom restaurant patterns
ruler = nlp.add_pipe("entity_ruler", before="ner")

patterns = [
    {"label": "RESTAURANT", "pattern": "Barbeque Nation"},
    {"label": "RESTAURANT", "pattern": "Domino's"},
    {"label": "RESTAURANT", "pattern": "Pizza Hut"},
    {"label": "RESTAURANT", "pattern": "McDonald's"},
    {"label": "RESTAURANT", "pattern": "KFC"}
]

ruler.add_patterns(patterns)

messages = [
    "Let's eat at Barbeque Nation tonight.",
    "I ordered pizza from Domino's.",
    "We visited Pizza Hut yesterday.",
    "Meeting at office tomorrow.",
    "Lunch from McDonald's was tasty."
]

restaurants_found = []

for message in messages:
    doc = nlp(message)

    for ent in doc.ents:
        if ent.label_ == "RESTAURANT":
            restaurants_found.append(ent.text)

print("Detected Restaurant Names")
print("-" * 35)

if restaurants_found:
    for name in restaurants_found:
        print(name)
else:
    print("No restaurant names detected.")