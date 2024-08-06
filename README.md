# Shake API
shake is a python Flask RESTful API that provides access to an end-to-end (Retrieval Augmented Generation) application. It analyses pdf data provided by a user and gives responses based only on the pdf data. It is built on langchain and openAI.

This README provides instructions on how to run the shake API Flask app.

## Prerequisites

Make sure you have the following installed before running the app:

- Python (version == 3.10)
- pip (Python package installer)
- Virtualenv (optional but recommended for creating isolated Python environments)
- OpenAI API key

## Installation

1. Clone this repository to your local machine:

### `git clone <repository_url>`
### `cd <project_directory>`
### `virtualenv venv`

2. Activate your virtual environment
### `venv\Scripts\activate`

3. Install dependencies
### `pip install -r requirements.txt`

4. Running the app
### `python server.py`
