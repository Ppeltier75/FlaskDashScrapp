# Utilisez une image de base qui a déjà Python 3.12
FROM python:3.12-slim

# Définissez le frontend non interactif pour éviter de bloquer sur les invites utilisateur
ENV DEBIAN_FRONTEND=noninteractive

# Mise à jour et installation des paquets nécessaires
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    nano \
    tzdata \
 && rm -rf /var/lib/apt/lists/*

# Copiez le script de configuration du fuseau horaire et exécutez-le
# Copiez le script de configuration du fuseau horaire et exécutez-le
COPY set-timezone.sh .
RUN chmod +x ./set-timezone.sh && ./set-timezone.sh


# Définissez le répertoire de travail à l'intérieur du conteneur
WORKDIR /Projetapp

# Créez le répertoire instance qui contiendra la base de données SQLite
RUN mkdir -p /Projetapp/instance

# Assurez-vous que le répertoire instance a les bonnes permissions
RUN chmod 755 /Projetapp/instance

# Copiez le fichier des exigences et installez les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir --ignore-installed -r requirements.txt

# Copiez le reste des fichiers de votre application
COPY . .

# Installez NLTK et téléchargez la ressource vader_lexicon nécessaire
RUN pip install nltk && \
    python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('stopwords'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"

# Exposez le port sur lequel l'application s'exécutera
EXPOSE 5000

# Définissez les variables d'environnement
ENV FLASK_APP=run.py
ENV FLASK_ENV=production

# Spécifiez la commande pour exécuter votre application Flask
CMD ["flask", "run", "--host=0.0.0.0"]
