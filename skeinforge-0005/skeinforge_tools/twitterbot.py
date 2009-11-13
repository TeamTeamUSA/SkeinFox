"""
Twitterbot is a tool to insert Twitterbot M-code into a gcode file so that a modified version of ReplicatorG can tweet printing progress to a Twitter account.
Rick Pollack wrote the code to enable ReplicatorG to call the Twitter API via the twitter4j library.
You can get the necessary files to modify ReplicatorG here: http://makerbot.googlegroups.com/web/TwitterBot+Src+Update+1.zip
This tool has been tested with Skeinforge-0005, Skeinforge-0006, and ReplicatorG-0009.

The default 'Activate Twitterbot' checkbox is off.  When it is on, the functions described below will be called. When it is off, the functions
will not be called.

The tool's Preferences are:

'Activate Twitterbot'   - Check this to enable the tool. Default is un-checked or off.
'Twitter Username'      - Username for the Twitter account. Default is empty.
'Twitter Password'      - Password for the Twitter account. Default is empty.
'Layers Between Tweets' - The number of layers between each tweet, e.g., 3 means tweet each 3rd layer. Default is 10.
'Hashtag(s)'            - Space-delimited hashtags to append to each tweet. Default is #MakerBot #Twitterbot.

Since your Twitter credentials are written to the generated gcode file, either remove them before sharing the file, or re-run with 'Activate Twitterbot' off. 

IMPORTANT! If you forget to remove your credentials after sharing a file, change your Twitter password immediately!

NOTE: For tall, and therefore many layered source files, it is quite possible to exceed the Twitter rate limit with a single print.
For more information see: http://apiwiki.twitter.com/Rate-limiting
This may be addressed in a future version of twitterbot.

To run twitterbot, in a shell type:
> python twitterbot.py

The following examples twitterbot - add Twitter M-code to - the files Screw Holder Bottom.gcode & Screw Holder Bottom.stl.  The examples are run in a terminal in the
folder which contains Screw Holder Bottom.gcode, Screw Holder Bottom.stl and twitterbot.py.  The twitterbot function will twitterbot if 'Activate Twitterbot' is true,
which can be set in the dialog or by changing the preferences file 'twitterbot.csv' in the '.skeinforge' folder in your home directory
with a text editor or a spreadsheet program set to separate tabs.  The functions writeOutput and getTwitterbotChainGcode check
to see if the text has been twitterbotted, if not they call getUnpauseChainGcode in unpause.py to unpause the text; once they have the
unpaused text, then they twitterbot.


> python twitterbot.py
This brings up the dialog, after clicking 'Twitterbot', the following is printed:
File Screw Holder Bottom.stl is being chain twitterbotted.
The twitterbotted file is saved as Screw Holder Bottom_twitterbot.gcode


> python twitterbot.py Screw Holder Bottom.stl
File Screw Holder Bottom.stl is being chain twitterbotted.
The twitterbotted file is saved as Screw Holder Bottom_twitterbot.gcode


> python
Python 2.5.1 (r251:54863, Jun 17 2009, 20:37:34) 
[GCC 4.0.1 (Apple Inc. build 5465)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import twitterbot
>>> twitterbot.main()
This brings up the twitterbot dialog.


>>> twitterbot.writeOutput()
Screw Holder Bottom.stl
File Screw Holder Bottom.stl is being chain twitterbotted.
The twitterbotted file is saved as Screw Holder Bottom_twitterbot.gcode


>>> twitter.getTwitterbotGcode("
( GCode generated by May 8, 2008 carve.py )
( Extruder Initialization )
..
many lines of gcode
..
")


>>> twitterbot.getTwitterbotChainGcode("
( GCode generated by May 8, 2008 carve.py )
( Extruder Initialization )
..
many lines of gcode
..
")

"""

#TODO:
#      * Make Starting, Printing layer, and Finishing, messages configurable, i.e., add them to Preferences. Need to figure out string replacing in Python first
#      * Add quips to Preferences so humorous tweets can be sent randomly or when certain events occur, e.g., What's that smell?, Copper is the new black!, This print sure is ugly!, Only at layer 5? I need a rest!
#      * To reduce the number of tweets per print, calculate the number of lines in the file (maybe G lines instead) and print a configurable percentage (dropdown menu?), 
#      e.g., 25 means tweet only when every 25% of the print is printing. 25 would result in 6 tweets (1 start tweet + 4 progress tweets + 1 end tweet)
#      * If Layers Between Tweets is less than 0 change to default, i.e., 5, and save to Preferencs file [twitterbot.csv]

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

