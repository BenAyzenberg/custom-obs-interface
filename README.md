# Setup Guide

## Code Stuff

* Download the project
* Install python, version 3.13 or later
    * https://www.python.org/downloads/
* Run install_packages.bat
    * Linux and Mac currently not supported but should be relatively simple for future implemenation
* (Optional) install notepad++ for simple code editing
    * https://notepad-plus-plus.org/downloads/
    * current version on the left side

## Setup the secrets.env


* Find the template.env and save a copy as secrets.env
* Use https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/ to find the TWITCH_BROADCASTER_ID
* Get the OBS port and password from Tools/Websocket Server Settings
* Create an application using the https://dev.twitch.tv/console
    * set the OAuthRedirect to http://localhost:3000
    * Copy the client ID into the secrets.env
* Create an access token by running the generate_twitch_access_token.py
    * This must be done after the Twitch Client ID is set 
    * You will be taken to a login and authorization page, once putting in your information you will be redirected to a new page
    * Your access token will be contained in the url of the webpage in the form `acesstoken=YOURTOKEN&scope`

### DO NOT SHOW THIS FILE ON STREAM

## Set up OBS

* The default setup uses a text field in obs called `RewardText`, you can configure this how you like since the code only chages the text contained
* Create a scene called `RewardTextSubScene` for placing and animation
    * https://obsproject.com/kb/dve-animating-sources-tutorial for a reference for animation
* Add the SubScene to the sources of any pages you want to display the text

## Configure it to make it yours

Below is an example of a piece of code use Notepad++ or any code editor to change it to your liking
* Include sound effects
* Adjust the time it lasts on screen
* Choose to or not to automatically complete the redemption

### IMPORTANT NOTES!

* Ensure that the section after `redemption['title'] =` matches the name of your twitch redepmtion
* Ensure that `noise.play()` matches the name of your sound effect file that you want to play
```
if redemption['title'] == 'Hydrate':
                obs.set_text('RewardText', 'Hydrate')
                obs.set_source_visibility(currentScene, 'RewardTextSubScene', True)
                noise.play('Hydrate')
                time.sleep(10)
                obs.set_source_visibility(currentScene, 'RewardTextSubScene', False)
                completeStatus = True
```

## How to Run

If you've done everything in the setup then running should be as simple as running `main.py`

It should run quietly in the background of your stream automatically processing your channel point redemptions.