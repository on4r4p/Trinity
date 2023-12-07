#!/usr/bin/python3

import g4f,pyaudio,pvporcupine,os,time,sys,struct,random,webrtcvad,subprocess,re,string,wikipedia,googlesearch,requests,signal
import google.cloud.texttospeech as tts

from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

from difflib import SequenceMatcher

from bs4 import BeautifulSoup

from google.cloud import speech_v1p1beta1 as speech
from google.cloud import language_v1
from queue import Queue
from threading import Thread
from ctypes import *
from contextlib import contextmanager

from unidecode import unidecode

@contextmanager
def ignoreStderr():
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    sys.stderr.flush()
    os.dup2(devnull, 2)
    os.close(devnull)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(old_stderr)


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'keys/google_adc.json'



def signal_handler(sig, frame):
    Xcb_Fix("set")
    sys.exit(0)



def PRINT(txt,other=None):
   tmp_txt = txt
   try:
       if DEBUG:
            if other:
                tmp_txt = str(txt) + " " +str(other)
            else:
                print(tmp_txt)
   except:
         pass
def LoadKeys():
   PRINT("-LoadKeys")
   if os.path.exists(script_path+"/keys/pico.key"):
       with open(script_path+"/keys/pico.key","r") as k:
           PICO_KEY = k.read()
           PICO_KEY = PICO_KEY.strip()
       if not PICO_KEY.endswith("=="):
            print("-Wrong Pico Api key.")
            print(PICO_KEY)
            sys.exit()
       else:
            return(PICO_KEY)
   else:
       print("-%s/keys/pico.key doesn't exist."%script_path)




def parse_response(data):

    PRINT("Orig Data before parse:\n",data)

    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)

    if "Bonjour, c'est Bing." in data:
        index = data.find("Bonjour, c'est Bing.")
        data = data[index+21:]            

    data = data.replace("**","")
    no_link = re.sub(r'\[\d+\]:\s*https?://[^\s]+ "[^"]*"\n?', '', data)
    no_emoj = re.sub(emoj,'',no_link)
    no_brak = re.sub(r'\[[^\]]+\]', '', no_emoj)
    no_brak2 = re.sub(r'\[\^?\d+\^?\]:', '', no_brak)

    final = ""
    for line in no_brak2.splitlines():
         if "http" in line :
            httpos = line.find("http")
            to_replace = line[httpos:line.find(" ")]
            if len(to_replace) == 0:
                  to_replace = line[httpos:]
            line = line.replace(to_replace," ")
            if len(line.replace(" ","")) <= 1:
                continue
            final += "\n"+line
         else:
             final += line
    return(final.replace("####","")) 


def fallbackGpt(input):
     PRINT("-fallbackgpt")

     global Current_Provider_Id
     global Blacklisted

     Answer_Known = Check_History(input)

     if Answer_Known or not No_Input.empty():
        return(Trinity())

     last_sentence.put(input)

#    os.system("aplay %s"%script_path+"local_sounds/server/gpt3.wav")
     rnd = str(random.randint(1,10))
     wait = script_path+"/local_sounds/wait/"+rnd+".wav"
     os.system("aplay %s"%wait)

     Err_msg = ""
     Err_cnt = 0
     response = ""

     allowed_models = [
        'code-davinci-002',
        'text-ada-001',
        'text-babbage-001',
        'text-curie-001',
        'text-davinci-002',
        'text-davinci-003']


     providers = [
     g4f.Provider.Bing,
     g4f.Provider.GptGo,
     g4f.Provider.You,
     g4f.Provider.Phind,
     g4f.Provider.AiAsk,
     g4f.Provider.GPTalk,
     g4f.Provider.Llama2,
     g4f.Provider.Vercel

 ]


     providers_names = [
     "Bing",
     "GptGo",
     "You",
     "Phind",
     "AiAsk",
     "GPTalk",
     "Llama2",
     "Vercel"

 ]

     p_cnt = 0
     while p_cnt <= (len(providers)- len(Blacklisted)) :
        if Current_Provider_Id > (len(providers)- len(Blacklisted)):
             Current_Provider_Id = 0
        if providers_names[Current_Provider_Id] in Blacklisted:
              PRINT("-skipping :",providers[Current_Provider_Id])
              Current_Provider_Id += 1
              continue

        PRINT("-Asking :",providers[Current_Provider_Id])
        try:
             response = g4f.ChatCompletion.create(
             model=g4f.models.default, 
             provider = providers[Current_Provider_Id],
             timeout=10,
             messages=[{"role": "user", "content": str(input)}])

             if len(response) < 1:
                 PRINT("-No answer from :",providers_names[Current_Provider_Id])
                 wait = script_path+"/local_sounds/providers/"+str(providers_names[Current_Provider_Id])+".wav"
                 os.system("aplay %s"%wait)
                 Current_Provider_Id += 1
             else:
                  Current_Provider_Id += 1
                  break

        except Exception as e:
                 print("Error:",str(e))
                 print("-No answer from :",providers_names[Current_Provider_Id])
                 wait = script_path+"/local_sounds/providers/"+str(providers_names[Current_Provider_Id])+".wav"
                 os.system("aplay %s"%wait)
                 Blacklisted.append(providers_names[Current_Provider_Id])
                 Current_Provider_Id += 1
        p_cnt += 1
        
     if len(response) < 1:
                os.system("aplay "+script_path+"local_sounds/errors/err_no_respons_allprovider.wav")
                return()
     else:
                return(Text_To_Speech(str(response),stayawake=False,savehistory=True))


def wake_up():
    PRINT("-wakeup")

#    word_key = script_path+"/models/Trinity_en_linux_v2_2_0.ppn"
    word_key = script_path+"/models/trinity_fr_raspberry-pi_v3_0_0.ppn"
    word_key2 = script_path+"/models/interpreteur_fr_raspberry-pi_v3_0_0.ppn"
    word_key3 = script_path+"/models/repete_fr_raspberry-pi_v3_0_0.ppn"
    pvfr = script_path+"/models/porcupine_params_fr.pv"
    porcupine = None
    keyword_index = None

    try:
        porcupine = pvporcupine.create(access_key=PICO_KEY, model_path = pvfr,keyword_paths=[word_key,word_key2,word_key3],sensitivities=[1,1,1] )
        with ignoreStderr():
            pa = pyaudio.PyAudio()
        audio_stream = pa.open(
                        rate=porcupine.sample_rate,
                        channels=1,
                        format=pyaudio.paInt16,
                        input=True,
                        frames_per_buffer=porcupine.frame_length)

        print("\nListening for 'Trinity'...")

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index == 0:
                PRINT("keyword_index:",keyword_index)
                
                rnd = str(random.randint(1,15))
                wake_sound = script_path+"/local_sounds/wakesounds/"+rnd+".wav"
                os.system("aplay %s"%wake_sound)
                break
            if keyword_index == 1:
                PRINT("keyword_index:",keyword_index)
                break
            if keyword_index == 2:
                PRINT("keyword_index:",keyword_index)
                break




    finally:
        PRINT("-Awake.")
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if keyword_index == None:
             print("Error keyword_index = None")
             sys.exit()
        if keyword_index == 0:
            return(Trinity("Speech_To_Text"))
        if keyword_index == 1:
            return(Fallback_Prompt())
        if keyword_index == 2:
            os.system("aplay %s"%script_path+"local_sounds/repeat/isaid.wav")
            os.system("aplay %s"%script_path+"tmp/current_answer.wav")
            return(wake_up())

def Record_Query():
    PRINT("-recordquery")


    with ignoreStderr():
        p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=FRAME_RATE,
                    input=True,
                    frames_per_buffer=FRAME_DURATION)

    wake_sound = script_path+"/local_sounds/wakesounds/record.wav"
    os.system("aplay %s"%wake_sound)


    while not record_on.empty():
        chunks.put(stream.read(FRAME_DURATION))

    PRINT("-Recording stopped.")
    wake_sound = script_path+"/local_sounds/wakesounds/record_end.wav"
    os.system("aplay %s"%wake_sound)

    stream.stop_stream()
    stream.close()
    p.terminate()
    return()


def Check_Silence():
    

    PRINT("-Checksilence")
    buffer = b""
    lock = True
    threshold = 1.5
    silence = 0
    no_input = 0
    time_cnt = 0
    VAD = webrtcvad.Vad(3)

    while not record_on.empty():
        if not chunks.empty():
             frames = chunks.get()
             assert webrtcvad.valid_rate_and_frame_length(FRAME_RATE, FRAME_DURATION)
             on_air = VAD.is_speech(frames, sample_rate=FRAME_RATE)

             if on_air:

                 if lock:
                     lock = False
                 buffer += frames
                 silence = 0

             elif not on_air and not lock:

                if silence < threshold * (FRAME_RATE/FRAME_DURATION):
                    silence += 1

                else:
                    lock = True
                    silence = 0
                    record_on.get()
                    to_speech = buffer
                    buffer = b""
                    PRINT("\n-Silence Detected-\n")
                    audio_datas.put(to_speech)
                    break
             elif not on_air and lock:
                  no_input += 1
                  if no_input > 1000:
                      lock = True
                      silence = 0
                      buffer = b""

                      record_on.get()

                      rnd = str(random.randint(1,11))
                      no_input_sound = script_path+"/local_sounds/noinput/"+rnd+".wav"
                      os.system("aplay  %s"%no_input_sound)
                      cancel_operation.put(True)
                      No_Input.put(True)
                      break

             time_cnt += 1
             if time_cnt > 3600:
                  lock = True
                  silence = 0
                  record_on.get()
                  to_speech = buffer
                  buffer = b""
                  audio_datas.put(to_speech)
                  os.system("aplay %s"%script_path+"/local_sounds/errors/err_too_long.wav")
                  break




