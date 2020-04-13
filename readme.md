# Personal Project: Discord Bot in Python

## Available commands/functions
### Listed by Extension/Cog
#### Available command prefixes **['=', '==', '-', '.', '!', '$', '?']**
* **Basic**
  * **ping** - *The ping command, answers Pong @User and displays ping time for the message*
    * No aliases for this command
    * How to use: **[command prefix]ping**
  * **say** - *The parrot/repeat command*
    * Also usable as: repeat, parrot
    * How to use: **[command prefix]say {text to be repeated}**
  * **hello** - *Greets the user*
    * Also usable as: hey, hi, sup, yo, waddap
    * How to use: **[command prefix]hello**
  * **8ball** - *A fortune telling 8ball*
    * Also usable as: ball, fortune
    * How to use: **[command prefix]8ball {question}**
    * Displays a random answer from a set list
* **Embed**
  * **embed** - *Create a custom Embed message with title and content fields*
    * No aliases for this command
    * How to use: **[command prefix]embed**
    * Prompts in chat will ask for Title and Content
  * **help** - *Shows more info for each cog/extension pack*
    * Also usable as: commands, command
    * How to use: **[command prefix]help {exntension pack or nothing to list all}**
  * **info** - *Shows bot info*
    * Also usable as: i
    * How to use: **[command prefix]info**
* **Poll**
  * **poll** - *Create a poll*
    * No aliases for this command
    * How to use: **[command prefix]Title, Option1, Option2, Option3.... max 10 options**
* **Music**
  * **join** - *Join the user's voice channel*
    * Also usable as: j
    * How to use: **[command prefix]join**
  * **summon** - *Summon the bot to a voice channel. If no channel is given it joins the user's channel*
    * No aliases for this command
    * How to use: **[command prefix]summon {voice channel name}**
  * **play** - *Play a song, currently doesn't support whole playlists*
    * Also usable as: p
    * How to use: **[command prefix]play {Artist} {Song name} or [command prefix]play {Song Youtube url}**
  * **volume** - *Change bot volume*
    * Also usable as: vol
    * How to use: **[command prefix]volume {0-100%}**
  * **now** - *Display currently playing song in chat*
    * Also usable as: playing, current
    * How to use: **[command prefix]now**
  * **pause** - *Pause currently playing song*
    * No aliases for this command
    * How to use: **[command prefix]pause**
  * **resume** - *Resume paused song*
    * No aliases for this command
    * How to use: **[command prefix]resume**
  * **stop** - *Stop bot and clear the queue*
    * Stop bot and clear the queue
    * How to use: **[command prefix]stop**
  * **skip** - *Vote to skip a song. The requester can automatically skip. 3 skip votes are needed for the song to be skipped*
    * No aliases for this command
    * How to use: **[command prefix]skip**
  * **queue** - *Display current queue in chat*
    * Also usable as: q
    * How to use: **[command prefix]queue**
  * **shuffle** - *Shuffle the current queue*
    * No aliases for this command
    * How to use: **[command prefix]shuffle**
  * **remove** - *Remove a song from the queue with the given index*
    * Also usable as: rem, r
    * How to use: **[command prefix]remove {index of song in queue}**
  * **disconnect** - *The bot clears the song queue and leaves the channel*
    * Also usable as: leave, l
    * How to use: **[command prefix]disconnect**
* **Google**
  * **google** - *Google web search*
    * No aliases for this command
    * How to use: **[command prefix]google [search term]**
  * **image** - *Google image search. First image result is sent in chat*
    * Also usable as: img
    * How to use: **[command prefix]image [search term]**
* **MessageSelect**
  * **bot_channel** - *Select text channel for custom join, leave and other bot custom messages*
    * Also usable as: bot_chnl, botchannel
    * How to use: **[command prefix]bot_channel #{channel}*8
  * **set_message** - *Set custom join message [currently unused in my code, but msg is saved in the db]*
    * Also usable as: set_msg, set_join_msg
    * How to use: **[command prefix]set_message [text]**
* **Leveling**
  * **stats** - *Cheack out your personal stats or another users by name or @*
    * Also usable as: level, lvl
    * How to use: **[command prefix]stats**
  * **leaderboard** - *View the leaderboard*
    * Also usable as: board, ranking, ranks
    * How to use: **[command prefix]stats**
    
    
## Extra Features

#### Displays custom messages on member joining/leaving the server when a channel is set by using the set_message command from MessageSelect cog
Custom Join Message | Custom Leave Message
<img src="https://imgur.com/HONGcbN.png" alt="Custom Leave Message" width="50%" height="200" hspace="30"> | <img src="https://imgur.com/BoxhTpW.png" alt="Custom Join Message" width="50%" height="200" hspace="30">
#### When joining any voice channel from a non-voice channel a timer is started per user. 
#### When the user leaves an EXP reward of 2 per 5min spent in the voice channels is awarded and a custom message is sent in the selected bot text channel
#### 
#### Custom messages are sent on level up| width=48

