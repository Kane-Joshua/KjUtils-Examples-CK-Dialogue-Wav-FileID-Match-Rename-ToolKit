# KjUtils-Examples-CK-Dialogue-Wav-FileID-Match-Rename-ToolKit
Simple Python Code I use to semi-automatically process the dialogue ID batch matching work with the actual lines, and on which we base on to batch rename .wav and sort into different voice actor folders. Plus a little aids on in-CK havok .hkx file preview and selectin by number-rename those files.

###### before all...
>Now first things first, fuck you dumbass bot this jap mesubuta moderator `AltheaR`. She, with her own efforts and her supporters, bring the whole Fallout 4 Nexus community into destruction. and **NOBODY** should have forgot this. 
- this kind of person should go baby sitting her barstard of her gigolo and her scum mother. So notorious! Stinky!

---

# Installation
Just intall the requirement in your active python environment, place files WITHIN the example folder and run which ever Utils you need.
- Don't guarantee all work.
- **Credit** `Kjeldahlocobot` if it help.
- Those `.hkx` assets provided as example are from **__Bethesda Mod School Resources__** by ***Kinggath***: `https://www.nexusmods.com/fallout4/mods/38669`. Also he did great tutorials. Big thanks for him, Seddon4494 and more ppl etc.

---

# Usage
→ `KjUtils_0_ScriptsConcateDifnLine.py` will handle any transcript deliberately split two multiple lines.

→ `KjUtils_1_MatchDialiguesFilenameID.py` will refill the filename ID(i.e. the one will be used to rename your voiced file) according to the actual lines' similarity using certain kind of fuzzy logic.
- Switch the fuzzy logic at your will, to get what you want. Currently it can handle `.wav` follows a special file naming rules, which is provided as example in `\wav_files`
- You need to first go in CK, Charactor>Quest>`<YourQuest>`>Export Dialogue where you'll get your `dialogueExport<YourQuest>.txt`, then set up `.xlsx` and link `.txt`s date in so you get your table B containe all entries with Lines and FileID
  - You need to rename the colume header to "台词(Lines)" and "ID" or whatever you want(you can config within `.py`) before hit run those `.py`.

→ `KjUtils_2_RenameVoiceFileWav.py` will rename your `.wav` file with what ever `.xlsx` contain columes of Lines and ID, which will be the name mapping.

→ `KjUtils_3_NumberRename4AnimFile.py` will add a none repeat number to the first word of any file so you have extra "hash" like data and files can be distincted within those pitiful small preview tabs in CK.
