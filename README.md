# YouTubeForAlexa
An Alexa Skill For Play YouTube with Echo Devices
## Unofficial YouTube skill for Alexa
__Last update: 24 Jan 2021 (USE Python 3.7 in Amazon AWS)__

# If you like my work buy me a coffe: [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/paypalme/wes93)

## Features
* Play audio from YouTube videos
* Play video (if supported) on live videos or if you ask for just one specific video (command 8)
* Makes a list of all the videos played, in the Alexa app

## Launching
* In English, say "Alexa, launch YouTube".
* In German, say "Alexa, öffne YouTube".
* In Italian, say "Alexa, avvia YouTube".
* In Spanish, say "Alexa, abrir YouTube".

## Skill Commands

1. Play a video, eg "Alexa, ask YouTube to play Gangnam Style"
2. Play a playlist, eg "Alexa, ask YouTube to play playlist Ultimate Beyonce"
3. Play a channel, eg "Alexa, ask YouTube to play channel Fall Out Boy Vevo"
4. You can replace "play" with "shuffle" to get a randomized version of the search results/channel/playlist, eg "Alexa, ask YouTube to shuffle channel Nicki Minaj"
5. Next / Previous / Start Over / Pause / Resume should all work
6. Ask what is playing by "Alexa, ask YouTube what song is playing" (or just "Alexa, can you repeat that?" should tell you)
7. Skip forward or back in the video by "Alexa, ask YouTube to skip forward/backward to/by one minute and one second"
8. Just play one video by "Alexa, ask YouTube to play one video Gangnam Style". You can switch in and out of "autoplay" mode by "Alexa, ask YouTube to turn on/off autoplay."
9. Find the current time in the video by "Alexa, ask YouTube what is the timestamp?"
11. Play related videos, by "Alexa, ask YouTube to play more like this". This is a YouTube feature, don't ask me why it plays what it plays.

Command 7 doesn't seem to work on Generation 1 Echo's, no idea why.
Commands 8, 9, 10 and 11 are only available in English at the moment. Need them in your language? Drop me an email and we can figure out the translation.

## Known issues

1. It appears this skill only works on Amazon Echo products, not on 3rd party products that support Alexa. If you get it to work on another device, please let me know.
2. Live videos work on Gen 2 devices onwards, not on the original Gen 1 Echo.
     
## __Setup Instructions__
## Obtain The AWS Lambda ARN
## Google Part
1. Wee Need a YouTube Developer Key.
2. Go to: https://developers.google.com/ login or create a new account
3. Go to: https://console.developers.google.com/project and click on "Make a New Project"
4. Give it a name, for example “Updated API Token”
5. Click on “Create”
6. Wait a few seconds that the project is created (You can check by a notification in upper right corner of the screen)
7. Open in a new page: https://console.developers.google.com/apis/library?project=tester-api-key
8. Select “Chose a Project” and click on the newly created project (“Updated API Token”)
9. From the search bar write “youtube” and select “YouTube Data API v3”
10. Click on it and select “ENABLE”
11. Click on "Create Credentials"
12. Set like this:
      - “Which API are you using?”: YouTube Data API v3
      - “From where you call the API?”: Server web (ex. node.js, Tomcat)
      - “Which data you use?”: Public Data
      - Click on “Which credentials i need?”
