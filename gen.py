from xkcdpass import xkcd_password as xp

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