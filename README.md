Python-Minecraft-Arcade
=======================

Various games from the PyGame examples on Raspberry Pi implemented in Minecraft world using the Minecraft API

To use these examples first you need to have Minecraft installed:

1. Go to http://pi.minecraft.net
2. Click on *Downloads* in the menu bar
3. Click on the download link
  * As of 15th May 2014 the link was:
  * https://s3.amazonaws.com/assets.minecraft.net/pi/minecraft-pi-0.1.1.tar.gz

4. Unzip/Uncompress this file by navigating to it in the *File Manager* and right clicking on it and click on *Extract here*
5. Go into the newly created folder *mcpi*
6. Double click on the file *minecraft-pi* and choose *Execute*
7. This will have opened up Minecraft, you need to start a game and create a new world

You also need to get the Python API and the blockData.py file from the Python-Minecraft-Examples before you can run these examples. For the Python API you can make a symbolic link to the API included with the minecraft download, or copy it into this folder from there. Alternatively you could obtain it from the Python-Minecraft-Examples repository.

Open LXTerminal change directory to where this readme file is located and at the prompt type:

`svn export https://github.com/hashbangstudio/Python-Minecraft-Examples/trunk/mcpi`

Now press enter, when this operation has completed type the following at the prompt and press enter:

`svn export https://github.com/hashbangstudio/Python-Minecraft-Examples/trunk/blockData.py`

Now once Minecraft is running and you are in the world you can run the examples.

To run examples, open LXTerminal if you haven't already, change directory to where this file is located and at the prompt type:

`python file.py`

Where *file.py* is replaced by your chosen example

NOTE: There is an unknown bug in inkspill.py. When quitting the inkspill.py the restore checkpoint appears to work but after leaving and re-entering the minecraft world the game boards may return.