def Commandes(txt):
    PRINT("-Commandes")

    decoded = unidecode(txt.lower())

    decoded = decoded.replace("s'il te plait","").replace("si te plait","").replace("sil te plait","")


    trinity_name = ["comment tu t'appelles","comment t'appelles tu","tu t'appelles comment","c'est quoi ton nom","quel est ton nom"]
    trinity_mean = ["pourquoi tu t'appelles trinity", "pourquoi t'appelles tu trinity","pourquoi trinity?","pourquoi tu t'appelles comme ca"]

    trinity_creator = ["qui t'a cree","qui t'a programe","qui t'a fait","qui t'a concu","qui t'a fabrique"]

    trinity_script = []

    trinity_help = ["affiche-moi ton aide","quelles sont tes fonction","a quoi sers-tu","quelles sont tes commande","parle-moi de toi"]



    show_words = ["affiche","montre","trouve","cherche","regarde","donne","racconte","parle"]


    prompt_request = ['moi le prompt', "que je t'ecrive", " t'ecrire ", "je te l'ecris", "vais l'ecrire", "va l'ecrire", "va te l'ecrire", "vais te l'ecrire", 'affiche le prompt', 'ouvre le prompt', 'active le prompt', "moi l'invite de commande", "affiche l'invite de commande", "active l'invite de commande", "ouvre l'invite de commande", 'moi le clavier', 'affiche le clavier', 'ouvre le clavier', "j'ai besoin de t'ecrire","tu peux m'ouvrir le clavier","interprete"]

    trinity_source_request = ["affiche ton code source","script trinity"]

    rnd_request = ["choix aleatoire","entre oui et non"]

    repeat_request = ['tu peux me repeter', 'tu peux repeter', 'ai pas entendu', 'ai pas compris', 'rien entendu', 'repete ta', 'repete moi',"repete-moi", 'redis ce que', 'redis ca',"tu as dis quoi","qu est ce que tu as dis","qu est ce que ta dis"]

    search_history_request = ["tu peux afficher","tu peux m'afficher","affiche moi","affiche-moi","montre moi","montre-moi","recherche historique","que tu me fasse","fais une recherche","tu peux chercher","tu peux rechercher","faire une recherche","rechercher sur","rechercher dans","recherche sur","regarder sur","regarder dans","cherche moi","cherche-moi","regarde dans","regarde sur","trouver sur","contenant","concernant","trouver dans","me trouver","trouve sur","trouve moi","trouve-moi","une page qui concerne","une entree parlant","une entree concernant","une entree parlant","une entree qui parle ","une entree sur","infos qui parles","info qui parle","infos parlant","infos sur","info sur","infos concernant","info concernant","infos qui concernent","info qui concerne","infos qui parlent","info qui parle","parle moi","parle-moi","quelque chose sur","quelque chose concernant","quelque chose qui concerne","quelque chose qui parle","quelque chose parlant","truc qui parle","trucs qui parlent","truc parlant","truc concernant","trucs concernant","truc qui concerne","trucs qui concernent","en rapport","si il y a","si il ya","si ya","l'historique","fais une"]

    read_link_request = ["donne moi","donne-moi","le contenu","du lien","d'un lien","de ce lien","peux me dire","fais moi","fais-moi","lis-moi","lis moi","tu peux me lire","que tu me lise","que tu lise","que tu regarde","regarde pour moi","racconte-moi","racconte moi","dis moi","dis-moi","ce qu'il y a","ce qu'il ya","ce que contient","dans ce lien","dans cette page","sur ce site","dans ce site","tu peux me racconter","que tu me racconte"]


    play_wav_request = ["fichier audio","lire fichier audio","ouvrir fichier audio","jouer fichier audio","lire un fichier audio","ouvrir un fichier audio","jouer un fichier audio","lis-moi un fichier audio","ouvre-moi un fichier audio","joue-moi un fichier audio"]

    google_request = ["tu peux afficher","tu peux m'afficher","affiche moi","affiche-moi","montre moi","montre-moi","recherche wikipedia","que tu me fasse","fais une recherche","faire une recherche","recherche google","recherche internet","rechercher sur","rechercher dans","recherche sur","regarder sur","regarder dans","regarde dans","regarde sur","trouver sur","trouver dans","me trouver","trouve sur","trouve moi","trouve-moi","une page qui concerne","une page google","une page concernant","une page parlant","une page qui parle ","une page sur","infos qui parles","info qui parle","infos parlant","infos sur","info sur","infos concernant","info concernant","infos qui concernent","info qui concerne","infos qui parlent","info qui parle","parle moi","parle-moi","quelque chose sur","quelque chose concernant","quelque chose qui concerne","quelque chose qui parle","quelque chose parlant","truc qui parle","trucs qui parlent","truc parlant","truc concernant","trucs concernant","truc qui concerne","trucs qui concernent","un article qui concerne","un article wikipedia","un article concernant","un article parlant","un article qui parle ","un article sur"]

#est-ce que tu peux chercher sur Wikipédia intelligence artificielle

    wikipedia_request = ["tu peux afficher","tu peux m'afficher","affiche moi","affiche-moi","montre moi","montre-moi","recherche wikipedia","que tu me fasse","fais une recherche","faire une recherche","chercher sur","rechercher sur","rechercher dans","recherche sur","regarder sur","regarder dans","regarde dans","regarde sur","trouver sur","trouver dans","me trouver","trouve sur","trouve moi","trouve-moi","une page qui concerne","une page wikipedia","une page concernant","une page parlant","une page qui parle ","une page sur","infos qui parles","info qui parle","infos parlant","infos sur","info sur","infos concernant","info concernant","infos qui concernent","info qui concerne","infos qui parlent","info qui parle","parle moi","parle-moi","quelque chose sur","quelque chose concernant","quelque chose qui concerne","quelque chose qui parle","quelque chose parlant","truc qui parle","trucs qui parlent","truc parlant","truc concernant","trucs concernant","truc qui concerne","trucs qui concernent","un article qui concerne","un article wikipedia","un article concernant","un article parlant","un article qui parle ","un article sur"]

    wikipedia_full_request = ["page complete","page complet","page en entier","page entiere","en detail","article complet","article entier","article en entier","toute la page","affiche tout","version complete"]

    wait_words = ["attends","attendre","laisse moi","pause","minute","seconde","arrete"]


    to_remove = [" fais ","estce"," peux faire "," recherche ","faismoi"," fais ","peux ","fais recherche "," parle ","s'il te plait"," stp "," svp"," sur ","sil plait"]


    ask_for_name = any(element in decoded for element in trinity_name)

    ask_for_mean = any(element in decoded for element in trinity_mean)

    ask_for_creator = any(element in decoded for element in trinity_creator)

    ask_for_help = any(element in decoded for element in trinity_help)

    ask_for_prompt = any(element in decoded for element in prompt_request)

    ask_to_show = any(element in decoded for element in show_words)

    ask_for_rnd = any(element in decoded for element in rnd_request)

    ask_for_repeat = any(element in decoded for element in repeat_request)

    ask_for_history = any(element in decoded for element in search_history_request)

    ask_for_google = any(element in decoded for element in google_request)

    ask_for_wiki = any(element in decoded for element in wikipedia_request)

    ask_to_read_link = any(element in decoded for element in read_link_request)

    ask_to_play_wav = any(element in decoded for element in play_wav_request)

    ask_for_full_wiki = any(element in decoded for element in wikipedia_full_request)

    ask_to_wait = any(element in decoded for element in wait_words)


    if ask_to_wait:
              for element in prompt_request:
                  if element in decoded:
                      PRINT("Found wait match cmd :",element)

              Standing_By()
              return(True)




    if ask_for_name:
         for element in trinity_name:
             if element in decoded:
                  PRINT("Found name match cmd :",element)
         os.system("aplay %s"%(script_path+"/local_sounds/saved_answer/trinity.wav"))
         return(True)
    if ask_for_mean:
         for element in trinity_mean:
             if element in decoded:
                  PRINT("Found matrix match cmd :",element)
         os.system("aplay %s"%(script_path+"/local_sounds/saved_answer/matrix.wav"))
         return(True)

    if ask_for_creator:
         for element in trinity_creator:
             if element in decoded:
                  PRINT("Found botmaster match cmd :",element)
         os.system("aplay %s"%(script_path+"/local_sounds/saved_answer/botmaster.wav"))
         return(True)
    if ask_for_help:
         for element in trinity_help:
             if element in decoded:
                  PRINT("Found help match cmd :",element)
         os.system("aplay %s"%(script_path+"/local_sounds/saved_answer/help.wav"))
         return(True)
    if ask_for_prompt:
         for element in prompt_request:
             if element in decoded:
                  PRINT("Found prompt match cmd :",element)
         Fallback_Prompt()
         return(True)

    if ask_for_rnd:
         for element in rnd_request: 
             if element in decoded:
                  PRINT("Found rnd match cmd :",element)
         rnd = str(random.randint(1,2))
         ouinon = script_path+"/local_sounds/ouinon/"+rnd+".wav"
         os.system("aplay %s"%ouinon)
         return(True)

    if ask_for_repeat:
         for element in repeat_request: 
             if element in decoded:
                  PRINT("Found repeat match cmd :",element)
         os.system("aplay %s"%script_path+"local_sounds/repeat/isaid.wav")
         os.system("aplay %s"%script_path+"tmp/current_answer.wav")
         return(True)

    if ask_to_show:

         if ask_to_play_wav:
              for element in play_wav_request: 
                   if element in decoded:
                        PRINT("Found play sound match cmd :",element)
                        decoded = decoded.replace(element," ")
              os.system("aplay %s"%script_path+"local_sounds/question/sound_file.wav")
              sound_input = input("Entrez le chemin du fichier à lire:")
              if sound_input.endswith(".wav"):
                  Play_Response(sound_input,stayawake=False,savehistory=False)
                  return(True)
              else:
                  return(True)

         if "historique" in decoded:
            if ask_for_history:
               for element in search_history_request: 
                   if element in decoded:
                        PRINT("Found historique match cmd :",element)
                        decoded = decoded.replace(element," ")

               for element in to_remove:
                  if element in decoded:
                      decoded = decoded.replace(element," ")


               decoded = decoded.replace("  ","")


               SearchHistory(decoded)
               return(True)





         if (" lien" in decoded) or ("page web" in decoded):
             if ask_to_read_link: 
                  for element in read_link_request: 
                     if element in decoded:
                          PRINT("Found read link match cmd :",element)
                  ReadLink(txt=decoded)

                  return(True)


         if "google" in decoded:

            if ask_for_google:
               for element in google_request: 
                   if element in decoded:
                        PRINT("Found google match cmd :",element)
                        decoded = decoded.replace(element," ")

               for element in to_remove:
                  if element in decoded:
                      decoded = decoded.replace(element," ")


               decoded = decoded.replace("  ","")


               Google(decoded)
               return(True)



         if "wikipedia" in decoded:

              if ask_for_wiki:

                  for element in wikipedia_request: 
                      if element in decoded:
                           PRINT("Found wiki match cmd :",element)

                  for element in wikipedia_request: 
                      if element in decoded:
                           decoded = decoded.replace(element," ")
                  decoded = decoded.replace("wikipedia"," ")
                  os.system("aplay %s"%script_path+"local_sounds/server/wikipedia.wav")

                  if ask_for_full_wiki:
                      for element in wikipedia_full_request: 
                          if element in decoded:
                               decoded = decoded.replace(element," ")
                      for element in to_remove:
                           if element in decoded:
                               decoded = decoded.replace(element," ")

                      decoded = decoded.replace("  ","")

                      Wikipedia(decoded,FULL=True)
                  else:
                      for element in to_remove:
                           if element in decoded:
                               decoded = decoded.replace(element," ")

                      decoded = decoded.replace("  ","")


                      Wikipedia(decoded)
                  return(True)
         else:
              PRINT("-Found no cmd match")
              return(False)


def GetTitleLink(txt,site=None):
    try:
        google_result = googlesearch.search(txt,num_results=10,lang="fr", advanced=True)

        title_search = ""

        for g in google_result:
            if site:
                if site in g.url:
                    PRINT("google_result:",g.title)
                    title_search = g.title
                    break
            else:
                    PRINT("google_result:",g.title)
                    title_search = g.title
                    break


        if len(title_search) == 0:
            PRINT("-GetTitleLink no result from google")
            os.system("aplay %s"%script_path+"local_sounds/errors/err_no_result_google.wav")
            return(None)

        else:
            return(title_search)



    except Exception as e:
         os.system("aplay %s"%script_path+"local_sounds/errors/err_google.wav")
         print("Error:",str(e))
         return(None)



