# FlaskProject Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Project Structure](#project-structure)
5. [Usage](#usage)
6. [Docker](#docker)


---

## Introduction

FlaskProject is a web application designed to facilitate the scraping of TrustPilot reviews, perform sentiment analysis, and visualize data through an interactive dashboard developed with Dash. It also allows for user registration and management.

## Requirements

To run FlaskProject, you will need the following:

- **Python**: Version 3.6 or newer.
- **Flask**: A lightweight WSGI web application framework.
- **Dash**: A productive Python framework for building web analytic applications.
- **SQLAlchemy**: The Python SQL toolkit and Object-Relational Mapper that gives application developers the full power and flexibility of SQL.
- **Flask-WTF**: Simple integration of Flask and WTForms, including CSRF protection.
- **SQLite**: A C library that provides a lightweight disk-based database that doesn’t require a separate server process.

Other required packages and specific versions can be found in the `requirements.txt` file, which can be installed using pip:

## Installation

Clone the Git repository:
```bash
git clone [repository_url]
```
Install the dependencies:
```bash
pip install -r requirements.txt
```
Set up the database:
```bash
flask db upgrade
```

## Project Structure

The FlaskProject is organized as follows:

- **Dashboard/**: 
  - `__init__.py`: Initializes the Flask app as a package to make it importable.
  - `dashboardapp.py`: Defines the layout and interactivity of the Dash dashboard.
  - `forms.py`: Contains the WTForms class definitions for user input forms.
  - `models.py`: Defines the SQLAlchemy ORM models for database interaction.
  - `routes.py`: Includes all the route definitions for the Flask application.
  - `scrapping.py`: Implements the functionality for scraping TrustPilot reviews.

- **instance/**: 
  - This directory contains the SQLite database files for the application. It is not typically checked into version control.

- **static/**: 
  - Contains static files such as CSS, JS, and user-generated CSV files. Each user's scraped data is stored in a subdirectory corresponding to their user ID.

- **templates/**: 
  - Holds the HTML templates that are rendered by Flask views. These templates use the Jinja2 templating language.

- **.dockerignore**: 
  - Lists files and directories that should be ignored when building a Docker image.

- **.gitignore**: 
  - Specifies intentionally untracked files to ignore when using Git.

- **Dockerfile**: 
  - Contains all the commands a user could call to assemble an image.

- **Readme.md**: 
  - The file you are reading right now, which provides documentation for the project.

## Usage

### Registration and Login
Users must create an account and log in to access the scraping and data visualization features.

### Scraping Reviews
After logging in, users can enter a company name to scrape its reviews from TrustPilot.

### Data Visualization
Scraping results can be visualized in a Dash dashboard, which can be launched from the user interface.

### Data Management
Users can download CSV data and word clouds, as well as delete companies from their scraping list.

## Docker 

Docker is a containerization platform that simplifies the deployment and management of your applications. Follow the steps below to use Docker with our application.

### Prerequisites

Make sure you have Docker installed on your machine. If Docker is not installed, you can download and install it from the [official Docker website](https://docs.docker.com/get-docker/).

### Building the Docker Image

Open a terminal and navigate to the root of the project where the `Dockerfile` is located. Ensure you are on the main branch that contains the desired Docker file.

Execute the following command to build your Docker image. The `-t` option tags your image to make it easier to reference later:

```sh
docker build -t essai .
```

This command will build a Docker image named `essai` following the instructions defined in your `Dockerfile`. The dot `.` at the end of the command indicates that Docker should use the current directory context.

## Running the Container

Once the Docker image is built, you are ready to run a container from this image. Use the following command to start the container in detached mode, map your application's port to the host machine's port, and configure persistent data storage.

```bash
docker run -d -p 5000:5000 -v my_local_volume:/Projetapp/instance essai
```

Details of the `docker run` command:

- `-d`: Runs the container in detached mode (in the background).
- `-p 5000:5000`: Maps the container's port 5000 (left) to your host machine's port 5000 (right), allowing access to your Flask application via the URL http://localhost:5000.
- `-v my_local_volume:/Projetapp/instance`: Creates (or uses an existing) Docker volume named `my_local_volume` and mounts it to the path `/Projetapp/instance` inside the container. This volume is used for storing and persisting your Flask application's SQLite database data, so it is not lost when the container is stopped or deleted.
- `essai`: The name of the Docker image to use to create the container. Ensure this image has been previously built and tagged with the name `essai`.

Once the container is launched, you can access your Flask application by going to http://localhost:5000 with your web browser.

### Stopping the Container

If you need to stop the container, use the `docker stop` command followed by the container's ID or name:

```bash
docker stop <container_id_or_name>
```

You can obtain the container's ID or name by using the `docker ps` command, which lists all currently running containers.

### Cleanup

To remove the container after stopping it:

```bash
docker rm <container_id_or_name>
```

To remove the Docker image if it is no longer needed:

```bash
docker rmi essai
```

And to remove the volume if you no longer need it:

```bash
docker volume rm my_local_volume
```

Make sure not to delete volumes containing important data without backing it up first.
