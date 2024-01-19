from Dashboard import app 
from flask import render_template, redirect, url_for, flash, request, send_from_directory, send_file, session, Flask
from flask_login import login_user, logout_user, login_required, current_user
from nltk.sentiment import SentimentIntensityAnalyzer
from Dashboard.scrapping import scrape_trustpilot_reviews
from Dashboard.forms import RegisterForm, LoginForm
from Dashboard.models import User, CompanyScrape
from Dashboard import db
import requests
import os 
from os.path import join
import sqlite3


sia = SentimentIntensityAnalyzer()

@app.route('/')
@app.route('/home')
def home_page():
    if current_user.is_authenticated:
        # Récupérez les entreprises scrapées par l'utilisateur actuel
        scraped_companies = CompanyScrape.query.filter_by(user_id=current_user.id).all()
    else:
        # Si l'utilisateur n'est pas connecté, scraped_companies sera une liste vide
        scraped_companies = []

    return render_template('home.html', scraped_companies=scraped_companies)



@app.route('/search', methods=['POST'])
def search():
    company = request.form['company']
    url = f"https://www.trustpilot.com/review/www.{company}.com"
    

    # Vérifiez d'abord si la page existe
    response = requests.get(url)
    if response.status_code == 404:
        return render_template('company.html', image_path=None, message="Page n'existe pas.")
    elif not current_user.is_authenticated:
        return redirect(url_for('login_page'))
# Vérifiez si l'entreprise a déjà été recherchée par l'utilisateur
    existing_scrape = CompanyScrape.query.filter_by(
        company_name=company, 
        user_id=current_user.get_id()
    ).first()

    if not current_user.is_authenticated:
        return redirect(url_for('login_page'))

    user_id = current_user.get_id()  # Obtenir l'ID de l'utilisateur connecté
    existing_scrape = CompanyScrape.query.filter_by(
        company_name=company, 
        user_id=user_id
    ).first()

    if existing_scrape:
        # Si l'entreprise existe déjà, informez l'utilisateur
        return render_template('company.html', image_path=True)
    else:
        # Passer user_id à la fonction de scraping
        scrape_trustpilot_reviews(company, user_id)
        new_scrape = CompanyScrape(company_name=company, user_id=user_id)
        db.session.add(new_scrape)
        db.session.commit()
        return render_template('company.html', image_path=True)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('home_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

@app.route('/delete_company', methods=['POST'])
def delete_company():
    company_name = request.form['company']

    # Créez le chemin relatif en utilisant le répertoire courant
    database_path = os.path.join('Projetapp', 'instance', 'Dashboard.db')
    # Récupérer l'ID de l'utilisateur courant depuis la session
    current_user_id=current_user.id
    # Etablir une connexion à la base de données
    conn = sqlite3.connect(database_path)
    cur = conn.cursor()
    # Vérifier si l'entreprise existe
    cur.execute("SELECT user_id FROM company_scrape WHERE company_name=? AND user_id=? LIMIT 1", (company_name, current_user_id))
    exists = cur.fetchone()
    
    if exists:
        # Si elle existe, supprimez-la de la base de données
        cur.execute("DELETE FROM company_scrape WHERE company_name=? AND user_id=?", (company_name, current_user_id))
        conn.commit()

        # Supprimer le fichier CSV associé
        excel_file_path = os.path.join(os.getcwd(),'Projetapp','Dashboard','static',str(current_user_id), f'{company_name}.csv')
        if os.path.exists(excel_file_path):
            os.remove(excel_file_path)

        # Supprimer l'image associée
        image_file_path = os.path.join(os.getcwd(),'Projetapp','Dashboard','static',str(current_user_id), f'{company_name}.png')
        if os.path.exists(image_file_path):
            os.remove(image_file_path)

        flash('L\'entreprise et les fichiers associés ont été supprimés.', 'success')
    else:
        # Sinon, affichez un message d'erreur
        flash('Le nom de l\'entreprise n\'est pas valide ou n\'existe pas.', 'error')
    
    
    # Fermer la connexion
    conn.close()
    
    return redirect(url_for('home_page'))



import zipfile
from flask import send_file, after_this_request
import os
from flask_login import login_required, current_user

@app.route('/download_csv/<company_name>')
@login_required
def download_csv(company_name):
    current_user_id = current_user.id
    directory = os.path.join(os.getcwd(), 'Projetapp', 'Dashboard', 'static', str(current_user_id))
    
    # Créez les chemins pour les deux fichiers
    csv_path = os.path.join(directory, f'{company_name}.csv')
    png_path = os.path.join(directory, f'{company_name}.png')

    # Créez un fichier ZIP temporaire pour contenir les deux fichiers
    zip_filename = f"{company_name}_files.zip"
    zip_path = os.path.join(directory, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(csv_path, arcname=f'{company_name}.csv')
        zipf.write(png_path, arcname=f'{company_name}.png')

    # Assurez-vous de supprimer le fichier zip temporaire après l'envoi
    @after_this_request
    def remove_file(response):
        try:
            os.remove(zip_path)
        except Exception as error:
            app.logger.error("Error removing or closing downloaded zip file handle", error)
        return response

    return send_file(zip_path, as_attachment=True, download_name=zip_filename)

