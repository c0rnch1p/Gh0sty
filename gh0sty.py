#!/usr/bin/env python3
from colorama import Fore, Style
from gradio_client import Client
from gtts import gTTS
from presets import presets
from pydub import AudioSegment
from termcolor import colored
from tqdm import tqdm
import atexit
import glob
import io
import json
import mpv
import openai
import os
import queue
import readline
def pthCompleter(text, state):
	line=readline.get_line_buffer().split()
	return [x+'/' if os.path.isdir(x) else x for x in glob.glob(text+'*')][:24][state]
readline.set_completer(pthCompleter)
readline.set_completer_delims('')
readline.parse_and_bind('tab: complete')
import requests
import subprocess
import sys
import tempfile
import termios
import time
import threading
import tty
sys.stdout=open(os.devnull, 'w')
import pygame
sys.stdout=sys.__stdout__

# openai pricing: https://openai.com/pricing
# stable diffusion pricing: https://stablediffusionapi.com/#pricing
# gpt: generative pretrained transformer
# token: text block which can be either a word, split word or char

lang='en' # tts language
#sys.stdout=open(os.devnull, 'w') # current musicgen link
#client=Client('https://facebook-musicgen.hf.space/')
#sys.stdout=sys.__stdout__

# for this chatbot to work a file called openai-api-key containing a valid
# openai api key needs to exist in this directory, and for stable diffusion
# to work, a stable-diffusion-api-key file as well, when the install.sh
# script is run it will copy the key over to ~/.local/share with the code

# GPT

# limits the length of the response, it has no affect on the prompt size
# limits which are affected by both the session history and the preset data
#maxTokens=1000 # no need to set this if it isnt being dynamically managed

# the default token limit here is 4096 tokens (aprx. $0.01 usd) for the
# gpt turbo model, output costs about +$0.003 usd (total=prompt+response)
model='gpt-3.5-turbo'

# randomness/spontaneity
# higher values increases the chance of the model selecting less probable
# tokens, while a lower value makes the model more likely to select the
# most probable tokens at each step of the response
temperature=0.6

# diversity/resourcefulness
# determines the level of diversity in the response using the cumulative
# token probability and influencing which tokens are considered at each
# step of the response, higher values increase diversity in the output
topP=0.7

# repetition/meticulousness
# penalises the selection of tokens that have already appeared in the
# response reducing the likelihood of repeating the same phrases, higher
# values will penalise repeated tokens more aggressively
frequencyPenalty=0.8

# relevance/attention
# penalises the generation of tokens not found in the input prompt,
# reducing the likelihood of introducing new ideas and making the output
# stick closer to the context provided
presencePenalty=0.2

# STABLE DIFFUSION

# note: stable diffusion will automatically store the generated image on
# one of their servers and it will be linked to the account that made the
# call, stable diffusion has a cheese pizza filter, prompts are logged in
# the api for traceability and are never deleted, please dont use this
# script for evil shit

sdWidth='512' # image width
sdHeight='512' # image height
negPrompt='badhandv4 easynegative lowres watermark unreadble'

# num images to be generated
sdSamples='1'

# num of diffusion steps to perform during generation, higher values
# increase quality, accepts 20, 30, 40 and 50
sdSteps='30'

# this is a flag to determine whether or not to perform nsfw or illegal
# safety checks on the generated image
sdSafetyCheck='no'

HOME=os.path.expanduser('~')
AUDDIR='/usr/share/gh0sty/audio/'
IMGDIR='/usr/share/gh0sty/images/'
RESPDIR='/tmp/gh0sty_response.mp3'
SPEEDUP='/tmp/gh0sty_sped.mp3'
SDAPIPATH='/usr/share/gh0sty/keys/stable_diffusion_api_key'
SDAPIKEY=open(SDAPIPATH, 'r').read().strip()
OAAPIPATH='/usr/share/gh0sty/keys/openai_api_key'
OAAPIKEY=open(OAAPIPATH, 'r').read().strip()
openai.api_key=OAAPIKEY

WHITE=Fore.WHITE
MAGENTA=Fore.MAGENTA
RED=Fore.RED
YELLOW=Fore.YELLOW
GREEN=Fore.GREEN
CYAN=Fore.CYAN
BLUE=Fore.BLUE
BLACK=Fore.BLACK

DIM=Style.DIM
NORMAL=Style.NORMAL
BOLD=Style.BRIGHT
RESET=Style.RESET_ALL

pygame.init()
pygame.mixer.init()
responseLck=threading.Lock()
responseQueue=queue.Queue()

def cleanup():
	pygame.mixer.quit()
	pygame.quit()
	os.system("killall -9 gh0sty &>'/dev/null'")

def printGpt():
	print(YELLOW+'⧼⧼ '+BOLD+'Chat GPT'+RESET+YELLOW+' ⧽⧽'+RESET)

def reloadChat(responseLck, interrupt, presets, originalPresets):
	print(YELLOW+'*'+DIM+'reloaded'+RESET+YELLOW+'*'+RESET)
	pygame.mixer.music.stop()
	presets.clear()
	presets.extend(originalPresets)
	return interrupt

