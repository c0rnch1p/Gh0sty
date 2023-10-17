## 
#### General
## 
#### Details
• Size: 7.4M  
• Arch: x86_64  
• Vers: v01.01.01
##### Weblinks
• MusicGen: https://facebook-musicgen.hf.space/  
• OpenAI: https://openai.com  
• Stable Diffusion: https://stablediffusionapi.com
##### Description
Gh0sty is a CLI chatbot that uses OpenAI, Stable Diffusion and MusicGen to generate
responses. Shes designed with effortlessness in mind and can be put to extensive use,
with the sacrifice of significantly longer API call times than the web interfaces for the
services mentioned (at standard connection speeds). The quality of the response content
itself isnt affected by the fact that the call is being made locally, which is great.
Text to speech (gTTS) is enabled by default and responses are spoken in a tolerable
voice. A keyword system is used for basic controls and navigation between ChatGPT, Stable
Diffusion, MusicGen, exiting and reloading etc.
## 
#### Installation
## 
##### Depends
• mpv: Free and open source media player  
• python-colorama: Cross platform colored terminal text  
• python-gradio-client: UI generation library for machine learning models  
• python-gtts: Google Text-to-Speech API wrapper  
• python-mpv: Python bindings for the mpv media player  
• python-openai: Python library for interfacing with OpenAIs language models  
• python-pydub: Audio processing library for Python  
• python-pygame: Python library for game development  
• python-termcolor: Cross platform colored terminal text  
• qview: Qt image viewer
##### MacOS & Linux
Open a terminal and clone this repo:
```shell
git clone 'https://github.com/c0rNCh1p/gh0sty.git' ||
git clone 'https://gitlab.com/c0rNCh1p/gh0sty.git'
```
##### Windows
Go grab git bash if not installed 'https://git-scm.com/download/win'. Open Git Bash and
follow the steps for MacOS and Linux.
##### API Keys
To put this chatbot to full use, valid API key for OpenAI and Stable Diffusion are
needed. These keys should be saved in files named 'stable_diffusion_api_key' and
'openai_api_key' in the program directory. When the install.sh script is run it will copy
the keys over to the install directory with the code:
```shell
echo 'sk_abcdefg123456789' >'gh0sty/keys/openai_api_key'
echo 'abcdefg123456789' >'gh0sty/keys/stable_diffusion_api_key'
```
##### Building
The 'install.sh' script will take care of the rest of the installation:
```shell
cd 'gh0sty'
chmod 764 'install.sh'
./'install.sh'
```
## 
#### Usage
## 
##### Keywords
These are the defined keywords:
```shell
<exit-|ex-|e-> leave the chat  
<keywords-|kw-|k-> show this message  
<reload-|rl-|r-> kill response and reset  
<image-|ig-|i-> text to image (Stable Diffusion)  
<music-|mc-|m-> text to audio (MusicGen)  
<cancel-|rc-|c-> return to text chat
```
##### Configuration
The main source file gh0sty.py contains configuration settings at the beginning of the
file for Chat GPT and Stable Diffusion response generation. Fine tuning and training can
be implemented via the 'presets.py' file for further customization.
## 
#### Notes
## 
##### No Lang Support
Support for English text to speech functionality is provided. This can be changed via the
lang variable in the source code, but other languages have not been tested.
##### No Input Navigation
Text navigation actions like the left and right keys or the home and end keys to move the
cursor are not supported (backspace works fine). However support for multiline input is
provided, allowing users to enter more complex queries or code snippets as prompts. While
the absence of traditional text editing shortcuts might limit some abilities, its easier
to write complex prompts in a text editor and paste them into the input feild anyway.
##### No XL Prompts
The prompt size includes the the entire session history and the preset data, so the limit
can be reached fairly quickly after a few large prompts. The current current prompt size
limit is approximately 120 lines if its the first prompt and no history has been built up.
Habitually restarting the session after responses to large inputs are generated is the
best workaround. Remebered context is nice, but also unecessary if prompts are structured
correctly to begin with.
## 
