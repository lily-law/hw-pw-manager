from xkcdpass import xkcd_password as xp
from flask import Flask, render_template
import math

app = Flask(__name__)

def gen_username (nWords=2, delimiter='-', acronym=False):
    # create a wordlist from the default wordfile
    wordfile = xp.locate_wordfile()
    mywords = xp.generate_wordlist(wordfile=wordfile, min_length=1, max_length=10)

    return (xp.generate_xkcdpassword(mywords, numwords=nWords, acrostic=acronym, delimiter=delimiter))

def gen_password (nWords=6, acronym=False):
    # create a wordlist from the default wordfile
    wordfile = xp.locate_wordfile()
    mywords = xp.generate_wordlist(wordfile=wordfile, min_length=4, max_length=8)
    gen = xp.generate_xkcdpassword(mywords, numwords=nWords, acrostic=acronym, random_delimiters = True, valid_delimiters = ['_', '.', '-'], case = "random")

    return (gen[1: len(gen)-1])

# Hold onto generated username and password so they can be seperated refreshed
next_entry = {
    'username': gen_username(),
    'password': gen_password()
}

@app.route('/')
def new_login():
    return render_template('index.html', username=next_entry['username'], password=next_entry['password'])

@app.route('/gen/password')
def new_password():
    next_entry['password'] = gen_password()

@app.route('/gen/username')
def new_username():
    next_entry['username'] = gen_username()