def ReadLink(txtinput=None,titleinput=None,urlinput=None):

    PRINT("txtinput:",txtinput)

    regex = re.compile(
        r'^(?:http://|https://|ftp://|.)'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not urlinput:
         urlinput = ""
         for word in txt.split():

             match = re.match(regex, word)
             if match:
                    urlinput = word
                    break

    if len(urlinput) > 0:
       if "wikipedia" in urlinput:
               if not titleinput:
                   wiki_title = GetTitleLink(txt,"wikipedia")
               else:
                   wiki_title = titleinput

               if wiki_title:
                   PRINT("wiki_title:",wiki_title)
                   return(Wikipedia(txt,title=wiki_title))

               else:
                   PRINT("no title using txtinput:",txtinput)
                   return(Wikipedia(txtinput))
       else:


                try:

                    response = requests.get(urlinput)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text_data = ''
                    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                         text_data += tag.get_text()
                    if len(text_data) >0:
                       os.system("aplay %s"%script_path+"/local_sounds/ok/reading_link.wav")
                       last_sentence.put(txtinput+" %s"%urlinput)
                       Text_To_Speech(text_data,stayawake=True)
                       return()
                    else:
                        os.system("aplay %s"%script_path+"local_sounds/errors/err_read_link_no_txt.wav")
                        return()
                except Exception as e:
                      print("Error:",str(e))
                      os.system("aplay %s"%script_path+"local_sounds/errors/err_read_link_request.wav")


    else:
         os.system("aplay %s"%script_path+"local_sounds/question/read_link_url.wav")

         url_input = input("Entrez un lien:")

         for word in url_input.split():
 
            match = re.match(regex, word)
            if match:
               urlinput = word
               break


    if len(urlinput) > 0:
           if "wikipedia" in urlinput:


               if not titleinput:
                   wiki_title = GetTitleLink(txt,"wikipedia")
               else:
                   wiki_title = titleinput

               if wiki_title:
                   PRINT("wiki_title:",wiki_title)
                   return(Wikipedia(txt,title=wiki_title))

               else:
                   PRINT("no title using txt:",txtintput)
                   return(Wikipedia(txtinput))

           else:

                try:

                    response = requests.get(urlinput)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text_data = ''
                    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                         text_data += tag.get_text()
                    if len(text_data) >0:
                       os.system("aplay %s"%script_path+"/local_sounds/ok/reading_link.wav")
                       last_sentence.put(txtinput+" %s"%urlinput)
                       Text_To_Speech(text_data,stayawake=True)
                       return()
                    else:
                        os.system("aplay %s"%script_path+"local_sounds/errors/err_read_link_no_txt.wav")
                        return()
                except Exception as e:
                      print("Error:",str(e))
                      os.system("aplay %s"%script_path+"local_sounds/errors/err_read_link_request.wav")
                      return()
    else:
              os.system("aplay %s"%script_path+"local_sounds/errors/err_url_not_valid.wav")
              return()


def Google(tosearch,rnbr=50): #,tstmode = True):

    Exit = False
    google_result = []

    PRINT("to search in google:",tosearch)

    def readlist(reslist,nbrlimit):
         PRINT("nbrlimit:",nbrlimit)
         PRINT("len(reslist):",len(reslist))

         for n,result in enumerate(reslist[:nbrlimit]):

            try:

               title = result[0]
               description = result[1]
               url = result[2]
               print("\n-Résultat %s\nTitle:%s\nDescription:%s\nUrl:%s\n"%(n+1,title,description,url))

#                totts = "Catégories:%s Texte utilisateur synthétisé:%s Score:%s"%(hist_cats,hist_txt,hist_bingo)
#                Text_To_Speech(totts,stayawake=True,savehistory=False)

            except Exception as e:
                 print("Error read list:",str(e))
                 continue

         Standing_By(self_launched=True)

    def readres(reslist,resnbr):

         PRINT("-readres resnbr:%s",resnbr)
         result = reslist[resnbr+1]

         try:

               title = result[0]
               description = result[1]
               url = result[2]
               print("\n-Résultat %s\nTitle:%s\nDescription:%s\nUrl:%s\n"%(resnbr,title,description,url))

#                totts = "Catégories:%s Texte utilisateur synthétisé:%s Score:%s"%(hist_cats,hist_txt,hist_bingo)
#                Text_To_Speech(totts,stayawake=True,savehistory=False)

         except Exception as e:
               print("Error read list:",str(e))

         while True:
             time.sleep(0.5)

             os.system("aplay  "+script_path+"local_sounds/question/search_history_cmd.wav")
             os.system("aplay  "+script_path+"local_sounds/question/do_i_read_link.wav")

             Start_Thread_Record()

             if Wait_for("audio"):
                   audio = audio_datas.get()
                   transcripts,transcripts_confidence,words,words_confidence,Err_msg = Speech_To_Text(audio)
                   txt,fconf = Check_Transcript(transcripts,transcripts_confidence,words,words_confidence,Err_msg)
                   txt = unidecode(txt.lower())
                   exit_words = ["rien","quitte","c'est bon","sors","sortir","partir","veille","laisse tomber","tant pis","c'est tout","fonction"]
                   ask_to_exit = any(element in txt for element in exit_words)
                   if ask_to_exit:
                       return(True)



                   if "non" in txt and not "oui" in txt:
                         os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")
                         return(False)
                   elif "oui" in txt and not "non" in txt:
                         os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")
                         return([description,title,url])




                   if len(txt)>0:
                      Question(txt)
                      Wait_for("question")
                   else:
                       score_sentiment.put(False)

                   opinion = score_sentiment.get()

                   if opinion == None:
                             os.system("aplay %s"%script_path+"/local_sounds/question/repeat.wav")
                   elif opinion == False:
                         os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")
                         return(False)
                   elif opinion == True:
                         os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")
                         return([description,title,url])


         

    def miniprompt(full):
        os.system("aplay %s"%script_path+"/local_sounds/prompt/2.wav")
        user_input = input("Que voulez vous faire avec les résultats? :")
        if len(str(user_input)) > 2:

              Exit = minicmd(user_input,full)
              if Exit:
                 return(True)
        else:
              miniprompt(full)


    def minicmd(txt_input,full):
         global Exit
         txt_input = unidecode(txt_input.lower())

         PRINT("minicmd:",txt_input)

         exit_words = ["rien","quitte","c'est bon","sors","sortir","partir","veille","laisse tomber","tant pis","c'est tout","fonction"]

         wait_words = ["attends","attendre","laisse moi","pause","minute","seconde","arrete"]

         number_words = {
    "plus important":0,
    "le meilleur":0,
    "le premier": 0,
    "le deuxieme": 1,
    "le troisieme": 2,
    "le quatrieme": 3,
    "le cinquieme": 4,
    "le sixieme": 5,
    "le septieme": 6,
    "le huitieme": 7,
    "le neuvieme": 8,
    "le dixieme": 9,
    "le onzieme": 10,
    "le douzieme": 11,
    "le treizieme": 12,
    "le quatorzieme": 13,
    "le quinzieme": 14,
    "le seizieme": 15,
    "le dix-septieme": 16,
    "le dix-huitieme": 17,
    "le dix-neuvieme": 18,
    "le vingtieme": 19,
    "le vingt et unieme": 20,
    "le vingt-deuxieme": 21,
    "le vingt-troisieme": 22,
    "le vingt-quatrieme": 23,
    "le vingt-cinquieme": 24,
    "le vingt-sixieme": 25,
    "le vingt-septieme": 26,
    "le vingt-huitieme": 27,
    "le vingt-neuvieme": 28,
    "le trentieme": 29,
    "le trente et unieme": 30,
    "le trente-deuxieme": 31,
    "le trente-troisieme": 32,
    "le trente-quatrieme": 33,
    "le trente-cinquieme": 34,
    "le trente-sixieme": 35,
    "le trente-septieme": 36,
    "le trente-huitieme": 37,
    "le trente-neuvieme": 38,
    "le quarantieme": 39,
    "le quarante et unieme": 40,
    "le quarante-deuxieme": 41,
    "le quarante-troisieme": 42,
    "le quarante-quatrieme": 43,
    "le quarante-cinquieme": 44,
    "le quarante-sixieme": 45,
    "le quarante-septieme": 46,
    "le quarante-huitieme": 47,
    "le quarante-neuvieme": 48,
    "le cinquantieme": 49,
    "le cinquante et unieme": 50,
    "le cinquante-deuxieme": 51,
    "le cinquante-troisieme": 52,
    "le cinquante-quatrieme": 53,
    "le cinquante-cinquieme": 54,
    "le cinquante-sixieme": 55,
    "le cinquante-septieme": 56,
    "le cinquante-huitieme": 57,
    "le cinquante-neuvieme": 58,
    "le soixantieme": 59,
    "le soixante et unieme": 60,
    "le soixante-deuxieme": 61,
    "le soixante-troisieme": 62,
    "le soixante-quatrieme": 63,
    "le soixante-cinquieme": 64,
    "le soixante-sixieme": 65,
    "le soixante-septieme": 66,
    "le soixante-huitieme": 67,
    "le soixante-neuvieme": 68,
    "le soixante-dixieme": 69,
    "le soixante et onzieme": 70,
    "le soixante-douzieme": 71,
    "le soixante-treizieme": 72,
    "le soixante-quatorzieme": 73,
    "le soixante-quinzieme": 74,
    "le soixante-seizieme": 75,
    "le soixante-dix-septieme": 76,
    "le soixante-dix-huitieme": 77,
    "le soixante-dix-neuvieme": 78,
    "le quatre-vingtieme": 79,
    "le quatre-vingt-unieme": 80,
    "le quatre-vingt-deuxieme": 81,
    "le quatre-vingt-troisieme": 82,
    "le quatre-vingt-quatrieme": 83,
    "le quatre-vingt-cinquieme": 84,
    "le quatre-vingt-sixieme": 85,
    "le quatre-vingt-septieme": 86,
    "le quatre-vingt-huitieme": 87,
    "le quatre-vingt-neuvieme": 88,
    "le quatre-vingt-dixieme": 89,
    "le quatre-vingt-onzieme": 90,
    "le quatre-vingt-douzieme": 91,
    "le quatre-vingt-treizieme": 92,
    "le quatre-vingt-quatorzieme": 93,
    "le quatre-vingt-quinzieme": 94,
    "le quatre-vingt-seizieme": 95,
    "le quatre-vingt-dix-septieme": 96,
    "le quatre-vingt-dix-huitieme": 97,
    "le quatre-vingt-dix-neuvieme": 98,
    "le centieme": 99,
    '1e': 0,
     '2e': 1,
     '3e': 2,
     '4e': 3,
     '5e': 4,
     '6e': 5,
     '7e': 6,
     '8e': 7,
     '9e': 8,
     '10e': 9,
     '11e': 10,
     '12e': 11,
     '13e': 12,
     '14e': 13,
     '15e': 14,
     '16e': 15,
     '17e': 16,
     '18e': 17,
     '19e': 18,
     '20e': 19,
     '21e': 20,
     '22e': 21,
     '23e': 22,
     '24e': 23,
     '25e': 24,
     '26e': 25,
     '27e': 26,
     '28e': 27,
     '29e': 28,
     '30e': 29,
     '31e': 30,
     '32e': 31,
     '33e': 32,
     '34e': 33,
     '35e': 34,
     '36e': 35,
     '37e': 36,
     '38e': 37,
     '39e': 38,
     '40e': 39,
     '41e': 40,
     '42e': 41,
     '43e': 42,
     '44e': 43,
     '45e': 44,
     '46e': 45,
     '47e': 46,
     '48e': 47,
     '49e': 48,
     '50e': 49,
     '51e': 50,
     '52e': 51,
     '53e': 52,
     '54e': 53,
     '55e': 54,
     '56e': 55,
     '57e': 56,
     '58e': 57,
     '59e': 58,
     '60e': 59,
     '61e': 60,
     '62e': 61,
     '63e': 62,
     '64e': 63,
     '65e': 64,
     '66e': 65,
     '67e': 66,
     '68e': 67,
     '69e': 68,
     '70e': 69,
     '71e': 70,
     '72e': 71,
     '73e': 72,
     '74e': 73,
     '75e': 74,
     '76e': 75,
     '77e': 76,
     '78e': 77,
     '79e': 78,
     '80e': 79,
     '81e': 80,
     '82e': 81,
     '83e': 82,
     '84e': 83,
     '85e': 84,
     '86e': 85,
     '87e': 86,
     '88e': 87,
     '89e': 88,
     '90e': 89,
     '91e': 90,
     '92e': 91,
     '93e': 92,
     '94e': 93,
     '95e': 94,
     '96e': 95,
     '97e': 96,
     '98e': 97,
     '99e': 98,
     '100e': 99,
    "hasard":"",
    "pif":"",
    "importe":"",
    "premiers":""}


         prompt_request = ['moi le prompt', "que je t'ecrive", " t'ecrire ", "je te l'ecris", "vais l'ecrire", "va l'ecrire", "va te l'ecrire", "vais te l'ecrire", 'affiche le prompt', 'ouvre le prompt', 'active le prompt', "moi l'invite de commande", "affiche l'invite de commande", "active l'invite de commande", "ouvre l'invite de commande", 'moi le clavier', 'affiche le clavier', 'ouvre le clavier', "j'ai besoin de t'ecrire","tu peux m'ouvrir le clavier","interprete"]

         read_request = ["moi","lire","lis","dire","dis","list","decrire","décris","resultat","affiche","afficher","selectionne","selectionner"]

         ask_to_wait = any(element in txt_input.lower() for element in wait_words)

         ask_to_exit = any(element in txt_input.lower() for element in exit_words)

         ask_to_read_results = any(element in txt_input.lower() for element in read_request)

         ask_for_prompt = any(element in txt_input.lower() for element in prompt_request)
      


         if ask_to_wait:
              for element in prompt_request:
                  if element in txt_input.lower():
                      PRINT("Found wait match cmd :",element)

              Standing_By()
              return(False)

         if ask_for_prompt:
              for element in prompt_request:
                  if element in txt_input.lower():
                      PRINT("Found prompt match cmd :",element)
              return(miniprompt(full))


         if ask_to_exit:
                   for element in exit_words:
                       if element in txt_input:
                            PRINT("Found exit match cmd :",element)
                   os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")
                   return(True)

         if ask_to_read_results:
                   for element in read_request:
                       if element in txt_input:
                            PRINT("Found read match cmd :",element)
                   chosen_one = False

                   lst_all = [" cent","100","complete","tout les","en entier","au total","en tout","combien","le reste"]
                   if any(element in txt_input.lower() for element in lst_all):
                         os.system("aplay %s"%script_path+"/local_sounds/ok/google_full.wav")
                         readlist(full,100)
                         return(False)

                   if "premiers" in txt_input:

                        for word in txt_input.split(" "):
                            try:
                                 chosen_one = int(word)
                                 break
                            except:
                                 continue

                        if chosen_one:
                              os.system("aplay %s"%script_path+"/local_sounds/ok/custom_google.wav")
                              readlist(full,chosen_one)
                              return(False)

                   for word,nbr in number_words.items():
                         if word in txt_input:
                              chosen_one = nbr
                              break

                   if chosen_one:
                        os.system("aplay %s"%script_path+"/local_sounds/ok/printed_google.wav")
                        quit = readres(full,chosen_one)
                        return(quit)
                   else:
                        for word in txt_input.split(" "):
                            try:
                                 chosen_one = int(word)
                                 break
                            except:
                                 continue
                   if chosen_one:
                       os.system("aplay %s"%script_path+"/local_sounds/ok/printed_google.wav")
                       quit = readres(full,chosen_one)
                       return(quit)
                   else:
                      os.system("aplay %s"%script_path+"/local_sounds/errors/err_number_notfound.wav")
                      return(False)

         if  not ask_to_wait and not ask_to_exit and not ask_to_read_results and not ask_for_prompt:

           os.system("aplay %s"%script_path+"/local_sounds/history/err_cmd.wav")
           return(False)


    try:
        google_query = googlesearch.search(tosearch,num_results=rnbr,lang="fr", advanced=True)


        for result in google_query:

            title = result.title
            description = result.description
            url = result.url
            google_result.append((title,description,url))

        if len(google_result) == 0:
            PRINT("-Google() no result from google")
            os.system("aplay %s"%script_path+"local_sounds/errors/err_no_result_google.wav")
            return()

    except Exception as e:
         os.system("aplay %s"%script_path+"local_sounds/errors/err_Google.wav")
         print("Error:",str(e))
         return()

    os.system("aplay %s"%script_path+"local_sounds/ok/googleres.wav")


    full = google_result[:100]

    PRINT("full\n:",full)

    for n,result in enumerate(full[:20]):
          title = result[0]
          description = result[1]
          url = result[2]
          print("\n-Résultat %s\nTitle:%s\nDescription:%s\nUrl:%s"%(n+1,title,description,url))


    Standing_By(self_launched=True)

    while True:
         time.sleep(0.5)

         os.system("aplay  "+script_path+"local_sounds/question/search_history_cmds.wav")

         Start_Thread_Record()

         if Wait_for("audio"):
               audio = audio_datas.get()
               transcripts,transcripts_confidence,words,words_confidence,Err_msg = Speech_To_Text(audio)
               txt,fconf = Check_Transcript(transcripts,transcripts_confidence,words,words_confidence,Err_msg)
               txt = unidecode(txt.lower())
               Exit = minicmd(txt,full)

         if Exit:
                 Go_Back_To_Sleep(go_trinity=False)
                 break
         else:
                 Go_Back_To_Sleep(go_trinity=False)

    if type(Exit) == list:
            return(ReadLink(txtinput=Exit[0],titleinput=Exit[1],urlinput=Exit[2]))

    Go_Back_To_Sleep(go_trinity=True)
    return

def Wikipedia(tosearch,Title= None ,FULL=None):

    PRINT("tosearch:",tosearch)
    PRINT("title:",Title)
    PRINT("FULL:",FULL)

    try:
        if Title:
            wiki_search = Title
        else:
            tosearch = "wikipedia " + tosearch
            wiki_search = GetTitleLink(tosearch,site="wikipedia")
          
        if not wiki_search:
            PRINT("-Wikipedia no result from google")
            os.system("aplay %s"%script_path+"local_sounds/errors/err_no_result_wiki.wav")
            return()

        wikipedia.set_lang("fr")



        query_list = wikipedia.search(wiki_search)
#        query_list = [i.replace(" ","_") for i in query_list]

        if len(query_list) > 0:
            for r in query_list:
               PRINT("-wiki reponse:",r)
        else:
            PRINT("-no result from wikipedia")
            os.system("aplay %s"%script_path+"local_sounds/errors/err_no_result_wiki.wav")
            return()

 
        if len(query_list) >0:
            PRINT("-Going to search : ",query_list[0])
            try:
                if not FULL:

                    os.system("aplay %s"%script_path+"local_sounds/question/wikipedia.wav")


                    Start_Thread_Record()

                    if Wait_for("audio"):
                                   audio = audio_datas.get()
                                   transcripts,transcripts_confidence,words,words_confidence,Err_msg = Speech_To_Text(audio)
                                   txt,fconf =Check_Transcript(transcripts,transcripts_confidence,words,words_confidence,Err_msg)



                    if  len(txt) > 0:
                         if "non" in txt.lower() and not "oui" in txt.lower():
                               opinion = False
                         elif "oui" in txt.lower() and not "non" in txt.lower():
                               opinion = True
                         else:
                              Question(txt)
                              Wait_for("question")
                              opinion = score_sentiment.get()
                    else:
                         opinion = False

                    if opinion == None:
                             choice = random.choice(["summary", "full"])
                             if choice == "summary":
                                     os.system("aplay %s"%script_path+"/local_sounds/ouinon/wiki_summary.wav")
                             if choice == "full":
                                     os.system("aplay %s"%script_path+"/local_sounds/ouinon/wiki_full.wav")
                    elif opinion == False:
                         choice = "summary"
                         os.system("aplay %s"%script_path+"/local_sounds/ok/wiki_summary.wav")
                    elif opinion == True:
                         choice = "full"
                         os.system("aplay %s"%script_path+"/local_sounds/ok/wiki_full.wav")

                elif FULL == True:
                     choice = "full"
                     os.system("aplay %s"%script_path+"/local_sounds/ouinon/wiki_full.wav")

                if choice == "summary":


                    try:
                        summary = wikipedia.summary(query_list[0])
                    except Exception as e:
                        try:
                            summary = wikipedia.summary(title=query_list[0],auto_suggest=True)
                        except Exception as e:
                            print("Error:",str(e))
                            try:
                                summary = wikipedia.summary(title=query_list[0].replace(" ","").replace("_",""),auto_suggest=True)
                            except Exception as e:
                                print("Error:",str(e))
                                os.system("aplay %s"%script_path+"local_sounds/errors/err_wiki.wav")
                                return()

                    last_sentence.put(tosearch)
                    Text_To_Speech(summary,stayawake=True)
                    return()

                else:

                    try:
                        page = wikipedia.page(query_list[0])
                        content = page.content
                    except Exception as e:
                        try:
                            page = wikipedia.page(title=query_list[0],auto_suggest=True)
                            content = page.content
                        except Exception as e:
                            print("Error:",str(e))
                            try:
                                page = wikipedia.page(title=query_list[0].replace(" ","").replace("_",""),auto_suggest=True)
                                content = page.content
                            except Exception as e:
                                print("Error:",str(e))
                                os.system("aplay %s"%script_path+"local_sounds/errors/err_wiki.wav")
                                return()

                    if "== Notes" in content:
                         content = content.split("== Notes")[0]

                    if "=== Notes" in content:
                         content = content.split("=== Notes")[0]

                    if "===" in content:
                         content = content.replace("==="," ")

                    if "==" in content:
                         content = content.replace("== "," ")

                    if len(content) >0:
                       last_sentence.put(tosearch)
                       Text_To_Speech(content,stayawake=True)
                       return()

                    else:
                         PRINT("-no result from content wikipedia")
                         os.system("aplay %s"%script_path+"local_sounds/errors/err_no_result_wiki.wav")
                         return()
            except Exception as e:
                os.system("aplay %s"%script_path+"local_sounds/errors/err_wiki.wav")
                print("Error:",str(e))
                return()

    except Exception as e:
       local_sounds/errors/err_func_wiki.wav
       os.system("aplay %s"%script_path+"local_sounds/errors/err_func_wiki.wav")
       print("Error:",str(e))
       return()



def Fallback_Prompt():
    PRINT("-fallbackprompt")
    os.system("aplay %s"%script_path+"/local_sounds/prompt/2.wav")
#    while True:
    if 1 == 1:
        user_input = input("Comment puis-je vous aider ?:")
        if len(str(user_input)) > 2:

              cmd = Commandes(user_input)
              if not cmd:
                  PRINT("-pas de cmd")
                  return(fallbackGpt(str(user_input)))
              else:
                    Go_Back_To_Sleep()


def Check_Transcript(transcripts,transcripts_confidence,words,words_confidence,Err_msg=""):


    avg_conf = 0
    bad_word = []
    bad_word_conf = []
    final_confidence = False
    
    PRINT("-checktranscript")

    if len(Err_msg) > 0:
        if Err_msg.startswith("Speech_To_Text:"):
            os.system("aplay  %s"%script_path+"/local_sounds/errors/err_stt.wav")
            Text_To_Speech(Err_msg,stayawake=True)
            os.system("aplay  %s"%script_path+"/local_sounds/errors/err_prompt.wav")
            return(Fallback_Prompt())

    if len(transcripts) > 0:
        PRINT("\n\ntranscripts:%s"%transcripts)
        PRINT("transcripts_confidence:%s"%transcripts_confidence)

        if len(words) > 0 and len(words_confidence) > 0:
            for w,wc in zip(words,words_confidence):
                    PRINT("confidence:%s word:%s"%(wc,w))
                    if wc < 0.9:
                          PRINT("That word has bad confidence : %s %s"%(w,wc))
                          bad_word_conf.append(w)
            avg_conf = sum(words_confidence)/len(words_confidence)
            PRINT("Average words confidence :%s"%avg_conf)



        if transcripts_confidence < 0.9:
           PRINT("Transcript has bad confidence\n.")
           final_confidence = False
        else:
           final_confidence = True
           PRINT("Transcript seems ok\n.")

        return(transcripts.replace("\\",""),final_confidence)
        
    else:
      os.system("aplay  %s"%script_path+"/local_sounds/errors/err_no_respons.wav")
      #      Go_Back_To_Sleep()
      return("",False)



def Question(txt):

    PRINT("-Question")
    score = 0
    try:

        client = language_v1.LanguageServiceClient()
        document = language_v1.Document(content=txt, language="fr",type_=language_v1.Document.Type.PLAIN_TEXT)
        sentiment = client.analyze_sentiment(request={'document': document}).document_sentiment

        PRINT("Text: {}".format(txt))
        PRINT("Sentiment: {}, {}".format(sentiment.score, sentiment.magnitude))

        PRINT("\n\nSentimentfull:\n%s"%sentiment)

        score = sentiment.score
    except Exception as e:
        PRINT("Error e:%s"%str(e))

    if score > -0.15 and score < 0.15:
        PRINT("Score is None")
        score_sentiment.put(None)
    elif score < -0.15:
        PRINT("Score is False")
        score_sentiment.put(False)
    elif score > 0.15:
        PRINT("Score is True")
        score_sentiment.put(True)

    return()

def Repeat(txt):

    negation = ["laisse tomber","c'est pas grave","non c'est bon","j'ai pas envie","j'ai plus envie","non merci"]
    prompt_request = ["affiche moi le prompt","préfère l'écrire","préfère écrire","vais l'écrire","va l'écrire","vais te l'écrire","t'as rien compris","tu n'as rien compris"]

    if "oui" in txt.lower() and not "non" in txt.lower():
           opinion = True
    elif "non" in txt.lower() and not "oui" in txt.lower():
           opinion = False
    else:
        Question(txt)
        Wait_for("question")
        opinion = score_sentiment.get()

    if opinion == False :
       no = any(element in txt.lower() for element in negation)
       if no:
          go_prompt = any(element in txt.lower() for element in prompt_request)
          if go_prompt:
              os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")
              return(Fallback_Prompt())
          else:
              os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")
              Go_Back_To_Sleep()
       else:
               os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")

               cmd = Commandes(txt)
               if cmd:
                  if cmd == "prompt":
                      return(Fallback_Prompt())
                  elif cmd == "random":
                       rnd = str(random.randint(1,2))
                       ouinon = script_path+"/local_sounds/ouinon/"+rnd+".wav"
                       os.system("aplay %s"%ouinon)
               else:
                     return(fallbackGpt(txt))
    else:

               os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")
               #go_to_function.put("Speech_To_Text")
               cmd = Commandes(txt)
               if cmd:
                  if cmd == "prompt":
                      return(Fallback_Prompt())
               else:
                     return(fallbackGpt(txt))

def Bad_Stt(txt):
    PRINT("-badstt")
    fname = "/tmp/last_bad_stt.wav"
    try:

            client = tts.TextToSpeechClient()
            audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

            text_input = tts.SynthesisInput(text=txt)
            voice_params = tts.VoiceSelectionParams(language_code="fr-FR", name="fr-FR-Neural2-A")

            response = client.synthesize_speech(input=text_input,voice=voice_params,audio_config=audio_config)
            audio_response = response.audio_content


            try:
                with open(script_path+fname, "wb") as out:
                     out.write(audio_response)
            except Exception as e:
                print("Error:",str(e))
                sys.exit()


    except Exception as e:
            PRINT("Error:%s"%str(e))
            Err = True
            try:
                os.system('pico2wave -l fr-FR -w %s "%s"'%(script_path+fname,txt))
            except Exception as e:
                print("Error:",str(e))
                sys.exit()

    os.system("aplay %s"%script_path+fname)



def Bad_Confidence(txt):
    PRINT("-badconf")

    Orig_sentence = txt

    PRINT("txt:",txt)
    PRINT("Orig_sentence:",Orig_sentence)

    rnd = str(random.randint(1,10))
    bad_sound = script_path+"/local_sounds/badconf/"+rnd+".wav"
    os.system("aplay %s"%bad_sound)

    Bad_Stt(txt)

    question_sound = script_path+"/local_sounds/question/1.wav"
    os.system("aplay %s"%question_sound)

    Start_Thread_Record()

    if Wait_for("audio"):
                   audio = audio_datas.get()
                   transcripts,transcripts_confidence,words,words_confidence,Err_msg = Speech_To_Text(audio)
                   txt,fconf =Check_Transcript(transcripts,transcripts_confidence,words,words_confidence,Err_msg)
                   if len(txt) > 0:
                       Question(txt)
                       Wait_for("question")
                   else:
                        score_sentiment.put(False)
    opinion = score_sentiment.get()
    
    if opinion == None:
             choice = random.choice(["repeat", "send","prompt"])
             if choice == "send":
                 if len(Orig_sentence) > 0:
                     os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")
                     return(fallbackGpt(Orig_sentence))
                 else:
                     os.system("aplay %s"%script_path+"local_sounds/forgot/1.wav")
                     choice = random.choice(["repeat","prompt"])
                     if choice == "repeat":
                         os.system("aplay %s"%script_path+"/local_sounds/repeat/1.wav")
                         return(Trinity("Repeat"))
                     if choice == "prompt":
                         os.system("aplay %s"%script_path+"/local_sounds/prompt/1.wav")
                         return(Fallback_Prompt())


             if choice == "repeat":
                 os.system("aplay %s"%script_path+"/local_sounds/repeat/1.wav")
                 return(Trinity("Repeat"))
             if choice == "prompt":
                 os.system("aplay %s"%script_path+"/local_sounds/prompt/1.wav")
                 return(Fallback_Prompt())
    elif opinion == False:
             choice = random.choice(["repeat","prompt"])
             if choice == "repeat":
                 os.system("aplay %s"%script_path+"/local_sounds/repeat/1.wav")
                 return(Trinity("Repeat"))
             if choice == "prompt":
                 os.system("aplay %s"%script_path+"/local_sounds/prompt/1.wav")
                 return(Fallback_Prompt())
    elif opinion == True:
                 os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")
                 if len(Orig_sentence) > 0:
                     return(fallbackGpt(Orig_sentence))
                 else:
                     os.system("aplay %s"%script_path+"local_sounds/forgot/1.wav")
                     choice = random.choice(["repeat","prompt"])
                     if choice == "repeat":
                         os.system("aplay %s"%script_path+"/local_sounds/repeat/1.wav")
                         return(Trinity("Repeat"))
                     if choice == "prompt":
                         os.system("aplay %s"%script_path+"/local_sounds/prompt/1.wav")
                         return(Fallback_Prompt())



def Split_Text(txt):


    PRINT("-Split text")
    result = []
    txt_len = len(txt)
    needle = 0
    while True:
        part = txt[needle:needle+450]
        if len(part) >=450:
#            print("len part > 450:\n",part)
            last_ponct = part.rfind('\n')  
            if last_ponct > 0:
                part = part[:last_ponct + 1]
            else:
                last_ponct = part.rfind('.')
                if last_ponct > 0:
                    part = part[:last_ponct + 1]
                else:
                     last_ponct = part.rfind(' ')
                     if last_ponct > 0:
                         part = part[:last_ponct + 1]
                     else:
                         part = txt[needle:needle+250]
        else:
#            print("len part < 450:\n",part)
            result.append(part.strip())
            break

        result.append(part.strip())

        if needle >= txt_len:
             break
        else: 
             needle += len(part)


    return(result)




def Speech_To_Text(audio):
    PRINT("-speechtotext")

    Err_msg = ""
    client = speech.SpeechClient()
    to_txt = speech.RecognitionAudio(content=audio)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#        max_alternatives=3,
        enable_word_confidence=True,
        enable_automatic_punctuation=True,
        sample_rate_hertz=16000,
        audio_channel_count=1,
        language_code="fr-FR",
    )
    try:
        google_stt = client.recognize(request={"config": config, "audio": to_txt})
    except Exception as e:
        PRINT("Error:%s"%str(e))
        Err_msg = "Speech_To_Text:"+str(e)
