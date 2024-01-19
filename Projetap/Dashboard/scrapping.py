import os
from time import sleep
import requests
import pandas as pd
from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from tqdm import tqdm
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm.notebook import tqdm
import nltk
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from Dashboard import app 

# Define the function to remove text after 'Date of experience:'
def remove_text_after_date(content):
    if 'Date of experience:' in content:
        return content.split('Date of experience:')[0].strip()
    return content

#Afin de faciliter la notation 
sia = SentimentIntensityAnalyzer()

#Fonction de scrapping
def soup2list(src, list_, attr=None):
    if attr:
        for val in src:
            list_.append(val[attr])
    else:
        for val in src:
            list_.append(val.get_text())

def scrape_trustpilot_reviews(company, user_id):

    user_folder_path = os.path.join(app.root_path, 'static', user_id)
     # Créer le dossier s'il n'existe pas
    if not os.path.exists(user_folder_path):
        os.makedirs(user_folder_path)


    ratings = []
    reviews = []

    from_page = 1
    to_page = 50
    

    for i in range(from_page, to_page+1):

        result = requests.get(fr"https://www.trustpilot.com/review/www.{company}.com?page={i}")
        soup = BeautifulSoup(result.content, features="html.parser")

        soup2list(soup.find_all('div', {'class','styles_reviewHeader__iU9Px'}), ratings, attr='data-service-review-rating')
        soup2list(soup.find_all('div', {'class','styles_reviewContent__0Q2Tg'}), reviews)

     # To avoid throttling
        sleep(1)

    data = pd.DataFrame(
    {
    'content':reviews,
    'Rating': ratings
    })

    # Apply the function to the 'content' column
    data['content'] = data['content'].apply(remove_text_after_date)

        # Dictionnaire pour stocker les résultats
        # Dictionnaire pour stocker les résultats des scores de polarité
    res = {}

    # Calculer le score de polarité pour chaque commentaire
    for index, row in data.iterrows():
        text = row['content']
        # Stocker le score de polarité pour chaque commentaire
        res[index] = sia.polarity_scores(text)

    # Convertir les résultats en DataFrame
    vaders = pd.DataFrame.from_dict(res).T

    # Fusionner le DataFrame original avec les scores de polarité
    data = pd.concat([data, vaders], axis=1)

    # Enregistrez le DataFrame résultant, si nécessaire
    data_path = os.path.join(user_folder_path, f'{company}.csv')
    data.to_csv(data_path)

    # Concaténation de tous les commentaires en une seule chaîne de texte
    text = " ".join(comment for comment in data['content'])

    # Liste des mots à exclure (stop words en anglais)
    stop_words = set(stopwords.words('english'))

    # Ajouter des mots spécifiques à exclure
    stop_words.update([company])

    # Tokenisation du texte
    tokens = word_tokenize(text)

    # Filtrage des adjectifs à l'aide de POS Tagging
    adjectives = [word for (word, pos) in pos_tag(tokens) if pos.startswith('JJ')]

    # Exclusion des stop words et des mots spécifiques
    adjectives_filtered = [word for word in adjectives if word.lower() not in stop_words]

    # Génération du nuage de mots à partir des adjectifs filtrés
    text_adjectives = " ".join(adjectives_filtered)
    wordcloud = WordCloud(stopwords=stop_words, background_color="white").generate(text_adjectives)
    # Dans votre fonction de scraping, après avoir généré le nuage de mots
    image_path = os.path.join(user_folder_path, f'{company}.png')
    wordcloud.to_file(image_path)




