# fantasy football lineup optimizer project

json folder:
This folder contains all the json files used in our project. This includes
our webscraped data, the random and realistic lineups used for evaluation, and  
the results from our evaluation. 

webscraping folder:
This folder contains the code we used to webscrape the data we used from various
websites.

allie_rostergen.py:
This file contains a function to generate a random lineup based on the players
in the 2024 NFL season. We used this function to generate our random lineups.
This file also contains a function to initiate the dictionary we used to keep
track of player data and our weights which we used in our 4 optimization methods.

calc.py:
This file contains code to calculate the average evaluation time per week and the
average overall score.

helperfunct.py:
This file contains various helper functions that we used. This includes code
to calculate the actual score of a lineup, the projected score of a lineup, 
generating a random roster, calculating a weighted average, calculating a position
vector, and creating the score vector. 

integer_program.py:
This file contains the implementation of our integer program.

linear_evaluate.py:
This file contains code to run 15 weeks of a normal season and pick a lineup. It
also contains code to check if the lineup is valid. 

linear_programs.py:
This file contains the implementation of our linear programs.

method_comparison.py:
This file contains code to run 15 weeks of a normal season and pick a lineup. It
does this for the integer and linear programs. 

stochastic_evaluate.py:
This file contains code to run 15 weeks of a normal season and pick a lineup. It
uses the stochastic optimization.

stochastic_montecarlo.py:
This file contains code to simulate a player score based on random variables,
generate all possible lineups given a roster, and run a monte carlo simulation.