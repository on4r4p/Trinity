#!/usr/bin/python3

import g4f,pyaudio,pvporcupine,os,time,sys,struct,random,webrtcvad,subprocess,re,csv,string,wikipedia,googlesearch,requests,signal,inspect,sox
import google.cloud.texttospeech as tts

from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

from difflib import SequenceMatcher

from datetime import datetime

from bs4 import BeautifulSoup

from shutil import move

from github import Github

from google.cloud import speech_v1p1beta1 as speech
from google.cloud import language_v1
from queue import Queue
from threading import Thread
from ctypes import *
from contextlib import contextmanager

from itertools import product

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
#   print("\n-Trinity:Dans la fonction PRINT().")
#   print("\n-Trinity:other:",other)
   try:
       if DEBUG:
            if other:
                tmp_txt = str(txt) + " " +str(other)
                print(tmp_txt)
            else:
                print(tmp_txt)
   except Exception as e:
         print("\n-Trinity:Erreur dans la fonction PRINT:",str(e))
         pass

def PicoLoadKeys():
   PRINT("\n-Trinity:Dans fonction PicoLoadKeys")
   if os.path.exists(SCRIPT_PATH+"/keys/pico.key"):
       with open(SCRIPT_PATH+"/keys/pico.key","r") as k:
           PICO_KEY = k.read()
           PICO_KEY = PICO_KEY.strip()
       if not PICO_KEY.endswith("=="):
            print("\n-Trinity:-Wrong Pico Api key.")
            print(PICO_KEY)
            sys.exit()
       else:
            return(PICO_KEY)
   else:
       print("\n-Trinity:-%s/keys/pico.key doesn't exist."%SCRIPT_PATH)
       sys.exit()

def GoogleLoadKeys():
   PRINT("\n-Trinity:Dans fonction GoogleLoadKeys")

   GOOGLE_KEY = ""
   GOOGLE_ENGINE = ""

   if os.path.exists(SCRIPT_PATH+"/keys/google_search.key"):
       with open(SCRIPT_PATH+"/keys/google_search.key","r") as k:
           GOOGLE_KEY = k.read()
           GOOGLE_KEY = GOOGLE_KEY.strip()
       if len(GOOGLE_KEY) != 39:
            print("\n-Trinity:-Wrong Google Api key (len).")
            print(GOOGLE_KEY)
            GOOGLE_KEY = ""
   else:
       print("\n-Trinity:-%s/keys/google_search_engine.key doesn't exist."%SCRIPT_PATH)

   if os.path.exists(SCRIPT_PATH+"/keys/google_search_engine.id"):
       with open(SCRIPT_PATH+"/keys/google_search_engine.id","r") as k:
           GOOGLE_ENGINE = k.read()
           GOOGLE_ENGINE = GOOGLE_ENGINE.strip()
       if len(GOOGLE_ENGINE) != 17:
            print("\n-Trinity:-Wrong Google engine id (len).")
            print(GOOGLE_ENGINE)
            GOOGLE_ENGINE = ""
   else:
       print("\n-Trinity:-%s/keys/google_search_engine.id doesn't exist."%SCRIPT_PATH)

   return(GOOGLE_KEY,GOOGLE_ENGINE)


def parse_response(data):

    PRINT("\n-Trinity:Original Data before parse:\n",data)

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

    if "Bonjour, je suis Copilot" in data:
        to_find = "Bonjour, je suis Copilot"
        index = data.find(to_find)
        after_to_find = index + len(to_find)
        next_point = None
        for n,c in enumerate(data[after_to_find:]):
            if c == ".":
                 next_point = n + 1
                 break
        if next_point:
           data = data[index+len(to_find)+next_point:]
        else:
           data = data[index+len(to_find):]

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


def To_Gpt(input):


   if GPT4FREE_SERVERS_STATUS:
       FreeGpt(input)

   else:
       #TODO
       print("\n-Trinity:Error only gpt4free providers are working atm.")
       sys.exit()

def Check_Free_Servers():
     PRINT("\n-Trinity:Dans la fonction Check_Free_Servers")

     active_with_auth = []
     active_no_auth = []
     unknown_with_auth = []
     unknown_no_auth = []

     providers_to_return = []


     try:

         response = requests.get("https://raw.githubusercontent.com/xtekky/gpt4free/main/README.md")
         markdown = response.text.splitlines()
         print("\n\n")
         for line in markdown:
              if "g4f.Provider." in line:
                    if "https://img.shields.io/badge/Active-brightgreen" in line:
                        provider =  "g4f.Provider." + line.split("g4f.Provider.")[1].split("`")[0]
                        if "❌" in line:
                            active_no_auth.append(provider)
                        else:
                            active_with_auth.append(provider)
                    if "https://img.shields.io/badge/Unknown-grey" in line:
                        provider =  "g4f.Provider." + line.split("g4f.Provider.")[1].split("`")[0]
                        if "❌" in line:
                            unknown_no_auth.append(provider)
                        else:   
                            unknown_with_auth.append(provider)

     except Exception as e:
         print("\n-Trinity Error:",str(e))

     if active_with_auth:
           PRINT("\n-Trinity:Free servers active_with_auth:\n")
           for aa in active_with_auth:
                PRINT(aa)
     if active_no_auth:
           PRINT("\n-Trinity:Free servers active_no_auth:\n")
           for an in active_no_auth:
                PRINT(an)

     if unknown_with_auth:
           PRINT("\n-Trinity:Free servers unknown_with_auth:\n")
           for ua in unknown_with_auth:
                PRINT(ua)
     if unknown_no_auth:
           PRINT("\n-Trinity:Free servers unknown_no_auth:\n")
           for un in unknown_no_auth:
                PRINT(un)

     if GPT4FREE_SERVERS_STATUS == "All":
         if GPT4FREE_SERVERS_AUTH == True:
              providers_to_return = active_with_auth + unknown_with_auth
         elif GPT4FREE_SERVERS_AUTH == False:
              providers_to_return = active_no_auth + unknown_no_auth
         elif GPT4FREE_SERVERS_AUTH == "All":
              providers_to_return = active_with_auth + active_no_auth + unknown_with_auth + unknown_no_auth

     elif GPT4FREE_SERVERS_STATUS == "Active":
         if GPT4FREE_SERVERS_AUTH == True:
              providers_to_return = active_with_auth 
         elif GPT4FREE_SERVERS_AUTH == False:
              providers_to_return = active_no_auth
         elif GPT4FREE_SERVERS_AUTH == "All":
              providers_to_return = active_with_auth + active_no_auth

     elif GPT4FREE_SERVERS_STATUS == "Unknown":
         if GPT4FREE_SERVERS_AUTH == True:
              providers_to_return = unknown_with_auth 
         elif GPT4FREE_SERVERS_AUTH == False:
              providers_to_return = unknown_no_auth
         elif GPT4FREE_SERVERS_AUTH == "All":
              providers_to_return = unknown_with_auth + unknown_no_auth

     if len(providers_to_return) == 0:
         PRINT("\n-Trinity:Error retrieving providers list.Using Saved lists from 05/03/2024 :\n")
         providers_to_return = [
               "g4f.Provider.Aura",
               "g4f.Provider.Bing",
               "g4f.Provider.DeepInfra",
               "g4f.Provider.Gemini",
               "g4f.Provider.GeminiPro",
               "g4f.Provider.GeminiProChat",
               "g4f.Provider.Koala",
               "g4f.Provider.Liaobots",
               "g4f.Provider.Llama2",
               "g4f.Provider.PerplexityLabs",
               "g4f.Provider.Phind",
               "g4f.Provider.Pi",
               "g4f.Provider.You"]

     return(providers_to_return)



def FreeGpt(input):
     PRINT("\n-Trinity:Dans la fonction FreeGpt")


     global Current_Provider_Id
     global Blacklisted

     def save_blacklist(server,err):
        err_file = str(SAVED_ANSWER+"/saved_error/g4f_providers.errors").replace("//","/")
        try:
            with open(err_file, "a+", newline="") as f:
                now = "===== " +str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")) +" =====\n"
                serverr = "g4f provider:%s error:%s\n"%(str(server),err)
                f.write(now)
                f.write(serverr)
        except Exception as e:
            print("\n-Trinity:Error:save_blacklist():%s"%str(e))
        
     Answer_Known = Check_History(input)

     if Answer_Known or not No_Input.empty():
        return(Trinity())

     last_sentence.put(input)

#    os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/server/gpt3.wav")
     rnd = str(random.randint(1,10))
     wait = SCRIPT_PATH+"/local_sounds/wait/"+rnd+".wav"
     os.system("aplay -q %s"%wait)

     Err_msg = ""
     Err_cnt = 0
     response = ""



     p_cnt = 0
     while p_cnt <= (len(Providers_To_Use)- len(Blacklisted)) :
        if Current_Provider_Id > (len(Providers_To_Use)- len(Blacklisted)):
             Current_Provider_Id = 0
        if Providers_To_Use[Current_Provider_Id] in Blacklisted:
              PRINT("\n-Trinity:skipping :",Providers_To_Use[Current_Provider_Id])
              Current_Provider_Id += 1
              continue

        PRINT("\n-Trinity:Asking :",Providers_To_Use[Current_Provider_Id])
        try:
             response = g4f.ChatCompletion.create(
             model=g4f.models.default, 
             provider = eval(Providers_To_Use[Current_Provider_Id]),
             timeout=10,
             messages=[{"role": "user", "content": str(input)}])

             if len(response) < 1:
                 PRINT("\n-Trinity:len(response) < 1:No answer from :",Providers_To_Use[Current_Provider_Id])
                 provider_name = Providers_To_Use[Current_Provider_Id].replace("g4f.Provider.","")
                 wait = SCRIPT_PATH+"/local_sounds/providers/"+str(provider_name)+".wav"
                 os.system("aplay -q %s"%wait)
                 Current_Provider_Id += 1
             else:
                  break

        except Exception as e:
                 print("\n-Trinity:Error:",str(e))
                 print("\n-Trinity:No answer from :",Providers_To_Use[Current_Provider_Id])
                 provider_name = Providers_To_Use[Current_Provider_Id].replace("g4f.Provider.","")
                 wait = SCRIPT_PATH+"/local_sounds/providers/"+str(provider_name)+".wav"
                 os.system("aplay -q %s"%wait)
                 save_blacklist(Providers_To_Use[Current_Provider_Id],str(e))
                 Blacklisted.append(Providers_To_Use[Current_Provider_Id])
                 Current_Provider_Id += 1
        p_cnt += 1
        
     if len(response) < 1:
                os.system("aplay -q "+SCRIPT_PATH+"local_sounds/errors/err_no_respons_allprovider.wav")
                return()
     else:
                PRINT("\n-Trinity:Le server %s à répondu."%(Providers_To_Use[Current_Provider_Id]))
                Current_Provider_Id += 1
                return(Text_To_Speech(str(response),stayawake=False,savehistory=True))


def wake_up():
    PRINT("\n-Trinity:Dans la fonction Wakeup")

#    word_key = SCRIPT_PATH+"/models/Trinity_en_linux_v2_2_0.ppn"
    word_key = SCRIPT_PATH+"/models/trinity_fr_raspberry-pi_v3_0_0.ppn"
    word_key2 = SCRIPT_PATH+"/models/interpreteur_fr_raspberry-pi_v3_0_0.ppn"
    word_key3 = SCRIPT_PATH+"/models/repete_fr_raspberry-pi_v3_0_0.ppn"
    word_key4 = SCRIPT_PATH+"/models/merci_fr_raspberry-pi_v3_0_0.ppn"
    pvfr = SCRIPT_PATH+"/models/porcupine_params_fr.pv"
    porcupine = None
    keyword_index = None

    try:
        porcupine = pvporcupine.create(access_key=PICO_KEY, model_path = pvfr,keyword_paths=[word_key,word_key2,word_key3,word_key4],sensitivities=[1,1,1,1] )
        with ignoreStderr():
            pa = pyaudio.PyAudio()
        audio_stream = pa.open(
                        rate=porcupine.sample_rate,
                        channels=1,
                        format=pyaudio.paInt16,
                        input=True,
                        frames_per_buffer=porcupine.frame_length)

        print("\n-Trinity: En attente ...")

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index == 0:
                PRINT("\n-Trinity:keyword_index:",keyword_index)
                
                rnd = str(random.randint(1,15))
                wake_sound = SCRIPT_PATH+"/local_sounds/wakesounds/"+rnd+".wav"
                os.system("aplay -q %s"%wake_sound)
                break
            if keyword_index == 1:
                PRINT("\n-Trinity:keyword_index:",keyword_index)
                break
            if keyword_index == 2:
                PRINT("\n-Trinity:keyword_index:",keyword_index)
                break
            if keyword_index == 3:
                PRINT("\n-Trinity:keyword_index:",keyword_index)
                rnd = str(random.randint(1,15))
                thk_sound = SCRIPT_PATH+"/local_sounds/merci/"+rnd+".wav"
                os.system("aplay -q %s"%thk_sound)


    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if keyword_index == None:
             print("\n-Trinity:Error keyword_index = None")
             sys.exit()
        if keyword_index == 0:
            return(Trinity("Speech_To_Text"))
        if keyword_index == 1:
            return(Fallback_Prompt())
        if keyword_index == 2:
            os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/repeat/isaid.wav")
            os.system("aplay -q %s"%SCRIPT_PATH+"tmp/current_answer.wav")
            return(wake_up())

def Record_Query():
    PRINT("\n-Trinity:Dans la fonction Record_Query")


    with ignoreStderr():
        p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=FRAME_RATE,
                    input=True,
                    frames_per_buffer=FRAME_DURATION)

    wake_sound = SCRIPT_PATH+"/local_sounds/wakesounds/record.wav"
    os.system("aplay -q %s"%wake_sound)


    while not record_on.empty():
        chunks.put(stream.read(FRAME_DURATION))

    PRINT("\n-Trinity:Enregistrement terminé.")
    wake_sound = SCRIPT_PATH+"/local_sounds/wakesounds/record_end.wav"
    os.system("aplay -q %s"%wake_sound)

    stream.stop_stream()
    stream.close()
    p.terminate()
    return()


def Check_Silence():
    

    PRINT("\n-Trinity:Dans la fonction Check_Silence")
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
                    PRINT("\n-Trinity:Silence détecté-\n")
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
                      no_input_sound = SCRIPT_PATH+"/local_sounds/noinput/"+rnd+".wav"
                      os.system("aplay -q  %s"%no_input_sound)
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
                  os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/errors/err_too_long.wav")
                  break










