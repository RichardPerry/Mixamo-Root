# Mixamo Root
The majority of the functionality was implemented by Johngoss725's original contributions,
which were published under a Creative Commons 1.0 Universal License (CC0-1.0) located at:
<https://github.com/Johngoss725/Mixamo-To-Godot>.

I have simply reworked some of the functions to be less error prone, and to work better inside an addon.


This is a Blender 2.8+ script for importing Mixamo Models and adding root bones to it.
This has only been tested with importing fbx files and exporting to a collection for Godot 4.

The addon may be compatible with other versions or engines, but as those have not been tested, they are not guaranteed to work.
 
This addon does the following things:
1) Imports the Mixamo animations from the folder you specify.
2) Adds a root motion bone to the skeleton and keyframes.
3) Removes all but one imported armatures, as it assumes all animations imported are tailored to a single model.
4) [Optionally] Renames the armature to remove the prefix.

Note, due to bugs with Godot (As this addon was designed with its compatibility in mind) it assumes that the desired start frame for actions is 0 and will be adjusted as such. Additionally, all animations imported will be set to start from 0. If this is not desired their keyframes can be shifted manually in the action editor by selecting the animation, moving the mouse over to the panel, typing 'A > G > X' and using the mouse to drag the frames.

A future feature may be added to allow the addon to do this automatically, however due to quirks in the way imports work this has not yet been implemented.

# How to use:
Install and enable the addon by downloading this repo as a zip file and directly importing it from the preferences menu.
Once activate a 'Mixamo Root' panel should be visible in the Mixamo tab. Specify the folder with your Mixamo animations and import them into the file by pressing 'Import Animations'

The file can also be run as a script under the blender scripting console, as long as you replace the path parameter in the main function with your animation library path.