#from skeinforge_tools.skeinforge_utilities import euclidean
from skeinforge_tools.skeinforge_utilities import gcodec
from skeinforge_tools.skeinforge_utilities import preferences
from skeinforge_tools import analyze
from skeinforge_tools import unpause
from skeinforge_tools.skeinforge_utilities import interpret
from skeinforge_tools import polyfile
import cStringIO
#import math
import sys
import os
import time


__author__ = "Miles Lightwood (m@teamteamusa.com)"
__date__ = "$Date: 2009/08/11 $"
__version__ = "$0.2 $"
__license__ = "GPL 3.0"

def getTwitterbotChainGcode( fileName, gcodeText, twitterbotPreferences = None ):
	"Add Twitterbot M-code to a gcode text.  Chain twitterbot the gcode if it is not already twitterbotted."
	gcodeText = gcodec.getGcodeFileText( fileName, gcodeText )
	if not gcodec.isProcedureDone( gcodeText, 'unpause' ):
		gcodeText = unpause.getUnpauseChainGcode( fileName, gcodeText )
		print( 'getTwitterbotChainGcode(fileName): ' + fileName )
	return getTwitterbotGcode( gcodeText, fileName, twitterbotPreferences )

def getTwitterbotGcode( gcodeText, fileName, twitterbotPreferences = None ):
	"Add Twitterbot M-code to a gcode text."
	if gcodeText == '':
		return ''
	if gcodec.isProcedureDone( gcodeText, 'twitterbot' ):
		return gcodeText
	if twitterbotPreferences == None:
		twitterbotPreferences = TwitterbotPreferences()
		preferences.readPreferences( twitterbotPreferences )
	if not twitterbotPreferences.activateTwitterbot.value:
		return gcodeText
	skein = TwitterbotSkein()
	skein.setGcodeFilePathAndName( fileName )
	skein.parseGcode( gcodeText, twitterbotPreferences )
	return skein.output.getvalue()

def writeOutput( fileName = '' ):
	"Twitterbot a gcode file.  Chain twitterbot the gcode if it is not already twitterbotted.  If no fileName is specified, twitterbot the first unmodified gcode file in this folder."
	if fileName == '':
		unmodified = interpret.getGNUTranslatorFilesUnmodified()
		if len( unmodified ) == 0:
			print( "There are no unmodified gcode files in this folder." )
			return
		fileName = unmodified[ 0 ]
	twitterbotPreferences = TwitterbotPreferences()
	preferences.readPreferences( twitterbotPreferences )
	startTime = time.time()
	print( 'File ' + gcodec.getSummarizedFilename( fileName ) + ' is being chain twitterbotted.' )
	suffixFilename = fileName[ : fileName.rfind( '.' ) ] + '_twitterbot.gcode'
	twitterbotGcode = getTwitterbotChainGcode( fileName, '', twitterbotPreferences )
	if twitterbotGcode == '':
		return
	gcodec.writeFileText( suffixFilename, twitterbotGcode )
	print( 'The twitterbotted file is saved as ' + gcodec.getSummarizedFilename( suffixFilename ) )
	analyze.writeOutput( suffixFilename, twitterbotGcode )
	print( 'It took ' + str( int( round( time.time() - startTime ) ) ) + ' seconds to add Twitterbot codes to the file.' )
			
class TwitterbotPreferences:
	"A class to handle the twitterbot preferences."
	def __init__( self ):
		"Set the default preferences, execute title & preferences fileName."
		self.archive = []
		self.activateTwitterbot = preferences.BooleanPreference().getFromValue( 'Activate Twitterbot', False )
		self.archive.append( self.activateTwitterbot )
		self.twitterUsername = preferences.StringPreference().getFromValue( 'Twitter Username:', '' )
		self.archive.append( self.twitterUsername )
		self.twitterPassword = preferences.StringPreference().getFromValue( 'Twitter Password:', '' )
		self.archive.append( self.twitterPassword )
		self.layersBetweenTweets = preferences.StringPreference().getFromValue( 'Layers Between Tweets:', '10' )
		self.archive.append( self.layersBetweenTweets )
		self.twitterHashtags = preferences.StringPreference().getFromValue( 'Hashtag(s):', '#MakerBot #Twitterbot' )
		self.archive.append( self.twitterHashtags )
		self.fileNameInput = preferences.Filename().getFromFilename( interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File to insert Twitterbot code into', '' )
		self.archive.append( self.fileNameInput )
		#Create the archive, title of the execute button, title of the dialog & preferences fileName.
		self.executeTitle = 'Twitterbot'
		self.saveTitle = 'Save Preferences'
		preferences.setHelpPreferencesFileNameTitleWindowPosition( self, 'skeinforge_tools.twitterbot.html' )

	def execute( self ):
		"Twitterbot button has been clicked."
		fileNames = polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, interpret.getImportPluginFilenames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )

