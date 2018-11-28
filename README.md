# cigobot
Discord bot

Go to [Discord developer site](https://discordapp.com/developers), sign in with discord login and create bot.

Go to [Authorize url](https://discordapp.com/oauth2/authorize?client_id=Bot_Client_ID&scope=bot&permissions=8) and add bot to your server (Switch out Bot_Client_ID with your client ID)

Create auth.json file and insert bot token
```
{
  "token": "TOKEN"
}
```
Add `ffmpeg-4.0.2-win64-static/bin` to PATH

Run `./gradlew setup` 

Run `./gradlew run`

add any mp3 files to audio folder