#    PRINT("google_stt %s:\n%s"%(type(google_stt),google_stt))


    transcripts = ""
    transcripts_confidence = 0
    words = []
    words_confidence = []

    if len(Err_msg) == 0:
        try:
            for result in google_stt.results:
                transcripts = result.alternatives[0].transcript
                transcripts_confidence = result.alternatives[0].confidence

                if result.alternatives[0].words:
                   for word in result.alternatives[0].words:
                        words.append(word.word)
                        words_confidence.append(word.confidence)
        except Exception as e:
            PRINT("Error:%s"%str(e))

    if len(transcripts) > 0:
         print("\n-User said:",transcripts)

    return(transcripts,transcripts_confidence,words,words_confidence,Err_msg)




def Text_To_Speech(txtinput,stayawake=False,savehistory=True):

    PRINT("-texttospeech")


    PRINT("len(txtinput:",len(txtinput))
    parsed_response = parse_response(str(txtinput))

    txt_list = Split_Text(parsed_response)
    ln_txt_list = len(txt_list)
    wav_list = []
    final_wav = script_path + "/tmp/current_answer.wav"
    Err = False

    for n,txt in enumerate(txt_list):
        time.sleep(0.5)
        if len(txt_list) > 1:
                fname = "/tmp/answer"+str(n)+".wav"
        else:
                fname = "/tmp/current_answer.wav"
        try:

            client = tts.TextToSpeechClient()
            audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

            text_input = tts.SynthesisInput(text=txt)
            voice_params = tts.VoiceSelectionParams(language_code="fr-FR", name="fr-FR-Neural2-A")

            response = client.synthesize_speech(input=text_input,voice=voice_params,audio_config=audio_config)
            audio_response = response.audio_content


            try:
                with open(script_path+fname, "wb") as out:
                     out.write(audio_response)
            except Exception as e:
                print("Error:",str(e))
                sys.exit()

            wav_list.append(script_path+fname)

        except Exception as e:
            PRINT("Error:%s"%str(e))
            Err = True
            try:
                os.system('pico2wave -l fr-FR -w %s "%s"'%(script_path+fname,txt))
            except Exception as e:
                print("Error:",str(e))
                sys.exit()
            wav_list.append(script_path+fname)

    if Err:
        os.system("aplay  "+script_path+"local_sounds/errors/err_tts.wav")



    if len(txt_list) > 1:

         wavs_path = " ".join(wav_list)
         cmd = str(wavs_path) + " "+ str(final_wav)
         PRINT("sox ",cmd)
         os.system("sox "+ str(cmd))

    return(Play_Response(audio_response=final_wav,stay_awake=stayawake,save_history=savehistory,answer_txt=txtinput))




