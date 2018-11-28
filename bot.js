var Discord = require('discord.io');
var logger = require('winston');
var auth = require('./auth.json');
var fs = require("fs");
// Configure logger settings
logger.remove(logger.transports.Console);
logger.add(new logger.transports.Console, {
    colorize: true
});
logger.level = 'debug';
// Initialize Discord Bot
var bot = new Discord.Client({
   token: auth.token,
   autorun: true
});


function playSound(name, channelId, voiceChannels) {
    if (!channelId) {
        channelId = voiceChannels[0].id;
    }

    if(!fileExists(name)) {
        return;
    }

    bot.joinVoiceChannel(channelId, function(error, events) {
        //Check to see if any errors happen while joining.
        if (error) return console.error(error);
      
        //Then get the audio context
        bot.getAudioContext(channelId, function(error, stream) {
            //Once again, check to see if any errors exist
            if (error) return console.error(error);
            //Create a stream to your file and pipe it to the stream
            //Without {end: false}, it would close up the stream, so make sure to include that.
          
            var rs = fs.createReadStream(`./audio/${name}.mp3`);
            rs.on('error', function (error) {
                bot.leaveVoiceChannel(channelId);
            });
            rs.on('readable', function () {
                rs.pipe(stream, {end: false}); 
            });
      
            //The stream fires `done` when it's got nothing else to send to Discord.
            stream.on('done', function() {
                //Handle
                bot.leaveVoiceChannel(channelId);
            });
        });
    });
}

function fileExists(name) {
    var files = fs.readdirSync('./audio/');
    return files.some(function(value, index, array) {
        return value.endsWith('.mp3') && value.slice(0, value.length - 4) === name;
    });
}

function outputHelp(channelID) {
    var files = fs.readdirSync('./audio/');
    var output = 'commands: \n';
    files.forEach(function(value, index, array) {
        if (value.endsWith('.mp3')) {
            var name = value.slice(0, value.length - 4);
            output += `!${name}\n`;
        }
    });
    bot.sendMessage({to: channelID, message: output});
}

function moveUser(server, args, voiceChannels) {
    var userToMove = args.join(" ");
    if (!userToMove || userToMove.length == 0) {
        return;
    }
    var user = Object.values(bot.users).find(u => u.username == userToMove);
    var channelToMoveTo = voiceChannels[Math.floor(Math.random()*voiceChannels.length)];
    if (user && channelToMoveTo) {
        bot.moveUserTo({serverID: server.id, userID: user.id, channelID: channelToMoveTo.id});
    }
}

bot.on('ready', function (evt) {
    logger.info('Connected');
    logger.info('Logged in as: ');
    logger.info(bot.username + ' - (' + bot.id + ')');
});

bot.on('message', function (user, userID, channelID, message, evt) {
    // Our bot needs to know if it will execute a command
    // It will listen for messages that will start with `!`

    var server = bot.servers[evt.d.guild_id];
    var voiceChannels = Object.values(server.channels).filter(c => c.type == 2);
    var userVoiceChannel = server.members[userID].voice_channel_id;

    if (message.substring(0, 1) == '!') {
        var args = message.substring(1).split(" ");
        var command = args.shift();
        switch(command) {
            case 'move':
                moveUser(server, args, voiceChannels);
                break;
            case 'help':
                outputHelp(channelID);
                break;
            default:
                playSound(command.toLowerCase(), userVoiceChannel, voiceChannels);
                break;
            // Just add any case commands if you want to..
         }
     }
});