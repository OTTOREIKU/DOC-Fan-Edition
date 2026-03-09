# DOC-Fan-Edition aka Derby Dynasty
A fan made Derby Owners Club *adjacent* game for the terminal and beyond

=============

The first version of this game was made with python and only worked in the terminal, it essentially was a turn based horse racing game. I have since been working on porting it into GoDOT and have a working alpha. Alpha 2.0 doesnt have the trading feature (*yet*) but I am slowly bringing everything online as I learn how to use this new game engine. The alpha release is no where close to how I want to game to feel however it is in a functional-playable state right now so I wanted to put it out there in case anyone else has the itch for a DOC-spirited game. Hopefully in the next year I'll have created a beautiful, functional, horse racing simulator.

ottoreiku@protonmail.com | Discord: OTTOREIKU

=============  

### Features:  

*(some of the features you have to purchase from the in-game store to be able to use)*  
  
- Market  
Dynamic marketplace generating random horses every month to purchase. New markets appear once you breed new generations of horses.  
  
- Active Stable / Racing  
Choose a horse and take on races throughout the month with dynamic random events. Train your horse in between weeks to build up their stats.  

- Tension / Strain system  (**This has been removed in 2.0**)  
Build tension by strategically holding your horse and unleash it when whipping. Whipping your horse will build strain and cause the horse to use extra stamina. Release strain by holding, coasting, or urging. Mix in different actions to balance these two.  
  
- Breeding / Genetics  
*This system has been expanded upon in 2.0 with a few extra features as well as a ton of new coat colors and markings*  
Fairly in depth breeding with systems built to pass down genetic markers, boss titles, and maximum potential stats. Currently supporting Generations 0-10 with Gen 6+ having legendary colors & coats.  
  
- Farm / Riding Academy  
Retired horses live on the farm and contribute lifetime earned titles to give bonuses to the entire stable.
Move your horse over to the Riding Academy to help train other horses and make extra monthly income based on the stats of the horse at retirement.  
  
- Store  
Tons of facility upgrades, gear, and consumables. 
  
- Hall of Fame  
Keep track of your retired horses and see which titles are giving bonuses to your entire stable. See which of your horses have contributed the most to your dynasty.  
  
- Compendium
*In 2.0 this section is much larger and covers more of the math behind the game*  
General rules and conditions are housed here as well as an area to keep track of discovered titles and what they do along with bosses. Preview discovered rare coats/colors.  

- Bosses
*Rivals have also been added to 2.0*  
Handful of powerful boss horses that have a low chance to spawn in your races. Beat them to take their titles and gain permanent buffs.    
  
- Trading Hub  
(**Not yet functional in 2.0**)  
Import or Export horses (Active and Retired) to trade with other players or simply generate a card for your collection. Horse trading data is encoded to the metadata of the generated PNG image so you can simply send someone the card file and the game can import directly from that. This is still a work in progress but I tried to emulate the physical cards from DOC.  
  
- Jockey System (**This system has been removed in 2.0**)  
This is a work in progress and not at a place that I am fully happy with. It is disabled by default but you can turn it on in the settings if you want to try it. Once enabled it will add a new area to the compendium where you can get more info on it.  
  
--- There are still a lot of things I need to fix up (this is an alpha after all) so a lot of the naming and prices etcetc are going to be changing as I refine everything. You will certainly find errors but I hope you have fun ---
  
=============  

Once you buy your first horse from the market the game will create your stable.json file **in the same location as the EXE** so keep that in mind if you end up moving your game to a new location. When using the Trade Hub to generate cards the game will **make a new 'cards' folder in the same location as the EXE** as well.  
  
*In 2.0 the save is currently stored in Appdata/Roaming/Godot/app_userdata/DerbyDynasty*
  
=============  

**Starting Tips:**  
- First thing you need to do is go to the market and buy a horse. Then back out to the main menu and go to your active stable, pick your horse, and enter the calendar to begin training and racing.
- Gen0 horses (your first horse) are not supposed to be super strong. You want to race your horse until you notice it's not getting stats anymore (it hit its cap) and then you want to purchase the opposite gender and race them. Once you have two horses max stats and retired, you breed them to make a Gen1 horse which will have higher max caps for their stats. Thats the basic loop - train to max, breed to get higher generation, etc
  
=============  

**Known Issues (for 1.0):**  
- Entering the market might crash the game. If you launch the exe as administrator it seems to fix it however it then changes all the icons so the game looks a little boring
- after a race when you feed your horse if a random event happens it skips the screen too quickly and you miss seeing the stat gain. Don't worry, it still got the stat it just cleared the screen too fast
    
=============  
  
This is a passion project for educational and entertainment purposes that has no official relation to Derby Owners Club or SEGA branding other than in name  
  
I've used AI in parts of the development, mainly the math for the stats, AI horses, scaling, and racing as well as text in the giant compendium in 2.0. Once I have it in a place that I like, I am going to hire an artist to create all of the assets and someone to copyedit/proof all of the text.
  
=============  
  
<img width="1913" height="998" alt="1" src="https://github.com/user-attachments/assets/faa49535-4f0d-4fac-b19e-c12d7b9b2da8" />

=============  
  
<img width="1916" height="1005" alt="2" src="https://github.com/user-attachments/assets/734adf51-455a-488b-8b67-403fdf27f644" />

  
=============  
  
<img width="1913" height="995" alt="3" src="https://github.com/user-attachments/assets/10d5d79d-f79b-4150-b549-1f83bfbf19ad" />

  
=============  
  
<img width="1913" height="1009" alt="4" src="https://github.com/user-attachments/assets/86e103b9-f328-4c77-a508-984819f35ea9" />

  
=============  
  
<img width="1912" height="997" alt="5" src="https://github.com/user-attachments/assets/169467b8-ca07-440a-a420-e2269f3d9c57" />

  
=============  
  
<img width="1916" height="999" alt="6" src="https://github.com/user-attachments/assets/083268c1-8e71-4e92-8f41-23a367ac47e5" />

  
=============  
  
<img width="1901" height="1000" alt="7" src="https://github.com/user-attachments/assets/9c3aecfc-4e27-491e-992a-681cc1cd2167" />

  
=============  


  
Alpha 1.0 Screenshots:  
  
<img width="587" height="374" alt="1" src="https://github.com/user-attachments/assets/890b55d0-b834-42e8-a748-bd9db018733a" />
  
=============  
  
<img width="589" height="532" alt="2" src="https://github.com/user-attachments/assets/8bc4ed76-3990-49f1-a503-d53d417aad5a" />
  
=============  
  
<img width="589" height="378" alt="4" src="https://github.com/user-attachments/assets/c7de835d-9901-4c61-999b-5ad4c6a4a353" />
  
=============  
  
<img width="602" height="432" alt="5" src="https://github.com/user-attachments/assets/0b1da003-a1c3-42b9-aa62-24f33c94fb33" />
  
  
=============  
  
<img width="700" height="578" alt="11" src="https://github.com/user-attachments/assets/c0d9015b-f22c-4129-bf4c-c2e146386a51" />
  
=============  
  
 <img width="400" height="860" alt="Noble Cloud_Gen1_Collection" src="https://github.com/user-attachments/assets/d70c1587-18d6-4526-97a3-3304fd97a3d1" />
 <img width="400" height="860" alt="Silent Knight_Gen0_Trade" src="https://github.com/user-attachments/assets/7c8b9ddb-36ac-4adc-835d-feed6f0d3912" />
  