def Play_Response(audio_response=None,stay_awake=False,save_history=True,answer_txt=None):
    PRINT("-playresponse")

    os.system("aplay  "+audio_response)

    if save_history:
       History(answer_txt)

    if not stay_awake:
        Go_Back_To_Sleep(True)

def dbg_queue():

            PRINT("\nsleep.empty:%s"%cancel_operation.empty())
            PRINT("start.empty:%s"%wake_me_up.empty())
            PRINT("chunks.empty:%s"%chunks.empty())
            PRINT("audio_datas:%s"%audio_datas.empty())
            PRINT("")

def Start_Thread_Record():
    PRINT("-start thread rec")
    record_on.put(True)

    RQ = Thread(target=Record_Query)
    RQ.start()
    CS = Thread(target=Check_Silence)
    CS.start()

def Go_Back_To_Sleep(go_trinity=True):

     global Current_Category

     PRINT("\n\n------goback to sleep-----\n\n")



     while True:
          if record_on.empty():
             break
          tmp = record_on.get()


     while True:
          if chunks.empty():
             break
          tmp = chunks.get()

     while True:
          if wake_me_up.empty():
              wake_me_up.put(True)
              break
          tmp = wake_me_up.get()

     while True:
          if awake.empty():
             break
          tmp = awake.get()

     while True:
          if cancel_operation.empty():
              break
          tmp = cancel_operation.get()



     while True:
          if No_Input.empty():
              break
          tmp = No_Input.get()

     while True:
          if score_sentiment.empty():
              break
          tmp = score_sentiment.get()

     while True:
          if audio_datas.empty():
              break
          tmp = audio_datas.get()

     while True:
          if last_sentence.empty():
              break
          tmp = last_sentence.get()

     while True:
          if cancel_operation.empty():
              break
          tmp = cancel_operation.get()

     if len(Current_Category) > 0:
            Current_Category  = []

     if go_trinity:
         PRINT("\nReturn to trinity()\n")
         return(Trinity("WakeMe"))
     else:
         return()