class TwitterbotSkein:
	"A class to insert Twitter M-code into a gcode file."
	def __init__( self ):
		self.lineIndex = 0
		self.lines = None
		self.output = cStringIO.StringIO()
		# Twitterbot
		self.gcodeFilePathAndName = ''
		self.gcodeFileName = ''
		self.gcodeFilePath = ''
		self.savedGcodeFilename = ''
		self.layerIndex = 1
		self.twitterbotClass = 'TwitterBot'
		self.mCodeInit = 'M997'
		self.mCodeMessage = 'M998'
		# Not used yet
		self.mCodeCleanup = 'M999'

	def setGcodeFilePathAndName( self, gcodeFilePathAndName ):
		"Save path and filename of gcode file to this class. Called by getTwitterbotGcode()"
		self.gcodeFilePathAndName = gcodeFilePathAndName
	
	def addLine( self, line ):
		"Add a line of text and a newline to the output."
		self.output.write( line + "\n" )

	def parseGcode( self, gcodeText, twitterbotPreferences ):
		"Parse gcode text and store the twitterbot gcode."
		self.lines = gcodec.getTextLines( gcodeText )
		self.twitterUsername = twitterbotPreferences.twitterUsername.value
		self.twitterPassword = twitterbotPreferences.twitterPassword.value
		self.layersBetweenTweets = twitterbotPreferences.layersBetweenTweets.value
		if int( self.layersBetweenTweets ) < 1:
			self.layersBetweenTweets = '5'
		self.twitterHashtags = twitterbotPreferences.twitterHashtags.value
		#self.fileName = twitterbotPreferences.fileNameInput.value
		self.parseInitialization( twitterbotPreferences )
		#print( "===> self.lineIndex: " + str( self.lineIndex ) )	
		for self.lineIndex in xrange( self.lineIndex, len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
		#	print( '===> Parsing line ' + str( self.lineIndex ) + ': ' + line )
			self.parseLine( line )

	def parseInitialization( self, twitterbotPreferences ):
		"Parse gcode initialization and store the parameters."
		for self.lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ self.lineIndex ]
			splitLine = line.split()
			firstWord = gcodec.getFirstWord( splitLine )
			if firstWord == '(<extruderInitialization>)':
				self.addLine( '(Twitterbot initialization)' )
				self.addLine( self.mCodeInit + ' ' + self.twitterbotClass + ' ' + self.twitterUsername + ',' + self.twitterPassword )
				self.getSavedGCodeFileName()
				print( 'self.savedGcodeFilename: ' + self.savedGcodeFilename )
				self.addLine( self.createMessage( 'Starting ' + self.savedGcodeFilename + '...' ) )
			elif firstWord == '(</extruderInitialization>)': 
				self.addLine( '(<procedureDone> twitterbot </procedureDone>)' )
				return
			self.addLine( line )

	def parseLine( self, line ):
		"Parse a gcode line and add Twitter M-code to it."
		splitLine = line.split()
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[ 0 ]
		#print( "===> firstWord: " + firstWord )	
		if firstWord == '(<layer>':
			if self.layerIndex == 1:
				self.addLine( self.createMessage( self.savedGcodeFilename + ': layer ' + str( self.layerIndex ) ) )
			if self.layerIndex % int( self.layersBetweenTweets ) == 0:
				self.addLine( self.createMessage( self.savedGcodeFilename + ': layer ' + str( self.layerIndex ) ) )
			self.layerIndex = self.layerIndex + 1
		elif firstWord == '(</extrusion>)':
			self.getSavedGCodeFileName()
			self.addLine( self.createMessage( 'Finished ' + self.savedGcodeFilename + '!' ) )			
		self.addLine( line )

	def getSavedGCodeFileName( self ):
		"Get original filename and change to the skeinforged one, i.e., ???_export.gcode."
		if self.savedGcodeFilename == '': 
			self.gcodeFilePath,self.gcodeFileName = os.path.split( self.gcodeFilePathAndName )
			self.savedGcodeFilename = self.gcodeFileName[ : self.gcodeFileName.rfind( '.' ) ] + '_export.gcode'
		
	def createMessage( self, messageText ):
		"Add the message M-Code to a string and return it."
		msg = self.mCodeMessage + " message '" + messageText + " " + self.twitterHashtags + "'"
		#print( '===> msg: ' + msg )
		return msg

def main( hashtable = None ):
	"Display the Twitterbot dialog."
	if len( sys.argv ) > 1:
		writeOutput( ' '.join( sys.argv[ 1 : ] ) )
	else:
		preferences.displayDialog( TwitterbotPreferences() )

if __name__ == "__main__":
	main()