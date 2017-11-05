# WSMMR
This is our product from Fall 2017 HackPSU.

It is a single hacked together Twitter Data miner/plotter aimed at quantifying public perceptions of a company or product
to aid in market anaylsis.

Currently written for python 2.7 and calls on a load of dependencies. The script executes loads a GUI to take the user entered
parameters. The GUI also allows for users to edit suggested search terms before executing. Once the script is run via the GUI,
it calls to three parameters currently in default config in the script. These are left just because of the finite Twitter API calls.
The API authentication can also be done directly at the top of the source. The run-time is upwards of hours due to the fact to fact it
mines data and sleeps a lot to deal with the finite API call limits. The plot function can operate independently of the data mining. 
The data is historically saved to an output file in the root.