def Wait_for(action):
    PRINT("-wait for %s"%action)

    while cancel_operation.empty():

       if action == "audio":
            if not audio_datas.empty():
                break

       if action == "question":
            if not score_sentiment.empty():
                break



    if not cancel_operation.empty():
           PRINT("-Operation %s cancelled."%action)
           return(False)
    else:
           PRINT("-Operation %s finished."%action)
           return(True)



#       time.sleep(1)


def similar(txt1,txt2):
    PRINT("txt1:",txt1)
    PRINT("txt2:",txt2)
    similarity = SequenceMatcher(None,txt1,txt2).ratio()
    PRINT("Similarity : ",similarity)
    return(similarity)

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  

def preprocess(txt):
    sentence = unidecode(txt)
    sentence = sentence.lower()
    sentence = ''.join(char for char in sentence if char not in string.punctuation)
    tokens = word_tokenize(sentence)
    stop_words = set(stopwords.words('french'))
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in pos_tag(tokens)]
    return ' '.join(tokens)



def Standing_By(self_launched=False):
    PRINT("-wakeup")

#    word_key = script_path+"/models/Trinity_en_linux_v2_2_0.ppn"
    word_key = script_path+"/models/trinity_fr_raspberry-pi_v3_0_0.ppn"
    pvfr = script_path+"/models/porcupine_params_fr.pv"
    porcupine = None
    keyword_index = None

    if self_launched:
        os.system("aplay %s"%script_path+"local_sounds/wait/selfwait.wav")

    else:
        os.system("aplay %s"%script_path+"local_sounds/history/wait.wav")


    try:
        porcupine = pvporcupine.create(access_key=PICO_KEY, model_path = pvfr,keyword_paths=[word_key],sensitivities=[1] )
        with ignoreStderr():
            pa = pyaudio.PyAudio()
        audio_stream = pa.open(
                        rate=porcupine.sample_rate,
                        channels=1,
                        format=pyaudio.paInt16,
                        input=True,
                        frames_per_buffer=porcupine.frame_length)
        PRINT("Listening for 'Trinity'...")

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index == 0:
                PRINT("keyword_index:",keyword_index)
                rnd = str(random.randint(1,15))
                wake_sound = script_path+"/local_sounds/wakesounds/"+rnd+".wav"
                os.system("aplay %s"%wake_sound)
                break

    finally:
        PRINT("-Awake.")
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()






