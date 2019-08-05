# grau
a geek compatible (text based) control/user interface for an mqtt based home automation system

This little script enables you to control your smart home automation stuff in a more geeky way. Nobody really likes web interfaces anyway...

How to configure this?
- put your mqtt brokers hostname, port and maybe credentials into grau.cfg
- put all your smart mqtt devices into grau.csv
- run grau.py and have fun

How to use this?
Just call the script grau.py and read the help.

or read this:

To switch something (with some alias like "lightOutdoors") on you can do something like this:

grau on lightoutdoors
grau on lightOutdoors (cases are ignored)
grau on lighto\*
grau on light\*

Of course if there is a an alias like lightIndoors

grau on light\* 

will switch on both lightOutdoors and lightIndoors.

You might want to check what is going to happen using the list feature:

grau list light\*

This little wildcard feature can be very useful, if you chose your aliases wisely.
In our hackerspace all lights are named according to the cardinal direction and the name of the room they are in:
´lightLabSouth
lightLabNorth
lightStudioSouth
lightStudioNorth
lightKitchenSouth
lightKitchenNorth´

and so on.

So switchting off all lights becomes very easy:

grau off light\*
