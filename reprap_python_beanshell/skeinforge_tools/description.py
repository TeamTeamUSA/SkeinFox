"""
Description is a script to store a description of the profile.

The suggested format is a description, followed by a link to the profile post or web page.

To change the description preference, in a shell in the description folder type:
> python description.py

An example of using description from the python interpreter follows below.


> python
Python 2.5.1 (r251:54863, Sep 22 2007, 01:43:31)
[GCC 4.2.1 (SUSE Linux)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import description
>>> description.main()
This brings up the description preference dialog.

"""

from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from skeinforge_tools.skeinforge_utilities import preferences


__author__ = "Enrique Perez (perez_enrique@yahoo.com)"
__date__ = "$Date: 2008/21/04 $"
__license__ = "GPL 3.0"


def getPreferencesConstructor():
	"Get the preferences constructor."
	return DescriptionPreferences()


class DescriptionPreferences:
	"A class to handle the description preferences."
	def __init__( self ):
		"Set the default preferences, execute title & preferences fileName."
		#Set the default preferences.
		self.archive = []
		description = 'Write your description of the profile here.\n\nSuggested format is a description, followed by a link to the profile post or web page.'
		self.descriptionText = preferences.TextPreference().getFromValue( 'Description Text:', description )
		self.archive.append( self.descriptionText )
		#Create the archive, title of the dialog & preferences fileName.
		self.executeTitle = None
		self.saveCloseTitle = 'Save and Close'
		preferences.setHelpPreferencesFileNameTitleWindowPosition( self, 'skeinforge_tools.description.html' )


def main():
	"Display the file or directory dialog."
	preferences.startMainLoopFromConstructor( getPreferencesConstructor() )

if __name__ == "__main__":
	main()