def SearchHistory(tosearch):
    Exit = False

    PRINT("Searching for %s in history."%tosearch)


    def seekndestroy(haystack,find):
       
       lnhaystack = len(haystack)
       lnfind = len(find)

       needle1 = 0
       needle2 = lnfind

       txt = ""

       while True:
          if needle2 > lnhaystack:
               return(haystack)
          if haystack[needle1:needle2] == find:
                 txt = haystack[:needle1] + haystack[needle2:]
                 return(txt)
          else:
                 needle1 += 1
                 needle2 += 1 



    def playlist(toplay):

         PRINT("\ntoplay:\n %s \n"%toplay)

         nbrtoplay = len(toplay)
         os.system("aplay %slocal_sounds/history/playlist_%s.wav"%(script_path,str(nbrtoplay)))

         for n,wavfile in enumerate(toplay):
             os.system("aplay %slocal_sounds/history/play_%s.wav"%(script_path,str(n+1)))
             if wavfile.endswith(".wav"):
                  os.system("aplay %s"%wavfile)
             else:
                  try:
                      args = [element for element in match.strip().split("***") if element]
                      hist_wav = args[2]
                      os.system("aplay %s"%hist_wav)
                  except Exception as e:
                      print("Error playlist:",str(e))

    def readlist(toread):
         PRINT("toread:",toread)
         for match in toread:

            args = [element for element in match.strip().split("***") if element]
            try:

                hist_cats = args[0]

                hist_txt = args[1]

                hist_wav = args[2]

                hist_bingo = args[3]

                totts = "Catégories:%s Texte utilisateur synthétisé:%s Score:%s"%(hist_cats,hist_txt,hist_bingo)

                Text_To_Speech(totts,stayawake=True,savehistory=False)

            except Exception as e:
               print("Error read list:",str(e))
               continue


    def minicmd(txt_input,top5,full):
         global Exit
         txt_input = unidecode(txt_input.lower())

         PRINT("minicmd:",txt_input)

         exit_words = ["rien","quitte","c'est bon","sors","sortir","partir","veille","laisse tomber","tant pis","c'est tout","fonction"]

         wait_words = ["attends","attendre","laisse moi","pause","minute","seconde","arrete"]

         audio_words = ["audio","wav","sonor","ecouter","entendre","enregistrement","rejoue","rejouer","joue","jouer","fichier"]

         number_words = {"plus important":"0:1","le meilleur":"0:1","le premier":"0:1","deux premier":"0:2","trois premier":"0:3","quatre premier":"0:4","tout les":"0:5","les cinq":"0:5","numero un":"0:1","numero deux":"1:2","numero trois":"2:3","numero quatre":"3:4","numero cinq":"4:5","numero 1 ":"0:1","numero 2":"1:2","numero 3":"2:3","numero 4":"3:4","numero 5":"4:5","le second":"1:2","le deuxieme":"1:2","le troisieme":"2:3","le quatrieme":"3:4","le cinquieme":"4:5","hasard":"","pif":"","importe":"","et un":"0:1","et deux":"1:2","et trois":"2:3","et quatre":"3:4","et cinq":"4:5","et 1":"1:2","et 2":"1:2","et 3":"2:3","et 4":"3:4","et 5":"4:5","fichier 1":"0:1","fichier 2":"1:2","fichier 3":"2:3","fichier 4":"3:4","fichier 5":"4:5","audio 1 ":"0:1","audio 2":"1:2","audio 3":"2:3","audio 4":"3:4","audio 5":"4:5","fichier un ":"0:1","fichier deux":"1:2","fichier trois":"2:3","fichier quatre":"3:4","fichier cinq":"4:5","audio un ":"0:1","audio deux":"1:2","audio trois":"2:3","audio quatre":"3:4","audio cinq":"4:5"," un":"0:1"," deux":"1:2"," trois":"2:3"," quatre":"3:4"," cinq":"4:5","1 et ":"0:1","2 et":"1:2","3 et":"2:3","4 et":"3:4","5 et":"4:5","1":"0:1","2":"1:2","3":"2:3","4":"3:4","5":"4:5"}

         prompt_request = ['moi le prompt', "que je t'ecrive", " t'ecrire ", "je te l'ecris", "vais l'ecrire", "va l'ecrire", "va te l'ecrire", "vais te l'ecrire", 'affiche le prompt', 'ouvre le prompt', 'active le prompt', "moi l'invite de commande", "affiche l'invite de commande", "active l'invite de commande", "ouvre l'invite de commande", 'moi le clavier', 'affiche le clavier', 'ouvre le clavier', "j'ai besoin de t'ecrire","tu peux m'ouvrir le clavier","interprete"]

         read_request = ["moi","lire","lis","dire","dis","list","décrire","décris","résultat","affiche","afficher","combien en tout","combien de résulat"]

         search_history_request = ["tu peux afficher","tu peux m'afficher","affiche moi","affiche-moi","montre moi","montre-moi","recherche historique","que tu me fasse","fais une recherche","tu peux chercher","tu peux rechercher","faire une recherche","rechercher sur","rechercher dans","recherche sur","regarder sur","regarder dans","cherche moi","cherche-moi","regarde dans","regarde sur","trouver sur","contenant","concernant","trouver dans","me trouver","trouve sur","trouve moi","trouve-moi","une page qui concerne","une entree parlant","une entree concernant","une entree parlant","une entree qui parle ","une entree sur","infos qui parles","info qui parle","infos parlant","infos sur","info sur","infos concernant","info concernant","infos qui concernent","info qui concerne","infos qui parlent","info qui parle","parle moi","parle-moi","quelque chose sur","quelque chose concernant","quelque chose qui concerne","quelque chose qui parle","quelque chose parlant","truc qui parle","trucs qui parlent","truc parlant","truc concernant","trucs concernant","truc qui concerne","trucs qui concernent","en rapport","si il y a","si il ya","si ya","l'historique","fais une","autre","encore"]

         ask_to_search = any(element in txt_input.lower() for element in search_history_request)

         ask_to_play = any(element in txt_input.lower() for element in audio_words)

         ask_to_wait = any(element in txt_input.lower() for element in wait_words)

         ask_to_exit = any(element in txt_input.lower() for element in exit_words)

         ask_to_read_results = any(element in txt_input.lower() for element in read_request)

         ask_for_prompt = any(element in txt_input.lower() for element in prompt_request)

         if ask_to_wait:
              for element in prompt_request:
                  if element in txt_input.lower():
                      PRINT("Found wait match cmd :",element)

              Standing_By()
              return()

         if ask_for_prompt:
              for element in prompt_request:
                  if element in txt_input.lower():
                      PRINT("Found prompt match cmd :",element)
              return(miniprompt(top5,full))


         if ask_to_search:
              if "historique" in txt_input.lower() and not "resultat" in txt_input.lower():
                   for element in search_history_request:
                       if element in txt_input:
                            txt_input = txt_input.replace(element," ") 
                            PRINT("Found search match cmd :",element)
                   Exit = True
                   return(SearchHistory(txt_input))
          
         if ask_to_exit:
                   for element in exit_words:
                       if element in txt_input:
                            PRINT("Found exit match cmd :",element)
                   os.system("aplay %s"%script_path+"/local_sounds/ok/1.wav")
                   return(True)

         if ask_to_play:
                   to_play_lst = []
                   found_nbr_lst = []
                   copy_txt_input = txt_input
                   for word,nbr in number_words.items():
                         if word in copy_txt_input:

                             if not word in ["hasard","pif","importe"]:
                                 found_nbr_lst.append(nbr)
                                 copy_txt_input = seekndestroy(copy_txt_input,word)
                             else:
                                       rnd_nbr = random.randint(0,4)
                                       chosen_line = top5[rnd_nbr]

                                       args = [element for element in chosen_line.strip().split("***") if element]

                                       hist_cats = args[0]

                                       hist_txt = args[1]

                                       hist_wav = args[2]

                                       hist_bingo = args[3]

                                       os.system("aplay  "+script_path+"local_sounds/history/choose_%s.wav"%(str(rnd_nbr + 1)))

                                       playlist([hist_wav])
                                       return(True)

                   if len(found_nbr_lst) > 0:
                       track_num = 0
                       res_to_show = []
                       for nums in found_nbr_lst:
                           start = int(nums.split(":")[0])
                           end = int(nums.split(":")[1])
                           if (track_num <= 5) and (track_num < len(top5)):
                               track_num += (end - start)
                               res_to_show.append("".join(top5[start:end]))
                           else:
                               break

                       if len(res_to_show) >0:
                           playlist(res_to_show)
                       else:
                           playlist([top5[0]])
                   else:
                        playlist([top5[0]])


                   return(True)

         if ask_to_read_results:
                   for element in read_request:
                       if element in txt_input:
                            PRINT("Found read match cmd :",element)

                   if ("combien" and "tout" in txt_input) or ("combien" and "total" in txt_input):

                           total_res = len(full)
                           answer = "Il y a %s résultats en tout correspondant à votre recherche . Les voici:"%total_res
                           Text_To_Speech(answer,stayawake=True,savehistory=False)
                           
                           for n,line in enumerate(full) :
                               if len(line) >0:
                                   args = [element for element in line.strip().split("***") if element]
                                   try:

                                       hist_cats = args[0]

                                       hist_txt = args[1]

                                       hist_answer = args[2]

                                       hist_wav = args[3]

                                       hist_bingo = args[4]

                                       print("\n-(Résultat numéro %s)\n    Categories:%s\n    Texte utilisateur synthétisé:%s\n    Réponse:%s\n    Score:%s"%(str(n+1),hist_cats,hist_txt,hist_answer,hist_bingo))


                                   except Exception as e:
                                        print("err :",str(e))
                                        continue
                           return()


                   found_nbr_lst = []
                   copy_txt_input = txt_input
                   for word,nbr in number_words.items():
                         if word in copy_txt_input:

                             if not word in ["hasard","pif","importe"]:
                                 found_nbr_lst.append(nbr)
                                 copy_txt_input = seekndestroy(copy_txt_input,word)
                             else:
                                       rnd_nbr = random.randint(0,4)
                                       chosen_line = top5[rnd_nbr]

                                       args = [element for element in chosen_line.strip().split("***") if element]

                                       hist_cats = args[0]

                                       hist_txt = args[1]

                                       hist_answer = args[2]

                                       hist_wav = args[3]

                                       hist_bingo = args[4]

                                       res_str = "\n-(Résultat numéro %s)\n    Catégories:%s\n    Texte utilisateur synthétisé:%s\n     Réponse:%s\n   Score:%s"%(str(n+1),hist_cats,hist_txt,hist_answer,hist_bingo)
                                       

                                       os.system("aplay  "+script_path+"local_sounds/history/choose_%s.wav"%(str(rnd_nbr + 1)))
                                       Text_To_Speech(res_str,stayawake=True,savehistory=False)
                                       return()



                   if len(found_nbr_lst) > 0:
                       track_num = 0
                       res_to_show = []
                       for nums in found_nbr_lst:
                           start = int(nums.split(":")[0])
                           end = int(nums.split(":")[1])
                           if (track_num <= 5) and (track_num < len(top5)):
                               track_num += (end - start)
                               res_to_show.append(" ".join(top5[start:end]))
                           else:
                               break
                       if len(res_to_show) >0:
                           readlist(res_to_show)
                       else:
                           readlist(top5)
                   else:
                        readlist(top5)




         if not ask_to_search and not ask_to_play and not ask_to_wait and not ask_to_exit and not ask_to_read_results and not ask_for_prompt:
           
           os.system("aplay %s"%script_path+"/local_sounds/history/err_cmd.wav")
           return()

    def miniprompt(top5,full):
        os.system("aplay %s"%script_path+"/local_sounds/prompt/2.wav")
        user_input = input("Que voulez vous faire avec l'historique? :")
        if len(str(user_input)) > 2:

              Exit = minicmd(user_input,top5,full)
              if Exit:
                 return(True)
        else:
              miniprompt(top5,full)



    files = [f for f in os.listdir(script_path+"/history/") if os.path.isfile(os.path.join(script_path+"/history/", f))]


    MatchResults =[]

    for file in files:
        try:
            with open(script_path+"/history/"+file) as f:
                  data = [line.strip() for line in f]


            for line in data :
                if len(line) >0:
                    args = [element for element in line.strip().split("***") if element]
                    try:

                        hist_cats = args[0]
     
                        hist_txt = args[1]
     
                        hist_answer = args[2]

                        hist_wav = args[3]

                    except Exception as e:
                         continue
                    bingoat = 0
                    for word in tosearch.split(" "):
                        if len(word.replace(" ","")) > 0:
                            if word.lower() in hist_txt.lower():
                                 bingoat += 1
                            if word.lower() in hist_answer.lower():
                                 bingoat += 1
                    if bingoat > 0:
                       MatchResults.append(line+"***"+str(bingoat))

        except Exception as e:
           print("Error:",str(e))

    SortedMatched = sorted(MatchResults, key=lambda s: int(re.findall(r'\d+', s)[-1] if re.findall(r'\d+', s) else 0), reverse=True)
    MatchedNbr = len(SortedMatched)


    if MatchedNbr > 5:
         MatchedNbr = 5

    if len(SortedMatched) == 1:
         os.system("aplay  "+script_path+"local_sounds/history/found_one.wav")
    elif len(SortedMatched) == 2:
         os.system("aplay  "+script_path+"local_sounds/history/found_two.wav")
    elif len(SortedMatched) == 3:
         os.system("aplay  "+script_path+"local_sounds/history/found_three.wav")
    elif len(SortedMatched) == 4:
         os.system("aplay  "+script_path+"local_sounds/history/found_four.wav")
    elif len(SortedMatched) >= 5:
         os.system("aplay  "+script_path+"local_sounds/history/found_five.wav")
    else:
        os.system("aplay  "+script_path+"local_sounds/history/no_result.wav")
        return()

    TopFive = SortedMatched[:MatchedNbr]

    for n,match in enumerate(TopFive):

            args = [element for element in match.strip().split("***") if element]
            try:

                hist_cats = args[0]

                hist_txt = args[1]

                hist_answer = args[2]

                hist_wav = args[3]

                hist_bingo = args[4]

                print("\n-(Résultat %s)\n    Catégories:%s\n    Texte utilisateur Synthétisé:%s\n    Réponse:%s\n    Fichier audio:%s\n    Score:%s\n"%(str(n+1),hist_cats,hist_txt,hist_answer,hist_wav,hist_bingo))

            except Exception as e:
                print("Error:",str(e))
                continue


    Standing_By(self_launched=True)

    while True:


         time.sleep(0.5)


         if len(TopFive) >1:
             os.system("aplay  "+script_path+"local_sounds/question/search_history_cmds.wav")
         else:
             os.system("aplay  "+script_path+"local_sounds/question/search_history_cmd.wav")




         Start_Thread_Record()

         if Wait_for("audio"):
               audio = audio_datas.get()
               transcripts,transcripts_confidence,words,words_confidence,Err_msg = Speech_To_Text(audio)
               txt,fconf = Check_Transcript(transcripts,transcripts_confidence,words,words_confidence,Err_msg)
               Exit = minicmd(txt.replace("-"," "),TopFive,SortedMatched)

         if Exit:
             Go_Back_To_Sleep(go_trinity=True)
             return()
         else:
             Go_Back_To_Sleep(go_trinity=False)