def Write_csv(function_name, trigger_word,filename):

    #CMDFILE,
    with open(filename, "a+", newline="") as csvfile:
        fieldnames = ["function", "trigger"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({"function": function_name, "trigger": trigger_word})

    return(Load_Csv())


def Special_Syntax(txt,filepath=None,line=None):

    def parse_cmd(cmd_txt):

#         def unnest(lst, append=False):
#             chunk = []
#             for x in lst:
#                 if isinstance(x, list):
#                     if chunk:
#                         yield chunk
#                     yield from unnest(x, True)
#                     chunk = []
#                 else:
#                     if append:
#                         chunk.append(x)
#                     else:
#                         yield [x]
#             if chunk:
#                 yield chunk




         def to_list(str_lst):

             def check_split(index):
                 coma = False
                 obracket = False
                 cbracket = False
                 quote = False

                 for c in str_lst[index:]:
         #            print("c:",c)
                     if c == " ":pass
                     elif c == ",":coma = True
                     elif c == "[":obracket = True
                     elif c == "]":cbracket = True
                     elif c in ["'",'"']:quote = True
                     else:
                         if coma and obracket:
         #                   print("coma and obracket")
                            return True
                         elif coma and quote:
         #                   print("coma and quote")
                            return True
                         elif cbracket:
         #                   print("cbracket")
                            return True
                         else:
         #                   print("\npas glop\n")
                            return False
         #        print("Rien")
                 return True

             bucket = ""
             to_split = False
         #    listing = []
             for e,char in enumerate(str_lst):
         #        print("bucket:",bucket)
                 if to_split:
                     if char in ["'",'"']:
    #                     print("bucket:",bucket)
                         if check_split(e+1):
                             yield (None, bucket)
                             #listing.append((None,bucket))
                             bucket = ""
                             to_split = False
                         else:
                             bucket += char
                     else:
                         bucket += char
                 else:
                     if char == "[":
         #                 listing.append(("[", None))
                         yield ("[", None)
                     elif char == "]":
         #                 listing.append(("]", None))
                         yield ("]", None)
                     elif char in ["'",'"']:
                         to_split = True
                     else:
                         pass
         #    print("listing\:",listing)
         #    return listing

         def make_list(listing):
             lst = []
             for id,data in listing:
                 if id == "[":
                     lst.append(make_list(listing))
                 elif id == "]":
                     return lst
                 else:
                     lst.append(data)
             return lst[0]



         def add_braks(cmd_txt,lbraks,rbraks):
             def check_around(idx):
                    while True:
                        if idx <= 0:return False
                        if cmd_txt[idx] == " ":pass
                        elif cmd_txt[idx] == "[":return False
                        elif cmd_txt[idx] == "]":return True
                        else:return False
                        idx -= 1
                    #return True

             outside_lvl = []
             bad_pos = []
             skip = 0
             start = None
             end = None
             for e,char in enumerate(cmd_txt):

                 if char == "[" and start is None:
                       start = e
                 elif char == "[":
                      skip += 1
                 elif char == "]":
                      if skip > 0:
                         skip -= 1
                      else:
                         end = e +1
                         outside_lvl.append((start,end))
                         start = None
                         end = None

             for st,ed in outside_lvl:
                 for i in range(st,ed):
                      bad_pos.append(i)

             braks_txt = ""
             opened = False
             badbool = False
             for e,char in enumerate(cmd_txt):
                 if e not in bad_pos:
                     badbool = False
                     if opened:
                         braks_txt += str(char)
                     else:
                         if check_around(e-1):
                             #print("cmd_txt[%s-1]:%s char:,[%s"%(e,cmd_txt[e-1],char))
                             braks_txt += ",["+str(char)
                         else:
                             #print("cmd_txt[%s-1]:%s char:[%s"%(e,cmd_txt[e-1],char))
                             braks_txt += "["+str(char)
                         opened = True
                          
                 else:
                     badbool = True
                     if opened:
                         braks_txt += "],"+str(char)
                         opened = False
                     else:
                         braks_txt += str(char)

             if opened:
                braks_txt += "]"

             return("["+braks_txt+"]")

         def add_quotes(fullbraks):

             def check_around(idx,coma=False):
                 if coma:
                     pos = idx -1
                     before = False
                     after = False
                     while True:
    #                     print("char before:",fullbraks[pos])
                         if pos == 0:break
                         if fullbraks[pos] == " ":pass
                         elif fullbraks[pos] == "[":
                              before = True
                              break
                         elif fullbraks[pos] == "]":
                              before = False
                              break
                         else:
                              before = True
                              break
                         pos -= 1

                     for c in fullbraks[idx+1:]:
    #                     print("char after:",c)
                         if c == " ":pass
                         if c == "[":
                             after = False
                             break
                         elif c == "]":
                             after = True
                             break
                         else:
                             after = True
                             break

                     if before and not after:
    #                         print("before and not after")
                             return('",')
                     elif after and not before:
    #                         print("after and not before")
                             return(',"')
                     elif not before and not after:
    #                         print("not before and not after")
                             return(",")
                     else:
    #                         print(" before and after")
                             return('","')
                               
                 else:
                    for c in fullbraks[idx:]:
                        if c == "[":return False
                        elif c == "]":return False
                        else:return True
                    return False

             fullquotes = ""
             for e,char in enumerate(fullbraks):
    #             print("char:",char)
                 if char == "[":
                      if check_around(e+1):
                        fullquotes += '["'
                      else:
                        fullquotes += "["
                 elif char == "]":
                      if check_around(e-1):
                        fullquotes += '"]'
                      else:
                        fullquotes += "]"
                 elif char == ",":

                      fullquotes += check_around(e,True)
                 else:
                      fullquotes += char
             return fullquotes

         def valid_lists(cmd_txt):
             lbraks = [pos for pos, char in enumerate(cmd_txt) if char == '[']
             rbraks = [pos for pos, char in enumerate(cmd_txt) if char == ']']
             lbrak_nbr = len(lbraks)
             rbrak_nbr = len(rbraks)

             lcurlys = [pos for pos, char in enumerate(cmd_txt) if char == '{']
             rcurlys = [pos for pos, char in enumerate(cmd_txt) if char == '}']
             lcurly_nbr = len(lcurlys)
             rcurly_nbr = len(rcurlys)


             if lbrak_nbr == 0 and rbrak_nbr == 0 and lcurly_nbr > 0 and rcurly_nbr > 0:
                 print("\n-Fichier:%s ligne:%s Les symboles '{' et '}' s'utilisent conjointement avec les symboles '[' et ']' mais pas seuls."%(filepath,line))
                 return("~PARSE~ERR~",None,None)
             elif lbrak_nbr == 0 and rbrak_nbr == 0 :
                 return(False,None,None)
             if lbrak_nbr != rbrak_nbr:
                if lbrak_nbr >rbrak_nbr:
                    print("\n-Fichier:%s ligne:%s Il ya %s '[' et %s ']' seulement."%(filepath,line,lbrak_nbr,rbrak_nbr))
                else:
                    print("\n-Fichier:%s ligne:%s Il ya seulement %s '[' et %s ']'."%(filepath,line,lbrak_nbr,rbrak_nbr))
                return("~PARSE~ERR~",None,None)

             if lcurly_nbr != rcurly_nbr:
                if lcurly_nbr >rcurly_nbr:
                    print("\n-Fichier:%s ligne:%s Il ya %s '{' et %s '}' seulement."%(filepath,line,lcurly_nbr,rcurly_nbr))
                else:
                    print("\n-Fichier:%s ligne:%s Il ya seulement %s '{' et %s '}'."%(filepath,line,lcurly_nbr,rcurly_nbr))
                return("~PARSE~ERR~",None,None)

             for o,c in zip(lbraks,rbraks):
    #             print("o:%s c:%s"%(o,c))
                 if o > c:
                       print("\n-Fichier:%s ligne:%s Mauvaise syntax."%(filepath,line))
                       return("~PARSE~ERR~",None,None)
             for o,c in zip(lcurlys,rcurlys):
    #             print("o:%s c:%s"%(o,c))
                 if o > c:
                       print("\n-Fichier:%s ligne:%s Mauvaise syntax."%(filepath,line))
                       return("~PARSE~ERR~",None,None)

             return(True,lbraks,rbraks)

         cmd_txt = cmd_txt.replace("/",",")

         list_inside,lbraks,rbraks = valid_lists(cmd_txt)
         if list_inside:
             if list_inside == "~PARSE~ERR~":
                return(list_inside,None)
             else:
                  try:
                       curlys = None
                       fullbraks = add_braks(cmd_txt,lbraks,rbraks)
                       if "{" in fullbraks and "}" in fullbraks:
                           fullbraks,curlys = extract_curly(fullbraks)
                           fullquotes = add_quotes(fullbraks)
         #                  fullquotes = putback_curly(fullquotes,curlys)
                       else:
                           fullquotes = add_quotes(fullbraks)

#                       PRINT("\nfullbraks:%s\n"%fullbraks)
#                       PRINT("\nfullquotes:%s\n"%fullquotes)


                       protolist = to_list(fullquotes)
                       actualist = make_list(protolist)

                       return(actualist,curlys)
                  except Exception as e:
                       print("-Trinity Error:",str(e))
                       return("~PARSE~ERR~",None)
         else:
             return(False,None) 

#    def putback_curly(str_to_check,dict):
#        for k,i in dict.items():
#            if k in str_to_check:
#                str_to_check = str_to_check.replace(k,i)
#        return(str_to_check)

    def extract_curly(str_to_check):

#        PRINT("\nstr_to_check:\n",str_to_check)
        def rnd_str(str_to_check,curly_dict):
             while True:
                  characters = string.ascii_letters + string.digits
                  rnd = ''.join(random.choice(characters) for _ in range(5))
                  if not rnd in curly_dict and not rnd in str_to_check:
                     return rnd

        curly_dict = {}
        while True:
            start = False
            end = False

            for n,c in enumerate(str_to_check):
                if c == "{" and not start and not end:
                     start = n
                if c == "}" and start and not end:
                     end = n+1
                if start and end:
                    break

            curly = str_to_check[start:end]
            marker = rnd_str(str_to_check,curly_dict)

            if "," in curly:
                curly = curly.replace("{","").replace("}","").split(",")
            else:
                curly = curly.replace("{","").replace("}","")

            curly_dict[marker] = curly
            str_to_check = str_to_check[:start] + str(marker) + str_to_check[end:]

            if "{" not in str_to_check and "}" not in str_to_check:
                break

    #    print("\nwithout curly:",str_to_check)
    #    print("\ncurly_dict:")

    #    for i,j in curly_dict.items():
    #        print("%s type= %s:%s"%(i,type(i),j))
        return(str_to_check,curly_dict)

#    def Mark_sublvl(lists_to_check,pos_lst=0,lvl=0,markers_dict={}):#TODO
    #    print("\nlists_to_check:",lists_to_check)
#        for pos_itm,lists in enumerate(lists_to_check):
            #print("pos_itm:%s lists:%s"%(pos_itm,lists))
#            if isinstance(lists,list):
#                key = "lvl:%s,posl:%s,posi%s"%(lvl,pos_lst,pos_itm)
#                if not key in markers_dict:
#                    markers_dict[key] = lists
#                    markers_dict = final_parse(lists,pos_lst,lvl+1,markers_dict = markers_dict)
    #        else:
    #             print("lists not a list:",lists)
        return markers_dict

    def Unfold_cmd(cmd_lst,curlys):

         unfolded = []

         for lst in cmd_lst:
             tmp_lst = []

             for item in lst:
                     skip = False

                     for k,i in curlys.items():
                         if k in item:

                            skip = True
                            if isinstance(i,list):
                                for j in i:
                                    tmp_lst.append(item.replace(k,j))
                            else:
                                tmp_lst.append(item.replace(k,i))

                            break
                     if not skip:
                         tmp_lst.append(item)

             unfolded.append(tmp_lst)

         for lst in unfolded:
             for item in lst:
                 for k in curlys:
                     if k in item:
                        return(Unfold_cmd(unfolded,curlys))

         return(unfolded)

    def join_and_replace(tojoin):
          joined = "".join(tojoin)
          if "  " in joined:
              replaced = joined
              while True:
                 replaced = replaced.replace("  "," ")
                 if not "  " in replaced:
                    joined_and_replaced = replaced
                    break
#                 else:
#                      print("replaced:",replaced)
#                      input("")
          else:
              joined_and_replaced = joined

          return(joined_and_replaced)


    parsed_cmd,curlys = parse_cmd(txt)

    if parsed_cmd:
         final_list = []
         if parsed_cmd == "~PARSE~ERR~":
             PRINT("\n-Trinity:Special_Syntax():~PARSE~ERR~:txt:\n%s\n"%txt)
             return(None)
#         PRINT("\ntxt:\n%s\n"%txt)
#         PRINT("\nparsed_cmd:\n%s\n"%parsed_cmd)
         if curlys:
#             PRINT("\n-Trinity:curlys is full:")
#             for i,j in curlys.items():
#                 PRINT("%s:%s"%(i,j))
             unfolded = Unfold_cmd(parsed_cmd,curlys)
             prod = product(*unfolded)
             final_list = [join_and_replace(i) for i in prod]
             PRINT("\n-Trinity:Output Special Syntax for:\n%s\n\n%s"%(txt,final_list))
             return(final_list)
         else:
             prod = product(*parsed_cmd)
             final_list = [join_and_replace(i) for i in prod]
             PRINT("\n-Trinity:Output Special Syntax for:\n%s\n\n%s"%(txt,final_list))
             return(final_list)
    else:
#        PRINT("no advanced syntax:\n",txt)
        return(txt)

    ##TODO sublvl etc ..
    #for n,p in enumerate(parsed_cmd):
    #   print("sending %s %s"%(n,p))
    #   markers = final_parse(p,pos_lst=n)


    #marker = final_parse(parsed_cmd)
    #print("\n\nfinal marker:")
    #for i,j in markers.items():print("%s:%s"%(i,j))

    #print("\nparsed_cmd:\n")
    #for n,i in enumerate(parsed_cmd):
    #    print("%s =  %s"%(n,i))
    #to_prod,markers = is_inner_lst(parsed_cmd)
    #sys.exit()

    #if markers:
    #    print("\nmarkers is full\n")
    #    prod = product(*parsed_cmd)
    #    for i in prod:
    #       print(i)
    #else:
    #    print("\n\nno markers final:\n")       
    #    prod = product(*parsed_cmd) 
    #    for i in prod:
    #       print(i)






def Load_Csv():

    global History_List
    global trinity_name
    global trinity_mean
    global trinity_creator
    global trinity_script
    global trinity_help
    global prompt_request
    global trinity_source_request
    global rnd_request
    global repeat_request
    global show_history_request
    global search_history_request
    global read_link_request
    global play_wav_request
    global web_request
    global wait_words
    global action_words
    global add_words
    global action_functions
    global alt_trigger
    global verb_lst
    global synonyms_list
    global fnc_verb

    History_List = []
    trinity_name = []
    trinity_mean = []
    trinity_creator = []
    trinity_script = []
    trinity_help = []
    prompt_request = []
    trinity_source_request = []
    rnd_request = []
    repeat_request = []
    show_history_request = []
    search_history_request = []
    read_link_request = []
    play_wav_request = []
    web_request = []
    wait_words = []
    add_words = []
    action_words = []
    action_functions = []
    alt_trigger = []
    verb_lst = []
    synonyms_list = []
    fnc_verb = {}


    PRINT("\n-Trinity:Dans la fonction Load_Csv .")



    if os.path.exists(SCRIPT_PATH+"/history"):
       hist_folder = SCRIPT_PATH+"/history"
       hist_files = [f for f in os.listdir(hist_folder)]
       for file in hist_files:
           filepath = os.path.join(hist_folder,file)
           try:
                with open(filepath, newline="") as csvfile:
                       reader = csv.DictReader(csvfile)
                       for row in reader:
                           try:
                               hist_file = row["hist_file"]
                               hist_cats = row["hist_cats"]
                               hist_txt = row["hist_txt"]
                               hist_answer = row["hist_answer"]
                               hist_epok = row["hist_epok"]
                               hist_tstamp = row["hist_tstamp"]
                               hist_wav = row["hist_wav"]
                               History_List.append( (hist_file,hist_cats,hist_txt,hist_answer,hist_epok,hist_tstamp,hist_wav)  )
                           except Exception as e:
                               print("\n-Trinity:Error:loadcsv:file:%s %s"%(filepath,str(e)))
                               input("stopeu")
     #                      print("\nhist_file:\n",hist_file)
     #                      print("hist_cats:\n",hist_cats)
     #                      print("hist_txt:\n",hist_txt)
     #                      print("hist_answer:\n",hist_answer)
     #                      print("hist_epok:\n",hist_epok)
     #                      print("hist_tstamp:\n",hist_tstamp)
     #                      print("hist_wav:\n",hist_wav)
           except Exception as e:
                 print("\n-Trinity:Error:loadcsv:file:%s %s"%(filepath,str(e)))

                 input("stop")


    if os.path.exists(SYNFILE):
         with open(SYNFILE, newline="") as f:
              data = f.readlines()
              
              for line in data:
                  tmplst = []
                  line = line.strip().split(",")
                  for l in line:
                      if l != "":
                          tmplst.append(l)
                  synonyms_list.append(tmplst)


    else:

          print("\n-Trinity:Error:%s not found."%SYNFILE)
          sys.exit()

    if os.path.exists(TRIFILE):
         with open(TRIFILE, newline="") as csvfile:
             reader = csv.DictReader(csvfile)
             for row in reader:
                 if "trigger" in row:
                      trigger= row["trigger"]
                 else:
                     continue
                 if not trigger in alt_trigger:
                      alt_trigger.append(trigger)

    else:

          print("\n-Trinity:Error:%s not found."%TRIFILE)
          sys.exit()


    if os.path.exists(CMDFILE):
         with open(CMDFILE, newline="") as csvfile:
             reader = csv.DictReader(csvfile)
             for line,row in enumerate(reader):
                 line = line + 2
                 if "function" in row:
                      function = row["function"]
                      if "trigger" in row:
                           trigger = row["trigger"]
                      else:
                          continue
                      if function == "trinity_name":
                          check_trigger = Special_Syntax(trigger,CMDFILE,line)
                          if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_name.append(t)
                               else:
                                   trinity_name.append(trigger)
                      elif function == "trinity_mean":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_mean.append(t)
                               else:
                                   trinity_mean.append(trigger)
                      elif function == "trinity_creator":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_creator.append(t)
                               else:
                                   trinity_creator.append(trigger)
                      elif function == "trinity_script":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_script.append(t)
                               else:
                                   trinity_script.append(trigger)
                      elif function == "trinity_help":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_help.append(t)
                               else:
                                   trinity_help.append(trigger)
                      elif function == "prompt_request":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       prompt_request.append(t)
                               else:
                                   prompt_request.append(trigger)
                      elif function == "trinity_source_request":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_source_request.append(t)
                               else:
                                   trinity_source_request.append(trigger)
                      elif function == "rnd_request":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       rnd_request.append(t)
                               else:
                                   rnd_request.append(trigger)
                      elif function == "repeat_request":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       repeat_request.append(t)
                               else:
                                   repeat_request.append(trigger)
                      elif function == "show_history_request":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       show_history_request.append(t)
                               else:
                                   show_history_request.append(trigger)

                      elif function == "search_history_request":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       search_history_request.append(t)
                               else:
                                   search_history_request.append(trigger)
                      elif function == "read_link_request":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       read_link_request.append(t)
                               else:
                                   read_link_request.append(trigger)
                      elif function == "play_wav_request":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       play_wav_request.append(t)
                               else:
                                   play_wav_request.append(trigger)
                      elif function == "web_request":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       web_request.append(t)
                               else:
                                   web_request.append(trigger)
                      elif function == "wait_words":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       wait_words.append(t)
                               else:
                                   wait_words.append(trigger)
                      elif function == "add_words":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       add_words.append(t)
                               else:
                                   add_words.append(trigger)
    else:

          print("\n-Trinity:Error:%s not found."%CMDFILE)
          sys.exit()



    if os.path.exists(ACTFILE) and os.path.exists(PREFILE):
         with open(ACTFILE, newline="") as csvfile:
             reader = csv.DictReader(csvfile)

             for row in reader:

                 if "verb" in row:
                      verb = row["verb"]
                 else:
                     continue
                 if "indicatif1" in row:
                      ind1 = row["indicatif1"]
                 else:
                     continue
                 if "indicatif2" in row:
                      ind2 = row["indicatif2"]
                 else:
                     continue
                 if "conditionnel1" in row:
                      cond1 = row["conditionnel1"]
                 else:
                     continue
                 if "conditionnel2" in row:
                      cond2 = row["conditionnel2"]
                 else:
                     continue
                 if "subjonctif1" in row:
                      sub1 = row["subjonctif1"]
                 else:
                     continue
                 if "subjonctif2" in row:
                      sub2 = row["subjonctif2"]
                 else:
                     continue
                 if "participe" in row:
                      participe = row["participe"]
                 else:
                     continue
                 if "suffix1" in row:
                      suffix1 = row["suffix1"]
                 else:
                     continue
                 if "suffix2" in row:
                      suffix2 = row["suffix2"]
                 else:
                     continue
                 if "suffix3" in row:
                      suffix3 = row["suffix3"]
                 else:
                     continue
                 if "functions" in row:
                      functions = row["functions"]
#                      print("fnc:",functions)
                 else:
                     continue


                 if verb not in action_words:
                         action_words.append(verb)
                         verb_lst.append(verb)
                         if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((verb,alf))
                                    if not alf in fnc_verb:
                                        fnc_verb[alf] = []
                                    if not verb in fnc_verb[alf]:
                                        fnc_verb[alf].append(verb)
                         else:
                               action_functions.append((verb,functions))
                               if not functions in fnc_verb:
                                     fnc_verb[functions] = []
                               if not verb in fnc_verb[functions]:
                                     fnc_verb[functions].append(verb)


                 if ind1 not in action_words:
                         action_words.append(ind1)
                         if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((ind1,alf))
                         else:
                               action_functions.append((ind1,functions))

                 if ind2 not in action_words:
                          action_words.append(ind2)

                          if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((ind2,alf))
                          else:
                               action_functions.append((ind2,functions))

                 if cond1 not in action_words:
                         action_words.append(cond1)
                         if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((cond1,alf))
                         else:
                               action_functions.append((cond1,functions))


                 if cond2 not in action_words:
                          action_words.append(cond2)

                          if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((cond2,alf))
                          else:
                               action_functions.append((cond2,functions))


                 if sub1 not in action_words:
                         action_words.append(sub1)
                         if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((sub1,alf))
                         else:
                               action_functions.append((sub1,functions))

                 if sub2 not in action_words:
                          action_words.append(sub2)

                          if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((sub2,alf))
                          else:
                               action_functions.append((sub2,functions))

                 if participe not in action_words:
                         action_words.append(participe)
                         if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((participe,alf))
                         else:
                               action_functions.append((participe,functions))

                 if ind1+suffix1 not in action_words:
                          action_words.append(ind1+suffix1)
                          if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((ind1+suffix1,alf))
                                    action_functions.append((ind1+suffix1.replace("-"," "),alf))
                          else:
                               action_functions.append((ind1+suffix1,functions))
                               action_functions.append((ind1+suffix1.replace("-"," "),functions))

                 if ind2+suffix1 not in action_words:
                          action_words.append(ind2+suffix1)
                          if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((ind2+suffix1,alf))
                                    action_functions.append((ind2+suffix1.replace("-"," "),alf))
                          else:
                               action_functions.append((ind2+suffix1,functions))
                               action_functions.append((ind2+suffix1.replace("-"," "),functions))



                 if cond1+suffix2 not in action_words:
                          action_words.append(cond1+suffix2)
                          if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((cond1+suffix2,alf))
                                    action_functions.append((cond1+suffix2.replace("-"," "),alf))
                          else:
                               action_functions.append((cond1+suffix2,functions))
                               action_functions.append((cond1+suffix2.replace("-"," "),functions))

                 if cond2+suffix3 not in action_words:
                          action_words.append(cond2+suffix3)
                          if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((cond2+suffix3,alf))
                                    action_functions.append((cond2+suffix3.replace("-"," "),alf))
                          else:
                               action_functions.append((cond2+suffix3,functions))
                               action_functions.append((cond2+suffix3.replace("-"," "),functions))

                 if cond1+suffix2 not in action_words:
                          action_words.append(cond1+suffix2)
                          if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((cond1+suffix2,alf))
                                    action_functions.append((cond1+suffix2.replace("-"," "),alf))
                          else:
                               action_functions.append((cond1+suffix2,functions))
                               action_functions.append((cond1+suffix2.replace("-"," "),functions))

                 if cond2+suffix3 not in action_words:
                          action_words.append(cond2+suffix3)
                          if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((cond2+suffix3,alf))
                                    action_functions.append((cond2+suffix3.replace("-"," "),alf))
                          else:
                               action_functions.append((sub2+suffix3,functions))
                               action_functions.append((sub2+suffix3.replace("-"," "),functions))


                 if cond1+suffix2 not in action_words:
                          action_words.append(cond1+suffix2)
                          if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((cond1+suffix2,alf))
                                    action_functions.append((cond1+suffix2.replace("-"," "),alf))
                          else:
                               action_functions.append((cond1+suffix2,functions))
                               action_functions.append((cond1+suffix2.replace("-"," "),functions))

                 if cond2+suffix3 not in action_words:
                          action_words.append(cond2+suffix3)
                          if "***" in functions:
                              allowed_fonctions = functions.split("***")
                              for alf in allowed_fonctions:
                                    action_functions.append((cond2+suffix3,alf))
                                    action_functions.append((cond2+suffix3.replace("-"," "),alf))
                          else:
                               action_functions.append((cond2+suffix3,functions))
                               action_functions.append((cond2+suffix3.replace("-"," "),functions))

                 with open(PREFILE, newline="") as csvfile2:
                      reader2 = csv.DictReader(csvfile2)

                      for row in reader2:
                           if "present1" in row:
                                present1= row["present1"]
                           else:
                                continue
                           if "present2" in row:
                                present2 = row["present2"]
                           else:
                                continue
                           if "condi1" in row:
                                cond1 = row["condi1"]
                           else:
                                continue
                           if "condi2" in row:
                                cond2 = row["condi2"]
                           else:
                                continue

                           if not any("que" in var for var in [present1,present2,cond1,cond2]):
                               pre1 =present1+"*"+verb
                               if not pre1 in action_words:
#                                    print(pres1)
                                    action_words.append(pre1)
                                    if "***" in functions:
                                        allowed_fonctions = functions.split("***")
                                        for alf in allowed_fonctions:
                                              action_functions.append((pre1,alf))
                                    else:
                                         action_functions.append((pre1,functions))

                               pre2 =present2+"*"+verb
                               if not pre2 in action_words:
#                                    print(pres2)
                                    action_words.append(pre2)
                                    if "***" in functions:
                                        allowed_fonctions = functions.split("***")
                                        for alf in allowed_fonctions:
                                              action_functions.append((pre2,alf))
                                    else:
                                         action_functions.append((pre2,functions))


                               pre3 =cond1+"*"+verb
                               if not pre3 in action_words:
#                                    print(pre3)
                                    action_words.append(pre3)
                                    if "***" in functions:
                                        allowed_fonctions = functions.split("***")
                                        for alf in allowed_fonctions:
                                              action_functions.append((pre3,alf))
                                    else:
                                         action_functions.append((pre3,functions))

                               pre4 =cond2+"*"+verb
                               if not pre4 in action_words:
#                                    print(pre4)
                                    action_words.append(pre4)
                                    if "***" in functions:
                                        allowed_fonctions = functions.split("***")
                                        for alf in allowed_fonctions:
                                              action_functions.append((pre4,alf))
                                    else:
                                         action_functions.append((pre4,functions))



                           else:
                               pre1 =present1+"*"+sub1 
                               if not pre1 in action_words:
#                                    print(pres1)
                                    action_words.append(pre1)
                                    if "***" in functions:
                                        allowed_fonctions = functions.split("***")
                                        for alf in allowed_fonctions:
                                              action_functions.append((pre1,alf))
                                    else:
                                         action_functions.append((pre1,functions))

                               pre2 =present2+"*"+sub2
                               if not pre2 in action_words:
#                                    print(pres2)
                                    action_words.append(pre2)
                                    if "***" in functions:
                                        allowed_fonctions = functions.split("***")
                                        for alf in allowed_fonctions:
                                              action_functions.append((pre2,alf))
                                    else:
                                         action_functions.append((pre2,functions))


         for k in fnc_verb:
             fnc_verb[k].append("pouvoir")
             fnc_verb[k].append("vouloir")
             fnc_verb[k].append("être")
             fnc_verb[k].append("falloir")
             fnc_verb[k].append("devoir")


    else:

          print("\n-Trinity:Error:%s not found."%ACTFILE)
          sys.exit()


    if os.path.exists(ALTFILE):
         with open(ALTFILE, newline="") as csvfile:
             reader = csv.DictReader(csvfile)
             for row in reader:
                 
                 if "function" in row:
                      function = row["function"]
                 else:
                     continue

                 if "trigger" in row:
                      trigger = row["trigger"]

                     
                      if function == "ask_for_name":
                          check_trigger = Special_Syntax(trigger,CMDFILE,line)
                          if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_name.append(t)
                               else:
                                   trinity_name.append(trigger)
                      elif function == "ask_for_mean":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_mean.append(t)
                               else:
                                   trinity_mean.append(trigger)
                      elif function == "ask_for_creator":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_creator.append(t)
                               else:
                                   trinity_creator.append(trigger)
                      elif function == "trinity_script":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_script.append(t)
                               else:
                                   trinity_script.append(trigger)
                      elif function == "ask_for_help":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_help.append(t)
                               else:
                                   trinity_help.append(trigger)
                      elif function == "ask_for_prompt":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       prompt_request.append(t)
                               else:
                                   prompt_request.append(trigger)
                      elif function == "trinity_source_request":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       trinity_source_request.append(t)
                               else:
                                   trinity_source_request.append(trigger)
                      elif function == "ask_for_rnd":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       rnd_request.append(t)
                               else:
                                   rnd_request.append(trigger)
                      elif function == "ask_for_repeat":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       repeat_request.append(t)
                               else:
                                   repeat_request.append(trigger)
                      elif function == "show_history_request":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       show_history_request.append(t)
                               else:
                                   show_history_request.append(trigger)

                      elif function == "ask_for_history":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       search_history_request.append(t)
                               else:
                                   search_history_request.append(trigger)
                      elif function == "ask_to_read_link":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       read_link_request.append(t)
                               else:
                                   read_link_request.append(trigger)

                      elif function == "ask_to_play_wav":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       play_wav_request.append(t)
                               else:
                                   play_wav_request.append(trigger)
                      elif function == "ask_for_web":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       web_request.append(t)
                               else:
                                   web_request.append(trigger)
                      elif function == "ask_to_wait":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       wait_words.append(t)
                               else:
                                   wait_words.append(trigger)

                      elif function == "ask_to_add":
                           check_trigger = Special_Syntax(trigger,CMDFILE,line)
                           if check_trigger:
                               if isinstance(check_trigger,list):
                                   for t in check_trigger:
                                       add_words.append(t)
                               else:
                                   add_words.append(trigger)
    else:

          print("\n-Trinity:Error %s not found."%ALTFILE)
          sys.exit()








def Add_Trigger():

    print("\n-Trinity:Dans la fonction Add_Trigger.\n")

    First_time = True

    def seeknreturn(var_to_check,list_elements):
          found_lst = []
          for element in list_elements:
               if "*" in element:
                   splited = element.split("*")
                   all_inside = all(e in var_to_check for e in splited)
                   if all_inside:
#                      for s in splited:
#                          found_lst.append(s)
                       found_lst.append(element)
               if element in var_to_check:
                    found_lst.append(element)
          return(found_lst)



    def checktrigger(to_check,funcname,s_syntax=None):
 


              def minitts(tx,fname):

                       try:

                           client = tts.TextToSpeechClient()
                           audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

                           text_input = tts.SynthesisInput(text=tx)
                           voice_params = tts.VoiceSelectionParams(language_code="fr-FR", name="fr-FR-Neural2-A")

                           response = client.synthesize_speech(input=text_input,voice=voice_params,audio_config=audio_config)
                           audio_response = response.audio_content
                           try:
                               with open("%s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,fname), "wb") as out:
                                    out.write(audio_response)
                           except Exception as e:
                               PRINT("\n-Trinity:Error:%s"%str(e))
                       except Exception as e:
                           PRINT("\n-Trinity:Error:%s"%str(e))



              def getwav(f,trigparts):

                   trigcat = None

                   if f == "ask_to_wait":
                             trigcat = "wait_words"
                   if f == "ask_for_name":
                             trigcat = "trinity_name"
                   if f == "ask_for_mean":
                             trigcat = "trinity_mean"
                   if f == "ask_for_creator":
                             trigcat = "trinity_creator"
                   if f == "ask_for_rnd":
                             trigcat = "rnd_request"
                   if f == "ask_for_repeat":
                             trigcat = "repeat_request"
                   if f == "ask_for_prompt":
                             trigcat = "prompt_request"
                   if f == "ask_for_help":
                             trigcat = "trinity_help"
                   if f == "ask_to_play_wav":
                             trigcat = "play_wav_request"
                   if f == "ask_for_history":
                             trigcat = "search_history_request"
                   if f == "ask_to_read_link":
                             trigcat = "read_link_request"
                   if f == "ask_for_web":
                             trigcat = "web_request"
                   if f == "ask_to_add":
                             trigcat = "add_words"

                   if not trigcat:
                        PRINT("\n-Trinity:Error getwav %s ne correspond pas a une fonction."%f)
                        return()

                   os.system("aplay -q %s/local_sounds/cmd/triggers/%s.wav"%(SCRIPT_PATH,trigcat))

                   for t in trigparts:
                        t = unidecode(t.replace(" ","_").replace("-","_").replace("*","_").replace("'","_"))
                        wavname = trigcat + "_" + t + ".wav"
                        if os.path.exists("%s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,wavname)):
                             os.system("aplay -q %s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,wavname))
                        else:
                             print("\n-Trinity:Error Wave file not found:%s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,wavname)) 
                             minitts(tx,wavname)
                             if os.path.exists("%s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,wavname)):
                                  os.system("aplay -q %s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,wavname))
                   return()


              if isinstance(to_check,list):
                   PRINT("\n-Trinity:checktrigger():Verification d'une liste de déclencheurs.")
                   Triggers = to_check
              else:
                   Triggers = [to_check]

              if s_syntax:
                  trigger_cmd = s_syntax
              else:
                  trigger_cmd = to_check

              new_ambiguity = {}

              for trigger in Triggers:

                   trigger = unidecode(trigger.lower().replace(","," ").replace("!"," ").replace("?"," ").replace("  "," ").replace("."," "))

                   ask_to_action = seeknreturn(trigger,action_words)

                   ask_to_add = seeknreturn(trigger,add_words)

                   ask_for_name = seeknreturn(trigger,trinity_name)

                   ask_for_mean = seeknreturn(trigger,trinity_mean)

                   ask_for_creator = seeknreturn(trigger,trinity_creator)

                   ask_for_help = seeknreturn(trigger,trinity_help)

                   ask_for_prompt = seeknreturn(trigger,prompt_request)

                   ask_for_rnd = seeknreturn(trigger,rnd_request)

                   ask_for_repeat = seeknreturn(trigger,repeat_request)

                   ask_for_history = seeknreturn(trigger,search_history_request)

                   ask_to_show_history = seeknreturn(trigger,show_history_request)

                   ask_for_web = seeknreturn(trigger,web_request)

                   ask_to_read_link = seeknreturn(trigger,read_link_request)

                   ask_to_play_wav = seeknreturn(trigger,play_wav_request)

                   ask_to_wait = seeknreturn(trigger,wait_words)


                   if ask_to_action :
                        if ask_to_wait and funcname != "ask_to_wait":

                            if "ask_to_wait" in new_ambiguity:
                                  new_ambiguity["ask_to_wait"].append((trigger,ask_to_wait))
                            else:
                                  new_ambiguity["ask_to_wait"] = [(trigger,ask_to_wait)]

                        if ask_for_name and funcname != "ask_for_name":

                            if "ask_for_name" in new_ambiguity:
                                 new_ambiguity["ask_for_name"].append((trigger,ask_for_name))
                            else:
                                 new_ambiguity["ask_for_name"] = [(trigger,ask_for_name)]

                        if ask_for_mean and funcname != "ask_for_mean":

                            if "ask_for_mean" in new_ambiguity:
                                new_ambiguity["ask_for_mean"].append((trigger,ask_for_mean)) 
                            else:
                                  new_ambiguity["ask_for_mean"] = [(trigger,ask_for_mean)]

                        if ask_for_creator and funcname != "ask_for_creator":

                            if "ask_for_creator" in new_ambiguity:
                                  new_ambiguity["ask_for_creator"].append((trigger,ask_for_creator))
                            else:
                                  new_ambiguity["ask_for_creator"] = [(trigger,ask_for_creator)]

                        if ask_for_rnd and funcname != "ask_for_rnd":

                            if "ask_for_rnd" in new_ambiguity:
                                  new_ambiguity["ask_for_rnd"].append((trigger,ask_for_rnd))
                            else:
                                  new_ambiguity["ask_for_rnd"] = [(trigger,ask_for_rnd)]

                        if ask_for_repeat and funcname != "ask_for_repeat":

                            if "ask_for_repeat" in new_ambiguity:
                                  new_ambiguity["ask_for_repeat"].append((trigger,ask_for_repeat))
                            else:
                                  new_ambiguity["ask_for_repeat"] = [(trigger,ask_for_repeat)]

                        if ask_for_prompt and funcname != "ask_for_prompt":

                            if "ask_for_prompt" in new_ambiguity:
                                  new_ambiguity["ask_for_prompt"].append((trigger,ask_for_prompt))
                            else:
                                  new_ambiguity["ask_for_prompt"] =[(trigger,ask_for_prompt)]

                        if ask_for_help and funcname != "ask_for_help":

                            if "ask_for_help" in new_ambiguity:
                                  new_ambiguity["ask_for_help"].append((trigger,ask_for_help))
                            else:
                                  new_ambiguity["ask_for_help"] = [(trigger,ask_for_help)]

                        if ask_to_play_wav and funcname != "ask_to_play_wav":

                            if "ask_to_play_wav" in new_ambiguity:
                                  new_ambiguity["ask_to_play_wav"].append((trigger,ask_to_play_wav))
                            else:
                                  new_ambiguity["ask_to_play_wav"] = [(trigger,ask_to_play_wav)]

                        if ask_for_history and funcname != "ask_for_history":

                            if "ask_for_history" in new_ambiguity:
                                  new_ambiguity["ask_for_history"].append((trigger,ask_for_history))
                            else:
                                  new_ambiguity["ask_for_history"] = [(trigger,ask_for_history)]

                        if ask_to_read_link and funcname != "ask_to_read_link":

                            if "ask_to_read_link" in new_ambiguity:
                                   new_ambiguity["ask_to_read_link"].append((trigger,ask_to_read_link))
                            else:
                                   new_ambiguity["ask_to_read_link"] = [(trigger,ask_to_read_link)]

                        if ask_for_web and funcname != "ask_for_web":

                            if "ask_for_web" in new_ambiguity:
                                  new_ambiguity["ask_for_web"].append((trigger,ask_for_web))
                            else:
                                  new_ambiguity["ask_for_web"] = [(trigger,ask_for_web)]

                        if ask_to_add and funcname != "ask_to_add":

                            if "ask_to_add" in new_ambiguity:
                                 new_ambiguity["ask_to_add"].append((trigger,ask_to_add))
                            else:
                                  new_ambiguity["ask_to_add"] = [(trigger,ask_to_add)]

              if len(new_ambiguity) == 0:

                    print("\n-Parfait,cette phrase semble déclencher la fonction:",funcname)  
                    os.system("aplay -q %s/local_sounds/cmd/valid.wav"%SCRIPT_PATH)
                    os.system("aplay -q %s/local_sounds/cmd/save.wav"%SCRIPT_PATH)
                    while True:
                       rusure =input("\n-Sauvegarder cette phrase dans la base de données ?:\n\n%s\n\n-Votre choix:(oui/non/abandonner):"%trigger_cmd).lower()
                       if rusure in ["oui","non","abandonner"]:
                          if rusure == "oui": 

                               for trigger in Triggers:
                                   Write_csv(trigger,funcname,ALTFILE)

                               return(True)
                          elif rusure == "non":
                               return(False)
                          elif rusure =="abandonner":
                               return(True)

              else:

                    os.system("aplay -q %s/local_sounds/cmd/new_ambiguity.wav"%SCRIPT_PATH)

                    print("\n-Cette phrase à déclenchée plusieurs commandes en même temps:\n%s\n"%trigger_cmd)

                    for fnc,trigged in new_ambiguity.items():
                             for t,p in trigged:
                                 if s_syntax:
                                    print("\n\n-Déclencheur généré:\n%s\n"%t)
                                 print("\n-La fonction %s est déclenchée par cette partie: %s"%(fnc,p))
                             if not s_syntax:
                                 getwav(fnc,p)

                    os.system("aplay -q %s/local_sounds/cmd/new_ambiguity2.wav"%SCRIPT_PATH)

#              print("\n\n-mini touchdown\n\n")
 

    os.system("aplay -q %s/local_sounds/question/newtrigger.wav"%SCRIPT_PATH)

    functions = [
         ('trinity_name', 'pour avoir le nom du script de Trinity',"Salut ça va ?Comment tu t'appelle?","comment * t'appelle","trinity_name"),
         ('trinity_mean', 'pour avoir le sens du nom du script de Trinity',"Pourquoi on a décidé de t'appeler comme ça?","pourquoi *t'appeler comme ça","trinity_mean"),
         ('trinity_creator', 'pour connaitre le nom du créateur du script de Trinity',"Qui est-ce qui t'a créé ?","qui * t'a créé","trinity_creator"),
         ('trinity_help', "pour avoir l'aide du script Trinity","Affiche moi l'aide de ton script.","affiche*moi *aide * ton script","ask_for_help"),
         ('prompt_request', 'pour pouvoir écrire à Trinity',"J'ai besoin de t'écrire un truc.","ai * de t'écrire","ask_for_prompt"),
         ('trinity_source_request', 'pour afficher la source du script Trinity',"tu peux me montrer ton code source?","peux* montrer * ton code","ask_for_src"),
         ('rnd_request', 'pour effectuer un choix aléatoire',"Peux-tu faire un choix entre 1 et 2?","peux*tu * choix entre * et ","ask_for_rnd"),
         ('repeat_request', 'pour demander à Trinity de répéter',"J'ai rien compris tu peux me redire ça ?","tu*peux* redire ça","ask_to_repeat"),
         ('search_history_request', "pour faire une recherche dans l'historique","Regarde dans l'historique si tu trouve Albert Einstein","regarde * l'historique * si * trouve","ask_for_history"),
         ('read_link_request', "pour lire une page web","Tu peux me lire ce qu'il y a dans cette page web?","tu*peux* lire * dans * page web","ask_to_read_link"),
         ('play_wav_request', 'Pour lire un fichier audio',"Tu peux me jouer ce fichier audio s'il te plaît?","tu*peux* jouer * fichier audio","ask_to_play_wav"),
         ('web_request', 'Pour faire une recherche sur internet',"Fais-moi une recherche sur google a propos du big bang","fais*moi recherche * google * a propos","ask_for_web"),
         ('wait_words', "Pour demander à Trinity d'attendre","Minute papillon je ne suis pas près!","Minute * je * suis pas près","ask_to_wait"),
         ('add_words', 'Pour ajouter un nouveau déclencheur de fonction',"j'aimerai ajouter un nouveau trigger.","ajouter * nouveau * trigger","ask_to_add"),
   ]


    for index, (function_name, function_description,_,_,_) in enumerate(functions, start=1):
         print(f"({index}) {function_name} :  {function_description}")

    while True:
         try:
             user_choice = int(input("\nChoisissez une fonction (1 à {}): ".format(len(functions))))
             if user_choice in range(1,len(functions)+1):
                selected_function = functions[user_choice - 1][0]
                selected_description = functions[user_choice - 1][1]
                exemple1 = functions[user_choice - 1][2]
                exemple2 = functions[user_choice - 1][3]
                seekname = functions[user_choice - 1][4]
                break
         except:
             pass
    print(f"Vous avez choisi {selected_function}: {selected_description}")




    while True:
#             print("\n\n===============\n\n")

         if First_time:
             First_time = False
             os.system("aplay -q %s/local_sounds/cmd/instruction.wav"%SCRIPT_PATH)
             print("\n\n\n\n==Ajouter un nouveau déclencheur pour la fonction: %s ==\n\n\n-Gardez la partie qui identifie l'action %s dans votre phrase."%(selected_function,selected_description))
             print("\n-Par example si votre phrase complète ressemble à ceci:\n\n\t-",exemple1)
             print("\n-J'aimerais que vous ne gardiez que cela:\n\n\t-",exemple2)
             print("\n-Le symbole * est utilisé içi afin de ne pas tenir compte des mots qu'il peut y avoir à cette position.\n\n")
             print("\n\n-Voici les déclencheurs déjà enregistrés pour cette fonction:\n")
             for n,i in enumerate(globals()[selected_function]):print("\t%s-:%s"%(n,i))

             if seekname in fnc_verb:
                 print("\n\n-Voici la liste de verbes déjà associés à cette fonction:\n")
                 for n,f in enumerate(fnc_verb[seekname]):print("\t%s-:%s"%(n,f))
             else:
                 for k in fnc_verb:
                    print(k)
             print("\n-Si votre phrase utilise l'un de ces verbes même sous une forme conjugué il n'est pas nécessaire de l'écrire.\n-Vous pouvez néanmoins le faire si vous souhaitez que votre déclencheur soit plus précis.\n\n-Les accents et caractére spéciaux et ponctuations sont automatiquement enlevés.\n")

             print("\n-Il est aussi possible de générer plusieurs déclencheurs en même temps en utilisant la syntaxe avancée par exemple:\n")

             print("\n\t-Nouveau déclencheur:Salutation!*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Salutation!*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Salutation!*Tout va bien?")
             print("\t-Nouveau déclencheur:Salutation!Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Salutation!Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Salutation!Tout va bien?")
             print("\t-Nouveau déclencheur:Salutation.*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Salutation.*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Salutation.*Tout va bien?")
             print("\t-Nouveau déclencheur:Salutation.Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Salutation.Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Salutation.Tout va bien?")
             print("\t-Nouveau déclencheur:Salut!*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Salut!*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Salut!*Tout va bien?")
             print("\t-Nouveau déclencheur:Salut!Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Salut!Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Salut!Tout va bien?")
             print("\t-Nouveau déclencheur:Salut.*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Salut.*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Salut.*Tout va bien?")
             print("\t-Nouveau déclencheur:Salut.Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Salut.Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Salut.Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur!*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur!*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur!*Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur!Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur!Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur!Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur.*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur.*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur.*Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur.Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur.Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Monsieur.Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame!*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame!*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame!*Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame!Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame!Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame!Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame.*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame.*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame.*Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame.Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame.Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour Madame.Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour!*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour!*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour!*Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour!Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour!Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour!Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour.*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour.*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour.*Tout va bien?")
             print("\t-Nouveau déclencheur:Bien le Bonjour.Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour.Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bien le Bonjour.Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur!*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur!*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur!*Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur!Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur!Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur!Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur.*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur.*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur.*Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur.Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur.Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour Monsieur.Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour Madame!*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour Madame!*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour Madame!*Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour Madame!Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour Madame!Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour Madame!Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour Madame.*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour Madame.*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour Madame.*Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour Madame.Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour Madame.Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour Madame.Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour!*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour!*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour!*Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour!Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour!Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour!Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour.*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour.*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour.*Tout va bien?")
             print("\t-Nouveau déclencheur:Bonjour.Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Bonjour.Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Bonjour.Tout va bien?")
             print("\t-Nouveau déclencheur:Coucou!*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Coucou!*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Coucou!*Tout va bien?")
             print("\t-Nouveau déclencheur:Coucou!Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Coucou!Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Coucou!Tout va bien?")
             print("\t-Nouveau déclencheur:Coucou.*Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Coucou.*Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Coucou.*Tout va bien?")
             print("\t-Nouveau déclencheur:Coucou.Tout va comme il faut ?")
             print("\t-Nouveau déclencheur:Coucou.Tout va comme vous voulez ?")
             print("\t-Nouveau déclencheur:Coucou.Tout va bien?\n")


             print("\n-Tous ces déclencheurs ont été générés par cette commande:")
             print("\n    -Nouveau déclencheur:[Salut{ation/}/{Bien le /}Bonjour{ Monsieur/ Madame/}/Coucou][!/.][*/]Tout va [comme {il faut/vous voulez} /bien]?\n\n")


             print("\n\n-Les symboles '[' et ']' servent à créer une liste d'éléments séparé par le symbole '/'.")
             print("-Les symboles '{' et '}' sont utilisés dans une liste pour créer une sous-liste d'éléments séparé par le symbole '/'.\n")
         else:
             os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/prompt/2.wav")

         new_trigger = input("\n-Nouveau déclencheur pour la fonction %s :"%selected_function)
         checksyntax = Special_Syntax(new_trigger,SCRIPT_PATH+"Trinity.py",Get_Line())
         if not checksyntax:
             while True:
                 new_trigger = input("\n-Nouveau déclencheur pour la fonction %s :"%selected_function)
                 checksyntax = Special_Syntax(new_trigger,SCRIPT_PATH+"Trinity.py",Get_Line())
                 if checksyntax:break
         if isinstance(checksyntax,list):

             valid = checktrigger(checksyntax,seekname,new_trigger)
         else:
             valid = checktrigger(checksyntax,seekname)

         if valid:
              return(selected_function)




def Get_Line():
    try:
        frame = inspect.currentframe()
        numero_ligne = frame.f_back.f_lineno
        return(numero_ligne)
    except Exception as e:
        PRINT("-Trinity:Error:Get_Line():%s"%str(e))
        return(0)



def Commandes(txt):


    def postprod(txt,funcname,specific_trigger=None,main_trigger=None):
        asked = False

        def has_syn(function_name,sentence,altlst = None):
            synlst = []
            syntoprint = []
            found = []

            if altlst:
                 for act in altlst:
                         synlst.append(act)
            else:
                 for syn in action_functions:
                     act = syn[0]
                     fn = syn[1]
                     if fn == function_name:
                         #print("adding:",act)
                         synlst.append(act)
                         for v in verb_lst:
                             if v in act and not v in syntoprint:
                                syntoprint.append(v)

            for syn in synlst:
                if syn in sentence:
                   found.append(syn)
            if len(found) == 0:
                 os.system("aplay -q %s/local_sounds/cmd/triggers/atleast.wav"%(SCRIPT_PATH))
                 if not altlst:
                      print("\n-Trinity:Votre phrase doit contenir au minimum l'un des mot suivant:\n\n%s\n\n"%(syntoprint))
                      return(False)
                 else:
                      print("\n-Trinity:Votre phrase doit contenir au minimum l'in des mots suivant:\n\n%s\n\n"%(altlst))
                      return(False)
            else:
                 return(True)


        def checktrigger(trigger,funcname,spec_trigger,main_action=None):


              def getwav(f,trigparts):


                   def minitts(tx,fname):

                       try:

                           client = tts.TextToSpeechClient()
                           audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

                           text_input = tts.SynthesisInput(text=tx)
                           voice_params = tts.VoiceSelectionParams(language_code="fr-FR", name="fr-FR-Neural2-A")

                           response = client.synthesize_speech(input=text_input,voice=voice_params,audio_config=audio_config)
                           audio_response = response.audio_content
                           try:
                               with open("%s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,fname), "wb") as out:
                                    out.write(audio_response)
                           except Exception as e:
                               PRINT("\n-Trinity:Error:%s"%str(e))
                       except Exception as e:
                           PRINT("\n-Trinity:Error:%s"%str(e))

                   trigcat = None

                   if f == "ask_to_wait":
                             trigcat = "wait_words"
                   if f == "ask_for_name":
                             trigcat = "trinity_name"
                   if f == "ask_for_mean":
                             trigcat = "trinity_mean"
                   if f == "ask_for_creator":
                             trigcat = "trinity_creator"
                   if f == "ask_for_rnd":
                             trigcat = "rnd_request"
                   if f == "ask_for_repeat":
                             trigcat = "repeat_request"
                   if f == "ask_for_prompt":
                             trigcat = "prompt_request"
                   if f == "ask_for_help":
                             trigcat = "trinity_help"
                   if f == "ask_to_play_wav":
                             trigcat = "play_wav_request"
                   if f == "ask_for_history":
                             trigcat = "search_history_request"
                   if f == "ask_to_read_link":
                             trigcat = "read_link_request"
                   if f == "ask_for_web":
                             trigcat = "web_request"

                   if not trigcat:
                        PRINT("\n-Trinity:Error getwav %s ne correspond pas a une fonction."%f)
                        return()

                   os.system("aplay -q %s/local_sounds/cmd/triggers/%s.wav"%(SCRIPT_PATH,trigcat))

                   for t in trigparts:
                        t = unidecode(t.replace(" ","_").replace("-","_").replace("*","_").replace("'","_"))
                        wavname = trigcat + "_" + t + ".wav"
                        if os.path.exists("%s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,wavname)):
                             os.system("aplay -q %s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,wavname))
                        else:
                             print("\n-Trinity:Error Wave file not found:%s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,wavname)) 
                             minitts(tx,wavname)
                             if os.path.exists("%s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,wavname)):
                                  os.system("aplay -q %s/local_sounds/cmd/triggers/%s"%(SCRIPT_PATH,wavname))
                   return()


              if isinstance(trigger,list):
                 print("check special syntax trigger:")
                 for i in trigger:
                     print(i)
                 sys.exit()


              new_ambiguity = {}

              trigger = unidecode(trigger.lower().replace(","," ").replace("!"," ").replace("?"," ").replace("  "," "))

              PRINT("\n-Trinity:main_action=None:",main_action)
              PRINT("\n-Trinity:spec_trigger:",spec_trigger)
              PRINT("\n-Trinity:funcname:",funcname)
              PRINT("\n-Trinity:trigger:",trigger)

              main_trigger = has_syn(funcname,trigger)
              func_trigger = has_syn(funcname,trigger,altlst=spec_trigger)

              if not main_trigger:
                  return(False)
              if not func_trigger:
                  return(False)


              ask_to_action = seeknreturn(trigger,action_words)

              ask_to_add = seeknreturn(trigger,add_words)

              ask_for_name = seeknreturn(trigger,trinity_name)

              ask_for_mean = seeknreturn(trigger,trinity_mean)

              ask_for_creator = seeknreturn(trigger,trinity_creator)

              ask_for_help = seeknreturn(trigger,trinity_help)

              ask_for_prompt = seeknreturn(trigger,prompt_request)

              ask_for_rnd = seeknreturn(trigger,rnd_request)

              ask_for_repeat = seeknreturn(trigger,repeat_request)

              ask_for_history = seeknreturn(trigger,search_history_request)

              ask_for_web = seeknreturn(trigger,web_request)

              ask_to_read_link = seeknreturn(trigger,read_link_request)

              ask_to_play_wav = seeknreturn(trigger,play_wav_request)

              ask_to_wait = seeknreturn(trigger,wait_words)


              if ask_to_action :
                   if ask_to_wait and funcname != "ask_to_wait":
                             new_ambiguity["ask_to_wait"] = ask_to_wait
                   if ask_for_name and funcname != "ask_for_name":
                             new_ambiguity["ask_for_name"] = ask_for_name 
                   if ask_for_mean and funcname != "ask_for_mean":
                             new_ambiguity["ask_for_mean"] = ask_for_mean
                   if ask_for_creator and funcname != "ask_for_creator":
                             new_ambiguity["ask_for_creator"] = ask_for_creator
                   if ask_for_rnd and funcname != "ask_for_rnd":
                             new_ambiguity["ask_for_rnd"] = ask_for_rnd
                   if ask_for_repeat and funcname != "ask_for_repeat":
                             new_ambiguity["ask_for_repeat"] = ask_for_repeat
                   if ask_for_prompt and funcname != "ask_for_prompt":
                             new_ambiguity["ask_for_prompt"] =ask_for_prompt
                   if ask_for_help and funcname != "ask_for_help":
                             new_ambiguity["ask_for_help"] = ask_for_help
                   if ask_to_play_wav and funcname != "ask_to_play_wav":
                             new_ambiguity["ask_to_play_wav"] = ask_to_play_wav
                   if ask_for_history and funcname != "ask_for_history":
                             new_ambiguity["ask_for_history"] =  ask_for_history
                   if ask_to_read_link and funcname != "ask_to_read_link":
                              new_ambiguity["ask_to_read_link"] = ask_to_read_link
                   if ask_for_web and funcname != "ask_for_web":
                             new_ambiguity["ask_for_web"] = ask_for_web

              if len(new_ambiguity) == 0:

                    print("\n-Trinity:Parfait,cette phrase semble déclencher la fonction:",funcname)  
                    os.system("aplay -q %s/local_sounds/cmd/valid.wav"%SCRIPT_PATH)
                    os.system("aplay -q %s/local_sounds/cmd/save.wav"%SCRIPT_PATH)
                    while True:
                       rusure =input("\n-Sauvegarder cette phrase dans la base de données ?:\n\n%s\n\n-Votre choix:(oui/non/abandonner)"%trigger).lower()
                       if rusure in ["oui","non","abandonner"]:
                          if rusure == "oui": 
                               Write_csv(trigger,funcname,ALTFILE)
                               return(True)
                          elif rusure == "non":
                               return(False)
                          elif rusure =="abandonner":
                               return(True)

              else:

                    os.system("aplay -q %s/local_sounds/cmd/new_ambiguity.wav"%SCRIPT_PATH)
                    for fnc,trigged in new_ambiguity.items():
                             print("\n-Trinity:La fonction %s est déclenchée par cette partie: %s"%(fnc,trigged))
                             getwav(fnc,trigged)

                    os.system("aplay -q %s/local_sounds/cmd/new_ambiguity2.wav"%SCRIPT_PATH)

#              print("\n\n-mini touchdown\n\n")
 

        while True:
          print("\n\n===============\n\n")

          if not asked:
               os.system("aplay -q %s/local_sounds/cmd/question_trigger.wav"%SCRIPT_PATH)
               while True:
                   helpme = input("-Pouvez-vous m'aider à mieux intégrer cette phrase dans ma base de données?\n-Cela ne prendra pas longtemps.\n\nVotre Choix (oui/non):").lower()
                   if helpme in  ["oui","non"]:
                           if "oui" in helpme:
                                  helpme = True
                                  asked = True
                           else:
                                  helpme = False
                           break
          else:
               helpme = True

          if helpme:
             os.system("aplay -q %s/local_sounds/cmd/instruction.wav"%SCRIPT_PATH)
             print("\n\n===============\n\n==Ajouter un nouveau declencheur pour la fonction: %s ==\n\n-Trinity:Pouvez-vous garder uniquement la partie qui identifie l'action dans votre phrase?"%funcname)
             print("\n-Trinity:Par example si vous auriez dis:\n\n\t-Peux-tu s'il te plaît chercher un truc sur Albert Einstein in wikipedia ce serait super cool!")
             print("\n-Trinity:J'aurais voulue que vous ne gardiez que cela:\n\n\t-Peux-tu * chercher * dans wikipedia")
             print("\n-Trinity:Le symbole * est utilisé içi afin de ne pas tenir compte des mots qu'il peut y avoir à cette position.")
             print("\n-Trinity:Voici votre phrase:\n%s\n"%txt)
             new_trigger = input("\nNouvelle déclencheur pour la fonction %s :"%funcname)
             valid = checktrigger(new_trigger,funcname,spec_trigger=specific_trigger,main_action=main_trigger)
             if valid:
                  return(funcname)
          else:
               os.system("aplay -q %s/local_sounds/cmd/sorry.wav"%SCRIPT_PATH)
               Write_csv(new_trigger,funcname,ALTFILE)
               return(funcname)
    def disambiguify(actions,function_names,txt,action_trigger= None):


       func_name_toadd = None
       trigger_words_toadd = None
       must_contain = None
       trigger_function = {}
       triggered_parts = {}
       score_function = {}

       for fnc in function_names:
               if fnc == "ask_to_action":
                      continue
               if fnc == "ask_for_web":
                   trigger_function[fnc] = web_request 
               if fnc == "ask_to_play_wav":
                   trigger_function[fnc] = play_wav_request
               if fnc == "ask_to_show_history":
                   trigger_function[fnc] = show_history_request
               if fnc == "ask_for_history":
                   trigger_function[fnc] = search_history_request 
               if fnc == "ask_to_read_link":
                   trigger_function[fnc] = read_link_request
               if fnc == "ask_to_wait":
                   trigger_function[fnc] = wait_words
               if fnc == "ask_for_name":
                   trigger_function[fnc] = trinity_name
               if fnc == "ask_for_mean":
                   trigger_function[fnc] = trinity_mean
               if fnc == "ask_for_creator":
                   trigger_function[fnc] = trinity_creator
               if fnc == "ask_for_help":
                   trigger_function[fnc] = trinity_help
               if fnc == "ask_for_prompt":
                   trigger_function[fnc] = prompt_request
               if fnc == "ask_for_rnd":
                   trigger_function[fnc] = rnd_request
               if fnc == "ask_for_repeat":
                   trigger_function[fnc] = repeat_request
               if fnc == "ask_to_wait":
                   trigger_function[fnc] = wait_words
               if fnc == "ask_to_add":
                   trigger_function[fnc] = add_words

               triggered_parts[fnc] = seeknreturn(txt,trigger_function[fnc])
               bonus = bonuspoint(txt,action_functions,fnc)
               bonus = 0
               score_function[fnc] = len(triggered_parts[fnc]) + bonus



       sorted_score = dict(sorted(score_function.items(), key=lambda item: item[1], reverse=True))

       ordered_list = list(dict(sorted(score_function.items(), key=lambda item: item[1], reverse=True)).keys())


       winner = bestvalue(sorted_score,ordered_list)

       if winner:

           PRINT("\n-Trinity:%s has the higher confidence score.\n"%winner)
           for n,(fnc) in enumerate(ordered_list):
                PRINT("\n-Trinity:Commande:%s\n-Déclenchée par %s parties:%s\n-Score de Confiance:%s"%(fnc,len(triggered_parts[fnc]),triggered_parts[fnc],score_function[fnc]))

           return(winner)
       else:
           print("\n\n===============\n\n\n-Trinity:Cette phrase à déclenchée plusieurs commandes en même temps:")
           print("\n-Trinity:Votre phrase:",txt)


       os.system("aplay -q %s"%(SCRIPT_PATH+"/local_sounds/cmd/ambiguty.wav"))
       while True:
           for n,(fnc) in enumerate(ordered_list):
                print("\n-Trinity:Commande:%s\n-Déclenchée par %s parties:%s\n-Score de Confiance:%s"%(fnc,len(triggered_parts[fnc]),triggered_parts[fnc],score_function[fnc]))
                print("\n==\n-Trinity:Pour choisir cette commande (%s) tapez:%s\n==\n"%(fnc,n))

                if n+1 == 1:
                    os.system("aplay -q %s/local_sounds/cmd/intro_%s.wav"%(SCRIPT_PATH,fnc))
                elif n+1 > 1 and n+1 < len(ordered_list):
                    os.system("aplay -q %s/local_sounds/cmd/%s.wav"%(SCRIPT_PATH,fnc))
                elif n+1 == len(ordered_list):
                    os.system("aplay -q %s/local_sounds/cmd/outro_%s.wav"%(SCRIPT_PATH,fnc))


           print("\n==\n-Trinity:Si ce n'était pas une commande tapez:%s\n==\n"%len(sorted_score))

           os.system("aplay -q %s/local_sounds/cmd/hit%s.wav"%(SCRIPT_PATH,len(sorted_score)))


           response = input("\n-Trinity:Choisissez la bonne réaction pour cette phrase:")
           try:
#           if 1 == 1 :
              response = int(response.strip())
              if response > len(sorted_score):
                   continue
              elif response == len(sorted_score):
                   return("")
              else:
                    func_name_toadd = ordered_list[response]
                    PRINT("\nfunc_name_toadd:%s"%func_name_toadd)
                    trigger_words_toadd = sorted_score[func_name_toadd]
                    PRINT("\ntrigger_words_toadd:%s"%txt)
                    must_contain = triggered_parts[ordered_list[response]]
                    break
           except Exception as e:
#                   print("\nerror:",e)
                   pass

       if func_name_toadd and trigger_words_toadd and must_contain:
       
            print("\n-Trinity:La fonction %s à été choisie pour cette phrase.\n"%func_name_toadd)
            if action_trigger:
                 goto = postprod(txt,func_name_toadd,specific_trigger=must_contain,main_trigger=action_trigger)
            else:
                 goto = postprod(txt,func_name_toadd,specific_trigger=must_contain)
            if goto:
                   return(goto)
       else:
           if not func_name_toadd:
                PRINT("\n-Trinity:func_name_toadd is missing")
           if not trigger_words_toadd:
                PRINT("\n-Trinity:trigger_words_toadd is missing")
           if not must_contain:
                PRINT("\n-Trinity:must_contain is missing")
           return()

    def bonuspoint(txt,aflist,function_tomatch):

          bonus = 0
          bonusyn = 0
          print("\n-Trinity:function_tomatch:%s"%function_tomatch)
          for af in aflist:
               act = af[0]
               fn = af[1]

               if act in txt and fn == function_tomatch:
                    PRINT("Bonus point +1 %s in txt and %s is matching %s"%(act,fn,function_tomatch))
                    bonus += 1

                    for syn in synonyms_list:
                        for s in syn:
                            if s in txt:
                               for newsyn in syn:

                                   newtxt = txt.replace(s,newsyn)

                                   if function_tomatch == "ask_for_web":
                                       bonusyn = len(seeknreturn(newtxt,web_request)) 
                                   if function_tomatch == "ask_to_play_wav":
                                       bonusyn = len(seeknreturn(newtxt,play_wav_request))
                                   if function_tomatch == "ask_to_show_history":
                                       bonusyn = len(seeknreturn(newtxt,show_history_request))
                                   if function_tomatch == "ask_for_history":
                                       bonusyn = len(seeknreturn(newtxt,search_history_request)) 
                                   if function_tomatch == "ask_to_read_link":
                                       bonusyn = len(seeknreturn(newtxt,read_link_request))
                                   if function_tomatch == "ask_to_wait":
                                       bonusyn = len(seeknreturn(newtxt,wait_words))
                                   if function_tomatch == "ask_for_name":
                                       bonusyn = len(seeknreturn(newtxt,trinity_name))
                                   if function_tomatch == "ask_for_mean":
                                       bonusyn = len(seeknreturn(newtxt,trinity_mean))
                                   if function_tomatch == "ask_for_creator":
                                       bonusyn = len(seeknreturn(newtxt,trinity_creator))
                                   if function_tomatch == "ask_for_help":
                                       bonusyn = len(seeknreturn(newtxt,trinity_help))
                                   if function_tomatch == "ask_for_prompt":
                                       bonusyn = len(seeknreturn(newtxt,prompt_request))
                                   if function_tomatch == "ask_for_rnd":
                                       bonusyn = len(seeknreturn(newtxt,rnd_request))
                                   if function_tomatch == "ask_for_repeat":
                                       bonusyn = len(seeknreturn(newtxt,repeat_request))

                                   bonusyn += len(seeknreturn(newtxt,alt_trigger))

                                   bonus += bonusyn

          return(bonus)


    def bestvalue(dictionary,ordered):
         if not dictionary:
             return(False)
         values = [dictionary[key] for key in ordered]
         max_value = max(values)
         count_max_value = values.count(max_value)
         if count_max_value == 1:
             max_value_key = ordered[values.index(max_value)]
             return(max_value_key)
         return(False)




    def seeknreturn(var_to_check,list_elements):
#          PRINT("\n-Trinity:Dans la fonction seeknreturn")
          found_lst = []
          for element in list_elements:
               if "*" in element:
                   splited = element.split("*")
                   all_inside = all(e in var_to_check for e in splited)
                   if all_inside:
#                      for s in splited:
#                          found_lst.append(s)
                       found_lst.append(element)
               if element in var_to_check:
                    found_lst.append(element)
          return(found_lst)


    def seekndestroy(list_elements, var_to_check):
          PRINT("\n-Trinity:Dans la fonction seekndestroy")
          for element in list_elements:
              if element in var_to_check:
                  PRINT("\n-Trinity:Detroying :",element)
                  var_to_check = var_to_check.replace(element," ")
          return(var_to_check.replace("  "," "))

    decoded = unidecode(txt.lower())

    ambiguity = []

    filter = ["s'il te plait","si te plait","sil te plait","merci"," stp "]

    to_remove = [" fais ","estce"," peux faire "," recherche ","faismoi"," fais ","peux ","fais recherche "," parle ","s'il te plait"," stp "," svp"," sur ","sil plait"]




    ask_to_action = seeknreturn(decoded,action_words)

    ask_to_add = seeknreturn(decoded,add_words)

    ask_for_name = seeknreturn(decoded,trinity_name)

    ask_for_mean = seeknreturn(decoded,trinity_mean)

    ask_for_creator = seeknreturn(decoded,trinity_creator)

    ask_for_help = seeknreturn(decoded,trinity_help)

    ask_for_prompt = seeknreturn(decoded,prompt_request)

    ask_for_rnd = seeknreturn(decoded,rnd_request)

    ask_for_repeat = seeknreturn(decoded,repeat_request)

    ask_to_show_history = seeknreturn(decoded,show_history_request)

    ask_for_history = seeknreturn(decoded,search_history_request)

    ask_for_web = seeknreturn(decoded,web_request)

    ask_to_read_link = seeknreturn(decoded,read_link_request)

    ask_to_play_wav = seeknreturn(decoded,play_wav_request)


    ask_to_wait = seeknreturn(decoded,wait_words)


    found_alt_trigger = seeknreturn(decoded,alt_trigger)


    decoded = seekndestroy(filter, decoded)


    if ask_to_action or found_alt_trigger:
         ambiguity.append("ask_to_action")

         if ask_to_wait:
              ambiguity.append("ask_to_wait")
         if ask_for_name:
              ambiguity.append("ask_for_name")
         if ask_for_mean:
              ambiguity.append("ask_for_mean")
         if ask_for_creator:
              ambiguity.append("ask_for_creator")
         if ask_for_rnd:
              ambiguity.append("ask_for_rnd")
         if ask_for_repeat:
              ambiguity.append("ask_for_repeat")
         if ask_for_prompt:
             ambiguity.append("ask_for_prompt")
         if ask_for_help:
             ambiguity.append("ask_for_help")
         if ask_to_play_wav:
             ambiguity.append("ask_to_play_wav")
         if ask_to_show_history:
             ambiguity.append("ask_to_show_history")
         if ask_for_history:
                 ambiguity.append("ask_for_history")
         if ask_to_read_link:
                 ambiguity.append("ask_to_read_link") 
         if ask_for_web:
                 ambiguity.append("ask_for_web")
         if ask_to_add:
                 ambiguity.append("ask_to_add")

    goto = None
    if len(ambiguity) > 1:
        if ask_to_action:
             goto = disambiguify(ask_to_action,ambiguity,decoded,ask_to_action)
        else:
             goto = disambiguify(ask_to_action,ambiguity,decoded)

        if goto:
            PRINT("\n-Trinity:Va dans la fonction :%s"%goto)
    elif len(ambiguity) == 1:
        PRINT("\n-Trinity:No ambiguity")
    else:
        PRINT("\n-Trinity:Aucune commande.")

    if goto:

       if goto == "ask_to_add":
              Add_Trigger()
              return(True)

       if goto == "ask_to_wait":
              Standing_By()
              return(True)

       elif goto == "ask_for_name":
          os.system("aplay -q %s"%(SCRIPT_PATH+"/local_sounds/saved_answer/trinity.wav"))
          return(True)

       elif goto == "ask_for_mean":
          os.system("aplay -q %s"%(SCRIPT_PATH+"/local_sounds/saved_answer/matrix.wav"))
          return(True)
       elif goto == "ask_for_creator":
          os.system("aplay -q %s"%(SCRIPT_PATH+"/local_sounds/saved_answer/botmaster.wav"))
          return(True)

       elif goto == "ask_for_rnd":
          rnd = str(random.randint(1,2))
          ouinon = SCRIPT_PATH+"/local_sounds/ouinon/"+rnd+".wav"
          os.system("aplay -q %s"%ouinon)
          return(True)
       elif goto == "ask_for_repeat":
          os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/repeat/isaid.wav")
          os.system("aplay -q %s"%SCRIPT_PATH+"tmp/current_answer.wav")
          return(True)

       elif goto == "ask_for_prompt":
              Fallback_Prompt()
              return(True)
       elif goto == "ask_for_help":
              os.system("aplay -q %s"%(SCRIPT_PATH+"/local_sounds/saved_answer/help.wav"))
              return(True)
       elif goto == "ask_to_play_wav":
              os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/question/sound_file.wav")
              sound_input = input("Entrez le chemin du fichier à lire:")
              if sound_input.endswith(".wav"):
                  Play_Response(sound_input,stayawake=False,savehistory=False)
                  return(True)
              else:
                  return(True)

       elif goto == "ask_to_show_history":

           Show_History()
           return(True)


       elif goto == "ask_for_history":
#               for element in to_remove:
#                  if element in decoded:
#                      decoded = decoded.replace(element," ")


               decoded = decoded.replace("  ","")

               to_search = Isolate_Search_Request(decoded,ask_for_history)
               Search_History(to_search)
               return(True)

       elif goto == "ask_to_read_link":
                  ReadLink(txtinput=decoded)

                  return(True)
       elif goto == "ask_for_web":

           if "wikipedia" in decoded:
#               for element in to_remove:
#                  if element in decoded:
#                      decoded = decoded.replace(element," ")

               decoded = decoded.replace("wikipedia"," ").replace("  "," ")
               os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/server/wikipedia.wav")

#               for element in to_remove:
#                   if element in decoded:
#                      decoded = decoded.replace(element," ")
               decoded = decoded.replace("  "," ")

               to_search = Isolate_Search_Request(decoded,ask_for_web)

               Wikipedia(to_search)

               return(True)
           else:
#               for element in to_remove:
#                  if element in decoded:
#                      decoded = decoded.replace(element," ")
               decoded = decoded.replace("  "," ")

               to_search = Isolate_Search_Request(decoded,ask_for_web)
               Google(to_search)
               return(True)


       else:
            return(False)
    else:
          return(False)





def GetTitleLink(txt,site=None):
    PRINT("\n-Trinity:Dans la fonction GetTitleLink()")
    PRINT("\n-Trinity:txt:",txt)
    PRINT("\n-Trinity:txt:",site)

    SearchFallback = False

    if (len(GOOGLE_KEY) != 0 and len(GOOGLE_ENGINE) != 0):

         PRINT("\n-Trinity:Using Custom Search Google Api.")

         try:
             google_query = "https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s&start=1"%(GOOGLE_KEY,GOOGLE_ENGINE,txt)

             response = requests.get(google_query)

             if response.status_code != 200:
                       SearchFallback = True
                       raise

             data = response.json()

             search_items = data.get("items")

             title_search = ""

             for result in search_items:

                  title_search = result.get("title")

                  if len(title_search) == 0:
                     continue
                  else:
                      break

         except Exception as e:
                   os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_Google.wav")
                   PRINT("\n-Trinity:Custom search Error:",str(e))
                   SearchFallback = True

         if len(title_search) == 0:
                 PRINT("\n-Trinity:-Google() no result from google")
                 os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_no_result_google.wav")
                 SearchFallback = True
         else:
               return(title_search)

    if (len(GOOGLE_KEY) == 0 and len(GOOGLE_ENGINE) == 0) or SearchFallback == True:

         try:
             google_result = googlesearch.search(txt,num_results=10,lang="fr", advanced=True)

             title_search = ""

             for g in google_result:
                 if site:
                     if site in g.url:
                         PRINT("\n-Trinity:google_result:",g.title)
                         title_search = g.title
                         break
                 else:
                         PRINT("\n-Trinity:google_result:",g.title)
                         title_search = g.title
                         break


             if len(title_search) == 0:
                 PRINT("\n-Trinity:GetTitleLink no result from google")
                 os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_no_result_google.wav")
                 return(None)

             else:
                 return(title_search)



         except Exception as e:
              os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_google.wav")
              PRINT("\n-Trinity:Error:",str(e))
              return(None)

    return(None) 



def ReadLink(txtinput=None,titleinput=None,urlinput=None):

    PRINT("\n-Trinity: txtinput: %s",txtinput)

    regex = re.compile(
        r'^(?:http://|https://|ftp://|.)'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not urlinput:
         urlinput = ""
         for word in txtinput.split():

             match = re.match(regex, word)
             if match:
                    urlinput = word
                    break

    if len(urlinput) > 0:
       if "wikipedia" in urlinput:
               if not titleinput:
                   wiki_title = GetTitleLink(txtinput,"wikipedia")
               else:
                   wiki_title = titleinput

               if wiki_title:
                   PRINT("\n-Trinity:wiki_title:",wiki_title)
                   return(Wikipedia(txtinput,Title=wiki_title))

               else:
                   PRINT("\n-Trinity:no title using txtinput:",txtinput)
                   return(Wikipedia(txtinput))
       else:


                try:

                    response = requests.get(urlinput)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text_data = ''
                    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                         text_data += tag.get_text()
                    if len(text_data) >0:
                       os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/reading_link.wav")
                       last_sentence.put(txtinput+" %s"%urlinput)
                       Text_To_Speech(text_data,stayawake=True)
                       return()
                    else:
                        os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_read_link_no_txt.wav")
                        return()
                except Exception as e:
                      PRINT("\n-Trinity:Error:",str(e))
                      os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_read_link_request.wav")


    else:
         os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/question/read_link_url.wav")

         url_input = input("Entrez un lien:")

         for word in url_input.split():
 
            match = re.match(regex, word)
            if match:
               urlinput = word
               break


    if len(urlinput) > 0:
#           if "wikipedia" in urlinput: ##TO REWRITE


#               if not titleinput: ####ToCHECKurlinputVStxtinput
#                   wiki_title = GetTitleLink(txtinput,"wikipedia")
#               else:
#                   wiki_title = titleinput
#
#               if wiki_title:
#                   PRINT("\n-Trinity:wiki_title:",wiki_title)
#                   return(Wikipedia(txtinput,title=wiki_title))

#               else:
#                   PRINT("\n-Trinity:Pas de titre title utilisation de txtinput:",txtintput)
#                   return(Wikipedia(txtinput))

#           else:
           if 1 == 1:
                try:

                    response = requests.get(urlinput)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text_data = ''
                    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                         text_data += tag.get_text()
                    if len(text_data) >0:
                       os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/reading_link.wav")
                       last_sentence.put(txtinput+" %s"%urlinput)
                       Text_To_Speech(text_data,stayawake=True)
                       return()
                    else:
                        os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_read_link_no_txt.wav")
                        return()
                except Exception as e:
                      PRINT("\n-Trinity:Error:",str(e))
                      os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_read_link_request.wav")
                      return()
    else:
              os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_url_not_valid.wav")
              return()


def Google(tosearch,rnbr=50): #,tstmode = True):

    Exit = False
    SearchFallback = False
    google_result = []

    PRINT("\n-Trinity: tosearch:",tosearch)

    def readlist(reslist,nbrlimit):
         PRINT("\n-Trinity:nbrlimit:",nbrlimit)
         PRINT("\n-Trinity:len(reslist):",len(reslist))

         for n,result in enumerate(reslist[:nbrlimit]):

            try:

               title = result[0]
               description = result[1]
               url = result[2]
               print("\n-Résultat %s\nTitle:%s\nDescription:%s\nUrl:%s\n"%(n+1,title,description,url))

#                totts = "Catégories:%s Texte utilisateur synthétisé:%s Score:%s"%(hist_cats,hist_txt,hist_bingo)
#                Text_To_Speech(totts,stayawake=True,savehistory=False)

            except Exception as e:
                 PRINT("\n-Trinity:Error read list:",str(e))
                 continue

         Standing_By(self_launched=True)

    def readres(reslist,resnbr):

         PRINT("\n-Trinity:readres resnbr:%s",resnbr)
         result = reslist[resnbr+1]

         try:

               title = result[0]
               description = result[1]
               url = result[2]
               print("\n-Résultat %s\nTitle:%s\nDescription:%s\nUrl:%s\n"%(resnbr,title,description,url))

#                totts = "Catégories:%s Texte utilisateur synthétisé:%s Score:%s"%(hist_cats,hist_txt,hist_bingo)
#                Text_To_Speech(totts,stayawake=True,savehistory=False)

         except Exception as e:
               PRINT("\n-Trinity:Error read list:",str(e))

         while True:
             time.sleep(0.5)

             os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/question/search_history_cmd.wav")
             os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/question/do_i_read_link.wav")

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
                         os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")
                         return(False)
                   elif "oui" in txt and not "non" in txt:
                         os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")
                         return([description,title,url])




                   if len(txt)>0:
                      Question(txt)
                      Wait_for("question")
                   else:
                       score_sentiment.put(False)

                   opinion = score_sentiment.get()

                   if opinion == None:
                             os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/question/repeat.wav")
                   elif opinion == False:
                         os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")
                         return(False)
                   elif opinion == True:
                         os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")
                         return([description,title,url])


         

    def miniprompt(full):
        os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/prompt/2.wav")
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

         PRINT("\n-Trinity:minicmd:",txt_input)

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
                      PRINT("\n-Trinity:Found wait match cmd :",element)

              Standing_By()
              return(False)

         if ask_for_prompt:
              for element in prompt_request:
                  if element in txt_input.lower():
                      PRINT("\n-Trinity:Found prompt match cmd :",element)
              return(miniprompt(full))


         if ask_to_exit:
                   for element in exit_words:
                       if element in txt_input:
                            PRINT("\n-Trinity:Found exit match cmd :",element)
                   os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")
                   return(True)

         if ask_to_read_results:
                   for element in read_request:
                       if element in txt_input:
                            PRINT("\n-Trinity:Found read match cmd :",element)
                   chosen_one = False

                   lst_all = [" cent","100","complete","tout les","en entier","au total","en tout","combien","le reste"]
                   if any(element in txt_input.lower() for element in lst_all):
                         os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/google_full.wav")
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
                              os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/custom_google.wav")
                              readlist(full,chosen_one)
                              return(False)

                   for word,nbr in number_words.items():
                         if word in txt_input:
                              chosen_one = nbr
                              break

                   if chosen_one:
                        os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/printed_google.wav")
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
                       os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/printed_google.wav")
                       quit = readres(full,chosen_one)
                       return(quit)
                   else:
                      os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/errors/err_number_notfound.wav")
                      return(False)

         if  not ask_to_wait and not ask_to_exit and not ask_to_read_results and not ask_for_prompt:

           os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/history/err_cmd.wav")
           return(False)



    if (len(GOOGLE_KEY) != 0 and len(GOOGLE_ENGINE) != 0):

         PRINT("\n-Trinity:Using Custom Search Google Api.")

         maxpage = int(rnbr/10)
         for page in range(maxpage):
              start = page * 10 + 1
              try:
                  google_query = "https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s&start=%s"%(GOOGLE_KEY,GOOGLE_ENGINE,tosearch,start)

                  response = requests.get(google_query)

                  if response.status_code != 200:
                       SearchFallback = True
                       continue
                  else:
                       SearchFallback = False
                  data = response.json()

                  search_items = data.get("items")

                  for result in search_items:

                      title = result.get("title")

                      description = result.get("snippet")
                      if len(description) == 0:
                          description = result.get("htmlSnippet")
                      if len(description) == 0:
                          try:
                              description = search_item["pagemap"]["metatags"][0]["og:description"]
                          except :
                              description = "no description"
                      url = result.get("link")

                      google_result.append((title,description,url))



              except Exception as e:
                   os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_Google.wav")
                   PRINT("\n-Trinity:Custom search Error:",str(e))
                   SearchFallback = True

         if len(google_result) == 0:
                 PRINT("\n-Trinity:-Google() no result from google")
                 os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_no_result_google.wav")
                 return()



    if (len(GOOGLE_KEY) == 0 and len(GOOGLE_ENGINE) == 0) or SearchFallback == True:


         PRINT("\n-Trinity:Using module googlesearch.")
         try:
             google_query = googlesearch.search(tosearch,num_results=rnbr,lang="fr", advanced=True)


             for result in google_query:

                 title = result.title
                 description = result.description
                 url = result.url
                 google_result.append((title,description,url))

             if len(google_result) == 0:
                 PRINT("\n-Trinity:-Google() no result from google")
                 os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_no_result_google.wav")
                 return()

         except Exception as e:
              os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_Google.wav")
              PRINT("\n-Trinity:Googlesearch Error:",str(e))
              return()



    os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/ok/googleres.wav")


    full = google_result[:100]

    PRINT("\n-Trinity:full\n:",full)

    for n,result in enumerate(full[:20]):
          title = result[0]
          description = result[1]
          url = result[2]
          print("\n-Résultat %s\nTitle:%s\nDescription:%s\nUrl:%s"%(n+1,title,description,url))


    Standing_By(self_launched=True)

    while True:
         time.sleep(0.5)

         os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/question/search_history_cmds.wav")

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

    tosearch = tosearch.strip()
    PRINT("\n-Trinity:Dans la fonction Wikipedia.")
    PRINT("\n-Trinity:tosearch:",tosearch)
    PRINT("\n-Trinity:title:",Title)
    PRINT("\n-Trinity:FULL:",FULL)

    try:
        if Title:
            wiki_search = Title
        else:
            tosearch = "wikipedia " + tosearch
            wiki_search = GetTitleLink(tosearch,site="wikipedia")
          
        if not wiki_search:
            PRINT("\n-Trinity:Wikipedia no result from google")
            os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_no_result_wiki.wav")
            return()

        wikipedia.set_lang("fr")



        query_list = wikipedia.search(wiki_search)
#        query_list = [i.replace(" ","_") for i in query_list]

        if len(query_list) > 0:
            for r in query_list:
               PRINT("\n-Trinity:wiki reponse:",r)
        else:
            PRINT("\n-Trinity:no result from wikipedia")
            os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_no_result_wiki.wav")
            return()

 
        if len(query_list) >0:
            PRINT("\n-Trinity:Going to search : ",query_list[0])
            try:
                if not FULL:

                    os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/question/wikipedia.wav")


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
                                     os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ouinon/wiki_summary.wav")
                             if choice == "full":
                                     os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ouinon/wiki_full.wav")
                    elif opinion == False:
                         choice = "summary"
                         os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/wiki_summary.wav")
                    elif opinion == True:
                         choice = "full"
                         os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/wiki_full.wav")

                elif FULL == True:
                     choice = "full"
                     os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ouinon/wiki_full.wav")

                if choice == "summary":


                    try:
                        summary = wikipedia.summary(query_list[0])
                    except Exception as e:
                        try:
                            summary = wikipedia.summary(title=query_list[0],auto_suggest=True)
                        except Exception as e:
                            PRINT("\n-Trinity:Error:",str(e))
                            try:
                                summary = wikipedia.summary(title=query_list[0].replace(" ","").replace("_",""),auto_suggest=True)
                            except Exception as e:
                                PRINT("\n-Trinity:Error:",str(e))
                                os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_wiki.wav")
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
                            PRINT("\n-Trinity:Error:",str(e))
                            try:
                                page = wikipedia.page(title=query_list[0].replace(" ","").replace("_",""),auto_suggest=True)
                                content = page.content
                            except Exception as e:
                                PRINT("\n-Trinity:Error:",str(e))
                                os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_wiki.wav")
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
                         PRINT("\n-Trinity:no result from content wikipedia")
                         os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_no_result_wiki.wav")
                         return()
            except Exception as e:
                os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_wiki.wav")
                PRINT("Error:",str(e))
                return()

    except Exception as e:
       local_sounds/errors/err_func_wiki.wav
       os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/errors/err_func_wiki.wav")
       PRINT("\n-Trinity:Error:",str(e))
       return()



def Fallback_Prompt():
    PRINT("\n-Trinity:Dans la fonction Fallback_Prompt")
    os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/prompt/2.wav")
#    while True:
    if 1 == 1:
        user_input = input("\n-Trinity:Comment puis-je vous aider ?:")
        if len(str(user_input)) > 2:

              cmd = Commandes(user_input)
              if not cmd:
                  PRINT("\n-Trinity:pas de cmd")
                  return(To_Gpt(str(user_input)))
              else:
                    Go_Back_To_Sleep()


def Check_Transcript(transcripts,transcripts_confidence,words,words_confidence,Err_msg=""):


    avg_conf = 0
    bad_word = []
    bad_word_conf = []
    final_confidence = False
    
    PRINT("\n-Trinity:checktranscript")

    if len(Err_msg) > 0:
        if Err_msg.startswith("Speech_To_Text:"):
            os.system("aplay -q  %s"%SCRIPT_PATH+"/local_sounds/errors/err_stt.wav")
            Text_To_Speech(Err_msg,stayawake=True)
            os.system("aplay -q  %s"%SCRIPT_PATH+"/local_sounds/errors/err_prompt.wav")
            return(Fallback_Prompt())

    if len(transcripts) > 0:
        PRINT("\n-Trinity:transcripts:\n\n%s"%transcripts)
        PRINT("\n-Trinity:transcripts_confidence:%s"%transcripts_confidence)

        if len(words) > 0 and len(words_confidence) > 0:
            for w,wc in zip(words,words_confidence):
                    PRINT("\n-Trinity:confidence:%s word:%s"%(wc,w))
                    if wc < 0.6:
                          PRINT("\n-Trinity:That word has bad confidence : %s %s"%(w,wc))
                          bad_word_conf.append(w)
            avg_conf = sum(words_confidence)/len(words_confidence)
            PRINT("\n-Trinity:Average words confidence :%s"%avg_conf)


        if transcripts_confidence == 0.0:
           #TODO
           #Google didnt care to give us a level of confidence...
           PRINT("\n-Trinity:Transcript no confidence level\n.")
           pass
        elif transcripts_confidence < 0.7:
           PRINT("\n-Trinity:Transcript has bad confidence\n.")
           final_confidence = False
        else:
           final_confidence = True
           PRINT("\n-Trinity:Transcript seems ok\n.")

        return(transcripts.replace("\\",""),final_confidence)
        
    else:
      os.system("aplay -q  %s"%SCRIPT_PATH+"/local_sounds/errors/err_no_respons.wav")
      #      Go_Back_To_Sleep()
      return("",False)



def Question(txt):

    PRINT("\n-Trinity:Dans la fonction Question")
    score = 0
    try:

        client = language_v1.LanguageServiceClient()
        document = language_v1.Document(content=txt, language="fr",type_=language_v1.Document.Type.PLAIN_TEXT)
        sentiment = client.analyze_sentiment(request={'document': document}).document_sentiment

        PRINT("\n-Trinity:Text: {}".format(txt))
        PRINT("\n-Trinity:Sentiment: {}, {}".format(sentiment.score, sentiment.magnitude))

        PRINT("\n\n\n-Trinity:Sentimentfull:\n%s"%sentiment)

        score = sentiment.score
    except Exception as e:
        PRINT("\n-Trinity:Error :%s"%str(e))

    if score > -0.15 and score < 0.15:
        PRINT("\n-Trinity:Score is None")
        score_sentiment.put(None)
    elif score < -0.15:
        PRINT("\n-Trinity:Score is False")
        score_sentiment.put(False)
    elif score > 0.15:
        PRINT("\n-Trinity:Score is True")
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
              os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")
              return(Fallback_Prompt())
          else:
              os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")
              Go_Back_To_Sleep()
       else:
               os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")

               cmd = Commandes(txt)
               if cmd:
                  if cmd == "prompt":
                      return(Fallback_Prompt())
                  elif cmd == "random":
                       rnd = str(random.randint(1,2))
                       ouinon = SCRIPT_PATH+"/local_sounds/ouinon/"+rnd+".wav"
                       os.system("aplay -q %s"%ouinon)
               else:
                     return(To_Gpt(txt))
    else:

               os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")
               #go_to_function.put("Speech_To_Text")
               cmd = Commandes(txt)
               if cmd:
                  if cmd == "prompt":
                      return(Fallback_Prompt())
               else:
                     return(To_Gpt(txt))

def Bad_Stt(txt):
    PRINT("\n-Trinity:Dans la fonction Bad_Stt")
    fname = "/tmp/last_bad_stt.wav"
    try:

            client = tts.TextToSpeechClient()
            audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

            text_input = tts.SynthesisInput(text=txt)
            voice_params = tts.VoiceSelectionParams(language_code="fr-FR", name="fr-FR-Neural2-A")

            response = client.synthesize_speech(input=text_input,voice=voice_params,audio_config=audio_config)
            audio_response = response.audio_content


            try:
                with open(SCRIPT_PATH+fname, "wb") as out:
                     out.write(audio_response)
            except Exception as e:
                PRINT("\n-Trinity:Error:",str(e))
                sys.exit()


    except Exception as e:
            PRINT("\n-Trinity:Error:%s"%str(e))
            Err = True
            try:
                os.system('pico2wave -l fr-FR -w %s "%s"'%(SCRIPT_PATH+fname,txt))
            except Exception as e:
                PRINT("\n-Trinity:Error:",str(e))
                sys.exit()

    os.system("aplay -q %s"%SCRIPT_PATH+fname)



def Bad_Confidence(txt):
    PRINT("\n-Trinity:Dans la fonction Bad_Confidence")

    Orig_sentence = txt

    PRINT("\n-Trinity:txt:",txt)
    PRINT("\n-Trinity:Orig_sentence:",Orig_sentence)

    rnd = str(random.randint(1,10))
    bad_sound = SCRIPT_PATH+"/local_sounds/badconf/"+rnd+".wav"
    os.system("aplay -q %s"%bad_sound)

    Bad_Stt(txt)

    question_sound = SCRIPT_PATH+"/local_sounds/question/1.wav"
    os.system("aplay -q %s"%question_sound)

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
                     os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")
                     return(To_Gpt(Orig_sentence))
                 else:
                     os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/forgot/1.wav")
                     choice = random.choice(["repeat","prompt"])
                     if choice == "repeat":
                         os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/repeat/1.wav")
                         return(Trinity("Repeat"))
                     if choice == "prompt":
                         os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/prompt/1.wav")
                         return(Fallback_Prompt())


             if choice == "repeat":
                 os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/repeat/1.wav")
                 return(Trinity("Repeat"))
             if choice == "prompt":
                 os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/prompt/1.wav")
                 return(Fallback_Prompt())
    elif opinion == False:
             choice = random.choice(["repeat","prompt"])
             if choice == "repeat":
                 os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/repeat/1.wav")
                 return(Trinity("Repeat"))
             if choice == "prompt":
                 os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/prompt/1.wav")
                 return(Fallback_Prompt())
    elif opinion == True:
                 os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")
                 if len(Orig_sentence) > 0:
                     return(To_Gpt(Orig_sentence))
                 else:
                     os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/forgot/1.wav")
                     choice = random.choice(["repeat","prompt"])
                     if choice == "repeat":
                         os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/repeat/1.wav")
                         return(Trinity("Repeat"))
                     if choice == "prompt":
                         os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/prompt/1.wav")
                         return(Fallback_Prompt())



def Split_Text(txt):


    PRINT("\n-Trinity:Dans la fonction Split_text")
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
    PRINT("\n-Trinity:Dans la fonction Speech_To_Text")

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
        PRINT("\n-Trinity:Error:%s"%str(e))
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
            PRINT("\n-Trinity:Error:%s"%str(e))

    if len(transcripts) > 0:
         print("\n-Trinity:User said:",transcripts)

    return(transcripts,transcripts_confidence,words,words_confidence,Err_msg)




def Text_To_Speech(txtinput,stayawake=False,savehistory=True):


    def Resample(file):
        try:
            to_rename = SCRIPT_PATH + "/tmp/resampled.wav"
            sample = sox.Transformer()
            sample.set_output_format(rate=24000)
            sample.build(file,to_rename)
            print("\n-Trinity:%s resampled to 24000."%file)
            os.rename(to_rename,file)
            print("\n-Trinity:%s saved."%file)
            return(True)
        except Exception as e:
            print("\n-Trinity:Error:Resample:",str(e))
            return(False)


    PRINT("\n-Trinity:Dans la fonction Text_To_Speech")


    PRINT("\n-Trinity:len(txtinput):",len(txtinput))

    print("\n-Trinity:\n\n%s\n\n"%txtinput)

    parsed_response = parse_response(str(txtinput))
    PRINT("\n-After Parse:\n%s\n\n"%parsed_response)

#    err_list = []#TODO
    txt_list = Split_Text(parsed_response)
    ln_txt_list = len(txt_list)
    wav_list = []
    to_sox = []

    final_wav = SCRIPT_PATH + "/tmp/current_answer.wav"


    Move_To_Error_Folder = False

    Err_Tts = False
    Err_Skip = False
    Err_Pysox = False
    Err_Sample = False
    Err_Concatenation = False

    for n,txt in enumerate(txt_list):
        time.sleep(0.5)
        leadn = str(n).zfill(4)
#        if len(txt_list) > 1:
#                fname = "/tmp/answer"+str(leadn)+".wav"
#        else:
#                fname = "/tmp/current_answer.wav"
        fname = "/tmp/answer"+str(leadn)+".wav"
        Err_cnt = 0
        while True:
             Retry = False
             try:

                 client = tts.TextToSpeechClient()
                 audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

                 text_input = tts.SynthesisInput(text=txt)
                 voice_params = tts.VoiceSelectionParams(language_code="fr-FR", name="fr-FR-Neural2-A")

                 response = client.synthesize_speech(input=text_input,voice=voice_params,audio_config=audio_config)
                 audio_response = response.audio_content


                 try:
                     with open(SCRIPT_PATH+fname, "wb") as out:
                          out.write(audio_response)
                     wav_list.append(SCRIPT_PATH+fname)
                 except Exception as e:
                     PRINT("\n-Trinity:Error:",str(e)) #TODO
#                     err_list.append("Err_cnt:%s write(gtss)file:%s err:%s"%(str(Err_cnt),SCRIPT_PATH+fname,str(e)))
                     Err_cnt +=1
                     Retry = True

             except Exception as e:
                 PRINT("\n-Trinity:Error:%s"%str(e))
                 Err_cnt += 1
                 Retry = True

             if Err_cnt == 2:
                 Err_Tts = True
                 Err_cnt = 0
                 try:
                     os.system('pico2wave -l fr-FR -w %s "%s"'%(SCRIPT_PATH+fname,txt))
                     #RESAMPLE 16000 to 24000
                     wav_list.append(SCRIPT_PATH+fname)
                     Retry = False
                 except Exception as e:
                     PRINT("\n-Trinity:Error:",str(e))
                     Retry = False
                     Err_Skip = True

             if not Retry:
                break
             else:
                time.sleep(0.5)

    for f in wav_list:
        if os.path.exists(f):
              try:
                   sample_rate = int(sox.file_info.sample_rate(f))
                   if sample_rate != 24000:
                      resampled = Resample(f)
                      if resampled:
                         to_sox.append(f)
                      else:
                         Err_Sample = True
                   else:
                        to_sox.append(f)
              except Exception as e:
                 print("\n-Trinity:Error:",str(e))
                 Err_Sample = True
        else:
            print("\n-Trinity:Error:Le fichier %s n'existe pas.",str(f))
            Err_Skip = True


#    print("to_sox:",to_sox)

    if len(to_sox) > 1:
         try:
              cbn = sox.Combiner()
              cbn.convert(samplerate=24000, n_channels=1)
              try:
                  cbn.set_input_format(file_type=['wav' for i in to_sox])
              except Exception as e:
                  print("\n-Trinity:Error:",str(e))
              cbn.build(to_sox,final_wav, 'concatenate')
         except Exception as e:
              print("\n-Trinity:Error:Concatenation:",str(e))
              Err_Concatenation = True
    elif len(to_sox) == 1:
             try:
                 sample = sox.Transformer()
                 sample.set_output_format(rate=24000)
                 sample.build(to_sox[0],final_wav)
             except Exception as e:
                 PRINT("\n-Trinity:to_sox:\n%s"%to_sox[0])
                 print("\n-Trinity:Error:pysox:",str(e))
                 Err_Pysox = True


    if Err_Tts:
        os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/errors/err_tts.wav")
    if Err_Skip:
        os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/errors/err_skip_sox.wav")
        Move_To_Error_Folder = True
    if Err_Pysox:
        os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/errors/err_answer_sox.wav")
        Move_To_Error_Folder = True
    if Err_Sample:
        os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/errors/err_sample_sox.wav")
        Move_To_Error_Folder = True
    if Err_Concatenation:
        os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/errors/err_conc_sox.wav")
        Move_To_Error_Folder = True


    tmp_folder = str(SCRIPT_PATH+"/tmp/").replace("//","/")
    err_folder = str(SAVED_ANSWER+"/saved_error/").replace("//","/")

    to_skip = ["current_answer.wav","last_bad_stt.wav"]

    wav_files = [f for f in os.listdir(tmp_folder) if f.endswith('.wav') and f not in to_skip]



    if Move_To_Error_Folder and len(to_sox)>0:

       while True:
              characters = string.ascii_letters + string.digits
              rnd = ''.join(random.choice(characters) for _ in range(5))
              rnd_folder = err_folder+rnd
              if not os.path.exists(rnd_folder):
                  try:
                     os.makedirs(rnd_folder)
                     err_folder = rnd_folder
                     break
                  except Exception as e:
                      print("\n-Trinity:Error:os.makedirs(rnd_folder):%s"%str(e))
                      break

       PRINT("\n-Trinity:Déplacements des fichiers wav temporaire vers %s"%err_folder)

       err_move = False
       for w in wav_files:
           try:
              move(tmp_folder+str(w), err_folder)
           except Exception as e:
              print("\n-Trinity:Error:Move:",str(e))
              err_move = True

       if err_move:
           os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/errors/err_while_moving_to_err.wav")
       else:
           os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/errors/err_move_to_err.wav")
    else:
       PRINT("\n-Trinity:Effacement des fichiers wav temporaire de %s"%tmp_folder)

       err_del = False
       for w in wav_files:
           try:
              os.remove(tmp_folder+str(w))
           except Exception as e:
              print("\n-Trinity:Error:Move:",str(e))
              err_del = True

       if err_del:
          os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/errors/err_del_wav.wav")

    if len(to_sox) > 0:

        if Err_Concatenation:
            return(Play_Response(stay_awake=stayawake,save_history=savehistory,answer_txt=txtinput))

        else:
            return(Play_Response(audio_response=final_wav,stay_awake=stayawake,save_history=savehistory,answer_txt=txtinput))

    else:

       os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/errors/err_no_audio_sox.wav")

       if len(txtinput) > 0:

            os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/errors/err_no_audio_but_txt_sox.wav")
            print("\n\n-Trinity:Réponse:\n",txtinput)

            return(Play_Response(stay_awake=stayawake,save_history=savehistory,answer_txt=txtinput))
       else:
           return(Play_Response(stay_awake=stayawake,save_history=False))

#    return(Play_Response(audio_response=final_wav,stay_awake=stayawake,save_history=savehistory,answer_txt=txtinput))




def Play_Response(audio_response=None,stay_awake=False,save_history=True,answer_txt=None):
    PRINT("\n-Trinity:Dans la fonction Play_Response")

    if audio_response:
        os.system("aplay -q  "+audio_response)

    if save_history:
       if audio_response:
           Save_History(answer_txt)
       else:
           Save_History(answer_txt,no_audio=True)

    if not stay_awake:
        Go_Back_To_Sleep(True)

def dbg_queue():

            PRINT("\n-Trinity:sleep.empty:%s"%cancel_operation.empty())
            PRINT("\n-Trinity:start.empty:%s"%wake_me_up.empty())
            PRINT("\n-Trinity:chunks.empty:%s"%chunks.empty())
            PRINT("\n-Trinity:audio_datas:%s"%audio_datas.empty())

def Start_Thread_Record():
    PRINT("\n-Trinity:start thread rec")
    record_on.put(True)

    RQ = Thread(target=Record_Query)
    RQ.start()
    CS = Thread(target=Check_Silence)
    CS.start()

def Go_Back_To_Sleep(go_trinity=True):

     global Current_Category

     PRINT("\n\n------\n-Trinity:Remise en veille-----\n\n")



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
         PRINT("\n-Trinity:Retour vers trinity()\n")
         return(Trinity("WakeMe"))
     else:
         return()

def Wait_for(action):
    PRINT("\n-Trinity:wait for %s"%action)

    while cancel_operation.empty():

       if action == "audio":
            if not audio_datas.empty():
                break

       if action == "question":
            if not score_sentiment.empty():
                break



    if not cancel_operation.empty():
           PRINT("\n-Trinity:Operation %s cancelled."%action)
           return(False)
    else:
           PRINT("\n-Trinity:Operation %s finished."%action)
           return(True)



#       time.sleep(1)


def similar(txt1,txt2):
    PRINT("\n-Trinity:txt1:",txt1)
    PRINT("\n-Trinity:txt2:",txt2)
    similarity = SequenceMatcher(None,txt1,txt2).ratio()
    PRINT("\n-Trinity:Similarity : ",similarity)
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
    PRINT("\n-Trinity:Dans la fonction Standing_By")

#    word_key = SCRIPT_PATH+"/models/Trinity_en_linux_v2_2_0.ppn"
    word_key = SCRIPT_PATH+"/models/trinity_fr_raspberry-pi_v3_0_0.ppn"
    pvfr = SCRIPT_PATH+"/models/porcupine_params_fr.pv"
    porcupine = None
    keyword_index = None

    if self_launched:
        os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/wait/selfwait.wav")

    else:
        os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/history/wait.wav")


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
        print("\n-Trinity:En attente d'instruction...")

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index == 0:
                PRINT("\n-Trinity:keyword_index:",keyword_index)
                rnd = str(random.randint(1,15))
                wake_sound = SCRIPT_PATH+"/local_sounds/wakesounds/"+rnd+".wav"
                os.system("aplay -q %s"%wake_sound)
                break

    finally:
        PRINT("\n-Trinity:Awake.")
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()






def Isolate_Search_Request(txt,triggers):


    PRINT("\n-Trinity:Isolate_Search_Request():%s"%txt)


    def check_artifact(to_check,original):
       originalst = original.lower().split(" ")
       to_check_lst = to_check.split(" ")
       trigger_words = []
       artifacts = []
       fixed = []

       for trigger in triggers:
           for word in trigger.split(" "):
               if word not in trigger_words:
                     trigger_words.append(word)

       for word in to_check_lst:
           iwasthere = False
           for orig_word in originalst:
               if orig_word == word:
                  iwasthere = True

           if not iwasthere:
               artifacts.append(word)

       for bad_word in artifacts:
          PRINT("\n-Trinity:check_artifact:artifact:%s"%word)
          for orig_word in originalst:
              if orig_word not in trigger_words:
                    if orig_word in bad_word:
                        fixed.append(orig_word)

       if fixed:
          fixed = " ".join(fixed)
          PRINT("\n-Trinity:check_artifact:fixed:%s"%fixed)
          return(fixed)
       else:
          return(to_check)

    def clean(to_clean):
         abc = """ &abcdefghijklmnopqrstuvwxyz0123456789-_"'/+."""
         cleaned = ""
         while True:
              if to_clean.endswith(" "):
                 to_clean = to_clean[:-1]
                 continue
              elif to_clean.startswith(" "):
                 to_clean = to_clean[1:]
                 continue
              elif "  " in to_clean:
                 to_clean = to_clean.replace("  "," ")
                 continue
              else:
                 break

         for c in to_clean: #??
             if c in abc:
                 cleaned += c

         return(cleaned)

    def remove(to_clean,remove_lst):

          for to_rm in remove_lst:
              pos = 0
              bucket = ""
              to_rm_lst = []
              while True:
                  if to_rm[pos] != "*":
                      bucket += to_rm[pos]
                  else:
                      if pos > 0:
                          if to_rm[pos-1] not in (" ","*"):
                             bucket += " "
                             to_rm_lst.append(bucket)
                             bucket = ""
                          else:
                             to_rm_lst.append(bucket)
                             bucket = ""
                      else:
                             bucket += " "
                             to_rm_lst.append(bucket)
                             bucket = ""
                  pos += 1
                  if pos >= len(to_rm):
                             to_rm_lst.append(bucket)
                             break
              to_rm_lst = [rm.replace("  "," ") for rm in to_rm_lst]

#              print("\nto_rm_lst:")

              for rm in to_rm_lst:
#                  print("'%s'"%rm)
#                  to_clean = to_clean.replace(rm," ")
#                  to_clean = " ".join([word for word in to_clean.split() if word != rm])
                  pos_rm = to_clean.find(rm)
                  while pos_rm != -1:
                        to_clean = to_clean[:pos_rm] + to_clean[pos_rm + len(rm):]
                        pos_rm = to_clean.find(rm)

          return(clean(to_clean))


    filter = ["s'il te plait","si te plait","sil te plait","merci"]

    orig_txt = txt

    txt = unidecode(txt.lower())

    for f in filter:
        txt = txt.replace(f," ")

    txt = clean(txt)

    txt = remove(txt,action_words)

    txt = remove(txt,triggers)

    txt = check_artifact(txt,orig_txt)

    PRINT("\n-Trinity:Isolate_Search_Request():output:%s"%txt)
    return(txt)


def Reducto(txt):
    if len(txt) > 300:
         txt = txt[:300]+"(...)"
    return(txt)


def Show_History():
    PRINT("\n-Trinity:Show_History()")
    if len(History_List) == 0:
        os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/errors/err_no_history.wav")
        return()

    history_sort_asc = sorted(History_List,key=lambda x: x[4])
    history_sort_dsc =  history_sort_asc[::-1]

    os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/history/show_history.wav")
    for n,args in enumerate(history_sort_asc):

         hist_file = args[0]
         hist_cats = args[1]
         hist_txt = args[2]
         hist_answer = Reducto(args[3])
         hist_epok = args[4]
         hist_tstamp = args[5]
         hist_wav = args[6]
         catres = "\n\n==Résultat %s== Catégories:"%str(n+1)
         txtres = "\n==Résultat %s== Question synthétisé:\n"%str(n+1)
         ansres = "\n\n==Résultat %s== Réponse:\n\n"%str(n+1) 
         datres = "\n\n==Résultat %s== Date:"%str(n+1)
         wavres = "\n==Résultat %s== Wav:"%str(n+1)

         print("%s%s%s%s%s%s%s%s"%(catres,hist_cats,txtres,hist_txt,ansres,hist_answer,datres,hist_tstamp))


def Search_History(tosearch):
    Exit = False

    PRINT("\n-Trinity:Dans la fonction SearchHistory tosearch %s in history."%tosearch)


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

         PRINT("\n-Trinity:toplay:\n %s \n"%toplay)

         nbrtoplay = len(toplay)
         os.system("aplay -q %slocal_sounds/history/playlist_%s.wav"%(SCRIPT_PATH,str(nbrtoplay)))

         for n,wavfile in enumerate(toplay):
             os.system("aplay -q %slocal_sounds/history/play_%s.wav"%(SCRIPT_PATH,str(n+1)))
             if wavfile.endswith(".wav"):
                  os.system("aplay -q %s"%wavfile)
             else:
                  hist_file = args[0]
                  hist_cats = args[1]
                  hist_txt = args[2]
                  hist_answer = args[3]
                  hist_epok = args[4]
                  hist_tstamp = args[5]
                  hist_wav = args[6]
                  hist_bingo = args[7]
                  os.system("aplay -q %s"%hist_wav)

    def readlist(toread):
         PRINT("\n-Trinity: toread:",toread)
         for args in toread:

            hist_file = args[0]
            hist_cats = args[1]
            hist_txt = args[2]
            hist_answer = args[3]
            hist_epok = args[4]
            hist_tstamp = args[5]
            hist_wav = args[6]
            hist_bingo = args[7]

            totts = "Catégories:%s Texte utilisateur synthétisé:%s Date:%s Score:%s"%(hist_cats,hist_txt,hist_tstamp,hist_bingo)

            Text_To_Speech(totts,stayawake=True,savehistory=False)



    def minicmd(txt_input,top5,full):
         global Exit
         txt_input = unidecode(txt_input.lower())

         PRINT("\n-Trinity:minicmd:",txt_input)

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
                      PRINT("\n-Trinity:Found wait match cmd :",element)

              Standing_By()
              return()

         if ask_for_prompt:
              for element in prompt_request:
                  if element in txt_input.lower():
                      PRINT("\n-Trinity:Found prompt match cmd :",element)
              return(miniprompt(top5,full))


         if ask_to_search:
              if "historique" in txt_input.lower() and not "resultat" in txt_input.lower():
                   for element in search_history_request:
                       if element in txt_input:
                            txt_input = txt_input.replace(element," ") 
                            PRINT("\n-Trinity:Found search match cmd :",element)
                   Exit = True
                   return(Search_History(txt_input))
          
         if ask_to_exit:
                   for element in exit_words:
                       if element in txt_input:
                            PRINT("\n-Trinity:Found exit match cmd :",element)
                   os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/ok/1.wav")
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

                                 args = [a for a in chosen_line]

                                 hist_file = args[0]
                                 hist_cats = args[1]
                                 hist_txt = args[2]
                                 hist_answer = args[3]
                                 hist_epok = args[4]
                                 hist_tstamp = args[5]
                                 hist_wav = args[6]
                                 hist_bingo = args[7]

                                 os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/history/choose_%s.wav"%(str(rnd_nbr + 1)))

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
                            PRINT("\n-Trinity:Found read match cmd :",element)

                   if ("combien" and "tout" in txt_input) or ("combien" and "total" in txt_input):

                           total_res = len(full)
                           answer = "Il y a %s résultats en tout correspondant à votre recherche . Les voici:"%total_res
                           Text_To_Speech(answer,stayawake=True,savehistory=False)
                           
                           for n,args in enumerate(full) :
                               hist_file = args[0]
                               hist_cats = args[1]
                               hist_txt = args[2]
                               hist_answer = Reducto(args[3])
                               hist_epok = args[4]
                               hist_tstamp = args[5]
                               hist_wav = args[6]
                               hist_bingo = args[7]
                               catres = "\n\n==Résultat %s== Catégories:"%str(n+1)
                               txtres = "\n==Résultat %s== Question synthétisé:\n"%str(n+1)
                               ansres = "\n\n==Résultat %s== Réponse:\n\n"%str(n+1) 
                               datres = "\n\n==Résultat %s== Date:"%str(n+1)
                               wavres = "\n==Résultat %s== Wav:"%str(n+1)
                               binres = "\n==Résultat %s== Score:"%str(n+1)

                               print("%s%s%s%s%s%s%s%s%s%s%s%s"%(catres,hist_cats,txtres,hist_txt,ansres,hist_answer,datres,hist_tstamp,wavres,hist_wav,binres,hist_bingo))


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
                                 args = [a for a in chosen_line]
                                 hist_file = args[0]
                                 hist_cats = args[1]
                                 hist_txt = args[2]
                                 hist_answer = Reducto(args[3])
                                 hist_epok = args[4]
                                 hist_tstamp = args[5]
                                 hist_wav = args[6]
                                 hist_bingo = args[7]





                                 res_str = "\n-(Résultat numéro %s)\n    \n-Catégories:\n%s\n    \n-Texte utilisateur synthétisé:\n%s\n     \n-Réponse:\n%s\n   -Date:%s\n    Score:%s"%(str(n+1),hist_cats,hist_txt,hist_answer,hist_tstamp,hist_bingo)

                                 os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/history/choose_%s.wav"%(str(rnd_nbr + 1)))
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
           
           os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/history/err_cmd.wav")
           return()

    def miniprompt(top5,full):
        os.system("aplay -q %s"%SCRIPT_PATH+"/local_sounds/prompt/2.wav")
        user_input = input("Que voulez vous faire avec l'historique? :")
        if len(str(user_input)) > 2:

              Exit = minicmd(user_input,top5,full)
              if Exit:
                 return(True)
        else:
              miniprompt(top5,full)

####


    MatchResults =[]

    PRINT("\n-Trinity:Search_History:%s"%tosearch)
    for args in History_List:

         hist_file = args[0]
         hist_cats = args[1]
         hist_txt = args[2]
         hist_answer = args[3]
         hist_epok = args[4]
         hist_tstamp = args[5]
         hist_wav = args[6]


         bingoat = 0
         if " " in tosearch:
              for n,word in enumerate(tosearch.split(" ")):

                  if n == 0:
                      word = "%s "%word
                  elif n == len(tosearch.split(" "))-1:
                      word = " %s"%word
                  else:
                      word = " %s "%word

                  if word in hist_txt.lower():
                          PRINT("\n-Trinity:Search_History:found partial result in hist_txt:[%s]"%word)
                          bingoat += 1
                  if word in hist_answer.lower():
                          PRINT("\n-Trinity:Search_History:found partial result in hist_answer:[%s]"%word)
                          bingoat += 1

              if tosearch in hist_txt.lower():
                          PRINT("\n-Trinity:Search_History:full match in hist_txt:[%s]"%tosearch)
                          bingoat += 5
              if tosearch in hist_answer.lower():
                          PRINT("\n-Trinity:Search_History:full match in hist_txt:[%s]"%tosearch)
                          bingoat += 5
         else:
              if tosearch in hist_txt.lower():
                          PRINT("\n-Trinity:Search_History:full match in hist_txt:[%s]"%tosearch)
                          bingoat += 1
              if tosearch in hist_answer.lower():
                          PRINT("\n-Trinity:Search_History:full match in hist_txt:[%s]"%tosearch)
                          bingoat += 1

         if bingoat > 0:
                MatchResults.append((hist_file,hist_cats,hist_txt,hist_answer,hist_epok,hist_tstamp,hist_wav,bingoat))

    if len(MatchResults) > 0:
        SortedMatched = sorted(MatchResults,key=lambda x: x[7], reverse=True)
        MatchedNbr = len(SortedMatched)
    else:
        SortedMatched = []
        MatchedNbr = 0


    if MatchedNbr > 5:
         MatchedNbr = 5

    if len(SortedMatched) == 1:
         os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/history/found_one.wav")
    elif len(SortedMatched) == 2:
         os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/history/found_two.wav")
    elif len(SortedMatched) == 3:
         os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/history/found_three.wav")
    elif len(SortedMatched) == 4:
         os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/history/found_four.wav")
    elif len(SortedMatched) >= 5:
         os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/history/found_five.wav")
    else:
        os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/history/no_result.wav")
        return()

    TopFive = SortedMatched[:MatchedNbr]

    for n,args in enumerate(TopFive):
         hist_file = args[0]
         hist_cats = args[1]
         hist_txt = args[2]
         hist_answer = Reducto(args[3])
         hist_epok = args[4]
         hist_tstamp = args[5]
         hist_wav = args[6]
         hist_bingo = args[7]
         catres = "\n\n==Résultat %s== Catégories:"%str(n+1)
         txtres = "\n==Résultat %s== Question synthétisé:\n"%str(n+1)
         ansres = "\n\n==Résultat %s== Réponse:\n\n"%str(n+1) 
         datres = "\n\n==Résultat %s== Date:"%str(n+1)
         wavres = "\n==Résultat %s== Wav:"%str(n+1)
         binres = "\n==Résultat %s== Score:"%str(n+1)

         print("%s%s%s%s%s%s%s%s%s%s%s%s"%(catres,hist_cats,txtres,hist_txt,ansres,hist_answer,datres,hist_tstamp,wavres,hist_wav,binres,hist_bingo))


    Standing_By(self_launched=True)

    while True:
         time.sleep(0.5)

         if len(TopFive) >1:
             os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/question/search_history_cmds.wav")
         else:
             os.system("aplay -q  "+SCRIPT_PATH+"local_sounds/question/search_history_cmd.wav")

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

def Save_History(answer,no_audio=False):

   global History_List

   PRINT("\n-Trinity:Dans la fonction History")

   if not answer:
        PRINT("\n-Trinity:No answer saved exiting History")
        return()

   if last_sentence.empty():
        PRINT("\n-Trinity:No last_ sentence saved exiting History")
        return()

   txt = last_sentence.get()

   PRINT("\n-Trinity:last sentence:",txt)


   if len(Current_Category) == 0:
       Classify(txt)

   Cat_File = str(Current_Category[0]).replace("-",".").replace("&","and").replace(",",".").replace(")",".").replace("(",".")

   if Cat_File.startswith("."):
        Cat_File = Cat_File[1:]

   Cat_List = ".".join(Current_Category)
   if Cat_List.startswith("."):
      Cat_List = Cat_List[1:] 

   Lemmatizer = preprocess(txt)

   PRINT("\n-Trinity:lemmatized last sentence:",Lemmatizer)

   if no_audio:

       new_wav = SCRIPT_PATH + "/local_sounds/errors/err_no_audio_saved.wav"
       
   else:

        rnd_name = str(''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))) + ".wav"

        new_wav = SAVED_ANSWER + rnd_name
        current_wav = SCRIPT_PATH + "/tmp/current_answer.wav"

        os.system("cp %s %s"%(current_wav,new_wav))

   tformat = "%Y-%m-%d %H:%M:%S"
   now = datetime.now()

   hist_epok = now.timestamp()

   hist_tstamp = time.strftime(tformat, time.localtime(hist_epok))

#  hist_file,hist_cats,hist_txt,hist_answer,hist_epok,hist_tstamp,hist_wav

   try:
        with open(SCRIPT_PATH+"/history/"+Cat_File, "a+", newline="") as csvfile:
             fieldnames = ["hist_file","hist_cats", "hist_txt","hist_answer","hist_epok","hist_tstamp","hist_wav"]
             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

             if csvfile.tell() == 0:
                 writer.writeheader()

             writer.writerow({
                  "hist_file": Cat_File,
                  "hist_cats": Cat_List,
                  "hist_txt": Lemmatizer,
                  "hist_answer": answer,
                  "hist_epok": hist_epok,
                  "hist_tstamp": hist_tstamp,
                  "hist_wav": new_wav

                  })

             PRINT("\n-Trinity:wrote history to:%s"%(SCRIPT_PATH+"/history/"+Cat_File))
             History_List.append( (Cat_File,Cat_List,Lemmatizer,answer,hist_epok,hist_tstamp,new_wav) )
             PRINT("\n-Trinity:History_List updated:%s"%len(History_List))

   except Exception as e:
       print("\n-Trinity:Save_History:Error:%s"%str(e))

def Check_History(question):


   PRINT("\n-Trinity:Dans la fonction Check_History")


   PRINT("\n-Trinity:question:",question)

   lemmatized = preprocess(question)

   if len(Current_Category) == 0:
       Classify(question)
   else:
       Categories = Current_Category

   Cat_File = str(Current_Category[0]).replace("-",".").replace("&","and").replace(",",".").replace(")",".").replace("(",".")
   if Cat_File.startswith("."):
        Cat_File = Cat_File[1:]

   Joined_Cat = ".".join(Current_Category)
   if Joined_Cat.startswith("."):
      Joined_Cat = Joined_Cat[1:]

   Best_Score = []
   Best_Txt = []
   Best_Answer = []
   Best_Wav = []

   for args in History_List:
  
         hist_file = args[0]
         hist_cats = args[1]
         hist_txt = args[2]
         hist_answer = args[3]
         hist_epok = args[4]
         hist_tstamp = args[5]
         hist_wav = args[6]

         if Cat_File == hist_file:
               if hist_cats == Joined_Cat:
                        score = similar(lemmatized,hist_txt)
                        if "wikipedia" in hist_txt:
                            if score > 0.85:

                                PRINT("\n-Trinity:hist_cats:",hist_cats)
                                PRINT("\n-Trinity:hist_txt:",hist_txt)
                                PRINT("\n-Trinity:hist_answer:",hist_answer)
                                PRINT("\n-Trinity:hist_wav:",hist_wav)
                                PRINT("\n-Trinity:Score:",score)


                                Best_Score.append(score)
                                Best_Txt.append(hist_txt)
                                Best_Answer(hist_answer)
                                Best_Wav.append(hist_wav)

                        else:
                            if score > 0.5:
                                PRINT("\n-Trinity:hist_cats:",hist_cats)
                                PRINT("\n-Trinity:hist_txt:",hist_txt)
                                PRINT("\n-Trinity:hist_answer:",hist_answer)
                                PRINT("\n-Trinity:hist_wav:",hist_wav)
                                PRINT("\n-Trinity:Score:",score)
                                Best_Score.append(score)
                                Best_Txt.append(hist_txt)
                                Best_Answer(hist_answer)
                                Best_Wav.append(hist_wav)

   final_score = 0
   final_wav = ""
   for s in Best_Score:
           if s > final_score:
                final_score = s

   for s,t,w in zip(Best_Score,Best_Txt,Best_Answer,Best_Wav):
            if s == final_score:
                PRINT("\n-Trinity:Best matches :",t)
                final_wav = w

   if len(final_wav) > 0:

       os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/already/1.wav")
       os.system("aplay -q %s"%final_wav)
       os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/question/amigood.wav")

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
               os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/notok/1.wav")
               return(False)
           elif opinion == False:
               os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/notok/1.wav")
               return(False)
           else:
               os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/ok/1.wav")
               return(True)
   else:
        return(False)




def Classify(text_content):

    global Current_Category
    PRINT("\n-Trinity:Dans la fonction Classify")
    
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
         PRINT("\n-Trinity:Error:",str(e))
         categories = ["nocat"]

    if len(categories) == 0 :
         categories = ["nocat"]

    Current_Category = categories
    PRINT("\n-Trinity:Current_Category:\n",Current_Category)

    return()


def Trinity(fname = "WakeMe"):

        PRINT("\n-Trinity:")
        PRINT("\n-Trinity:fname:",fname)

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
                                  To_Gpt(txt)

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
                PRINT("\n-Trinity:TOUCHDOWN\n")
                return(Go_Back_To_Sleep())




def GetConf():
   global DEBUG
   global XCB_ERROR_FIX
   global SAVED_ANSWER
   global GPT4FREE_SERVERS_STATUS
   global GPT4FREE_SERVERS_AUTH
   global CHECK_UPDATE

   options = ["DEBUG","XCB_ERROR_FIX","SAVED_ANSWER","GPT4FREE_SERVERS_STATUS","GPT4FREE_SERVERS_AUTH","CHECK_UPDATE"]
   folder = False
   conf = False

   if os.path.exists(SCRIPT_PATH+"/datas/conf.trinity"):
           with open(SCRIPT_PATH+"/datas/conf.trinity","r") as f:
              f = f.readlines()

           for l in f:

              if "=" not in l:
                 continue

              l = l.strip()

              if "#" in l:
                  l = l.split("#")[0]

              option = next((r for r in options if r in l),"")

              if not option:
                 PRINT("\n-Trinity:Error skipped line :",l)
                 continue
            
              conf = l.split('=')[1]

              while conf.startswith(" "):
                    conf = conf[1:]

              while conf.endswith(" "):
                    conf = conf[:-1]

              conf = conf.replace("'","").replace('"',"")

              if option == "SAVED_ANSWER":

                      if conf.lower() == "default":
                         SAVED_ANSWER = SCRIPT_PATH+"/local_sounds/saved_answer/"
                      else:
                          SAVED_ANSWER = conf

                      if not os.path.exists(SAVED_ANSWER):
                          print("\n-Trinity:Error:GetConf:Le dossier:%s n'existe pas."%SAVED_ANSWER)
                          sys.exit()
                      else:
                          saved_error = str(SAVED_ANSWER+"/saved_error").replace("//","/")
                          if not os.path.exists(saved_error):
                             print("\n-Trinity:Error:GetConf:Le dossier:%s n'existe pas."%saved_error)
                             print("\n-Trinity:Création du dossier:",saved_error)
                             try:
                                 os.makedirs(saved_error)
                             except Exception as e:
                                 print("\n-Trinity:Error:Impossible de créer le dossier:%s :%s"%(saved_error,str(e)))
                                 sys.exit()

              elif  option == "GPT4FREE_SERVERS_STATUS":
                   if conf.lower() == "all":
                        GPT4FREE_SERVERS_STATUS = "All"
                   elif conf.lower() == "active":
                        GPT4FREE_SERVERS_STATUS = "Active"
                   elif conf.lower() == "unknown":
                        GPT4FREE_SERVERS_STATUS = "Unknown"
                   elif conf.lower() == "none":
                        GPT4FREE_SERVERS_STATUS = None
                   else:
                          print("-Trinity:Error GPT4FREE_SERVERS_STATUS has to be All,Active,Unknown or None.")

              elif  option == "GPT4FREE_SERVERS_AUTH":
                   if conf.lower() == "true":
                        GPT4FREE_SERVERS_AUTH = True
                   elif conf.lower() == "false":
                        GPT4FREE_SERVERS_AUTH = False
                   elif conf.lower() == "all":
                        GPT4FREE_SERVERS_AUTH = "All"
                   else:
                          print("-Trinity:Error GPT4FREE_SERVERS_STATUS has to be All,True or False.")

              elif option == "CHECK_UPDATE":
                   if conf.lower() == "true":
                           CHECK_UPDATE = True
                   elif conf.lower() == "false":
                           CHECK_UPDATE = False
                   else:
                          print("-Trinity:Error CHECK_UPDATE has to be either True or False.")

              elif option == "DEBUG":
                   if conf.lower() == "true":
                           DEBUG = True
                   elif conf.lower() == "false":
                           DEBUG = False
                   else:
                          print("-Trinity:Error DEBUG has to be either True or False.")

              elif option == "XCB_ERROR_FIX":
                   if conf.lower() == "true":
                           XCB_ERROR_FIX = True
                   elif conf.lower() == "false":
                           XCB_ERROR_FIX = False
                   else:
                          print("-Trinity:Error XCB_ERROR_FIX has to be either True or False.")



   else:
           with open(SCRIPT_PATH+"conf.trinity","w") as f:
                data = """SAVED_ANSWER = default
GPT4FREE_SERVERS_STATUS = Active #Active or Unknown or All or None
GPT4FREE_SERVERS_AUTH = False #True or False or All
CHECK_UPDATE = True
DEBUG = False
XCB_ERROR_FIX = False"""
                f.write(data)

           DEBUG = False
           CHECK_UPDATE = True
           SAVED_ANSWER = SCRIPT_PATH+"/local_sounds/saved_answer/"
           GPT4FREE_SERVERS_STATUS = "Active"
           GPT4FREE_SERVERS_AUTH = False
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

def Check_Update():
   PRINT("\n-Trinity:Dans Check_Update().")

   datas_folder = SCRIPT_PATH + "/datas/"
   gitobj = Github()

   to_update = []
   Gpt4free_Is_Up = False
   Gpt4free_current_version = ""
   Gpt4free_latest_version = ""
   try:
       if hasattr(g4f, "version"):
           if hasattr(g4f.version, "utils"):
               if hasattr(g4f.version.utils, "current_version"):
                   Gpt4free_current_version = g4f.version.utils.current_version
               if hasattr(g4f.version.utils, "latest_version"):
                   Gpt4free_latest_version = g4f.version.utils.latest_version
       if Gpt4free_current_version == Gpt4free_latest_version:
           Gpt4free_Is_Up = True

   except Exception as e:
       print("\n-Trinity:Error:Check_Update n'a pas pu déterminer la version de gpt4free:%s"%str(e))
       Gpt4free_Is_Up = True

   Trinity_Is_Up = False

   try:
       repo_trinity = gitobj.get_repo("on4r4p/Trinity")
       commits_trinity = repo_trinity.get_commits()
       last_trinity = commits_trinity[1].sha
       next_trinity = commits_trinity[0].sha

       if last_trinity == LAST_SHA:
           Trinity_Is_Up = True

   except Exception as e:
       print("\n-Trinity:Error:Check_Update n'a pas pu déterminer la version de Trinity:%s"%str(e))
       Trinity_Is_Up = True

   PRINT("\n-Trinity:Vérification de mise à jour pour Gpt4free:\n")
   if not Gpt4free_Is_Up:
       to_update.append("gpt4free")
       try:
           if hasattr(g4f.version.utils, "check_version"):
               g4f.version.utils.check_version()
               print()
       except:
           pass
   else:
       print("\n-Trinity:La version de gpt4free est à jour .")

   PRINT("\n-Trinity:Vérification de mise à jour pour Trinity:")
   if not Trinity_Is_Up:
       to_update.append("Trinity")
       PRINT("\n-Trinity:Github SHA doesn't matched:\n%s=!%s\n"%(LAST_SHA,last_trinity))
   else:
#       PRINT("\n-Trinity:Github SHA matched:\n%s==%s\n"%(LAST_SHA,last_trinity))
       PRINT("\n-Trinity:next_sha:%s\n"%(next_trinity))
       print("\n-Trinity:La version de Trinity est à jour .")

   if len(to_update) >0:
       print("\n-Trinity:Error:Une nouvelle version pour %s a été publiée.\n-Trinity:Mettez à jour votre version pour continuer.\n-Trinity:Ou changez CHECK_UPDATE à False dans datas/conf.trinity."%" et ".join(to_update))
       sys.exit()


if __name__ == "__main__":

    SCRIPT_PATH = os.path.dirname(__file__)
    if SCRIPT_PATH.endswith("."):
       SCRIPT_PATH = SCRIPT_PATH[:-1]


    LAST_SHA = "8bfc726884bfe2ae56a1f1b4b0cc55cc83950dce"
    DISPLAY = ""
    Providers_To_Use = []
    GPT4FREE_SERVERS_STATUS = "Active"
    GPT4FREE_SERVERS_AUTH = False
    CHECK_UPDATE = True
    DEBUG = False
    XCB_ERROR_FIX = False
    SAVED_ANSWER = SCRIPT_PATH +"/local_sounds/saved_answer/"

    GetConf()

    if GPT4FREE_SERVERS_STATUS:
        Providers_To_Use = Check_Free_Servers()


    FRAME_DURATION = 480
    FRAME_RATE = 16000

    History_List = []
    Current_Category = []
    Blacklisted = []

    PICO_KEY = PicoLoadKeys()
    GOOGLE_KEY,GOOGLE_ENGINE = GoogleLoadKeys()
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
    trinity_name = []
    trinity_mean = []
    trinity_creator = []
    trinity_script = []
    trinity_help = []
    prompt_request = []
    trinity_source_request = []
    rnd_request = []
    repeat_request = []
    show_history_request = []
    search_history_request = []
    read_link_request = []
    play_wav_request = []
    web_request = []
    wait_words = []
    add_words = []
    action_words = []
    action_functions = []
    alt_trigger = []
    verb_lst = []
    synonyms_list = []
    fnc_verb = {}

    CMDFILE = SCRIPT_PATH + "/datas/cmd.trinity"
    ALTFILE = SCRIPT_PATH + "/datas/alt_cmd.trinity"
    TRIFILE = SCRIPT_PATH + "/datas/alt_trigger.trinity"
    ACTFILE = SCRIPT_PATH + "/datas/action.trinity"
    PREFILE = SCRIPT_PATH + "/datas/prefix.trinity"
    SYNFILE = SCRIPT_PATH + "/datas/synonym.trinity"

    Load_Csv()

    if XCB_ERROR_FIX:
         Xcb_Fix("unset")

    os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/boot/psx.wav")
    signal.signal(signal.SIGINT, signal_handler)

    PRINT("\n-Trinity:CHECK_UPDATE:%s"%CHECK_UPDATE)
    PRINT("-Trinity:DEBUG:%s"%DEBUG)
    PRINT("-Trinity:GPT4FREE_SERVERS_STATUS:%s"%GPT4FREE_SERVERS_STATUS)
    PRINT("-Trinity:GPT4FREE_SERVERS_AUTH:%s"%GPT4FREE_SERVERS_AUTH)
    PRINT("-Trinity:XCB_ERROR_FIX:%s"%XCB_ERROR_FIX)
    PRINT("-Trinity:SAVED_ANSWER:%s"%SAVED_ANSWER)
    PRINT("-Trinity:History categories loaded:%s"%len(History_List))

    if GPT4FREE_SERVERS_STATUS:
         PRINT("-Trinity:Free Gpt servers to use:")
         for i in Providers_To_Use:
              PRINT("\t",i)
    if CHECK_UPDATE:
       Check_Update()

#####
    Trinity()
#####
