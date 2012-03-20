# GAME: is X the sameAs Y? #

## README ##

The idea of this script is quite simple: it is designed as a game, where the user is asked to assess whether
the matching between a Smith-Perseus URI and a DBpedia URI which is suggested by the software is 
likely to be correct or not.

How the suggestion mechanism work? The Smith's dictionary has an entry for each entity as does Wiki-/DBpedia.


## USAGE ##

To start the game in iterative mode (you'll be asked at every "round" if you want to quit) just type

    python play.py

The code comes with a list of IDs, each corresponding to an entry in the Smith's dictionary. You may want to launch the game for one particular entity.
In this case try

    python play.py --id sosicles-1

or

    python play.py --id sosicles-1

![screenshot](http://dl.dropbox.com/u/1015658/sosicles-1_2.png)
	

There are cases where the wikipedia entry is taken (almost) entirely from the Smith's entry from Perseus (as a result, the LSI score is 1 or close to 1).

Some interesting examples:

    python play.py --id albinus-24
    python play.py --id lysianassa-1
    python play.py --id fannia-2
    python play.py --id nicanor-saevius-1

![screenshot](http://dl.dropbox.com/u/1015658/serena-1.png)

## TODO ##


		