def History(answer):

   PRINT("-History")

   if not answer:
        PRINT("No answer saved exiting History")
        return()

   if last_sentence.empty():
        PRINT("No last_ sentence saved exiting History")
        return()

   txt = last_sentence.get()

   PRINT("last sentence:",txt)


   if len(Current_Category) == 0:
       Classify(txt)

   Cat_File = str(Current_Category[0]).replace("-",".").replace("&","and").replace(",",".")
   if Cat_File.startswith("."):
        Cat_File = Cat_File[1:]

   Cat_List = ".".join(Current_Category)

   Lemmatizer = preprocess(txt)

   PRINT("lemmatized last sentence:",Lemmatizer)

   rnd_name = str(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))) + ".wav"

   new_wav = SAVED_ANSWER + rnd_name
   current_wav = script_path + "/tmp/current_answer.wav"

   os.system("cp %s %s"%(current_wav,new_wav))

   if os.path.exists(script_path+"/history/"+Cat_File):
       with open(script_path+"/history/"+Cat_File,"a+") as f:
            data = "\n"
            data += "***" + str(Cat_List)
            data += "***" + Lemmatizer
            data += "***" + answer
            data += "***" + new_wav
            PRINT("data:",data)
            PRINT("wrote to ",script_path+"/history/"+Cat_File)
            f.write(data)
 
   else:

       with open(script_path+"/history/"+Cat_File,"w") as f:
            data = "\n"
            data += "***" + str(Cat_List)
            data += "***" +Lemmatizer
            data += "***" + answer
            data += "***" + new_wav
            PRINT("data:",data)   
            PRINT("wrote to ",script_path+"/history/"+Cat_File)
            f.write(data)

def Check_History(question):


   PRINT("-Check_History")


   PRINT("question:",question)

   lemmatized = preprocess(question)

   if len(Current_Category) == 0:
       Classify(question)
   else:
       Categories = Current_Category

   Cat_File = str(Current_Category[0])
   Joined_Cat = "_".join(Current_Category)

   Best_Score = []
   Best_Txt = []
   Best_Answer = []
   Best_Wav = []
  
   if os.path.exists(script_path+"/history/"+Cat_File):
       with open(script_path+"/history/"+Cat_File,"r") as f:
             data = [line.strip() for line in f]


       for line in data :
           if len(line) >0:
               args = [element for element in line.strip().split("***") if element]
               try:
                   hist_cats = args[0]

                   hist_txt = args[1]

                   hist_answer = args[2]

                   hist_wav = args[3]

                   if hist_cats == Joined_Cat:
                        score = similar(lemmatized,hist_txt)
                        if "wikipedia" in hist_txt:
                            if score > 0.85:

                                print("hist_cats:",hist_cats)
                                print("hist_txt:",hist_txt)
                                print("hist_answer:",hist_answer)
                                print("hist_wav:",hist_wav)
                                print("Score:",score)


                                Best_Score.append(score)
                                Best_Txt.append(hist_txt)
                                Best_Answer(hist_answer)
                                Best_Wav.append(hist_wav)

                        else:
                            if score > 0.5:
                                print("hist_cats:",hist_cats)
                                print("hist_txt:",hist_txt)
                                print("hist_answer:",hist_answer)
                                print("hist_wav:",hist_wav)
                                print("Score:",score)
                                Best_Score.append(score)
                                Best_Txt.append(hist_txt)
                                Best_Answer(hist_answer)
                                Best_Wav.append(hist_wav)

                   else:
                       pass
               except Exception as e:
                   print("Error: ",str(e))
                   continue

       final_score = 0
       final_wav = ""
       for s in Best_Score:
           if s > final_score:
                final_score = s

       for s,t,w in zip(Best_Score,Best_Txt,Best_Answer,Best_Wav):
            if s == final_score:
                PRINT("-Best matches :",t)
                final_wav = w

       if len(final_wav) > 0:




                            os.system("aplay %s"%script_path+"local_sounds/already/1.wav")
                            os.system("aplay %s"%final_wav)
                            os.system("aplay %s"%script_path+"local_sounds/question/amigood.wav")

                            Start_Thread_Record()

                            if Wait_for("audio"):
                                audio = audio_datas.get()
                                transcripts,transcripts_confidence,words,words_confidence,Err_msg = Speech_To_Text(audio)
                                txt,fconf =Check_Transcript(transcripts,transcripts_confidence,words,words_confidence,Err_msg)
                                if len(txt) > 0:
                                      Question(txt)
                                      Wait_for("question")
                                else:
                                      score_sentiment.put(False)
                                opinion = score_sentiment.get()
                                if opinion == None:
                                        os.system("aplay %s"%script_path+"local_sounds/notok/1.wav")
                                        return(False)
                                elif opinion == False:
                                        os.system("aplay %s"%script_path+"local_sounds/notok/1.wav")
                                        return(False)
                                else:
                                        os.system("aplay %s"%script_path+"local_sounds/ok/1.wav")
                                        return(True)




   else:
        return(False)




def Classify(text_content):

    global Current_Category
    PRINT("-Classify")
    
    categories = []

    try:
        client = language_v1.LanguageServiceClient()

        type_ = language_v1.Document.Type.PLAIN_TEXT
        language = "fr"
        document = {"content": text_content, "type_": type_, "language": language}
        content_categories_version = (
        language_v1.ClassificationModelOptions.V2Model.ContentCategoriesVersion.V2
    )
        response = client.classify_text(
            request={
            "document": document,
            "classification_model_options": {
                "v2_model": {"content_categories_version": content_categories_version}
            },
        }
    )

        for category in response.categories:
            categories.append(category.name.replace("/","-").replace(" ","-"))
    except Exception as e:
         print("Error:",str(e))
         categories = ["nocat"]

    if len(categories) == 0 :
         categories = ["nocat"]

    Current_Category = categories
    PRINT("Current_Category:\n",Current_Category)

    return()


def Trinity(fname = "WakeMe"):

        PRINT("\n-Trinity\n")
        PRINT("fname:",fname)

        if fname == "WakeMe":

            wake_up()
            awake.put(True)
        else:

            if fname == "Speech_To_Text":
               Start_Thread_Record()
               if Wait_for("audio"):
                      audio = audio_datas.get()
                      transcripts,transcripts_confidence,words,words_confidence,Err_msg = Speech_To_Text(audio)
                      txt,fconf = Check_Transcript(transcripts,transcripts_confidence,words,words_confidence,Err_msg)

                      if len(txt) > 0:
                          if fconf:
                              cmd = Commandes(txt)
                              if cmd:
                                  return(Go_Back_To_Sleep())
                              else:
                                  fallbackGpt(txt)

                          else:
                              return(Bad_Confidence(txt))
                      else:
                              return(Go_Back_To_Sleep())
               else:
                      return(Go_Back_To_Sleep())

            elif fname == "Repeat":

               Start_Thread_Record()
               if Wait_for("audio"):
                   audio = audio_datas.get()
                   transcripts,transcripts_confidence,words,words_confidence,Err_msg = Speech_To_Text(audio)
                   txt,fconf =Check_Transcript(transcripts,transcripts_confidence,words,words_confidence,Err_msg)
                   if len(txt) > 0:
                       Repeat(txt)
                   else:
                        return(Go_Back_To_Sleep())
               else:
                   return(Go_Back_To_Sleep())
            else:
                PRINT("\nTOUCHDOWN\n")
                return(Go_Back_To_Sleep())




def GetConf():
   global DEBUG
   global XCB_ERROR_FIX
   global SAVED_ANSWER

   options = ["DEBUG","XCB_ERROR_FIX","SAVED_ANSWER"]
   folder = False
   conf = False

   if os.path.exists(script_path+"conf.trinity"):
           with open(script_path+"conf.trinity","r") as f:
              f = f.readlines()

           for l in f:
              l = l.strip()
              option = next((r for r in options if r in l),"")
              if option == "SAVED_ANSWER":
                  if '=' in l:


                      folder = l.split('=')[1]

                      while folder.startswith(" "):
                         folder = folder[1:]
                      while folder.endswith(" "):
                         folder = folder[:-1]

                      folder = folder.replace("'","").replace('"',"")

                      if folder == "default":
                         SAVED_ANSWER = script_path+"/local_sounds/saved_answer/"
                      else:
                          SAVED_ANSWER = folder
              elif option in options:
                      conf = l.split('=')[1]

                      while conf.startswith(" "):
                         conf = conf[1:]
                      while conf.endswith(" "):
                         conf = conf[:-1]

                      conf = conf.replace("'","").replace('"',"")

                      conf = conf.lower()
                      if conf == "true":
                           if option == "DEBUG":
                                DEBUG = True
                           elif option == "XCB_ERROR_FIX":
                                XCB_ERROR_FIX = True
                      else:
                          if option == "DEBUG":
                                DEBUG = False
                          elif option == "XCB_ERROR_FIX":
                               XCB_ERROR_FIX = False

   else:
           with open(script_path+"conf.trinity","w") as f:
                data = """Saved_Answers = default
DEBUG = False
XCB_ERROR_FIX = False"""
                f.write(data)

           DEBUG = False
           SAVED_ANSWER = script_path+"/local_sounds/saved_answer/"
           XCB_ERROR_FIX = False

def Xcb_Fix(mode):
   global DISPLAY

   if mode == "unset":
         DISPLAY = os.getenv('DISPLAY')
         try:
             del os.environ['DISPLAY']
         except:
              DISPLAY = ""
   if mode == "set":
        if len("DISPLAY") > 0:
            try:
                os.environ['DISPLAY'] = DISPLAY
            except:
                pass

if __name__ == "__main__":

    script_path = os.path.dirname(__file__)
    if script_path.endswith("."):
       script_path = script_path[:-1]



    DISPLAY = ""
#    DEBUG = False
#    XCB_ERROR_FIX = False
#    SAVED_ANSWER = script_path +"/local_sounds/saved_answer/"

    GetConf()

    print("DEBUG:",DEBUG)
    print("XCB_ERROR_FIX:",XCB_ERROR_FIX)
    print("SAVED_ANSWER:",SAVED_ANSWER)

    FRAME_DURATION = 480
    FRAME_RATE = 16000

    Current_Category = []
    Blacklisted = []

    PICO_KEY = LoadKeys()
    record_on = Queue()
    chunks = Queue()
    last_sentence = Queue()
    No_Input = Queue()
    score_sentiment = Queue()
    audio_datas = Queue()
    wake_me_up = Queue()
    cancel_operation = Queue()
    awake = Queue()
    wake_me_up.put(True)
    Current_Provider_Id = 0
    Repeat_Last_One=""
    

    if XCB_ERROR_FIX:
         Xcb_Fix("unset")

    signal.signal(signal.SIGINT, signal_handler)
#####
    Trinity()
#####
