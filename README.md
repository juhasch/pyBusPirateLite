# pyBusPirateLite
Python library for BusPirate

Based on code from Garrett Berg <cloudform511@gmail.com>

http://dangerousprototypes.com/2011/03/14/new-version-of-pybuspiratelite-python-library/

-------------------------

This is a rewrite for the pyBusPirateLite library.  Really more than a rewrite,
it is a complete overhaul.  I first started it with the intention of making a
library that allowed you to interface the bus pirate as if it were a microcontroller.
Well, that is still what the library is for, but as time has gone on (and I have used
the library more and more in creating my extend-able oscilloscope program) I went at
it and put recursion in all of the main functions.  The reason for this is because
sometimes the bus pirate gets stuck, or a communication is failed, etc, and you have
to try and re-send something.  I got really sick of continuouly resending things
explicitly in my code, so I made this library keep trying until it succeeded.
What this means is that if you call a function and it fails the first time,
the function will try again, as many as 15 times, to get it to work.  If it doesn't
work, it probably means you don't have the bus pirate connected :D  If it doesn't
work it will simply raise an error, as there is probably an error in your code,
not mine (and if it is in mine, then tell me so that I can say this with more
confidence! )

So take a look at the library and try it out with your old code.  Let me know what
you think!

Use the library as follows:

1) instantiate a UC object:
my_buspirate = UC()

2) connect:
my_buspirate.connect() 	#will normally work in linux.

# OR

my_buspirate.connect(port)	#define your own port

3) do stuff:
my_buspirate.enter_bb()		#always do first after connected.  gets into bit bang

my_buspirate.enter_i2c() # get into i2c mode
... do stuff in i2c...

my_buspirate.enter_bb() #get back into bb mode

my_buspirate.configure_peripherals(
		power = 'on', pullups = 'on') # turn on power and
									  # pullups, can be used in any
									  # mode

my_buspirate.set_dir(0x00) # set the direction of all the pins to output

my_buspirate.set_port(0b10101) # set the pins to output 10101
							   # (AUX is the high pin, MISO the low pin.
							   # Specify reverse order (AUX still high, but
							   # CS low) by setting translate = False)


...etc...

almost everything in the file BitBang.py implements recursion--so you can be sure that
if you tell the bus pirate to do something, it will do it!