def printKeywords():
	print('▸'+BOLD+WHITE+' <exit-|ex-|e-> '+RESET+'leave the chat')
	print('▸'+BOLD+WHITE+' <keywords-|kw-|k-> '+RESET+'show this message')
	print('▸'+BOLD+WHITE+' <reload-|rl-|r-> '+RESET+'kill response and reset')
	print('▸'+BOLD+WHITE+' <image-|ig-|i-> '+RESET+'text to image (Stable Diffusion)')
	#print('▸'+BOLD+WHITE+' <music-|mc-|m-> '+RESET+'text to audio (MusicGen)')
	print('▸'+BOLD+WHITE+' <cancel-|rc-|c-> '+RESET+'return to text chat')

def genResponse(tempText, presets, gptParams, responseLck, interrupt, result):
	with open(tempText, 'r') as f:
		prompt=f.read()
	os.remove(tempText)
	message=presets+[{'role': 'user', 'content': prompt}]
	try:
		response=openai.ChatCompletion.create(
			model=model,
			messages=message,
			**gptParams)
		result.append(response['choices'][0]['message']['content'])
		gh0sty=response['choices'][0]['message']['content']
		playResponse(gh0sty, responseLck, interrupt)
		print(BOLD+GREEN+'GH0STY'+DIM+': '+RESET+gh0sty)
	except openai.error.RateLimitError:
		print(YELLOW+'*'+DIM+'tweaks spastically'+RESET+YELLOW+'*'+RESET)
		return None
	except openai.error.OpenAIError as e:
		print(YELLOW+'*'+DIM+'dies inside'+RESET+YELLOW+'*'+RESET)
		return None
	except Exception as e:
		print(BOLD+YELLOW+'⚠ '+RESET+f'{e}'+YELLOW+BOLD+' ⚠'+RESET)
		return None

def playResponse(gh0sty, responseLck, interrupt):
	with responseLck:
		if interrupt:
			return
	tts=gTTS(text=gh0sty, lang=lang, slow=False)
	tts.save(RESPDIR)
	audio=AudioSegment.from_mp3(RESPDIR)
	speededUp=audio.speedup(playback_speed=1.3)
	speededUp.export(SPEEDUP, format='mp3')
	pygame.mixer.init()
	pygame.mixer.music.load(SPEEDUP)
	pygame.mixer.music.play()

def genSDImg(sdParams):
	print(YELLOW+'⧼⧼ '+BOLD+'Stable Diffusion'+RESET+YELLOW+' ⧽⧽'+RESET)
	prompt=input(BOLD+BLUE+'PR0MPT'+DIM+': '+RESET)
	try:
		if prompt.lower() in ['cancel-', 'rc-', 'c-']:
			print(YELLOW+'*'+DIM+'cancelled'+RESET+YELLOW+'*'+RESET)
			printGpt()
			return
		with tqdm(total=100, bar_format=(
			BOLD+RED+'{l_bar}|🭮🮊'+DIM+'{bar}'+RESET+BOLD+RED+'🮊🭬|{r_bar}')) as pbar:
			time.sleep(1)
			pbar.update(30)
			url='https://stablediffusionapi.com/api/v3/text2img'
			payload=json.dumps({
				'key': SDAPIKEY,
				'prompt': prompt,
				**sdParams})
			headers={'Content-Type': 'application/json'}
			time.sleep(1)
			pbar.update(30)
			response=requests.request('POST', url, headers=headers, data=payload)
			time.sleep(1)
			pbar.update(40)
		pbar.close()
		responseJson=response.json()
		imgPth=responseJson['output'][0]
		imgResponse=requests.get(imgPth, timeout=10)
		print(BOLD+BLUE+'URL'+DIM+': '+RESET+f'{imgPth}')
		with open('temp.png', 'wb') as f:
			f.write(imgResponse.content)
			if os.path.exists('temp.png'):
				os.system("qview temp.png &>'/dev/null'")
				os.remove('temp.png')
				saveImg(imgPth, imgResponse.content)
		printGpt()
	except requests.exceptions.RequestException as e:
		print(YELLOW+'*'+DIM+'tweaks spastically'+RESET+YELLOW+'*'+RESET)
		printGpt()
	except json.JSONDecodeError as e:
		print(YELLOW+'*'+DIM+'dies inside'+RESET+YELLOW+'*'+RESET)
		printGpt()
	except Exception as e:
		print(BOLD+YELLOW+'⚠ '+RESET+f'{e}'+YELLOW+BOLD+' ⚠'+RESET)
		printGpt()

def saveImg(imgPth, imgData):
	saveResponse=input(BOLD+GREEN+'SAVE?'+DIM+': '+RESET).lower()
	if any(saveResponse.startswith(x) for x in [
		'1', 'y', 'ya', 'ye', 'ta', 'ok', 'pl', 'th']):
		imgName=input(BOLD+BLUE+'NAME'+DIM+': '+RESET)
		imgPth=os.path.join(IMGDIR, f'{imgName}.png')
		os.makedirs(os.path.dirname(imgPth), exist_ok=True)
		with open(imgPth, 'wb') as handler:
			handler.write(imgData)
		print(BOLD+GREEN+'SAVED AS'+DIM+': '+RESET+f'{imgPth}')