13.  After some seconds you will see under “Get your credentials” the key that wee need.
14. **COPY** and **SAVE** the key in the notepad.
## Amazon AWS Part
###### For people that don'y have an Amazon AWS Account
1. Go to: http://aws.amazon.com
2. Click on “Open Console” in upper right
3. Create a new AWS Account by clicking on “Create a new AWS account”
4. ***During the registration SELECT THE FREE BASIC PLAN! (If you don't see a page to chose the plan means that you have the free basic plan selected).*** 
   ***For confirm your identity Amazon will ask for a Credit Card, THIS IS NORMAL, you don't pay anythig but you need to have at least 1 € on the card for pre-authorization. To confirm the activation of your account Amazon can take from some minutes to some hours.***
   ***You will se this page:***

   ***To speed up the process try to click on “Complete your AWS registration” and confirm you mobile number. If will take more than 24 hours try to contact the support.***
5. After the activation of the Account go here: http://aws.amazon.com.
6. Click on “Open Console”.
7. ***VERY IMPORTANT check the region in the upper right corner “N. Virginia” an select the correct region, EX:***
   ***US East (N.Virginia) region for English (US) or English (CA) skills***
   ***EU (Ireland) region for English (UK), English (IN), German (DE), Spanish (ES) or French (FR) skills***
   ***US West (Oregon) region for Japanese and English (AU) skills.***
8. Click on Services and search for Lambda
9. Click on Create Function
10. Select Plan "Author From Scratch
    Give a Function Name and chose Python 3.7 for Runtime
11. Click on Choose or create an execution role
    Put "basic_lambda_execution" in Role Name and "Basic Lambda@Edge Permissions (for CloudFront trigger)" in Policy templates -             optional
12. After the creation select Add Trigger and chose "Alexa Skills Kit".
13. Disable Skill ID verification
14. Near Function Code click Actions and Upload a Zip File, upload this file:            https://github.com/wes1993/YouTubeForAlexa/blob/master/YouTubeForAlexaLambda.zip
15. In the Lambda Funcion Page near Environment variables click edit (in the bottom of the page).
16. Add Environment variables with DEVELOPER_KEY and the code that we have taken from Google (saved before).
17. In the Basic settings fields set 512 in Memory (MB) and 10 Sec in Timeout
18. Click save and copy the ARN - in the top right corner of the page.



## Setting Up the Alexa Skill
1. Go to the Alexa Console (https://developer.amazon.com/alexa/console/ask)
2. If you have not registered as an Amazon Developer then you will need to do so. Fill in your details and ensure you answer "NO" for "Do you plan to monetize apps by charging for apps or selling in-app items" and "Do you plan to monetize apps by displaying ads from the Amazon Mobile Ad Network or Mobile Associates?"
3. Once you are logged into your account click "Create Skill" on the right hand side.
4. Give your skill any name, eg "My YouTube Skill".
5. **Important** Set the language to whatever your Echo device is set to. If you are not sure, go to the Alexa app, go to Settings, Device Settings, then click on your Echo device, and look under Language. If your Echo is set to English (UK), then the skill must be English (UK), other types of English will not work!
6. Choose "Custom" as your model, and "Provision Your Own" as your method, then click "Create Skill". On the template page, choose "Start from scratch".
7. On the left hand side, click "JSON Editor".
8. Delete everything in the text box, and copy in the text from https://raw.githubusercontent.com/wes1993/YouTubeForAlexa/master/InteractionModel/InteractionModel_en.json, (or use InteractionModel_fr.json, InteractionModel_it.json, InteractionModel_de.json, InteractionModel_es.json, InteractionModel_ja.json or InteractionModel_pt-br.json for French, Italian, German, Spanish, Japanese or Brazilian Portuguese.)
9. Click "Save Model" at the top.
10. Click "Interfaces" in the menu on the left, and enable "Audio Player" and "Video App". Click "Save Interfaces".
11. Click "Endpoint" in the menu on the left, and select "AWS Lambda ARN". Under "Default Region", put the ARN (from the Amazon AWS    Part).
12. Click "Save Endpoints"
13. Click "Permissions", at the very bottom on the left.
14. Turn on "Lists Read" and "Lists Write".
15. Click "Custom" in the menu on the left.
16. Click "Invocation" in the menu on the left.
17. If you want to call the skill anything other than "youtube", change it here. Click "Save Model" if you change anything.
18. Click "Build Model". This will take a minute, be patient. It should tell you if it succeeded.
19. **Important:** At the top, click "Test". Where it says "Test is disabled for this skill", change the dropdown from "Off" to "Development".

## Keeping a list of what you have played
This skill can make a list of the last 90 videos played, but you have to give it permissions in the Alexa app:
1. Go to the Alexa app on your phone. In the menu, go to "Skills & Games", then "Your Skills", then scroll to the right and click on "Dev".
2. Click on your YouTube skill. You should see a button marked "Settings", click that.
3. Then press on "Manage Settings", and tick the boxes marked "Lists Read Access" and "Lists Write Access", and press "Save Settings".
4. Say "Alexa, launch YouTube", that will create the list, and from then on, videos will be added to it.
The list can be viewed in the Alexa app, click Lists from the main menu.

That's it!

## Extra step (Optional):
Unfortunately for some video Youtube pretend that the request (Amazon AWS Server) come from the client that listen the video (Alexa Device).
For fixing this there are some ways:
Simple Way but not 100% working:
##### 1. Using a 3RD party API service (you need to use your card):
  1. Go to this link: https://rapidapi.com/convertisseur.mp3.video/api/download-video-youtube1, and register to the website (the api if free only for the first 1000 request in        24H, it's about 50 hours of video with duration of 3 minutes)
  2. After you are registered and obtained your api key create the following Variable in the Amazon AWS Lambda:
     - apikey with your api key from rapidapi
     - rapidapi with value true
Simple Way also, work 100% but you must run a server in your home (Like Raspberry or others) and have static IP or DDNS service like duckdns etc.:
##### 2. Using your Proxy Server in your LAN with the alexa devices:
  1. install Docker: https://docs.docker.com/get-docker/ on the server
  2. install this proxy server: https://hub.docker.com/r/vimagick/tinyproxy, using this command: docker pull vimagick/tinyproxy.
  3. Chose the port where the proxy is exposed and change <port> with chosen port then run the proxy(container in docker) with this command: 
     '''docker run --name TinyProxy --restart=always -d -p <port>:8888 -v TinyProxy_Config:/etc/tinyproxy vimagick/tinyproxy:latest'''
  5. You need to add this variables in the Amazon AWS Lambda:
     - proxy_enabled with value true
     - proxy with value yourip/ddns:8888

## Favorites List
If you enable list permissions as above, the skill will make a second list called "YouTube Favorites". You can use this to set shortcuts to videos you want often, or that are hard to find in search results.
Look in the lists in the Alexa app, or at alexa.amazon.com, and you will see how it works. You add an item like:

That song I like | https://youtu.be/ZyhrYis509A

super awesome playlist | https://www.youtube.com/playlist?list=PL1EQjK4xc6hsirkCQq-MHfmUqGMkSgUTn

Then you can just say "Alexa, ask YouTube to play that song I like" or "Alexa, ask YouTube to play super awesome playlist", and it shoulds play whatever you have linked. The | character separates the name from the link (on mobile it can be hard to find, on Android go to the second page of symbols).
If you find a video/playlist that you like, and want to add it to your favorites, you can just say "Alexa, ask YouTube to add this video/playlist/ to my favorites". It will then appear in the list, but you probably want to edit the name, as it just takes the video title.

## FAQ
* **Alexa tells me she can't find any supported video skills, what does that mean?**
Alexa is trying to be too clever, and not launching this skill. Start your request by saying 'Alexa, launch YouTube' and then when she says 'Welcome to YouTube', ask for the video you want.
* **She still says she can't find any video skills.**
Make sure to follow step 19 above, enabling Testing for Development.
* **She still says she can't find any video skills!**
Try using a different word to start the skill. In English, say "Alexa, launch YouTube". In German, say "Alexa, öffne YouTube". In Italian, say "Alexa, avvia YouTube". In Spanish, say "Alexa, abrir YouTube".
* **I am getting another issue, can you fix it?**
Hopefully, drop me an email!
* **If I try and test in the Developer Console, it says 'Unsupported Directive. AudioPlayer is currently an unsupported namespace. Check the device log for more information.'**
That is normal, the Developer Console doesn't play audio. You just need to enable testing through the Developer Console, then you can use the skill through your Alexa device.
* **Why don't more videos work as video?**
Alexa doesn't provide any ability to enqueue videos, so you only get one video, then it stops. So it only plays videos if you ask for one specific video, or if it is a live video.
