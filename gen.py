import time
from xkcdpass import xkcd_password as xp
import random

called = {
        'service': {
            'count': 0,
            'time': 0
        },
        'username': {
            'count': 0,
            'time': 0
        },
        'password': {
            'count': 0,
            'time': 0
        }
}

def count_call(to, timeout):
    if time.time() - called[to]['time'] <= timeout:
        called[to]['time'] = time.time()
        called[to]['count'] += 1
    else:
        called[to]['time'] = time.time() 
        called[to]['count'] = 0 


def service (nWords=2, acronym=False):
    wordfile = xp.locate_wordfile()
    words = xp.generate_wordlist(wordfile=wordfile, min_length=1, max_length=10)
    domainsfile = './wordfiles/domains.txt'
    domains = xp.generate_wordlist(wordfile=domainsfile, min_length=1, max_length=10)
    random_words = xp.generate_xkcdpassword(words, numwords=nWords, acrostic=acronym, random_delimiters = True, valid_delimiters = ['', '-', '.', '@'])
    random_domain = xp.generate_xkcdpassword(domains, 1)
    return f"{random_words[1: -1]}.{random_domain}"


def username (nWords=2, delimiter='-', acronym=False):
    # create a wordlist from the default wordfile
    wordfile = xp.locate_wordfile()
    mywords = xp.generate_wordlist(wordfile=wordfile, min_length=1, max_length=10)
    return (xp.generate_xkcdpassword(mywords, numwords=nWords, acrostic=acronym, delimiter=delimiter))


charset = '1234567890!@#$%^&*()_+-=qwertyuiop[]/\asdfghjkl;\'zxcvbnm,./`~QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?'
charset_len = len(charset)
rng = random.SystemRandom()
passprase_delimiters = ['_', '.', '-']
def password (nWords=8, max_chars=64, acronym=False):
    count_call('password', 1)
    if called['password']['count'] % 2 == 1: # give human friendly passprase 
        wordfile = xp.locate_wordfile()
        mywords = xp.generate_wordlist(wordfile=wordfile)
        gen = xp.generate_xkcdpassword(mywords, numwords=nWords, acrostic=acronym, delimiter=passprase_delimiters[rng.randrange(len(passprase_delimiters))])

        return gen
    else: # give password
        gen = ''
        for i in range(max_chars):
            gen += charset[rng.randrange(charset_len)]

        return gen

