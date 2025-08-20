import spacy
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Load spaCy model
nlp = spacy.load("en_core_web_sm")
# Specify the model you want, e.g., distilbart-cnn
tokenizer = AutoTokenizer.from_pretrained("sshleifer/distilbart-cnn-12-6")
model = AutoModelForSeq2SeqLM.from_pretrained("sshleifer/distilbart-cnn-12-6")
generator = pipeline('text-generation', model='gpt2')

def analyze_text(text):
  try:
    doc = nlp(text)
        
    # Extract basic NLP features
    entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]
    tokens = [{'text': token.text, 'lemma': token.lemma_, 'pos': token.pos_, 'tag': token.tag_} for token in doc]

    response = {
      'status': 200,
      'message': '',
      'data': {
        'entities': entities,
        'tokens': tokens
      }
    }
  except Exception as e:
    return {
      'status': 500,
      'message': f"An unexpected error occurred: {e}",
      'data': {}
    }
  else:
    return response
  
def analyze_summarize(text):
  try:
    inputs = tokenizer.encode(text, return_tensors="pt")
    summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    response = {
      'status': 200,
      'message': '',
      'data': {
        'summary': summary
      }
    }
  except Exception as e:
    return {
      'status': 500,
      'message': f"An unexpected error occurred: {e}",
      'data': {}
    }
  else:
    return response
  
def analyze_sentiment(text):
  try:
    # Initialize the VADER sentiment analyzer
    sia = SentimentIntensityAnalyzer()
    # Perform sentiment analysis
    sentiment = sia.polarity_scores(text)

    # Output the sentiment scores
    response = {
      'status': 200,
      'message': '',
      'data': {
        'sentiment': sentiment
      }
    }
  except Exception as e:
    return {
      'status': 500,
      'message': f"An unexpected error occurred: {e}",
      'data': {}
    }
  else:
    return response

def text_generator(text):
  try:
    # Generate the text
    result = generator(text, max_length=999, num_return_sequences=1, truncation=True)

    response = {
      'status': 200,
      'message': '',
      'data': {
        'result': result
      }
    }
  except Exception as e:
    return {
      'status': 500,
      'message': f"An unexpected error occurred: {e}",
      'data': {}
    }
  else:
    return response