def genMusic():
	print(YELLOW+'⧼⧼ '+BOLD+'MusicGen'+RESET+YELLOW+' ⧽⧽'+RESET)
	sampleFile=os.path.join(AUDDIR, 'sample1.wav')
	prompt=input(BOLD+BLUE+'PR0MPT'+DIM+': '+RESET)
	try:
		if prompt.lower() in ['cancel-', 'rc-', 'c-']:
			print(YELLOW+'*'+DIM+'cancelled'+RESET+YELLOW+'*'+RESET)
			printGpt()
			return
		with tqdm(total=100, bar_format=(
			BOLD+RED+'{l_bar}|🭮🮊'+DIM+'{bar}'+RESET+BOLD+RED+'🮊🭬|{r_bar}')) as pbar:
			time.sleep(1)
			pbar.update(50)
			result=client.predict(prompt, sampleFile, fn_index=0)
			time.sleep(1)
			pbar.update(50)
			subprocess.run(['mpv', result],
				stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		pbar.close()
		print(BOLD+BLUE+'URL'+DIM+': '+RESET+f'{result}')
		saveResponse=input(BOLD+GREEN+'SAVE?'+DIM+': '+RESET).lower()
		if any(saveResponse.startswith(x) for x in [
			'1', 'y', 'ya', 'ye', 'ta', 'ok', 'pl', 'th']):
			savePth=input(BOLD+BLUE+'SAVE AS'+DIM+': ')
			with open(savePth, 'wb') as f:
				f.write(result)
			print(BOLD+GREEN+'SAVED AS'+DIM+': '+RESET+f'{savePth}')
		printGpt()
	except Exception as e:
		print(BOLD+YELLOW+'⚠ '+RESET+f'{e}'+YELLOW+BOLD+' ⚠'+RESET)
		printGpt()
		return None

def main():
	global interrupt
	atexit.register(cleanup)
	originalPresets=presets.copy()
	print('PROMPT: '+BOLD+WHITE+'hi-'+RESET)
	print(BOLD+WHITE+'<k-> '+RESET+'keywords'+RESET)
	print(YELLOW+'⧼⧼ '+BOLD+'Chat GPT'+RESET+YELLOW+' ⧽⧽'+RESET)
	gptParams={
		'temperature': temperature,
		#'max_tokens': maxTokens,
		'top_p': topP,
		'frequency_penalty': frequencyPenalty,
		'presence_penalty': presencePenalty}
	sdParams={
		'width': sdWidth,
		'height': sdHeight,
		'negative_prompt': negPrompt,
		'samples': sdSamples,
		'num_inference_steps': sdSteps,
		'safety_checker': sdSafetyCheck}
	thread=None
	while True:
		if thread:
			thread.join()
		readline.set_completer_delims('')
		print(BOLD+BLUE+'PR0MPT'+DIM+': '+RESET, end='')
		usrInput='PR0MPT: '
		sys.stdout.flush()
		while True:
			char=sys.stdin.read(1)
			if (char == '\b' or char == '\x7f') and len(usrInput) > len('PR0MPT: '):
				usrInput=usrInput[:-1]
				sys.stdout.write('\b \b')
				sys.stdout.flush()
			else:
				usrInput += char
				sys.stdout.flush()
			if usrInput.endswith('-\n'):
				break
		readline.set_completer_delims(' \t\n')
		usrInput=usrInput[len('PR0MPT: '):].strip()
		if usrInput.lower() in ['exit-', 'ex-', 'e-']:
			break
		elif usrInput.lower() in ['keywords-', 'kw-', 'k-']:
			printKeywords()
		elif usrInput.lower() in ['reload-', 'rl-', 'r-']:
			with responseLck:
				interrupt=True
			interrupt=reloadChat(responseLck, interrupt, presets, originalPresets)
		elif usrInput.lower() in ['image-', 'ig-', 'i-']:
			genSDImg(sdParams)
		#elif usrInput.lower() in ['music-', 'mc-', 'm-']:
			#genMusic()
		else:
			with responseLck:
				interrupt=False
			presets.append({'role': 'user', 'content': usrInput})
			with tempfile.NamedTemporaryFile(delete=False) as temp:
				temp.write(usrInput.encode('utf-8'))
				tempText=temp.name
			try:
				result=[]
				thread=threading.Thread(
					target=genResponse, args=(
						tempText, presets, gptParams, responseLck, interrupt, result))
				thread.start()
				thread.join()
				response=result[0]
				presets.append({'role': 'system', 'content': response})
			except Exception as e:
				print(BOLD+YELLOW+'⚠'+RESET+f' {e}'+YELLOW+BOLD+' ⚠')

if __name__ == '__main__':
	main()
