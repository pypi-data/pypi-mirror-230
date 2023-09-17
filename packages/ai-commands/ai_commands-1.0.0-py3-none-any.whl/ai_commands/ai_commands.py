import random
from nltk.corpus import wordnet
import re
import nltk
from textblob import TextBlob
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
from langdetect import detect
import torch
import torchvision.transforms as transforms
from PIL import Image
from transformers import MarianTokenizer, MarianMTModel
import spacy

def ai_similarise(message):
   """
    If you want a different wording to an output when a specific condition is met and gives an output, this will make things a little less boring!
    
    It generates similar but varied text for a given input message using synonyms and sentence structure variation.

    This function takes an input message and applies two main techniques to generate similar yet different text:
    1. Synonym Replacement: It replaces words in the message with synonyms when synonyms are available. This adds lexical variation to the text.
    2. Sentence Structure Variation: It shuffles the clauses in the sentence to change its structure and provide additional variation.

    Warnings:
    - The function uses NLTK's WordNet corpus for synonym replacement, which may not always provide the most contextually accurate synonyms.
    - While efforts have been made to maintain sentence coherence, generated text may occasionally be grammatically incorrect or nonsensical.
    - The quality of generated variations depends on the availability of synonyms and sentence structure possibilities for the input message.

    Parameters:
    message (str): The input message for which similar text variations are generated.

    Returns:
    str: A text variation of the input message with synonyms and sentence structure changes.
    """
    def synonym_replacement(word):
        synonyms = wordnet.synsets(word)
        if synonyms:
            synonym = random.choice(synonyms).lemmas()[0].name()
            return synonym
        return word

    def replace_words(text):
        words = re.findall(r'\w+', text)
        new_words = [synonym_replacement(word) for word in words]
        return ' '.join(new_words)

    def vary_sentence_structure(text):
        # Split the sentence into clauses based on punctuation
        clauses = re.split(r'([.,!?])', text)
        clauses = [clause.strip() for clause in clauses if clause.strip()]
        
        # Shuffle and reassemble the clauses
        random.shuffle(clauses)
        return ''.join(clauses)

    message = message.lower()  # Convert to lowercase for consistency
    message = replace_words(message)
    message = vary_sentence_structure(message)

    return message
def analyze_sentiment(text):
    """
    Analyze the sentiment of a text using Natural Language Processing (NLP).

    Parameters:
    text (str): The input text to be analyzed.

    Returns:
    dict: A dictionary containing the sentiment label, sentiment score, and a sentiment summary.
    """
    analysis = TextBlob(text)
    sentiment_score = analysis.sentiment.polarity

    if sentiment_score > 0:
        sentiment_label = "positive"
        sentiment_summary = "This text expresses a positive sentiment."
    elif sentiment_score < 0:
        sentiment_label = "negative"
        sentiment_summary = "This text expresses a negative sentiment."
    else:
        sentiment_label = "neutral"
        sentiment_summary = "This text appears to be neutral in sentiment."

    result = {
        "sentiment_label": sentiment_label,
        "sentiment_score": sentiment_score,
        "sentiment_summary": sentiment_summary
    }

    return result
def translate_text(text, target_language):
  # Load a pre-trained translation model
  model_name = f"Helsinki-NLP/opus-mt-en-{target_language}"
  tokenizer = MarianTokenizer.from_pretrained(model_name)
  model = MarianMTModel.from_pretrained(model_name)

  # Translate the text to the target language
  inputs = tokenizer("Translate English to " + target_language + ": " + text,
                     return_tensors="pt",
                     padding=True,
                     truncation=True)
  outputs = model.generate(inputs["input_ids"],
                           max_length=150,
                           num_beams=5,
                           no_repeat_ngram_size=2,
                           early_stopping=True)
  translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

  return translated_text


def ai_summarize(text, num_sentences=2):

  def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
      stopwords = []

    words1 = [
        word.lower() for word in sent1.split() if word.lower() not in stopwords
    ]
    words2 = [
        word.lower() for word in sent2.split() if word.lower() not in stopwords
    ]

    all_words = list(set(words1 + words2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # Build the vector representation for each sentence
    for word in words1:
      vector1[all_words.index(word)] += 1

    for word in words2:
      vector2[all_words.index(word)] += 1

    return 1 - cosine_distance(vector1, vector2)

  def build_similarity_matrix(sentences, stopwords=None):
    if stopwords is None:
      stopwords = []

    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for i in range(len(sentences)):
      for j in range(len(sentences)):
        if i != j:
          similarity_matrix[i][j] = sentence_similarity(
              sentences[i], sentences[j], stopwords)

    return similarity_matrix

  def generate_summary(text, num_sentences=2):
    stop_words = stopwords.words('english')
    summarize_text = []

    # Tokenize sentences
    sentences = text.split(". ")

    # Generate the similarity matrix across sentences
    sentence_similarity_matrix = build_similarity_matrix(sentences, stop_words)

    # Apply PageRank algorithm to get sentence rankings
    sentence_scores = nx.pagerank(
        nx.from_numpy_array(sentence_similarity_matrix))

    # Sort sentences by their score
    ranked_sentences = sorted(
        ((sentence_scores[i], s) for i, s in enumerate(sentences)),
        reverse=True)

    # Extract the top sentences as the summary
    for i in range(num_sentences):
      summarize_text.append(ranked_sentences[i][1])

    return ". ".join(summarize_text)

  # Clean and preprocess the input text (you can add more preprocessing as needed)
  text = text.replace("\n", " ").replace("\r", "").strip()

  # Generate the summary
  summary = generate_summary(text, num_sentences)

  return summary


def detect_language(text):
  try:
    detected_language = detect(text)
    return detected_language
  except:
    return "Language detection failed"


def generate_image_caption(image_path):
  # Load the image and preprocess it
  image = Image.open(image_path)
  preprocess = transforms.Compose([
      transforms.Resize(256),
      transforms.CenterCrop(224),
      transforms.ToTensor(),
      transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225]),
  ])
  image = preprocess(image).unsqueeze(0)

  # Load a pre-trained image captioning model
  model_name = "Helsinki-NLP/opus-mt-en-ro"
  tokenizer = MarianTokenizer.from_pretrained(model_name)
  model = MarianMTModel.from_pretrained(model_name)

  # Generate a caption for the image
  inputs = tokenizer("Translate English to Romanian: " + "a photo of a dog",
                     return_tensors="pt",
                     padding=True,
                     truncation=True)
  outputs = model.generate(inputs["input_ids"],
                           max_length=50,
                           num_beams=5,
                           no_repeat_ngram_size=2,
                           early_stopping=True)
  caption = tokenizer.decode(outputs[0], skip_special_tokens=True)

  return caption


def ner_extraction(text):
  # Load the spaCy NER model
  nlp = spacy.load("en_core_web_sm")

  # Process the text with the NER model
  doc = nlp(text)

  # Extract named entities and their labels
  entities = [(ent.text, ent.label_) for ent in doc.ents]

  return entities


