#!/usr/bin/python3

import g4f, pyaudio, pvporcupine, os, time, sys, struct, random, webrtcvad, re, csv, string, googlesearch, requests, signal, inspect, sox ,spacy,html,detectlanguage
#,wikipedia

import g4f.debug
g4f.debug.logging = True

import google.cloud.texttospeech as tts

from g4f.cookies import set_cookies_dir, read_cookie_files

from deep_translator import GoogleTranslator

from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

from urlextract import URLExtract

from difflib import SequenceMatcher

from datetime import datetime

from bs4 import BeautifulSoup

from shutil import move

from github import Github

from google.cloud import speech_v1p1beta1 as speech
from google.cloud import language_v1
from google.cloud import translate_v2
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


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/google_adc.json"


def signal_handler(sig, frame):
    Xcb_Fix("set")
    sys.exit(0)


def PRINT(txt, other=None):
    tmp_txt = txt
    #   print("\n-Trinity:Dans la fonction PRINT().")
    #   print("\n-Trinity:other:",other)
    try:
        if DEBUG:
            if other:
                tmp_txt = str(txt) + " " + str(other)
                print(tmp_txt)
            else:
                print(tmp_txt)
    except Exception as e:
        print("\n-Trinity:Erreur dans la fonction PRINT:", str(e))
        pass


def PicoLoadKeys():
    PRINT("\n-Trinity:Dans fonction PicoLoadKeys")
    if os.path.exists(SCRIPT_PATH + "/keys/pico.key"):
        with open(SCRIPT_PATH + "/keys/pico.key", "r") as k:
            PICO_KEY = k.read()
            PICO_KEY = PICO_KEY.strip()
        if not PICO_KEY.endswith("=="):
            print("\n-Trinity:-Wrong Pico Api key.")
            print(PICO_KEY)
            sys.exit()
        else:
            return PICO_KEY
    else:
        print("\n-Trinity:-%s/keys/pico.key doesn't exist." % SCRIPT_PATH)
        sys.exit()

def DetectLanguageLoadKeys():
    PRINT("\n-Trinity:Dans fonction DetectLanguageLoadKeys")
    if os.path.exists(SCRIPT_PATH + "/keys/detectlanguage.key"):
        with open(SCRIPT_PATH + "/keys/detectlanguage.key", "r") as k:
            DLANG_KEY = k.read()
            DLANG_KEY = DLANG_KEY.strip()
        if not len(DLANG_KEY) == 32:
            print("\n-Trinity:-Wrong DetectLanguage Api key.")
            print(DLANG_KEY)
            sys.exit()
        else:
            return DLANG_KEY
    else:
        print("\n-Trinity:-%s/keys/detectlanguage.key doesn't exist." % SCRIPT_PATH)
        #sys.exit()
        return None

def GoogleLoadKeys():
    PRINT("\n-Trinity:Dans fonction GoogleLoadKeys")

    GOOGLE_KEY = ""
    GOOGLE_ENGINE = ""
    GOOGLE_TRANSLATE = ""

    if os.path.exists(SCRIPT_PATH + "/keys/google_translate.key"):
        with open(SCRIPT_PATH + "/keys/google_translate.key", "r") as k:
            GOOGLE_TRANSLATE = k.read()
            GOOGLE_TRANSLATE = GOOGLE_TRANSLATE.strip()
        if len(GOOGLE_TRANSLATE) != 39:
            print("\n-Trinity:-Wrong Google Translate Api key (len).")
            print(GOOGLE_TRANSLATE)
            GOOGLE_TRANSLATE = ""
    else:
        print("\n-Trinity:-%s/keys/google_translate.key doesn't exist." % SCRIPT_PATH)


    if os.path.exists(SCRIPT_PATH + "/keys/google_search.key"):
        with open(SCRIPT_PATH + "/keys/google_search.key", "r") as k:
            GOOGLE_KEY = k.read()
            GOOGLE_KEY = GOOGLE_KEY.strip()
        if len(GOOGLE_KEY) != 39:
            print("\n-Trinity:-Wrong Google Api key (len).")
            print(GOOGLE_KEY)
            GOOGLE_KEY = ""
    else:
        print("\n-Trinity:-%s/keys/google_search_engine.key doesn't exist." % SCRIPT_PATH)

    if os.path.exists(SCRIPT_PATH + "/keys/google_search_engine.id"):
        with open(SCRIPT_PATH + "/keys/google_search_engine.id", "r") as k:
            GOOGLE_ENGINE = k.read()
            GOOGLE_ENGINE = GOOGLE_ENGINE.strip()
        if len(GOOGLE_ENGINE) != 17:
            print("\n-Trinity:-Wrong Google engine id (len).")
            print(GOOGLE_ENGINE)
            GOOGLE_ENGINE = ""
    else:
        print("\n-Trinity:-%s/keys/google_search_engine.id doesn't exist." % SCRIPT_PATH)

    return (GOOGLE_KEY, GOOGLE_ENGINE,GOOGLE_TRANSLATE)


def parse_response(data):

    PRINT("\n-Trinity:Original Data before parse:\n", data)

    input_lang = None

    data = html.unescape(data)


    if DLANG_KEY and GOOGLE_TRANSLATE:
         try:
             input_lang = detectlanguage.simple_detect(data)
             PRINT("\n-Trinity:detectlanguage:input_lang set to :",input_lang)
         except Exception as e:
            PRINT("\n-Trinity:Error:detectlanguage.simple_detect:")
            PRINT(e)

    if GOOGLE_TRANSLATE:
        if not input_lang:
             try:
                  client = translate_v2.Client()
                  input_lang = client.detect_language(data)
                  input_lang = input_lang['language']
                  PRINT("\n-Trinity:google.detect_language:input_lang set to :",input_lang)
             except Exception as e:
                  PRINT("\n-Trinity:Error:client.detect_language:")
                  PRINT(e)
                  input_lang = "fr"

        if input_lang != "fr":
            try:
               data_translated = GoogleTranslator(source=input_lang, target='fr').translate(text=data)
               os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/trad/traduction.wav")
               PRINT("\n-Trinity:GoogleTranslator:Translation successful.") 
               return(final_translated)
            except Exception as e:
                  PRINT("\n-Trinity:Error:GoogleTranslator:")
                  PRINT(e)





    emoj = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+",
        re.UNICODE,
    )

    if "Bonjour, c'est Bing." in data:
        index = data.find("Bonjour, c'est Bing.")
        data = data[index + 21 :]

    if "Bonjour, je suis Copilot" in data:
        to_find = "Bonjour, je suis Copilot"
        index = data.find(to_find)
        after_to_find = index + len(to_find)
        next_point = None
        for n, c in enumerate(data[after_to_find:]):
            if c == ".":
                next_point = n + 1
                break
        if next_point:
            data = data[index + len(to_find) + next_point :]
        else:
            data = data[index + len(to_find) :]

    data = data.replace("**", "")
    no_link = re.sub(r'\[\d+\]:\s*https?://[^\s]+ "[^"]*"\n?', "", data)
    no_emoj = re.sub(emoj, "", no_link)
    no_brak = re.sub(r"\[[^\]]+\]", "", no_emoj)
    no_brak2 = re.sub(r"\[\^?\d+\^?\]:", "", no_brak)

    final = ""
    for line in no_brak2.splitlines():
        if "http" in line:
            httpos = line.find("http")
            to_replace = line[httpos : line.find(" ")]
            if len(to_replace) == 0:
                to_replace = line[httpos:]
            line = line.replace(to_replace, " ")
            if len(line.replace(" ", "")) <= 1:
                continue
            final += "\n" + line
        else:
            final += line


    return final.replace("####", "")


def To_Gpt(input):

    if GPT4FREE_SERVERS_STATUS:
        FreeGpt(input)

    else:
        # TODO
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
            try:
                 if "g4f.Provider." in line:
                     if "https://img.shields.io/badge/Active-brightgreen" in line:
                         provider = "g4f.Provider." + line.split("g4f.Provider.")[1].split("`")[0]
                         if "❌" in line:
                             active_no_auth.append(provider)
                         else:
                             active_with_auth.append(provider)
                     if "https://img.shields.io/badge/Unknown-grey" in line:
                         provider = "g4f.Provider." + line.split("g4f.Provider.")[1].split("`")[0]
                         if "❌" in line:
                             unknown_no_auth.append(provider)
                         else:
                             unknown_with_auth.append(provider)
            except Exception as e:
                PRINT("\n-Trinity Error:Check_Free_Servers():Error:%s"%str(e))
                

    except Exception as e:
        print("\n-Trinity Error:Check_Free_Servers()", str(e))

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
            "g4f.Provider.You",
        ]

    providers_to_return = [p for p in providers_to_return if p.startswith("g4f.Provider.")]
    return providers_to_return


def FreeGpt(input):
    PRINT("\n-Trinity:Dans la fonction FreeGpt")

    global LAST_DIALOG
    global Current_Provider_Id
    global Blacklisted

    def minitts(tx, fname):

            try:

                client = tts.TextToSpeechClient()
                audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

                text_input = tts.SynthesisInput(text=tx)
                voice_params = tts.VoiceSelectionParams(language_code="fr-FR", name="fr-FR-Neural2-A")

                response = client.synthesize_speech(input=text_input, voice=voice_params, audio_config=audio_config)
                audio_response = response.audio_content
                try:
                    with open(fname, "wb") as out:
                        out.write(audio_response)
                except Exception as e:
                    PRINT("\n-Trinity:Error:%s" % str(e))
            except Exception as e:
                PRINT("\n-Trinity:Error:%s" % str(e))


    def save_blacklist(server, err):
        err_file = str(SAVED_ANSWER + "/saved_error/g4f_providers.errors").replace("//", "/")
        try:
            with open(err_file, "a+", newline="") as f:
                now = "===== " + str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")) + " =====\n"
                serverr = "g4f provider:%s error:%s\n" % (str(server), err)
                f.write(now)
                f.write(serverr)
        except Exception as e:
            print("\n-Trinity:Error:save_blacklist():%s" % str(e))

    Answer_Known = Check_History(input)

    if Answer_Known or not No_Input.empty():
        return Trinity()

    last_sentence.put(input)

    #    os.system("aplay -q %s"%SCRIPT_PATH+"local_sounds/server/gpt3.wav")
    rnd = str(random.randint(1, 10))
    wait = SCRIPT_PATH + "/local_sounds/wait/" + rnd + ".wav"
#    os.system("aplay -q %s" % wait)
    print("wait:",wait)
    Err_msg = ""
    Err_cnt = 0
    response = ""

    p_cnt = 0
    while p_cnt <= (len(Providers_To_Use) - len(Blacklisted)):
        if Current_Provider_Id > (len(Providers_To_Use) - len(Blacklisted)):
            Current_Provider_Id = 0
        if Providers_To_Use[Current_Provider_Id] in Blacklisted:
            PRINT("\n-Trinity:skipping :", Providers_To_Use[Current_Provider_Id])
            Current_Provider_Id += 1
            continue

        PRINT("\n-Trinity:Asking :", Providers_To_Use[Current_Provider_Id])
        if Providers_To_Use[Current_Provider_Id] in ["g4f.Provider.PerplexityLabs","g4f.Provider.ChatgptFree"]: ##tmpfix
             PRINT("\n-Trinity:Adding '. Réponds en français.':")
             input = str(input) + " . Réponds en français."

        try:
            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                provider=eval(Providers_To_Use[Current_Provider_Id]),
                timeout=10,
                messages=[{"role": "user", "content": str(input)}],
            )

            if len(response) < 1:
                PRINT(
                    "\n-Trinity:len(response) < 1:No answer from :",
                    Providers_To_Use[Current_Provider_Id],
                )
                provider_name = Providers_To_Use[Current_Provider_Id].replace("g4f.Provider.", "")
                wait = SCRIPT_PATH + "/local_sounds/providers/" + str(provider_name) + ".wav"
                os.system("aplay -q %s" % wait)
                Current_Provider_Id += 1
            else:
                break

        except Exception as e:
            print("\n-Trinity:Error:", str(e))
            print("\n-Trinity:No answer from :", Providers_To_Use[Current_Provider_Id])
            provider_name = Providers_To_Use[Current_Provider_Id].replace("g4f.Provider.", "")
            wait = SCRIPT_PATH + "/local_sounds/providers/" + str(provider_name) + ".wav"
            if not os.path.exists(wait):
                err_txt = "Le serveur %s n'a pas répondu , je vais essayer le suivant"%provider_name
                minitts(err_txt, wait)
            os.system("aplay -q %s" % wait)
            save_blacklist(Providers_To_Use[Current_Provider_Id], str(e))
            Blacklisted.append(Providers_To_Use[Current_Provider_Id])
            Current_Provider_Id += 1
        p_cnt += 1

    if len(response) < 1:
        os.system("aplay -q " + SCRIPT_PATH + "local_sounds/errors/err_no_respons_allprovider.wav")
        return(Quit())
    else:
        PRINT("\n-Trinity:Le server %s à répondu." % (Providers_To_Use[Current_Provider_Id]))
        Current_Provider_Id += 1
        ##checktime
        return Text_To_Speech(str(response), stayawake=False)

def wake_up():
    PRINT("\n-Trinity:Dans la fonction Wakeup")

    #    word_key = SCRIPT_PATH+"/models/Trinity_en_linux_v2_2_0.ppn"
    word_key = SCRIPT_PATH + "/models/trinity_fr_raspberry-pi_v3_0_0.ppn"
    word_key2 = SCRIPT_PATH + "/models/interpreteur_fr_raspberry-pi_v3_0_0.ppn"
    word_key3 = SCRIPT_PATH + "/models/repete_fr_raspberry-pi_v3_0_0.ppn"
    word_key4 = SCRIPT_PATH + "/models/merci_fr_raspberry-pi_v3_0_0.ppn"
    pvfr = SCRIPT_PATH + "/models/porcupine_params_fr.pv"
    porcupine = None
    keyword_index = None

    try:
        porcupine = pvporcupine.create(
            access_key=PICO_KEY,
            model_path=pvfr,
            keyword_paths=[word_key, word_key2, word_key3, word_key4],
            sensitivities=[1, 1, 1, 1],
        )
#        print("hey")
        with ignoreStderr():
            pa = pyaudio.PyAudio()
#        pa = pyaudio.PyAudio()
#        print("hey2")
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )

        print("\n-Trinity: En attente ...")

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index == 0:
                PRINT("\n-Trinity:keyword_index:", keyword_index)

                rnd = str(random.randint(1, 15))
                wake_sound = SCRIPT_PATH + "/local_sounds/wakesounds/" + rnd + ".wav"
                os.system("aplay -q %s" % wake_sound)
                break
            if keyword_index == 1:
                PRINT("\n-Trinity:keyword_index:", keyword_index)
                break
            if keyword_index == 2:
                PRINT("\n-Trinity:keyword_index:", keyword_index)
                break
            if keyword_index == 3:
                PRINT("\n-Trinity:keyword_index:", keyword_index)
                rnd = str(random.randint(1, 15))
                thk_sound = SCRIPT_PATH + "/local_sounds/merci/" + rnd + ".wav"
                os.system("aplay -q %s" % thk_sound)

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
            return Trinity("Speech_To_Text")
        if keyword_index == 1:
            return Prompt()
        if keyword_index == 2:
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/repeat/isaid.wav")
            os.system("aplay -q %s" % SCRIPT_PATH + "tmp/current_answer.wav")
            return wake_up()


def Record_Query():
    PRINT("\n-Trinity:Dans la fonction Record_Query")

    with ignoreStderr():
        p = pyaudio.PyAudio()

    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=FRAME_RATE,
        input=True,
        frames_per_buffer=FRAME_DURATION,
    )

    wake_sound = SCRIPT_PATH + "/local_sounds/wakesounds/record.wav"
    os.system("aplay -q %s" % wake_sound)

    while not record_on.empty():
        chunks.put(stream.read(FRAME_DURATION))

    PRINT("\n-Trinity:Enregistrement terminé.")
    wake_sound = SCRIPT_PATH + "/local_sounds/wakesounds/record_end.wav"
    os.system("aplay -q %s" % wake_sound)

    stream.stop_stream()
    stream.close()
    p.terminate()
    return ()


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

                if silence < threshold * (FRAME_RATE / FRAME_DURATION):
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

                    rnd = str(random.randint(1, 11))
                    no_input_sound = SCRIPT_PATH + "/local_sounds/noinput/" + rnd + ".wav"
                    os.system("aplay -q  %s" % no_input_sound)
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
                os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/errors/err_too_long.wav")
                break


def Write_csv(function_name, trigger_word, filename):

    # CMDFILE,
    with open(filename, "a+", newline="") as csvfile:
        fieldnames = ["function", "trigger"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

        writer.writerow({"function": function_name, "trigger": trigger_word})

    return Load_Csv()


def Special_Syntax(txt, filepath=None, line=None):


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
                    if c == " ":
                        pass
                    elif c == ",":
                        coma = True
                    elif c == "[":
                        obracket = True
                    elif c == "]":
                        cbracket = True
                    elif c in ["'", '"']:
                        quote = True
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
            for e, char in enumerate(str_lst):
                #        print("bucket:",bucket)
                if to_split:
                    if char in ["'", '"']:
                        #                     print("bucket:",bucket)
                        if check_split(e + 1):
                            yield (None, bucket)
                            # listing.append((None,bucket))
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
                    elif char in ["'", '"']:
                        to_split = True
                    else:
                        pass

        #    print("listing\:",listing)
        #    return listing

        def make_list(listing):
            lst = []
            for id, data in listing:
                if id == "[":
                    lst.append(make_list(listing))
                elif id == "]":
                    return lst
                else:
                    lst.append(data)
            return lst[0]

        def add_braks(cmd_txt, lbraks, rbraks):
            def check_around(idx):
                while True:
                    if idx <= 0:
                        return False
                    if cmd_txt[idx] == " ":
                        pass
                    elif cmd_txt[idx] == "[":
                        return False
                    elif cmd_txt[idx] == "]":
                        return True
                    else:
                        return False
                    idx -= 1
                # return True

            outside_lvl = []
            bad_pos = []
            skip = 0
            start = None
            end = None
            for e, char in enumerate(cmd_txt):

                if char == "[" and start is None:
                    start = e
                elif char == "[":
                    skip += 1
                elif char == "]":
                    if skip > 0:
                        skip -= 1
                    else:
                        end = e + 1
                        outside_lvl.append((start, end))
                        start = None
                        end = None

            for st, ed in outside_lvl:
                for i in range(st, ed):
                    bad_pos.append(i)

            braks_txt = ""
            opened = False
            badbool = False
            for e, char in enumerate(cmd_txt):
                if e not in bad_pos:
                    badbool = False
                    if opened:
                        braks_txt += str(char)
                    else:
                        if check_around(e - 1):
                            # print("cmd_txt[%s-1]:%s char:,[%s"%(e,cmd_txt[e-1],char))
                            braks_txt += ",[" + str(char)
                        else:
                            # print("cmd_txt[%s-1]:%s char:[%s"%(e,cmd_txt[e-1],char))
                            braks_txt += "[" + str(char)
                        opened = True

                else:
                    badbool = True
                    if opened:
                        braks_txt += "]," + str(char)
                        opened = False
                    else:
                        braks_txt += str(char)

            if opened:
                braks_txt += "]"

            return "[" + braks_txt + "]"

        def add_quotes(fullbraks):

            def check_around(idx, coma=False):
                if coma:
                    pos = idx - 1
                    before = False
                    after = False
                    while True:
                        #                     print("char before:",fullbraks[pos])
                        if pos == 0:
                            break
                        if fullbraks[pos] == " ":
                            pass
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

                    for c in fullbraks[idx + 1 :]:
                        #                     print("char after:",c)
                        if c == " ":
                            pass
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
                        return '",'
                    elif after and not before:
                        #                         print("after and not before")
                        return ',"'
                    elif not before and not after:
                        #                         print("not before and not after")
                        return ","
                    else:
                        #                         print(" before and after")
                        return '","'

                else:
                    for c in fullbraks[idx:]:
                        if c == "[":
                            return False
                        elif c == "]":
                            return False
                        else:
                            return True
                    return False

            fullquotes = ""
            for e, char in enumerate(fullbraks):
                #             print("char:",char)
                if char == "[":
                    if check_around(e + 1):
                        fullquotes += '["'
                    else:
                        fullquotes += "["
                elif char == "]":
                    if check_around(e - 1):
                        fullquotes += '"]'
                    else:
                        fullquotes += "]"
                elif char == ",":

                    fullquotes += check_around(e, True)
                else:
                    fullquotes += char
            return fullquotes

        def valid_lists(cmd_txt):
            lbraks = [pos for pos, char in enumerate(cmd_txt) if char == "["]
            rbraks = [pos for pos, char in enumerate(cmd_txt) if char == "]"]
            lbrak_nbr = len(lbraks)
            rbrak_nbr = len(rbraks)

            lcurlys = [pos for pos, char in enumerate(cmd_txt) if char == "{"]
            rcurlys = [pos for pos, char in enumerate(cmd_txt) if char == "}"]
            lcurly_nbr = len(lcurlys)
            rcurly_nbr = len(rcurlys)

            if lbrak_nbr == 0 and rbrak_nbr == 0 and lcurly_nbr > 0 and rcurly_nbr > 0:
                print(
                    "\n-Fichier:%s ligne:%s Les symboles '{' et '}' s'utilisent conjointement avec les symboles '[' et ']' mais pas seuls."
                    % (filepath, line)
                )
                return ("~PARSE~ERR~", None, None)
            elif lbrak_nbr == 0 and rbrak_nbr == 0:
                return (False, None, None)
            if lbrak_nbr != rbrak_nbr:
                if lbrak_nbr > rbrak_nbr:
                    print(
                        "\n-Fichier:%s ligne:%s Il ya %s '[' et %s ']' seulement."
                        % (filepath, line, lbrak_nbr, rbrak_nbr)
                    )
                else:
                    print(
                        "\n-Fichier:%s ligne:%s Il ya seulement %s '[' et %s ']'."
                        % (filepath, line, lbrak_nbr, rbrak_nbr)
                    )
                return ("~PARSE~ERR~", None, None)

            if lcurly_nbr != rcurly_nbr:
                if lcurly_nbr > rcurly_nbr:
                    print(
                        "\n-Fichier:%s ligne:%s Il ya %s '{' et %s '}' seulement."
                        % (filepath, line, lcurly_nbr, rcurly_nbr)
                    )
                else:
                    print(
                        "\n-Fichier:%s ligne:%s Il ya seulement %s '{' et %s '}'."
                        % (filepath, line, lcurly_nbr, rcurly_nbr)
                    )
                return ("~PARSE~ERR~", None, None)

            for o, c in zip(lbraks, rbraks):
                #             print("o:%s c:%s"%(o,c))
                if o > c:
                    print("\n-Fichier:%s ligne:%s Mauvaise syntax." % (filepath, line))
                    return ("~PARSE~ERR~", None, None)
            for o, c in zip(lcurlys, rcurlys):
                #             print("o:%s c:%s"%(o,c))
                if o > c:
                    print("\n-Fichier:%s ligne:%s Mauvaise syntax." % (filepath, line))
                    return ("~PARSE~ERR~", None, None)

            return (True, lbraks, rbraks)

        cmd_txt = cmd_txt.replace("/", ",")

        list_inside, lbraks, rbraks = valid_lists(cmd_txt)
        if list_inside:
            if list_inside == "~PARSE~ERR~":
                return (list_inside, None)
            else:
                try:
                    curlys = None
                    fullbraks = add_braks(cmd_txt, lbraks, rbraks)
                    if "{" in fullbraks and "}" in fullbraks:
                        fullbraks, curlys = extract_curly(fullbraks)
                        fullquotes = add_quotes(fullbraks)
                    #                  fullquotes = putback_curly(fullquotes,curlys)
                    else:
                        fullquotes = add_quotes(fullbraks)

                    #                       PRINT("\nfullbraks:%s\n"%fullbraks)
                    #                       PRINT("\nfullquotes:%s\n"%fullquotes)

                    protolist = to_list(fullquotes)
                    actualist = make_list(protolist)

                    return (actualist, curlys)
                except Exception as e:
                    print("-Trinity Error:", str(e))
                    return ("~PARSE~ERR~", None)
        else:
            return (False, None)

    #    def putback_curly(str_to_check,dict):
    #        for k,i in dict.items():
    #            if k in str_to_check:
    #                str_to_check = str_to_check.replace(k,i)
    #        return(str_to_check)

    def extract_curly(str_to_check):

        #        PRINT("\nstr_to_check:\n",str_to_check)
        def rnd_str(str_to_check, curly_dict):
            while True:
                characters = string.ascii_letters + string.digits
                rnd = "".join(random.choice(characters) for _ in range(5))
                if not rnd in curly_dict and not rnd in str_to_check:
                    return rnd

        curly_dict = {}
        while True:
            start = False
            end = False

            for n, c in enumerate(str_to_check):
                if c == "{" and not start and not end:
                    start = n
                if c == "}" and start and not end:
                    end = n + 1
                if start and end:
                    break

            curly = str_to_check[start:end]
            marker = rnd_str(str_to_check, curly_dict)

            if "," in curly:
                curly = curly.replace("{", "").replace("}", "").split(",")
            else:
                curly = curly.replace("{", "").replace("}", "")

            curly_dict[marker] = curly
            str_to_check = str_to_check[:start] + str(marker) + str_to_check[end:]

            if "{" not in str_to_check and "}" not in str_to_check:
                break

        #    print("\nwithout curly:",str_to_check)
        #    print("\ncurly_dict:")

        #    for i,j in curly_dict.items():
        #        print("%s type= %s:%s"%(i,type(i),j))
        return (str_to_check, curly_dict)

        #    def Mark_sublvl(lists_to_check,pos_lst=0,lvl=0,markers_dict={}):#TODO
        #    print("\nlists_to_check:",lists_to_check)
        #        for pos_itm,lists in enumerate(lists_to_check):
        # print("pos_itm:%s lists:%s"%(pos_itm,lists))
        #            if isinstance(lists,list):
        #                key = "lvl:%s,posl:%s,posi%s"%(lvl,pos_lst,pos_itm)
        #                if not key in markers_dict:
        #                    markers_dict[key] = lists
        #                    markers_dict = final_parse(lists,pos_lst,lvl+1,markers_dict = markers_dict)
        #        else:
        #             print("lists not a list:",lists)
        return markers_dict

    def Unfold_cmd(cmd_lst, curlys):

        unfolded = []

        for lst in cmd_lst:
            tmp_lst = []

            for item in lst:
                skip = False

                for k, i in curlys.items():
                    if k in item:

                        skip = True
                        if isinstance(i, list):
                            for j in i:
                                tmp_lst.append(item.replace(k, j))
                        else:
                            tmp_lst.append(item.replace(k, i))

                        break
                if not skip:
                    tmp_lst.append(item)

            unfolded.append(tmp_lst)

        for lst in unfolded:
            for item in lst:
                for k in curlys:
                    if k in item:
                        return Unfold_cmd(unfolded, curlys)

        return unfolded

    def join_and_replace(tojoin):
        joined = "".join(tojoin)
        if "  " in joined:
            replaced = joined
            while True:
                replaced = replaced.replace("  ", " ")
                if not "  " in replaced:
                    joined_and_replaced = replaced
                    break
        #                 else:
        #                      print("replaced:",replaced)
        #                      input("")
        else:
            joined_and_replaced = joined

        return joined_and_replaced

    parsed_cmd, curlys = parse_cmd(txt)

    if parsed_cmd:
        final_list = []
        if parsed_cmd == "~PARSE~ERR~":
            PRINT("\n-Trinity:Special_Syntax():~PARSE~ERR~:txt:\n%s\n" % txt)
            return None
        #         PRINT("\ntxt:\n%s\n"%txt)
        #         PRINT("\nparsed_cmd:\n%s\n"%parsed_cmd)
        if curlys:
            #             PRINT("\n-Trinity:curlys is full:")
            #             for i,j in curlys.items():
            #                 PRINT("%s:%s"%(i,j))
            unfolded = Unfold_cmd(parsed_cmd, curlys)
            prod = product(*unfolded)
            final_list = [join_and_replace(i) for i in prod]
            if SYNTAX_DBG:
                PRINT("\n-Trinity:Output Special Syntax for:\n%s\n\n%s" % (txt, final_list))
            return final_list
        else:
            prod = product(*parsed_cmd)
            final_list = [join_and_replace(i) for i in prod]
            if SYNTAX_DBG:
                PRINT("\n-Trinity:Output Special Syntax for:\n%s\n\n%s" % (txt, final_list))
            return final_list
    else:
        #        PRINT("no advanced syntax:\n",txt)
        return txt

    ##TODO sublvl etc ..
    # for n,p in enumerate(parsed_cmd):
    #   print("sending %s %s"%(n,p))
    #   markers = final_parse(p,pos_lst=n)

    # marker = final_parse(parsed_cmd)
    # print("\n\nfinal marker:")
    # for i,j in markers.items():print("%s:%s"%(i,j))

    # print("\nparsed_cmd:\n")
    # for n,i in enumerate(parsed_cmd):
    #    print("%s =  %s"%(n,i))
    # to_prod,markers = is_inner_lst(parsed_cmd)
    # sys.exit()

    # if markers:
    #    print("\nmarkers is full\n")
    #    prod = product(*parsed_cmd)
    #    for i in prod:
    #       print(i)
    # else:
    #    print("\n\nno markers final:\n")
    #    prod = product(*parsed_cmd)
    #    for i in prod:
    #       print(i)


def Load_Csv():

    global Loaded_History_List
    global Loaded_Trinity_Name_Requests
    global Loaded_Trinity_Mean_Requests
    global Loaded_Trinity_Dev_Requests
    global Loaded_Trinity_Script_Requests
    global Loaded_Trinity_Help_Requests
    global Loaded_Prompt_Requests
    global Loaded_Rnd_Requests
    global Loaded_Read_Results
    global Loaded_Repeat_Requests
    global Loaded_Show_History_Requests
    global Loaded_Search_History_Requests
    global Loaded_Read_Link_Requests
    global Loaded_Play_Audio_File_Requests
    global Loaded_Search_Web_Requests
    global Loaded_Wait_Words_Requests
    global Loaded_Quit_Words_Requests
    global Loaded_Sort_Results_Requests
    global Loaded_Actions_Words_Requests
    global Loaded_Add_Triggers_Requests
    global Loaded_Mix_Actions_Functions
    global Loaded_Alternatives_Triggers
    global Loaded_Verbs_Words_List
    global Loaded_Synonyms_Words_List
    global Loaded_Mix_Functions_verbs

    Loaded_History_List = []
    Loaded_Trinity_Name_Requests = []
    Loaded_Trinity_Mean_Requests = []
    Loaded_Trinity_Dev_Requests = []
    Loaded_Trinity_Script_Requests = []
    Loaded_Trinity_Help_Requests = []
    Loaded_Prompt_Requests = []
    Loaded_Rnd_Requests = []
    Loaded_Repeat_Requests = []
    Loaded_Show_History_Requests = []
    Loaded_Search_History_Requests = []
    Loaded_Read_Results = []
    Loaded_Read_Link_Requests = []
    Loaded_Play_Audio_File_Requests = []
    Loaded_Search_Web_Requests = []
    Loaded_Wait_Words_Requests = []
    Loaded_Quit_Words_Requests = []
    Loaded_Sort_Results_Requests = []
    Loaded_Add_Triggers_Requests = []
    Loaded_Actions_Words_Requests = []
    Loaded_Mix_Actions_Functions = []
    Loaded_Alternatives_Triggers = []
    Loaded_Verbs_Words_List = []
    Loaded_Synonyms_Words_List = []
    Loaded_Mix_Functions_verbs = {}

    PRINT("\n-Trinity:Dans la fonction Load_Csv .")

    if os.path.exists(SCRIPT_PATH + "/history"):
        hist_folder = SCRIPT_PATH + "/history"
        hist_files = [f for f in os.listdir(hist_folder)]
        for file in hist_files:
            filepath = os.path.join(hist_folder, file)
            try:
                with open(filepath, newline="") as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        try:
                            hist_file = row["hist_file"]
                            hist_cats = row["hist_cats"]
                            hist_input_full = row["hist_input_full"]
                            hist_input_short = row["hist_input_short"]
                            hist_input_wav = row["hist_input_wav"]
                            hist_output = row["hist_output"]
                            hist_output_wav = row["hist_output_wav"]
                            hist_urls = row["hist_urls"]
                            hist_epok = row["hist_epok"]
                            hist_tstamp = row["hist_tstamp"]
                            Loaded_History_List.append(
                                {
                                    "hist_file":hist_file,
                                    "hist_cats":hist_cats,
                                    "hist_input_full":hist_input_full,
                                    "hist_input_short":hist_input_short,
                                    "hist_input_wav":hist_input_wav,
                                    "hist_output":hist_output,
                                    "hist_output_wav":hist_output_wav,
                                    "hist_urls":hist_urls,
                                    "hist_epok":hist_epok,
                                    "hist_tstamp":hist_tstamp,
                                }
                            )


                        except Exception as e:
                            print("\n-Trinity:Error:loadcsv:file:%s %s" % (filepath, str(e)))
            #                      print("\nhist_file:\n",hist_file)
            #                      print("hist_cats:\n",hist_cats)
            #                      print("hist_txt:\n",hist_txt)
            #                      print("hist_answer:\n",hist_answer)
            #                      print("hist_epok:\n",hist_epok)
            #                      print("hist_tstamp:\n",hist_tstamp)
            #                      print("hist_wav:\n",hist_wav)
            except Exception as e:
                print("\n-Trinity:Error:loadcsv:file:%s %s" % (filepath, str(e)))

    PRINT("\n-Trinity:Loaded_History_List Loaded")

    if os.path.exists(SYNFILE):
        with open(SYNFILE, newline="") as f:
            data = f.readlines()

            for line in data:
                tmplst = []
                line = line.strip().split(",")
                for l in line:
                    if l != "":
                        tmplst.append(l)
                Loaded_Synonyms_Words_List.append(tmplst)

    else:

        print("\n-Trinity:Error:%s not found." % SYNFILE)
        sys.exit()

    PRINT("\n-Trinity:Loaded_Synonyms_Words_List Loaded")

    if os.path.exists(TRIFILE):
        with open(TRIFILE, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if "trigger" in row:
                    trigger = row["trigger"]
                else:
                    continue
                if not trigger in Loaded_Alternatives_Triggers:
                    Loaded_Alternatives_Triggers.append(trigger)

    else:

        print("\n-Trinity:Error:%s not found." % TRIFILE)
        sys.exit()

    PRINT("\n-Trinity:Loaded_Alternatives_Triggers Loaded")
    if os.path.exists(CMDFILE):
        with open(CMDFILE, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for line, row in enumerate(reader):
                line = line + 2
                if "function" in row:
                    function = row["function"]
                    if "trigger" in row:
                        trigger = row["trigger"]
                    else:
                        continue 
                    if function == "F_trinity_name":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Trinity_Name_Requests.append(t)
                            else:
                                Loaded_Trinity_Name_Requests.append(trigger)
                    elif function == "F_trinity_mean":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Trinity_Mean_Requests.append(t)
                            else:
                                Loaded_Trinity_Mean_Requests.append(trigger)
                    elif function == "F_trinity_dev":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Trinity_Dev_Requests.append(t)
                            else:
                                Loaded_Trinity_Dev_Requests.append(trigger)
                    elif function == "F_trinity_script":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Trinity_Script_Requests.append(t)
                            else:
                                Loaded_Trinity_Script_Requests.append(trigger)
                    elif function == "F_trinity_help":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Trinity_Help_Requests.append(t)
                            else:
                                Loaded_Trinity_Help_Requests.append(trigger)
                    elif function == "F_prompt":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Prompt_Requests.append(t)
                            else:
                                Loaded_Prompt_Requests.append(trigger)
                    elif function == "F_rnd":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Rnd_Requests.append(t)
                            else:
                                Loaded_Rnd_Requests.append(trigger)

                    elif function =="F_read_results":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Read_Results.append(t)
                            else:
                                Loaded_Read_Results.append(trigger)

                    elif function == "F_repeat":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Repeat_Requests.append(t)
                            else:
                                Loaded_Repeat_Requests.append(trigger)
                    elif function == "F_show_history":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Show_History_Requests.append(t)
                            else:
                                Loaded_Show_History_Requests.append(trigger)

                    elif function == "F_search_history":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Search_History_Requests.append(t)
                            else:
                                Loaded_Search_History_Requests.append(trigger)
                    elif function == "F_read_link":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Read_Link_Requests.append(t)
                            else:
                                Loaded_Read_Link_Requests.append(trigger)
                    elif function == "F_play_audio":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Play_Audio_File_Requests.append(t)
                            else:
                                Loaded_Play_Audio_File_Requests.append(trigger)
                    elif function == "F_search_web":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Search_Web_Requests.append(t)
                            else:
                                Loaded_Search_Web_Requests.append(trigger)
                    elif function == "F_wait":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Wait_Words_Requests.append(t)
                            else:
                                Loaded_Wait_Words_Requests.append(trigger)

                    elif function == "F_quit":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Quit_Words_Requests.append(t)
                            else:
                                Loaded_Quit_Words_Requests.append(trigger)

                    elif function == "F_sort_results":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Sort_Results_Requests.append(t)
                            else:
                                Loaded_Sort_Results_Requests.append(trigger)

                    elif function == "F_add_trigger":
                        check_trigger = Special_Syntax(trigger, CMDFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Add_Triggers_Requests.append(t)
                            else:
                                Loaded_Add_Triggers_Requests.append(trigger)
    else:

        print("\n-Trinity:Error:%s not found." % CMDFILE)
        sys.exit()
    PRINT("\n-Trinity:CMDFILE Loaded")
    #print("Loaded_Read_Results:",Loaded_Read_Results)
    #if len(Loaded_Read_Results) == 0:
    #    exit()
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

                if verb not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(verb)
                    Loaded_Verbs_Words_List.append(verb)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((verb, alf))
                            if not alf in Loaded_Mix_Functions_verbs:
                                Loaded_Mix_Functions_verbs[alf] = []
                            if not verb in Loaded_Mix_Functions_verbs[alf]:
                                Loaded_Mix_Functions_verbs[alf].append(verb)
                    else:
                        Loaded_Mix_Actions_Functions.append((verb, functions))
                        if not functions in Loaded_Mix_Functions_verbs:
                            Loaded_Mix_Functions_verbs[functions] = []
                        if not verb in Loaded_Mix_Functions_verbs[functions]:
                            Loaded_Mix_Functions_verbs[functions].append(verb)

                if ind1 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(ind1)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((ind1, alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((ind1, functions))

                if ind2 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(ind2)

                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((ind2, alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((ind2, functions))

                if cond1 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(cond1)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((cond1, alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((cond1, functions))

                if cond2 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(cond2)

                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((cond2, alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((cond2, functions))

                if sub1 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(sub1)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((sub1, alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((sub1, functions))

                if sub2 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(sub2)

                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((sub2, alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((sub2, functions))

                if participe not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(participe)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((participe, alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((participe, functions))

                if ind1 + suffix1 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(ind1 + suffix1)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((ind1 + suffix1, alf))
                            Loaded_Mix_Actions_Functions.append((ind1 + suffix1.replace("-", " "), alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((ind1 + suffix1, functions))
                        Loaded_Mix_Actions_Functions.append((ind1 + suffix1.replace("-", " "), functions))

                if ind2 + suffix1 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(ind2 + suffix1)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((ind2 + suffix1, alf))
                            Loaded_Mix_Actions_Functions.append((ind2 + suffix1.replace("-", " "), alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((ind2 + suffix1, functions))
                        Loaded_Mix_Actions_Functions.append((ind2 + suffix1.replace("-", " "), functions))

                if cond1 + suffix2 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(cond1 + suffix2)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((cond1 + suffix2, alf))
                            Loaded_Mix_Actions_Functions.append((cond1 + suffix2.replace("-", " "), alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((cond1 + suffix2, functions))
                        Loaded_Mix_Actions_Functions.append((cond1 + suffix2.replace("-", " "), functions))

                if cond2 + suffix3 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(cond2 + suffix3)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((cond2 + suffix3, alf))
                            Loaded_Mix_Actions_Functions.append((cond2 + suffix3.replace("-", " "), alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((cond2 + suffix3, functions))
                        Loaded_Mix_Actions_Functions.append((cond2 + suffix3.replace("-", " "), functions))

                if cond1 + suffix2 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(cond1 + suffix2)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((cond1 + suffix2, alf))
                            Loaded_Mix_Actions_Functions.append((cond1 + suffix2.replace("-", " "), alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((cond1 + suffix2, functions))
                        Loaded_Mix_Actions_Functions.append((cond1 + suffix2.replace("-", " "), functions))

                if cond2 + suffix3 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(cond2 + suffix3)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((cond2 + suffix3, alf))
                            Loaded_Mix_Actions_Functions.append((cond2 + suffix3.replace("-", " "), alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((sub2 + suffix3, functions))
                        Loaded_Mix_Actions_Functions.append((sub2 + suffix3.replace("-", " "), functions))

                if cond1 + suffix2 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(cond1 + suffix2)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((cond1 + suffix2, alf))
                            Loaded_Mix_Actions_Functions.append((cond1 + suffix2.replace("-", " "), alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((cond1 + suffix2, functions))
                        Loaded_Mix_Actions_Functions.append((cond1 + suffix2.replace("-", " "), functions))

                if cond2 + suffix3 not in Loaded_Actions_Words_Requests:
                    Loaded_Actions_Words_Requests.append(cond2 + suffix3)
                    if "***" in functions:
                        allowed_fonctions = functions.split("***")
                        for alf in allowed_fonctions:
                            Loaded_Mix_Actions_Functions.append((cond2 + suffix3, alf))
                            Loaded_Mix_Actions_Functions.append((cond2 + suffix3.replace("-", " "), alf))
                    else:
                        Loaded_Mix_Actions_Functions.append((cond2 + suffix3, functions))
                        Loaded_Mix_Actions_Functions.append((cond2 + suffix3.replace("-", " "), functions))

                with open(PREFILE, newline="") as csvfile2:
                    reader2 = csv.DictReader(csvfile2)

                    for row in reader2:
                        if "present1" in row:
                            present1 = row["present1"]
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

                        if not any("que" in var for var in [present1, present2, cond1, cond2]):
                            pre1 = present1 + "*" + verb
                            if not pre1 in Loaded_Actions_Words_Requests:
                                #                                    print(pres1)
                                Loaded_Actions_Words_Requests.append(pre1)
                                if "***" in functions:
                                    allowed_fonctions = functions.split("***")
                                    for alf in allowed_fonctions:
                                        Loaded_Mix_Actions_Functions.append((pre1, alf))
                                else:
                                    Loaded_Mix_Actions_Functions.append((pre1, functions))

                            pre2 = present2 + "*" + verb
                            if not pre2 in Loaded_Actions_Words_Requests:
                                #                                    print(pres2)
                                Loaded_Actions_Words_Requests.append(pre2)
                                if "***" in functions:
                                    allowed_fonctions = functions.split("***")
                                    for alf in allowed_fonctions:
                                        Loaded_Mix_Actions_Functions.append((pre2, alf))
                                else:
                                    Loaded_Mix_Actions_Functions.append((pre2, functions))

                            pre3 = cond1 + "*" + verb
                            if not pre3 in Loaded_Actions_Words_Requests:
                                #                                    print(pre3)
                                Loaded_Actions_Words_Requests.append(pre3)
                                if "***" in functions:
                                    allowed_fonctions = functions.split("***")
                                    for alf in allowed_fonctions:
                                        Loaded_Mix_Actions_Functions.append((pre3, alf))
                                else:
                                    Loaded_Mix_Actions_Functions.append((pre3, functions))

                            pre4 = cond2 + "*" + verb
                            if not pre4 in Loaded_Actions_Words_Requests:
                                #                                    print(pre4)
                                Loaded_Actions_Words_Requests.append(pre4)
                                if "***" in functions:
                                    allowed_fonctions = functions.split("***")
                                    for alf in allowed_fonctions:
                                        Loaded_Mix_Actions_Functions.append((pre4, alf))
                                else:
                                    Loaded_Mix_Actions_Functions.append((pre4, functions))

                        else:
                            pre1 = present1 + "*" + sub1
                            if not pre1 in Loaded_Actions_Words_Requests:
                                #                                    print(pres1)
                                Loaded_Actions_Words_Requests.append(pre1)
                                if "***" in functions:
                                    allowed_fonctions = functions.split("***")
                                    for alf in allowed_fonctions:
                                        Loaded_Mix_Actions_Functions.append((pre1, alf))
                                else:
                                    Loaded_Mix_Actions_Functions.append((pre1, functions))

                            pre2 = present2 + "*" + sub2
                            if not pre2 in Loaded_Actions_Words_Requests:
                                #                                    print(pres2)
                                Loaded_Actions_Words_Requests.append(pre2)
                                if "***" in functions:
                                    allowed_fonctions = functions.split("***")
                                    for alf in allowed_fonctions:
                                        Loaded_Mix_Actions_Functions.append((pre2, alf))
                                else:
                                    Loaded_Mix_Actions_Functions.append((pre2, functions))

        for k in Loaded_Mix_Functions_verbs:
            Loaded_Mix_Functions_verbs[k].append("pouvoir")
            Loaded_Mix_Functions_verbs[k].append("vouloir")
            Loaded_Mix_Functions_verbs[k].append("être")
            Loaded_Mix_Functions_verbs[k].append("falloir")
            Loaded_Mix_Functions_verbs[k].append("devoir")

    else:

        print("\n-Trinity:Error:%s not found." % ACTFILE)
        sys.exit()

    PRINT("\n-Trinity:ACTFILE Loaded")

    if os.path.exists(ALTFILE):
        with open(ALTFILE, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for line, row in enumerate(reader):
                line = line + 2

                if "function" in row:
                    function = row["function"]
                else:
                    continue

                if "trigger" in row:
                    trigger = row["trigger"]

                    if function == "F_trinity_name":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Trinity_Name_Requests.append(t)
                            else:
                                Loaded_Trinity_Name_Requests.append(trigger)
                    elif function == "F_trinity_mean":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Trinity_Mean_Requests.append(t)
                            else:
                                Loaded_Trinity_Mean_Requests.append(trigger)
                    elif function == "F_trinity_dev":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Trinity_Dev_Requests.append(t)
                            else:
                                Loaded_Trinity_Dev_Requests.append(trigger)
                    elif function == "F_trinity_script":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Trinity_Script_Requests.append(t)
                            else:
                                Loaded_Trinity_Script_Requests.append(trigger)
                    elif function == "F_trinity_help":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Trinity_Help_Requests.append(t)
                            else:
                                Loaded_Trinity_Help_Requests.append(trigger)
                    elif function == "F_prompt":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Prompt_Requests.append(t)
                            else:
                                Loaded_Prompt_Requests.append(trigger)
                    elif function == "F_rnd":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Rnd_Requests.append(t)
                            else:
                                Loaded_Rnd_Requests.append(trigger)
                    elif function == "F_repeat":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Repeat_Requests.append(t)
                            else:
                                Loaded_Repeat_Requests.append(trigger)
                    elif function == "F_show_history":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Show_History_Requests.append(t)
                            else:
                                Loaded_Show_History_Requests.append(trigger)

                    elif function == "F_search_history":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Search_History_Requests.append(t)
                            else:
                                Loaded_Search_History_Requests.append(trigger)
                    elif function == "F_read_link":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Read_Link_Requests.append(t)
                            else:
                                Loaded_Read_Link_Requests.append(trigger)

                    elif function == "F_read_results":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Read_Results.append(t)
                            else:
                                Loaded_Read_Results.append(trigger)

                    elif function == "F_play_audio":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Play_Audio_File_Requests.append(t)
                            else:
                                Loaded_Play_Audio_File_Requests.append(trigger)
                    elif function == "F_search_web":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Search_Web_Requests.append(t)
                            else:
                                Loaded_Search_Web_Requests.append(trigger)
                    elif function == "F_wait":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Wait_Words_Requests.append(t)
                            else:
                                Loaded_Wait_Words_Requests.append(trigger)
                    elif function == "F_quit":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Quit_Words_Requests.append(t)
                            else:
                                Loaded_Quit_Words_Requests.append(trigger)



                    elif function == "F_sort_results":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Sort_Results_Requests.append(t)
                            else:
                                Loaded_Sort_Results_Requests.append(trigger)

                    elif function == "F_add_trigger":
                        check_trigger = Special_Syntax(trigger, ALTFILE, line)
                        if check_trigger:
                            if isinstance(check_trigger, list):
                                for t in check_trigger:
                                    Loaded_Add_Triggers_Requests.append(t)
                            else:
                                Loaded_Add_Triggers_Requests.append(trigger)
    else:

        print("\n-Trinity:Error %s not found." % ALTFILE)
        sys.exit()

    PRINT("\n-Trinity:ALTFILE Loaded")
#    for his in Loaded_History_List:
#        print(his)       
#        if action_trigger:
#            goto = PostProd(txt,func_name_toadd,specific_trigger=must_contain,main_trigger=action_trigger)
#        else:
#        goto = PostProd(txt, func_name_toadd, specific_trigger=must_contain)

#            valid = checktrigger(
#                new_trigger,
#                funcname,
#                specific_trigger=specific_trigger,
#                main_action=main_trigger,
#            )






def Add_Trigger(trigger_input=None, func_name_to_add=None, specific_trigger=None):

    print("\n-Trinity:Dans la fonction Add_Trigger.\n")

    help_already_print = False
    help_already_ask = False
    
    functions_help = [
            (
                "Trinity_Name()",
                "pour avoir le nom du script de Trinity",
                "Salut ça va ?Comment tu t'appelle?",
                "comment * t'appelles",
                "[comment {tu t'appelles/vous vous appelez/t'appelles-tu/vous appelez-vous}/quel est {ton/votre} {nom/prénom}]",
                Loaded_Trinity_Name_Requests,
                "F_trinity_name",
            ),
            (
                "Trinity_Mean()",
                "pour avoir le sens du nom du script de Trinity",
                "Pourquoi on a décidé de t'appeler comme ça?",
                "pourquoi *t'appeler comme ça",
                "pourquoi [t'a-t-on/on t'a] [nommé{e/}/appelé{e/}] [ainsi/comme ça/trinity]",
                Loaded_Trinity_Mean_Requests,
                "F_trinity_mean",
            ),
            (
                "Trinity_Dev()",
                "pour connaitre le nom du créateur du script de Trinity",
                "Qui est-ce qui t'a créé ?",
                "qui * t'a créé",
                "qui [est-ce qui/] [t'a/vous a] [créé{e/}/fabriqué{e/}/développé{e/}/conçu{e/}]",
                Loaded_Trinity_Dev_Requests,
                "F_trinity_dev",
            ),
            (
                "Trinity_Help()",
                "pour avoir l'aide du script Trinity",
                "Affiche moi l'aide de ton script.",
                "affiche*moi *aide * ton script",
                "[montre{-/*/}/affiche{-/*/}] [moi/] [*/l']aide * [ton/votre/du] script [*trinity/]",
                Loaded_Trinity_Help_Requests,
                "F_trinity_help",
            ),
            (
                "Prompt()",
                "pour pouvoir écrire à Trinity",
                "J'ai besoin de t'écrire un truc.",
                "ai * de t'écrire",
                "[{lance/ouvre} {l'interpreteur/le clavier}/j{'ai besoin de/e dois} t'écrire}]",
                Loaded_Prompt_Requests,
                "F_prompt",
            ),
            (
                "Trinity_Script()",
                "pour afficher la source du script Trinity",
                "tu peux me montrer ton code source?",
                "peux* montrer * ton code",
                "[montre/affiche][{-/ }moi] [{ton/votre/le} code source/la source {du */de *}{ trinity/}]",
                Loaded_Trinity_Script_Requests,
                "F_trinity_script",
            ),
            (
                "Rnd()",
                "pour effectuer un choix aléatoire",
                "Peux-tu faire un choix entre 1 et 2?",
                "peux*tu * choix entre * et ",
                "[peux{-/*/ }tu/pouvez{-/*/ }vous] * [choi{x/sir}] * entre * et ",
                Loaded_Rnd_Requests,
                "F_rnd",
            ),
            (
                "Repeat()",
                "pour demander à Trinity de répéter",
                "J'ai rien compris tu peux me redire ça ?",
                "tu*peux* redire ça",
                "[{je n'/j'}ai {pas/rien} * compris] [peux{-/*/ }tu/pouvez{-/*/ }vous/tu peux/vous pouvez] répéter",
                Loaded_Repeat_Requests,
                "F_repeat",
            ),
            (
                "Show_History()",
                "pour faire afficher l'historique",
                "Tu peux m'afficher tout l'historique s'il te plaît?",
                "m'afficher * l'historique",
                "[montre/affiche/ouvre][{-/ }moi] l'historique",
                Loaded_Show_History_Requests,
                "F_show_history",
            ),
            (
                "Search_History()",
                "pour faire une recherche dans l'historique",
                "Regarde dans l'historique si tu trouve Albert Einstein",
                "regarde * l'historique * si * trouve",
                "[recherche{z/}/regarde{z/}/trouve{-/ }moi] * dans [ton/] l'historique",
                Loaded_Search_History_Requests,
                "F_search_history",
            ),
            (
                "Read_Link()",
                "pour lire une page web",
                "Tu peux me lire ce qu'il y a dans cette page web?",
                "tu*peux* lire * dans * page web",
                "[{lis/dis}{ moi/-moi/}] [ce qu'il y a/] [sur/dans] [ce{tte page/ site/s pages}/ce site]",
                Loaded_Read_Link_Requests,
                "F_read_link",
            ),
            (
                "Read_Results()",
                "pour lire les résultats d'une recherche",
                "Dis-moi ce que tu as trouvé dans les résultats",
                "dis-moi * trouvé * les résultats",
                "[{lis/dis}{ moi/-moi/}] [ce qu'il y a/ce que {tu as/vous avez} trouv{é/ez}] dans les résultats]",
                Loaded_Read_Results_Requests,
                "F_read_link",
            ),
            (
                "Play_Audio()",
                "Pour lire un fichier audio",
                "Tu peux me jouer ce fichier audio s'il te plaît?",
                "tu*peux* jouer * fichier audio",
                "[{lis/joue}{ moi/-moi/}] [ce qu'il y a/] [sur/dans] [ce{s/} fichier{s/}] ",
                Loaded_Play_Audio_File_Requests,
                "F_play_audio",
            ),
            (
                "Search_Web()",
                "Pour faire une recherche sur internet",
                "Fais-moi une recherche sur google a propos du big bang",
                "fais*moi recherche * google * a propos",
                "[recherche{z/}/regarde{z/}/trouve{-/ }moi] * [dans/sur/avec] * [google/internet/wikipedia]",
                Loaded_Search_Web_Requests,
                "F_search_web",
            ),
            (
                "Wait()",
                "Pour demander à Trinity d'attendre",
                "Minute papillon je ne suis pas près!",
                "Minute * je * suis pas près",
                "[attends{ moi/-moi/}/arrête] [*/] [je * suis pas près/]",
                Loaded_Wait_Words_Requests,
                "F_wait",
            ),
            (
                "Quit()",
                "Pour demander à Trinity de quitter le programme ou la fonction en cours",
                "Non c'est bon tu peux quitter Trinity.",
                "tu * quitter Trinity",
                "[{tu peux /vous pouvez} {quitter/partir} Trinit{y/i/ie}]",
                Loaded_Quit_Words_Requests,
                "F_quit",
            ),

            (
                "Add_Trigger()",
                "Pour ajouter un nouveau déclencheur de fonction",
                "j'aimerai ajouter un nouveau trigger.",
                "ajouter * nouveau * trigger",
                "[ajoute{r/z/} * [des/un/] [nouveau{x/}/nouvel{les/}] [déclencheur/activateur/trigger]",
                Loaded_Add_Triggers_Requests,
                "F_add_trigger",
            ),
        ]



    def print_help_with_syntax(choice_input): 


        try:
           choice_input = int(choice_input)
        except:
          for index, (_,_,_, _, _, _, function_name) in enumerate(functions_help, start=1):
                     if function_name == choice_input:
                          choice_input = index
                          break
          try:
             choice_input = int(choice_input)
          except Exception as e:
             print("\n-Trinity:print_help_with_syntax():Error:%s"%str(e))
             sys.exit()


        function_to_print = functions_help[choice_input - 1][0]
        function_description = functions_help[choice_input - 1][1]
        function_ex1 = functions_help[choice_input - 1][2]
        function_ex2 = functions_help[choice_input - 1][3]
        function_ex3 = functions_help[choice_input - 1][4]
        function_requests = functions_help[choice_input - 1][5]
        function_id_name = functions_help[choice_input - 1][6]


        if help_already_print:
            print(f"Vous avez choisi {function_to_print}: {function_description}")
            os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/prompt/2.wav")
            return(function_to_print)
        else:
            print(f"Vous avez choisi {function_to_print}: {function_description}")
            os.system("aplay -q %s/local_sounds/cmd/instruction.wav" % SCRIPT_PATH)


        print("\n\n\n\n")
        print("==Ajouter un nouveau déclencheur pour la fonction: %s =="%function_to_print)
        print("\n\n\n-Gardez la partie qui identifie l'action %s dans votre phrase."%function_description)
        print("\n-Par example si votre phrase complète ressemble à ceci:\n\n\t-",function_ex1)
        print("\n-J'aimerais que vous ne gardiez que cela:\n\n\t-", function_ex2)
        print("\n-Le symbole * est utilisé içi afin de ne pas tenir compte des mots qu'il peut y avoir à cette position.\n\n")
        print("\n\n-Voici les déclencheurs déjà enregistrés pour cette fonction:\n")

        if len(function_requests) > 25:

            first = function_requests[:10]
            left = len(function_requests) - 20
            last = function_requests[-10:]

            for n, i in enumerate(first):
                 print("\t%s-:%s" % (n, i))

            print("\n\t...(+ %s déclencheurs)..."%str(left))
            print("\t(Liste compléte dans %s et %s)\n"%(CMDFILE,ALTFILE))
            for n, i in enumerate(last,start=len(function_requests)-10):
                 print("\t%s-:%s" % (n, i))
        else:
             for n, i in enumerate(function_requests):
                 print("\t%s-:%s" % (n, i))

        if function_id_name in Loaded_Mix_Functions_verbs:
             print("\n\n-Voici la liste de verbes déjà associés à cette fonction:\n")
             for n, f in enumerate(Loaded_Mix_Functions_verbs[function_id_name]):
                        print("\t%s-:%s" % (n, f))
        else:
             PRINT("\n-Trinity:print_help_with_syntax():%s not in Loaded_Mix_Functions_verbs:"%function_id_name)
             for k in Loaded_Mix_Functions_verbs:
                 PRINT("-%s"%k)
             PRINT("\n-Trinity:But not:%s"%function_id_name)

        print("\n-Si votre phrase utilise l'un de ces verbes même sous une forme conjugué il n'est pas nécessaire de l'écrire.")
        print("\n-Vous pouvez néanmoins le faire si vous souhaitez que votre déclencheur soit plus précis.\n")
        print("\n-Les caractéres spéciaux et ponctuations sont automatiquement enlevés.\n")
        print("\n-Il est aussi possible de générer plusieurs déclencheurs en même temps en utilisant la syntaxe avancée par exemple:\n")
        special_ex = Special_Syntax(function_ex3, SCRIPT_PATH+"/Trinity.py", Get_Line)
        for t in special_ex:
            print("-\t%s"%t)
        print("\n-Tous ces déclencheurs ont été générés par cette commande:\n\n-\t%s"%(function_ex3))
##
        print("\n\n-Les symboles '[' et ']' servent à créer une liste d'éléments séparé par le symbole '/'.")
        print("-Les symboles '{' et '}' sont utilisés dans une liste pour créer une sous-liste d'éléments séparé par le symbole '/'.\n")

        return(function_id_name)

    def checktrigger(to_check, funcname, s_syntax=None):

        def has_syn(function_name, sentences, altlst=None):
            synlst = []
            syntoprint = []
            found_syn = []

            if altlst:
                for act in altlst:
                    synlst.append(act)
            else:
                for syn in Loaded_Mix_Actions_Functions:
                    act = syn[0]
                    fn = syn[1]
                    if fn == function_name:
                        # print("adding:",act)
                        synlst.append(act)
                        for v in Loaded_Verbs_Words_List:
                            if v in act and not v in syntoprint:
                                syntoprint.append(v)


            check_sentences = Special_Syntax(sentences, SCRIPT_PATH + "Trinity.py", Get_Line())
            if not check_sentences:
                return(False)
            
            if isinstance(check_sentences, list):
                 for sentence in check_sentences:
                      found = SeeknReturn(sentence, synlst)
                      if found:
                         found_syn.append(found)
            else:
                 found = SeeknReturn(sentences, synlst)
                 if found:
                         found_syn.append(found)

            if len(found_syn) == 0:
                os.system("aplay -q %s/local_sounds/cmd/triggers/atleast.wav" % (SCRIPT_PATH))
                if not altlst:
                    print(
                        "\n-Trinity:Votre phrase doit contenir au minimum l'un des mots suivant:\n\n%s\n\n"
                        % (syntoprint)
                    )
                    return False
                else:
                    print(
                        "\n-Trinity:Votre phrase doit contenir au minimum l'un des mots suivant:\n\n%s\n\n" % (altlst)
                    )
                    return False
            else:
                return True

        def minitts(tx, fname):

            try:

                client = tts.TextToSpeechClient()
                audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

                text_input = tts.SynthesisInput(text=tx)
                voice_params = tts.VoiceSelectionParams(language_code="fr-FR", name="fr-FR-Neural2-A")

                response = client.synthesize_speech(input=text_input, voice=voice_params, audio_config=audio_config)
                audio_response = response.audio_content
                try:
                    with open("%s/local_sounds/cmd/triggers/%s" % (SCRIPT_PATH, fname), "wb") as out:
                        out.write(audio_response)
                except Exception as e:
                    PRINT("\n-Trinity:Error:%s" % str(e))
            except Exception as e:
                PRINT("\n-Trinity:Error:%s" % str(e))

        def getwav(f, trigparts):


            function_wav = "%s/local_sounds/cmd/triggers/%s.wav"%(SCRIPT_PATH, f)

            if os.path.exists(function_wav):
                os.system("aplay -q %s"%function_wav)
            else:
                PRINT("\n-Trinity:Error getwav(): %s n'existe pas." % function_wav)
                return()

            to_rm = [" ","_","-","*","'"]
            for t in trigparts:
                t = unidecode(t.replace(" ", "_").replace("-", "_").replace("*", "_").replace("'", "_"))
                wavname = t + ".wav"
                while True:
                    if wavname[0] in to_rm:
                       wavname = wavname[1:]
                    else:
                       break
                while True:
                   if "__" in wavname:
                        wavname = wavname.replace("__","_")
                   else:
                        break

                if os.path.exists("%s/local_sounds/cmd/triggers/%s" % (SCRIPT_PATH, wavname)):
                    os.system("aplay -q %s/local_sounds/cmd/triggers/%s" % (SCRIPT_PATH, wavname))
                else:
                    print(
                        "\n-Trinity:Error Wave file not found:%s/local_sounds/cmd/triggers/%s" % (SCRIPT_PATH, wavname)
                    )
                    minitts(t, wavname)
                    if os.path.exists("%s/local_sounds/cmd/triggers/%s" % (SCRIPT_PATH, wavname)):
                        os.system("aplay -q %s/local_sounds/cmd/triggers/%s" % (SCRIPT_PATH, wavname))
            return ()

    ################################################
        if isinstance(to_check,list) and s_syntax:
            trigger_cmd = s_syntax
        else:

            trigger_cmd = to_check


        if specific_trigger:
            mandatory_trigger = has_syn(funcname,to_check,specific_trigger)

            if not mandatory_trigger:
                    return(False)



        ambiguity = Check_Ambiguity(to_check,to_match=func_name_to_add)

        if not ambiguity:

            if ambiguity is None:
                  PRINT("\n-Trinity:Add_Trigger():Check_Ambiguity():Main cmd trigger:None.")

            elif ambiguity is False:
                 PRINT("\n-Trinity:Add_Trigger():Check_Ambiguity():len(ambiguity) == 0")

            print("\n-Parfait,cette phrase semble déclencher la fonction:", funcname)
            os.system("aplay -q %s/local_sounds/cmd/valid.wav" % SCRIPT_PATH)
            os.system("aplay -q %s/local_sounds/cmd/save.wav" % SCRIPT_PATH)
            while True:
                rusure = input(
                    "\n-Sauvegarder cette phrase dans la base de données ?:\n\n%s\n\n-Votre choix:(oui/non/abandonner):"
                    % trigger_cmd
                ).lower()
                if rusure in ["oui", "non", "abandonner"]:
                    if rusure == "oui":
                        if isinstance(to_check,list):
                             for trigger in to_check:
                                 Write_csv(trigger, funcname, ALTFILE)
                        else:
                                Write_csv(to_check, funcname, ALTFILE)
                        return True
                    elif rusure == "non":
                        return False
                    elif rusure == "abandonner":
                        return True

        else:

            os.system("aplay -q %s/local_sounds/cmd/new_ambiguity.wav" % SCRIPT_PATH)

            print("\n-Cette phrase à déclenchée plusieurs commandes en même temps:\n%s\n" % trigger_cmd)

            for fnc, trigged in ambiguity.items():
                for t, p in trigged:
                    if s_syntax:
                        print("\n\n-Déclencheur généré:\n%s\n" % t)
                    print("\n-La fonction %s est déclenchée par cette partie: %s" % (fnc, p))
                if not s_syntax:
                    getwav(fnc, p)

            os.system("aplay -q %s/local_sounds/cmd/new_ambiguity2.wav" % SCRIPT_PATH)

##########################################################################
    if not trigger_input and not func_name_to_add and not specific_trigger:

        os.system("aplay -q %s/local_sounds/question/newtrigger.wav" % SCRIPT_PATH)


        for index, (function_name, function_description, _, _, _,_,_) in enumerate(functions_help, start=1):
            print(f"({index}) {function_name} :  {function_description}")

        while True:
            try:
                user_choice = int(input("\nChoisissez une fonction (1 à {}): ".format(len(functions_help))))
                if user_choice in range(1, len(functions_help) + 1):
                    break
            except:
                pass

        while True:

            selected_function = print_help_with_syntax(user_choice)
            help_already_print = True

            new_trigger = input("\n-Nouveau déclencheur pour la fonction %s :" % selected_function)
            checksyntax = Special_Syntax(new_trigger, SCRIPT_PATH + "Trinity.py", Get_Line())
            if not checksyntax:
                while True:
                    new_trigger = input("\n-Nouveau déclencheur pour la fonction %s :" % selected_function)
                    checksyntax = Special_Syntax(new_trigger, SCRIPT_PATH + "Trinity.py", Get_Line())
                    if checksyntax:
                        break
            if isinstance(checksyntax, list):
                valid = checktrigger(checksyntax, selected_function, new_trigger)
            else:
                valid = checktrigger(checksyntax, selected_function)

            if valid:
                return selected_function

    #  if trigger_input and func_name_to_add and specific_trigger:
    else:

        while True:
            print("\n\n===============\n\n")

            if not help_already_ask:
                os.system("aplay -q %s/local_sounds/cmd/question_trigger.wav" % SCRIPT_PATH)
                while True:
                    helpme = input(
"-Pouvez-vous m'aider à mieux intégrer cette phrase dans ma base de données?\n-Cela ne prendra pas longtemps.\n\nVotre Choix (oui/non):"
                    ).lower()
                    if helpme in ["oui", "non"]:
                        if "oui" in helpme:
                            helpme = True
                            help_already_ask = True
                        else:
                            helpme = False
                        break
            else:
                helpme = True

            if helpme:

                selected_function = print_help_with_syntax(func_name_to_add)
                help_already_print = True

                print("\n-Trinity:Voici votre phrase initial:\n%s\n"%trigger_input)


                new_trigger = input("\nNouvelle déclencheur pour la fonction %s :" % func_name_to_add)

                checksyntax = Special_Syntax(new_trigger, SCRIPT_PATH + "Trinity.py", Get_Line())
                if not checksyntax:
                     while True:
                         new_trigger = input("\n-Nouveau déclencheur pour la fonction %s :" % selected_function)
                         checksyntax = Special_Syntax(new_trigger, SCRIPT_PATH + "Trinity.py", Get_Line())
                         if checksyntax:
                             break

                if isinstance(checksyntax, list):
                     valid = checktrigger(checksyntax, func_name_to_add, new_trigger)
                else:
                     valid = checktrigger(checksyntax, func_name_to_add)

                if valid:
                    return func_name_to_add
            else:
                os.system("aplay -q %s/local_sounds/cmd/sorry.wav" % SCRIPT_PATH)
                Write_csv(trigger_input, func_name_to_add, ALTFILE)
                return func_name_to_add


def Get_Line():
    try:
        frame = inspect.currentframe()
        numero_ligne = frame.f_back.f_lineno
        return numero_ligne
    except Exception as e:
        PRINT("-Trinity:Error:Get_Line():%s" % str(e))
        return 0


def SeeknReturn(var_to_check, list_elements):
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
    return found_lst


def Disambiguify(ambiguities, txt):

    PRINT("\n-Trinity:Disambiguify()")

    def bestvalue(dictionary, ordered):
        if not dictionary:
            return False
        values = [dictionary[key] for key in ordered]
        max_value = max(values)
        count_max_value = values.count(max_value)
        if count_max_value == 1:
            max_value_key = ordered[values.index(max_value)]
            return max_value_key
        return False

    def bonuspoint(txt, function_tomatch):

        bonus = 0
        bonusyn = 0
        print("\n-Trinity:function_tomatch:%s" % function_tomatch)
        for af in Loaded_Mix_Actions_Functions:
            action = af[0]
            function = af[1]

            if action in txt and function == function_tomatch:
                PRINT("Bonus point +1 %s in txt and %s is matching %s" % (action, function, function_tomatch))
                bonus += 1

                for syn_group in Loaded_Synonyms_Words_List:
                    for synonym in syn_group:
                        if synonym in txt:
                            for newsyn in syn_group:

                                newtxt = txt.replace(synonym, newsyn)

                                get_triggers = Check_Ambiguity(newtxt, to_get=function_tomatch)

                                if get_triggers:
                                    bonusyn = len(get_triggers[function_tomatch][1])

                                bonusyn += len(SeeknReturn(newtxt, Loaded_Alternatives_Triggers))

                                bonus += bonusyn

        return bonus

    fnc_to_add = None
    trigger_words_toadd = None
    must_contain = None

    score_function = {}
    triggered_parts = {}

    for function_name, seek_results in ambiguities.items():
        for result in seek_results:
            txt_checked = result[0]
            triggers_found = result[1]

#            bonus = bonuspoint(txt, function_name)
            bonus = 0
            score_function[function_name] = len(triggers_found) + bonus
            triggered_parts[function_name] = triggers_found

    sorted_score = dict(sorted(score_function.items(), key=lambda item: item[1], reverse=True))

    ordered_list = list(dict(sorted(score_function.items(), key=lambda item: item[1], reverse=True)).keys())

    winner = bestvalue(sorted_score, ordered_list)

    if winner:

        PRINT("\n-Trinity:%s has the higher confidence score.\n" % winner)
        for n, (fnc) in enumerate(ordered_list):
            PRINT(
                "\n-Trinity:Commande:%s\n-Déclenchée par %s parties:%s\n-Score de Confiance:%s"
                % (
                    fnc,
                    len(triggered_parts[fnc]),
                    triggered_parts[fnc],
                    score_function[fnc],
                )
            )

        return winner
    else:
        print("\n\n===============\n\n\n-Trinity:Cette phrase à déclenchée plusieurs commandes en même temps:")
        print("\n-Trinity:Votre phrase:", txt)

    os.system("aplay -q %s" % (SCRIPT_PATH + "/local_sounds/cmd/ambiguty.wav"))

    while True:
        for n, (fnc) in enumerate(ordered_list):
            print(
                "\n-Trinity:Commande:%s\n-Déclenchée par %s parties:%s\n-Score de Confiance:%s"
                % (
                    fnc,
                    len(triggered_parts[fnc]),
                    triggered_parts[fnc],
                    score_function[fnc],
                )
            )
            print("\n==\n-Trinity:Pour choisir cette commande (%s) tapez:%s\n==\n" % (fnc, n))

            if n + 1 == 1:
                os.system("aplay -q %s/local_sounds/cmd/intro_%s.wav" % (SCRIPT_PATH, fnc))
            elif n + 1 > 1 and n + 1 < len(ordered_list):
                os.system("aplay -q %s/local_sounds/cmd/%s.wav" % (SCRIPT_PATH, fnc))
            elif n + 1 == len(ordered_list):
                os.system("aplay -q %s/local_sounds/cmd/outro_%s.wav" % (SCRIPT_PATH, fnc))

        print("\n==\n-Trinity:Pour choisir une autre fonction tapez:%s\n==\n" % len(sorted_score))

        print("\n==\n-Trinity:Si ce n'était pas une commande tapez:%s\n==\n" % str(len(sorted_score) + 1))

        os.system("aplay -q %s/local_sounds/cmd/hit%s.wav" % (SCRIPT_PATH, str(len(sorted_score)+1)))

        response = input("\n-Trinity:Choisissez la bonne réaction pour cette phrase:")
        try:
            #           if 1 == 1 :
            response = int(response.strip())
            if response > len(sorted_score) + 1:
                continue
            elif response == len(sorted_score) + 1:
                return False
            elif response == len(sorted_score):
                return Add_Trigger()
            else:
                fnc_to_add = ordered_list[response]
                PRINT("\n-Trinity:Disambiguify():fnc_to_add:%s" % fnc_to_add)
                trigger_words_toadd = sorted_score[fnc_to_add]
                PRINT("\n-Trinity:Disambiguify():trigger_words_toadd:%s" % trigger_words_toadd)
                must_contain = triggered_parts[ordered_list[response]]
                break
        except Exception as e:
            PRINT("\n-Trinity:Disambiguify():response:error:%s"%str(e))

    if fnc_to_add and trigger_words_toadd and must_contain:

        print("\n-Trinity:La fonction %s à été choisie pour cette phrase.\n" % fnc_to_add)

#        goto = PostProd(txt, func_name_toadd, specific_trigger=must_contain)

        goto = Add_Trigger(txt, fnc_to_add, must_contain)

        if goto:
            return goto
        else:
            return False
    else:
        if not fnc_to_add:
            PRINT("\n-Trinity:Disambiguify():fnc_to_add is missing")
        if not trigger_words_toadd:
            PRINT("\n-Trinity:Disambiguify():trigger_words_toadd is missing")
        if not must_contain:
            PRINT("\n-Trinity:Disambiguify():must_contain is missing")
        return False


def Check_Ambiguity(txt_input,allowed_functions=None, to_match=None, to_get=None,from_function=None):

    new_ambiguity = {}
    main_check = False

    if isinstance(txt_input, list):
        PRINT("\n-Trinity:Check_Ambiguity():Verification d'une liste de déclencheurs.")
        Triggers = txt_input
    else:
        PRINT("\n-Trinity:Check_Ambiguity():Verification d'un déclencheur.")
        Triggers = [txt_input]

    for trigger in Triggers:

        PRINT("\n-Trinity:Check_Ambiguity():vérification de:%s"%trigger) 

        found_actions_triggers = SeeknReturn(trigger, Loaded_Actions_Words_Requests)  ##
        found_alt_triggers = SeeknReturn(trigger, Loaded_Alternatives_Triggers)  ##

        found_add_trigger = ("F_add_trigger", SeeknReturn(trigger, Loaded_Add_Triggers_Requests))

        found_trinity_name = ("F_trinity_name", SeeknReturn(trigger, Loaded_Trinity_Name_Requests))

        found_trinity_mean = ("F_trinity_mean", SeeknReturn(trigger, Loaded_Trinity_Mean_Requests))

        found_trinity_dev = ("F_trinity_dev", SeeknReturn(trigger, Loaded_Trinity_Dev_Requests))

        found_trinity_script = ("F_trinity_script", SeeknReturn(trigger, Loaded_Trinity_Script_Requests))

        found_trinity_help = ("F_trinity_help", SeeknReturn(trigger, Loaded_Trinity_Help_Requests))

        found_prompt = ("F_prompt", SeeknReturn(trigger, Loaded_Prompt_Requests))

        found_rnd = ("F_rnd", SeeknReturn(trigger, Loaded_Rnd_Requests))

        found_repeat = ("F_repeat", SeeknReturn(trigger, Loaded_Repeat_Requests))

        found_read_results = ("F_read_results",SeeknReturn(trigger, Loaded_Read_Results))

        found_show_history = ("F_show_history",SeeknReturn(trigger, Loaded_Show_History_Requests))

        found_search_history = ("F_search_history",SeeknReturn(trigger, Loaded_Search_History_Requests))

        found_search_web = ("F_search_web", SeeknReturn(trigger, Loaded_Search_Web_Requests))

        found_read_link = ("F_read_link", SeeknReturn(trigger, Loaded_Read_Link_Requests))

        found_play_audio = ("F_play_audio", SeeknReturn(trigger, Loaded_Play_Audio_File_Requests))

        found_wait = ("F_wait", SeeknReturn(trigger, Loaded_Wait_Words_Requests))

        found_quit = ("F_quit", SeeknReturn(trigger, Loaded_Quit_Words_Requests))

        found_sort = ("F_sort_results", SeeknReturn(trigger, Loaded_Sort_Results_Requests))

        print("found_quit:",found_quit)

        if allowed_functions:
             allowed_functions.append("F_wait")
             allowed_functions.append("F_quit")
             Tmp_Found_Lists = [
                 found_add_trigger,
                 found_trinity_name,
                 found_trinity_mean,
                 found_trinity_dev,
                 found_trinity_help,
                 found_prompt,
                 found_rnd,
                 found_repeat,
                 found_show_history,
                 found_search_history,
                 found_search_web,
                 found_read_link,
                 found_play_audio,
                 found_wait,
                 found_sort,
                 found_read_results,
             ]

#             Found_List = [f for f in Tmp_Found_Lists if f[0] in allowed_functions]
             Found_Lists = []
             for f in Tmp_Found_Lists:
                 if f[0] in allowed_functions:
#                      print("f[0] in allowed_functions::",f[0])
                      try:
                          if f[1]:
                              Found_Lists.append(f)
                      except Exception as e:
                          PRINT("\n-Trinity:Check_Ambiguity():failed:Found_Lists:", str(e))
             print("Found_List:",Found_Lists)
        else:
             Found_Lists = [
                 found_add_trigger,
                 found_trinity_name,
                 found_trinity_mean,
                 found_trinity_dev,
                 found_trinity_help,
                 found_prompt,
                 found_rnd,
                 found_repeat,
                 found_show_history,
                 found_search_history,
                 found_search_web,
                 found_read_link,
                 found_play_audio,
                 found_wait,
                 found_quit,
                 found_sort,
             ]

        if found_actions_triggers or found_alt_triggers:

            main_check = True

            for seek_tuple in Found_Lists:

                function_name = seek_tuple[0]
                triggers_found = seek_tuple[1]

                PRINT("function_name:%s triggers_found:%s"%(function_name,triggers_found))

                if to_match:
                    if triggers_found and to_match != function_name:
                        if function_name in new_ambiguity:
                            new_ambiguity[function_name].append((trigger, triggers_found))
                        else:
                            new_ambiguity[function_name] = [(trigger, triggers_found)]
                elif to_get:
                    if triggers_found and to_get == function_name:
                        if function_name in new_ambiguity:
                            new_ambiguity[function_name].append((trigger, triggers_found))
                        else:
                            new_ambiguity[function_name] = [(trigger, triggers_found)]
                else:
                    if triggers_found:
                        if function_name in new_ambiguity:
                            new_ambiguity[function_name].append((trigger, triggers_found))
                        else:
                            new_ambiguity[function_name] = [(trigger, triggers_found)]


    if main_check or to_get: # or to_match
        if len(new_ambiguity) > 0:
            PRINT("\n-Trinity:Check_Ambiguity():main_check or to_get:new_ambiguity:\n%s"%new_ambiguity)
            return new_ambiguity
        else:

            PRINT("\n-Trinity:Check_Ambiguity():main_check or to_get:failed:found_actions_triggers:\n%s"%found_actions_triggers)
            PRINT("\n-Trinity:Check_Ambiguity():main_check or to_get:failed:found_alt_triggers:\n%s"%found_alt_triggers)
            return False
    else:
        PRINT("\n-Trinity:Check_Ambiguity():main_check:%s or to_get:%s"%(main_check,to_get))
        return None



def Dbg_Search():

    PRINT("\n\n-Trinity:Dans la fonction Dbg_Search()")
    while True:
         print("\n\t-1: F_search_history")
         print("\t-2: F_search_web")
         user_input = input("\n-Trinity:Dbg_Search():Choix fonction [1/2]:")
         if user_input == "1":
            user_input = "F_search_history"
            break
         elif user_input == "2":
             user_input = "F_search_web"
             break
    txt_input = input("\n-Trinity:Dbg_Search():Phrase à verifier:")
    output = Isolate_Search(txt_input, user_input)
    print("\n-Trinity:Dbg_Search():Output:%s"%output)
    return Dbg_Search()




def Dbg_Input():
    PRINT("\n-Trinity:Dans la fonction Dbg_Input()")
    user_input = input("\n-Trinity:Dbg_Input():Comment puis-je vous aider ?:")
    if len(str(user_input)) > 0:

            cmd = Commandes(user_input)
            if not cmd:
                print("\n-Trinity:Dbg_Input():Pas de cmd")
                return Dbg_Input()
            else:
                print("\n-Trinity:Dbg_Input():commande:%s"%cmd)
                return Dbg_Input()
    else:
        print("\n-Trinity:Dbg_Input():Pas d'input")
        return Dbg_Input()

def Commandes(txt=None,allowed_functions=None,from_function=None):

    decoded = unidecode(
             txt.lower()
            .replace(",", " ")
            .replace("!", " ")
            .replace("?", " ")
            .replace("  ", " ")
            .replace(".", " ")
            )

    #    filter = ["s'il te plait","si te plait","sil te plait","merci"," stp "]
    #    to_remove = [" fais ","estce"," peux faire "," recherche ","faismoi"," fais ","peux ","fais recherche "," parle ","s'il te plait"," stp "," svp"," sur ","sil plait"]
    #    decoded = SeeknDestroy(filter, decoded)
    if allowed_functions:
        ambiguity = Check_Ambiguity(decoded,allowed_functions)
    else:
        ambiguity = Check_Ambiguity(decoded)
    goto = None

    if ambiguity is None:
        PRINT("\n-Trinity:Commandes():Check_Ambiguity():Main cmd trigger:None.")
    elif ambiguity is False:
        PRINT("\n-Trinity:Commandes():Check_Ambiguity():len(ambiguity) == 0")
    elif len(ambiguity) > 1:
        PRINT("\n-Trinity:Commandes():Ambiguités détectée.")
        goto = Disambiguify(ambiguity, decoded)
    elif len(ambiguity) == 1:
        PRINT("\n-Trinity:Commandes():Commande détecté.")
        goto = next(k for k in ambiguity)

    if CMD_DBG:
       if ambiguity:
           PRINT("\n-Trinity:Commandes():len(ambiguity):%s"%len(ambiguity))
       else:
           PRINT("\n-Trinity:Commandes():ambiguity:%s"%ambiguity)

       PRINT("%s"%ambiguity)
       return(goto)


    if from_function:
       print("from_function:",from_function)
       if goto:
          print("goto:",goto)
       print("txt:",txt)
       print("allowed_functions:",allowed_functions)

    if goto:

        PRINT("\n-Trinity:Commandes():Va dans la fonction :%s" % goto)

        #Commandes(txt, allowed_functions, "Results_Hub")


        if goto == "F_add_trigger":
            Add_Trigger()
            return True

        if goto == "F_wait":
            Wait()
            return True

        elif goto == "F_trinity_name":
            os.system("aplay -q %s" % (SCRIPT_PATH + "/local_sounds/saved_answer/trinity.wav"))
            return True

        elif goto == "F_trinity_mean":
            os.system("aplay -q %s" % (SCRIPT_PATH + "/local_sounds/saved_answer/matrix.wav"))
            return True
        elif goto == "F_trinity_dev":
            os.system("aplay -q %s" % (SCRIPT_PATH + "/local_sounds/saved_answer/botmaster.wav"))
            return True

        elif goto == "F_rnd":
            rnd = str(random.randint(1, 2))
            ouinon = SCRIPT_PATH + "/local_sounds/ouinon/" + rnd + ".wav"
            os.system("aplay -q %s" % ouinon)
            return True
        elif goto == "F_repeat":
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/repeat/isaid.wav")
            os.system("aplay -q %s" % SCRIPT_PATH + "tmp/current_answer.wav")
            return True

        elif goto == "F_prompt":
            Prompt()
            return True
        elif goto == "F_trinity_help":
            os.system("aplay -q %s" % (SCRIPT_PATH + "/local_sounds/saved_answer/help.wav"))
            return True
        elif goto == "F_play_audio":
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/question/sound_file.wav")
            sound_input = input("Entrez le chemin du fichier à lire:")
            if sound_input.endswith(".wav"):
                Play_Response(sound_input, stayawake=False, savehistory=False)
                return True
            else:
                return True

        elif goto == "F_show_history":

            Show_History()
            return True

        elif goto == "F_search_history":

            Search_History(decoded)

            return True

        elif goto == "F_read_link":
            ReadLink(txtinput=decoded)

            return True
        elif goto == "F_search_web":

            if "wikipedia" in decoded: 
                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/server/wikipedia.wav")
                Wikipedia(decoded)
                return True
            else:
                Google(decoded)
                return True

        else:
            return False
    else:
        print("return false")
        return False


def GetTitleLink(txt, site=None):
    PRINT("\n-Trinity:Dans la fonction GetTitleLink()")
    PRINT("\n-Trinity:txt:", txt)
    PRINT("\n-Trinity:txt:", site)

    SearchFallback = False

    if len(GOOGLE_KEY) != 0 and len(GOOGLE_ENGINE) != 0:

        PRINT("\n-Trinity:Using Custom Search Google Api.")

        try:
            google_query = "https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s&start=1" % (
                GOOGLE_KEY,
                GOOGLE_ENGINE,
                txt,
            )

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
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_Google.wav")
            PRINT("\n-Trinity:Custom search Error:", str(e))
            SearchFallback = True

        if len(title_search) == 0:
            PRINT("\n-Trinity:-Google() no result from google")
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_no_result_google.wav")
            SearchFallback = True
        else:
            return title_search

    if (len(GOOGLE_KEY) == 0 and len(GOOGLE_ENGINE) == 0) or SearchFallback == True:

        try:
            google_result = googlesearch.search(txt, num_results=10, lang="fr", advanced=True)

            title_search = ""

            for g in google_result:
                if site:
                    if site in g.url:
                        PRINT("\n-Trinity:google_result:", g.title)
                        title_search = g.title
                        break
                else:
                    PRINT("\n-Trinity:google_result:", g.title)
                    title_search = g.title
                    break

            if len(title_search) == 0:
                PRINT("\n-Trinity:GetTitleLink no result from google")
                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_no_result_google.wav")
                return None

            else:
                return title_search

        except Exception as e:
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_google.wav")
            PRINT("\n-Trinity:Error:", str(e))
            return None

    return None


def ReadLink(txtinput=None, titleinput=None, urlinput=None):

    PRINT("\n-Trinity: txtinput: %s", txtinput)

    regex = re.compile(
        r"^(?:http://|https://|ftp://|.)"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

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
                wiki_title = GetTitleLink(txtinput, "wikipedia")
            else:
                wiki_title = titleinput

            if wiki_title:
                PRINT("\n-Trinity:wiki_title:", wiki_title)
                return Wikipedia(txtinput, Title=wiki_title)

            else:
                PRINT("\n-Trinity:no title using txtinput:", txtinput)
                return Wikipedia(txtinput)
        else:

            try:

                response = requests.get(urlinput)
                soup = BeautifulSoup(response.text, "html.parser")
                text_data = ""
                for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"]):
                    text_data += tag.get_text()
                if len(text_data) > 0:
                    os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ok/reading_link.wav")
                    last_sentence.put(txtinput + " %s" % urlinput)
                    Text_To_Speech(text_data, stayawake=True)
                    return ()
                else:
                    os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_read_link_no_txt.wav")
                    return ()
            except Exception as e:
                PRINT("\n-Trinity:Error:", str(e))
                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_Loaded_Read_Link_Requests.wav")

    else:
        os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/question/read_link_url.wav")

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
                soup = BeautifulSoup(response.text, "html.parser")
                text_data = ""
                for tag in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"]):
                    text_data += tag.get_text()
                if len(text_data) > 0:
                    os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ok/reading_link.wav")
                    last_sentence.put(txtinput + " %s" % urlinput)
                    Text_To_Speech(text_data, stayawake=True)
                    return ()
                else:
                    os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_read_link_no_txt.wav")
                    return ()
            except Exception as e:
                PRINT("\n-Trinity:Error:", str(e))
                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_Loaded_Read_Link_Requests.wav")
                return ()
    else:
        os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_url_not_valid.wav")
        return ()


def Google(to_search, rnbr=50,wiki_failed=False):  # ,tstmode = True):

    Exit = False
    SearchFallback = False
    google_result = []

    original_search = to_search

    to_search = Isolate_Search(to_search,"F_search_web")

    PRINT("\n-Trinity:Google():to_search:%s"%to_search)
    PRINT("\n-Trinity:Google():wiki_failed:%s"%wiki_failed)

    if len(GOOGLE_KEY) != 0 and len(GOOGLE_ENGINE) != 0:

        PRINT("\n-Trinity:Using Custom Search Google Api.")

        maxpage = int(rnbr / 10)
        for page in range(maxpage):
            start = page * 10 + 1
            try:
                if wiki_failed:
                    siteSearch = "&siteSearch=fr.wikipedia.org&siteSearchFilter=i"
                else:
                    siteSearch = ""

                google_query = "https://www.googleapis.com/customsearch/v1?key=%s&cx=%s&q=%s%s&start=%s" % (
                    GOOGLE_KEY,
                    GOOGLE_ENGINE,
                    to_search,
                    siteSearch,
                    start,
                )

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
                        except:
                            description = "no description"
                    url = result.get("link")

                    google_result.append({"google_title":title,"google_description":description, "google_url":url})

            except Exception as e:
                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_Google.wav")
                PRINT("\n-Trinity:Custom search Error:", str(e))
                SearchFallback = True

        if len(google_result) == 0:
            PRINT("\n-Trinity:-Google() no result from google")
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_no_result_google.wav")
            return ()

    if (len(GOOGLE_KEY) == 0 and len(GOOGLE_ENGINE) == 0) or SearchFallback == True:

        PRINT("\n-Trinity:Using module googlesearch.")
        try:
            google_query = googlesearch.search(to_search, num_results=rnbr, lang="fr", advanced=True)

            for result in google_query:

                title = result.title
                description = result.description
                url = result.url
                google_result.append({"google_title":title,"google_description":description, "google_url":url})

#                if wiki_failed:
#                   if "wikipedia" in url:
#                       google_result.append((title, description, url))

            if len(google_result) == 0:
                PRINT("\n-Trinity:-Google() no result from google")
                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_no_result_google.wav")
                return ()

        except Exception as e:
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_Google.wav")
            PRINT("\n-Trinity:Googlesearch Error:", str(e))
            return ()

    top20 = google_result[:20]

    return(Results_Hub(google_result,top20,from_function="Google"))


def Wikipedia(to_search, Title=None, FULL=None):

    to_search = to_search.strip()


    original_search = to_search

    to_search = Isolate_Search(to_search,"F_search_web")


    PRINT("\n-Trinity:Dans la fonction Wikipedia.")
    PRINT("\n-Trinity:to_search:", to_search)
    PRINT("\n-Trinity:title:", Title)
    PRINT("\n-Trinity:FULL:", FULL)


    try:
        if Title:
            wiki_search = Title
        else:

            if not "wikipedia" in to_search.lower():
                to_search_title = "wikipedia " + to_search
            else:
                to_search_title = to_search

            wiki_search = GetTitleLink(to_search_title, site="wikipedia")

        if not wiki_search:
            PRINT("\n-Trinity:Wikipedia no result from google")
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_no_result_wiki.wav")

            return(Google(original_search,wiki_failed=True))

        wikipedia.set_lang("fr")

        query_list = wikipedia.search(wiki_search)
        #        query_list = [i.replace(" ","_") for i in query_list]

        if len(query_list) > 0:
            for r in query_list:
                PRINT("\n-Trinity:wiki reponse:", r)
        else:
            PRINT("\n-Trinity:no result from wikipedia")
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_no_result_wiki.wav")
            return(Google(original_search,wiki_failed=True))

        if len(query_list) > 0:
            PRINT("\n-Trinity:Going to search : ", query_list[0])
            try:
                if not FULL:

                    os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/question/wikipedia.wav")

                    Start_Thread_Record()

                    if Wait_for("audio"):
                        audio = audio_datas.get()
                        (
                            transcripts,
                            transcripts_confidence,
                            words,
                            words_confidence,
                            Err_msg,
                        ) = Speech_To_Text(audio)
                        txt, fconf = Check_Transcript(
                            transcripts,
                            transcripts_confidence,
                            words,
                            words_confidence,
                            Err_msg,
                        )

                    if len(txt) > 0:
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
                            os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ouinon/wiki_summary.wav")
                        if choice == "full":
                            os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ouinon/wiki_full.wav")
                    elif opinion == False:
                        choice = "summary"
                        os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ok/wiki_summary.wav")
                    elif opinion == True:
                        choice = "full"
                        os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ok/wiki_full.wav")

                elif FULL == True:
                    choice = "full"
                    os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ouinon/wiki_full.wav")

                if choice == "summary":

                    try:
                        summary = wikipedia.summary(query_list[0])
                    except Exception as e:
                        try:
                            summary = wikipedia.summary(title=query_list[0], auto_suggest=True)
                        except Exception as e:
                            PRINT("\n-Trinity:Error:", str(e))
                            try:
                                summary = wikipedia.summary(
                                    title=query_list[0].replace(" ", "").replace("_", ""),
                                    auto_suggest=True,
                                )
                            except Exception as e:
                                PRINT("\n-Trinity:Error:", str(e))
                                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_wiki.wav")
                                return(Google(original_search,wiki_failed=True))

#                    last_sentence.put(to_search)
                    last_sentence.put(original_search)
                    Text_To_Speech(summary, stayawake=True)
                    return ()

                else:

                    try:
                        page = wikipedia.page(query_list[0])
                        content = page.content
                    except Exception as e:
                        try:
                            page = wikipedia.page(title=query_list[0], auto_suggest=True)
                            content = page.content
                        except Exception as e:
                            PRINT("\n-Trinity:Error:", str(e))
                            try:
                                page = wikipedia.page(
                                    title=query_list[0].replace(" ", "").replace("_", ""),
                                    auto_suggest=True,
                                )
                                content = page.content
                            except Exception as e:
                                PRINT("\n-Trinity:Error:", str(e))
                                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_wiki.wav")
                                return(Google(original_search,wiki_failed=True))

                    if "== Notes" in content:
                        content = content.split("== Notes")[0]

                    if "=== Notes" in content:
                        content = content.split("=== Notes")[0]

                    if "===" in content:
                        content = content.replace("===", " ")

                    if "==" in content:
                        content = content.replace("== ", " ")

                    if len(content) > 0:
                        #last_sentence.put(to_search)
                        last_sentence.put(original_search)
                        Text_To_Speech(content, stayawake=True)
                        return ()

                    else:
                        PRINT("\n-Trinity:no result from content wikipedia")
                        os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_no_result_wiki.wav")
                        return ()
            except Exception as e:
                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_wiki.wav")
                PRINT("Error:", str(e))
                return(Google(original_search,wiki_failed=True))

    except Exception as e:
        local_sounds / errors / err_func_wiki.wav
        os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/errors/err_func_wiki.wav")
        PRINT("\n-Trinity:Error:", str(e))
        return(Google(original_search,wiki_failed=True))


def Prompt(allowed_functions=None,from_function=None):
    PRINT("\n-Trinity:Dans la fonction Prompt")
    if from_function == "Results_Hub":
        os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/question/search_history_cmds.wav")
    os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/prompt/2.wav")
    #    while True:
    if 1 == 1:
        user_input = input("\n-Trinity:Comment puis-je vous aider ?:")
        if len(str(user_input)) > 2:

            cmd = Commandes(user_input,allowed_functions=allowed_functions,from_function=from_function)
            if not cmd and not from_function:
                PRINT("\n-Trinity:Prompt():pas de cmd")
                return To_Gpt(str(user_input))
            elif not cmd and from_function:
                PRINT("\n-Trinity:Prompt():pas de cmd mais from_function:%s"%from_function)
                return("no cmd")
            elif cmd and from_function:
                PRINT("\n-Trinity:Prompt():cmd:%s  from_function:%s"%(cmd,from_function))
                return(cmd)
            else:
                Go_Back_To_Sleep()


def Check_Transcript(transcripts, transcripts_confidence, words, words_confidence, Err_msg=""):

    avg_conf = 0
    bad_word = []
    bad_word_conf = []
    final_confidence = False

    PRINT("\n-Trinity:checktranscript")

    if len(Err_msg) > 0:
        if Err_msg.startswith("Speech_To_Text:"):
            os.system("aplay -q  %s" % SCRIPT_PATH + "/local_sounds/errors/err_stt.wav")
            Text_To_Speech(Err_msg, stayawake=True)
            os.system("aplay -q  %s" % SCRIPT_PATH + "/local_sounds/errors/err_prompt.wav")
            return Prompt()

    if len(transcripts) > 0:
        PRINT("\n-Trinity:transcripts:\n\n%s" % transcripts)
        PRINT("\n-Trinity:transcripts_confidence:%s" % transcripts_confidence)

        if len(words) > 0 and len(words_confidence) > 0:
            for w, wc in zip(words, words_confidence):
                PRINT("\n-Trinity:confidence:%s word:%s" % (wc, w))
                if wc < 0.6:
                    PRINT("\n-Trinity:That word has bad confidence : %s %s" % (w, wc))
                    bad_word_conf.append(w)
            avg_conf = sum(words_confidence) / len(words_confidence)
            PRINT("\n-Trinity:Average words confidence :%s" % avg_conf)

        if transcripts_confidence == 0.0:
            # TODO
            # Google didnt care to give us a level of confidence...
            PRINT("\n-Trinity:Transcript no confidence level\n.")
            pass
        elif transcripts_confidence < 0.7:
            PRINT("\n-Trinity:Transcript has bad confidence\n.")
            final_confidence = False
        else:
            final_confidence = True
            PRINT("\n-Trinity:Transcript seems ok\n.")

        return (transcripts.replace("\\", ""), final_confidence)

    else:
        os.system("aplay -q  %s" % SCRIPT_PATH + "/local_sounds/errors/err_no_respons.wav")
        #      Go_Back_To_Sleep()
        return ("", False)


def Question(txt):

    PRINT("\n-Trinity:Dans la fonction Question")
    score = 0
    try:

        client = language_v1.LanguageServiceClient()
        document = language_v1.Document(content=txt, language="fr", type_=language_v1.Document.Type.PLAIN_TEXT)
        sentiment = client.analyze_sentiment(request={"document": document}).document_sentiment

        PRINT("\n-Trinity:Text: {}".format(txt))
        PRINT("\n-Trinity:Sentiment: {}, {}".format(sentiment.score, sentiment.magnitude))

        PRINT("\n\n\n-Trinity:Sentimentfull:\n%s" % sentiment)

        score = sentiment.score
    except Exception as e:
        PRINT("\n-Trinity:Error :%s" % str(e))

    if score > -0.15 and score < 0.15:
        PRINT("\n-Trinity:Score is None")
        score_sentiment.put(None)
    elif score < -0.15:
        PRINT("\n-Trinity:Score is False")
        score_sentiment.put(False)
    elif score > 0.15:
        PRINT("\n-Trinity:Score is True")
        score_sentiment.put(True)

    return ()


def Repeat(txt):

    negation = [
        "laisse tomber",
        "c'est pas grave",
        "non c'est bon",
        "j'ai pas envie",
        "j'ai plus envie",
        "non merci",
    ]
    Loaded_Prompt_Requests = [
        "affiche moi le prompt",
        "préfère l'écrire",
        "préfère écrire",
        "vais l'écrire",
        "va l'écrire",
        "vais te l'écrire",
        "t'as rien compris",
        "tu n'as rien compris",
    ]

    if "oui" in txt.lower() and not "non" in txt.lower():
        opinion = True
    elif "non" in txt.lower() and not "oui" in txt.lower():
        opinion = False
    else:
        Question(txt)
        Wait_for("question")
        opinion = score_sentiment.get()

    if opinion == False:
        no = any(element in txt.lower() for element in negation)
        if no:
            go_prompt = any(element in txt.lower() for element in Loaded_Prompt_Requests)
            if go_prompt:
                os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ok/1.wav")
                return Prompt()
            else:
                os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ok/1.wav")
                Go_Back_To_Sleep()
        else:
            os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ok/1.wav")

            return Commandes(txt)
    else:

        os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ok/1.wav")
        return Commandes(txt)

def Bad_Stt(txt):
    PRINT("\n-Trinity:Dans la fonction Bad_Stt")
    fname = "/tmp/last_bad_stt.wav"
    try:

        client = tts.TextToSpeechClient()
        audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

        text_input = tts.SynthesisInput(text=txt)
        voice_params = tts.VoiceSelectionParams(language_code="fr-FR", name="fr-FR-Neural2-A")

        response = client.synthesize_speech(input=text_input, voice=voice_params, audio_config=audio_config)
        audio_response = response.audio_content

        try:
            with open(SCRIPT_PATH + fname, "wb") as out:
                out.write(audio_response)
        except Exception as e:
            PRINT("\n-Trinity:Error:", str(e))
            sys.exit()

    except Exception as e:
        PRINT("\n-Trinity:Error:%s" % str(e))
        Err = True
        try:
            os.system('pico2wave -l fr-FR -w %s "%s"' % (SCRIPT_PATH + fname, txt))
        except Exception as e:
            PRINT("\n-Trinity:Error:", str(e))
            sys.exit()

    os.system("aplay -q %s" % SCRIPT_PATH + fname)


def Bad_Confidence(txt):
    PRINT("\n-Trinity:Dans la fonction Bad_Confidence")

    Orig_sentence = txt

    PRINT("\n-Trinity:txt:", txt)
    PRINT("\n-Trinity:Orig_sentence:", Orig_sentence)

    rnd = str(random.randint(1, 10))
    bad_sound = SCRIPT_PATH + "/local_sounds/badconf/" + rnd + ".wav"
    os.system("aplay -q %s" % bad_sound)

    Bad_Stt(txt)

    question_sound = SCRIPT_PATH + "/local_sounds/question/1.wav"
    os.system("aplay -q %s" % question_sound)

    Start_Thread_Record()

    if Wait_for("audio"):
        audio = audio_datas.get()
        transcripts, transcripts_confidence, words, words_confidence, Err_msg = Speech_To_Text(audio)
        txt, fconf = Check_Transcript(transcripts, transcripts_confidence, words, words_confidence, Err_msg)
        if len(txt) > 0:
            Question(txt)
            Wait_for("question")
        else:
            score_sentiment.put(False)
    opinion = score_sentiment.get()

    if opinion == None:
        choice = random.choice(["repeat", "send", "prompt"])
        if choice == "send":
            if len(Orig_sentence) > 0:
                os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ok/1.wav")
                return To_Gpt(Orig_sentence)
            else:
                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/forgot/1.wav")
                choice = random.choice(["repeat", "prompt"])
                if choice == "repeat":
                    os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/repeat/1.wav")
                    return Trinity("Repeat")
                if choice == "prompt":
                    os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/prompt/1.wav")
                    return Prompt()

        if choice == "repeat":
            os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/repeat/1.wav")
            return Trinity("Repeat")
        if choice == "prompt":
            os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/prompt/1.wav")
            return Prompt()
    elif opinion == False:
        choice = random.choice(["repeat", "prompt"])
        if choice == "repeat":
            os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/repeat/1.wav")
            return Trinity("Repeat")
        if choice == "prompt":
            os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/prompt/1.wav")
            return Prompt()
    elif opinion == True:
        os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/ok/1.wav")
        if len(Orig_sentence) > 0:
            return To_Gpt(Orig_sentence)
        else:
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/forgot/1.wav")
            choice = random.choice(["repeat", "prompt"])
            if choice == "repeat":
                os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/repeat/1.wav")
                return Trinity("Repeat")
            if choice == "prompt":
                os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/prompt/1.wav")
                return Prompt()


def Split_Text(txt):

    PRINT("\n-Trinity:Dans la fonction Split_text")
    result = []
    txt_len = len(txt)
    needle = 0
    while True:
        part = txt[needle : needle + 450]
        if len(part) >= 450:
            #            print("len part > 450:\n",part)
            last_ponct = part.rfind("\n")
            if last_ponct > 0:
                part = part[: last_ponct + 1]
            else:
                last_ponct = part.rfind(".")
                if last_ponct > 0:
                    part = part[: last_ponct + 1]
                else:
                    last_ponct = part.rfind(" ")
                    if last_ponct > 0:
                        part = part[: last_ponct + 1]
                    else:
                        part = txt[needle : needle + 250]
        else:
            #            print("len part < 450:\n",part)
            result.append(part.strip())
            break

        result.append(part.strip())

        if needle >= txt_len:
            break
        else:
            needle += len(part)

    return result


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
        PRINT("\n-Trinity:Error:%s" % str(e))
        Err_msg = "Speech_To_Text:" + str(e)
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
            PRINT("\n-Trinity:Error:%s" % str(e))

    if len(transcripts) > 0:
        print("\n-Trinity:User said:", transcripts)

    return (transcripts, transcripts_confidence, words, words_confidence, Err_msg)


def Text_To_Speech(txtinput, stayawake=False, savehistory=True):

    def Resample(file):
        try:
            to_rename = SCRIPT_PATH + "/tmp/resampled.wav"
            sample = sox.Transformer()
            sample.set_output_format(rate=24000)
            sample.build(file, to_rename)
            print("\n-Trinity:%s resampled to 24000." % file)
            os.rename(to_rename, file)
            print("\n-Trinity:%s saved." % file)
            return True
        except Exception as e:
            print("\n-Trinity:Error:Resample:", str(e))
            return False

    PRINT("\n-Trinity:Dans la fonction Text_To_Speech")

    PRINT("\n-Trinity:len(txtinput):", len(txtinput))

    print("\n-Trinity:\n\n%s\n\n" % txtinput)

    parsed_response = parse_response(str(txtinput))
    PRINT("\n-After Parse:\n%s\n\n" % parsed_response)

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

    for n, txt in enumerate(txt_list):
        time.sleep(0.5)
        leadn = str(n).zfill(4)
        #        if len(txt_list) > 1:
        #                fname = "/tmp/answer"+str(leadn)+".wav"
        #        else:
        #                fname = "/tmp/current_answer.wav"
        fname = "/tmp/answer" + str(leadn) + ".wav"
        Err_cnt = 0
        while True:
            Retry = False
            try:

                client = tts.TextToSpeechClient()
                audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.LINEAR16)

                text_input = tts.SynthesisInput(text=txt)
                voice_params = tts.VoiceSelectionParams(language_code="fr-FR", name="fr-FR-Neural2-A")

                response = client.synthesize_speech(input=text_input, voice=voice_params, audio_config=audio_config)
                audio_response = response.audio_content

                try:
                    with open(SCRIPT_PATH + fname, "wb") as out:
                        out.write(audio_response)
                    wav_list.append(SCRIPT_PATH + fname)
                except Exception as e:
                    PRINT("\n-Trinity:Error:", str(e))  # TODO
                    #                     err_list.append("Err_cnt:%s write(gtss)file:%s err:%s"%(str(Err_cnt),SCRIPT_PATH+fname,str(e)))
                    Err_cnt += 1
                    Retry = True

            except Exception as e:
                PRINT("\n-Trinity:Error:%s" % str(e))
                Err_cnt += 1
                Retry = True

            if Err_cnt == 2:
                Err_Tts = True
                Err_cnt = 0
                try:
                    os.system('pico2wave -l fr-FR -w %s "%s"' % (SCRIPT_PATH + fname, txt))
                    # RESAMPLE 16000 to 24000
                    wav_list.append(SCRIPT_PATH + fname)
                    Retry = False
                except Exception as e:
                    PRINT("\n-Trinity:Error:", str(e))
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
                print("\n-Trinity:Error:", str(e))
                Err_Sample = True
        else:
            print("\n-Trinity:Error:Le fichier %s n'existe pas.", str(f))
            Err_Skip = True

    #    print("to_sox:",to_sox)

    if len(to_sox) > 1:
        try:
            cbn = sox.Combiner()
            cbn.convert(samplerate=24000, n_channels=1)
            try:
                cbn.set_input_format(file_type=["wav" for i in to_sox])
            except Exception as e:
                print("\n-Trinity:Error:", str(e))
            cbn.build(to_sox, final_wav, "concatenate")
        except Exception as e:
            print("\n-Trinity:Error:Concatenation:", str(e))
            Err_Concatenation = True
    elif len(to_sox) == 1:
        try:
            sample = sox.Transformer()
            sample.set_output_format(rate=24000)
            sample.build(to_sox[0], final_wav)
        except Exception as e:
            PRINT("\n-Trinity:to_sox:\n%s" % to_sox[0])
            print("\n-Trinity:Error:pysox:", str(e))
            Err_Pysox = True

    if Err_Tts:
        os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/errors/err_tts.wav")
    if Err_Skip:
        os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/errors/err_skip_sox.wav")
        Move_To_Error_Folder = True
    if Err_Pysox:
        os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/errors/err_answer_sox.wav")
        Move_To_Error_Folder = True
    if Err_Sample:
        os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/errors/err_sample_sox.wav")
        Move_To_Error_Folder = True
    if Err_Concatenation:
        os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/errors/err_conc_sox.wav")
        Move_To_Error_Folder = True

    tmp_folder = str(SCRIPT_PATH + "/tmp/").replace("//", "/")
    err_folder = str(SAVED_ANSWER + "/saved_error/").replace("//", "/")

    to_skip = ["current_answer.wav", "last_bad_stt.wav"]

    wav_files = [f for f in os.listdir(tmp_folder) if f.endswith(".wav") and f not in to_skip]

    if Move_To_Error_Folder and len(to_sox) > 0:

        while True:
            characters = string.ascii_letters + string.digits
            rnd = "".join(random.choice(characters) for _ in range(5))
            rnd_folder = err_folder + rnd
            if not os.path.exists(rnd_folder):
                try:
                    os.makedirs(rnd_folder)
                    err_folder = rnd_folder
                    break
                except Exception as e:
                    print("\n-Trinity:Error:os.makedirs(rnd_folder):%s" % str(e))
                    break

        PRINT("\n-Trinity:Déplacements des fichiers wav temporaire vers %s" % err_folder)

        err_move = False
        for w in wav_files:
            try:
                move(tmp_folder + str(w), err_folder)
            except Exception as e:
                print("\n-Trinity:Error:Move:", str(e))
                err_move = True

        if err_move:
            os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/errors/err_while_moving_to_err.wav")
        else:
            os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/errors/err_move_to_err.wav")
    else:
        PRINT("\n-Trinity:Effacement des fichiers wav temporaire de %s" % tmp_folder)

        err_del = False
        for w in wav_files:
            try:
                os.remove(tmp_folder + str(w))
            except Exception as e:
                print("\n-Trinity:Error:Move:", str(e))
                err_del = True

        if err_del:
            os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/errors/err_del_wav.wav")

    if len(to_sox) > 0:

        if Err_Concatenation:
            return Play_Response(stay_awake=stayawake, save_history=savehistory, answer_txt=txtinput)

        else:
            return Play_Response(
                audio_response=final_wav,
                stay_awake=stayawake,
                save_history=savehistory,
                answer_txt=txtinput,
            )

    else:

        os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/errors/err_no_audio_sox.wav")

        if len(txtinput) > 0:

            os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/errors/err_no_audio_but_txt_sox.wav")
            print("\n\n-Trinity:Réponse:\n", txtinput)

            return Play_Response(stay_awake=stayawake, save_history=savehistory, answer_txt=txtinput)
        else:
            return Play_Response(stay_awake=stayawake, save_history=False)


#    return(Play_Response(audio_response=final_wav,stay_awake=stayawake,save_history=savehistory,answer_txt=txtinput))


def Play_Response(audio_response=None, stay_awake=False, save_history=True, answer_txt=None):
    PRINT("\n-Trinity:Dans la fonction Play_Response")

    if audio_response:
        os.system("aplay -q  " + audio_response)

    if save_history:
        if audio_response:
            Save_History(answer_txt)
        else:
            Save_History(answer_txt, no_audio=True)

    if not stay_awake:
        Go_Back_To_Sleep(True)


def dbg_queue():

    PRINT("\n-Trinity:sleep.empty:%s" % cancel_operation.empty())
    PRINT("\n-Trinity:start.empty:%s" % wake_me_up.empty())
    PRINT("\n-Trinity:chunks.empty:%s" % chunks.empty())
    PRINT("\n-Trinity:audio_datas:%s" % audio_datas.empty())


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
        Current_Category = []

    if go_trinity:
        PRINT("\n-Trinity:Retour vers trinity()\n")
        return Trinity("WakeMe")
    else:
        return ()


def Wait_for(action):
    PRINT("\n-Trinity:wait for %s" % action)

    while cancel_operation.empty():

        if action == "audio":
            if not audio_datas.empty():
                break

        if action == "question":
            if not score_sentiment.empty():
                break

    if not cancel_operation.empty():
        PRINT("\n-Trinity:Operation %s cancelled." % action)
        return False
    else:
        PRINT("\n-Trinity:Operation %s finished." % action)
        return True


#       time.sleep(1)


def similar(txt1, txt2):
    PRINT("\n-Trinity:txt1:", txt1)
    PRINT("\n-Trinity:txt2:", txt2)
    similarity = SequenceMatcher(None, txt1, txt2).ratio()
    PRINT("\n-Trinity:Similarity : ", similarity)
    return similarity


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    elif treebank_tag.startswith("V"):
        return wordnet.VERB
    elif treebank_tag.startswith("N"):
        return wordnet.NOUN
    elif treebank_tag.startswith("R"):
        return wordnet.ADV
    else:
        return wordnet.NOUN


def preprocess(txt,Isolate_Search=False):
    sentence = unidecode(txt)
    sentence = sentence.lower()
    sentence = "".join(char for char in sentence if char not in string.punctuation)
    tokens = word_tokenize(sentence)
    stop_words = set(stopwords.words("french"))
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in pos_tag(tokens)]
    return " ".join(tokens)

def Quit(from_function=None):


    if from_function:
        os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/quit/quit_fnc.wav")
    else:
        hour = datetime.now().hour
        if hour > 20 and hour < 8:
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/quit/quit_night.wav")
        elif hour >= 8 and hour < 13:
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/quit/quit_day.wav")
        elif hour >= 13 and hour < 18:
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/quit/quit_evening.wav")
        elif hour >= 18 and hour <=20:
            os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/quit/quit_afternoon.wav")

        os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/boot/psx.wav")
        sys.exit(0)

def Wait(self_launched=False,allowed_functions=None,from_function=None):
    PRINT("\n-Trinity:Dans la fonction Standing_By")

    #    word_key = SCRIPT_PATH+"/models/Trinity_en_linux_v2_2_0.ppn"
    word_key = SCRIPT_PATH + "/models/trinity_fr_raspberry-pi_v3_0_0.ppn"
    word_key2 = SCRIPT_PATH + "/models/interpreteur_fr_raspberry-pi_v3_0_0.ppn"
    pvfr = SCRIPT_PATH + "/models/porcupine_params_fr.pv"
    porcupine = None
    keyword_index = None

    if self_launched:
        os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/wait/selfwait.wav")

    else:
        os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/history/wait.wav")

    try:
        porcupine = pvporcupine.create(
            access_key=PICO_KEY,
            model_path=pvfr,
            keyword_paths=[word_key,word_key2],
            sensitivities=[1,1],
        )
        with ignoreStderr():
            pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )
        print("\n-Trinity:En attente d'instruction...")

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index == 0:
                PRINT("\n-Trinity:keyword_index:", keyword_index)
                rnd = str(random.randint(1, 15))
                wake_sound = SCRIPT_PATH + "/local_sounds/wakesounds/" + rnd + ".wav"
                os.system("aplay -q %s" % wake_sound)
                break
            if keyword_index == 1:
                break
    finally:
        PRINT("\n-Trinity:Awake.")
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if keyword_index == 1:
            return Prompt(allowed_functions,from_function)


def Isolate_Search(txt, function_name):

    def rm_trigger(trigtok,isolated_tokens,full_tokens):

       Forbiden_Id = []

       for trig in trigtok:
           bucket_name = []
           bucket_id = []
           starlock = False
           idx = 0
           for token in full_tokens:
               PRINT(f"\n-Trinity:rm_trigger:Texte: {token.text}, Hash: {token.orth} i:{token.i} idx:{token.idx}")
               if idx >= len(trig):
                  print("\n-Trinity:rm_trigger:Break: idx %s > len(trig) %s"%( idx,len(trig)) )
                  break
               elif trig[idx] == "*":
                  idx += 1
                  starlock = True
               elif trig[idx] == token.text:
                    print(f"\n-Trinity:rm_trigger:trig[idx]:{trig[idx]} == token:{token.text}")
                    bucket_id.append(token.i)
                    bucket_name.append(token.text)
                    idx += 1
                    PRINT("\n-Trinity:rm_trigger:bucket_name:",bucket_name)
                    PRINT("\n-Trinity:rm_trigger:bucket_id:",bucket_id)
                    if starlock:
                       starlock = False
               elif starlock :
                       continue
               else:
                       bucket_id = []
                       bucket_name = []
                       starlock = False
                       idx =  0
                       PRINT("\n-Trinity:rm_trigger:starlock reset bucket reset")

           for id in bucket_id:
              if id not in Forbiden_Id:
                  Forbiden_Id.append(id)


       clean_request = []
       for it in isolated_tokens:
            print(f"\n-Trinity:rm_trigger:it.txt {it.text} it.i {it.i} it.i in bucket_id:{it.i in bucket_id}")
            if not it.i in Forbiden_Id:
                clean_request.append(it.text)

       PRINT("\n-Trinity:Isolate_Search():rm_trigger:txt:",txt)
       PRINT("\n-Trinity:Isolate_Search():rm_trigger:function_name:%s" % function_name)
       PRINT("\n-Trinity:rm_trigger:trigtok:",trigtok)
       PRINT("\n-Trinity:rm_trigger:Isolated_token:%s\n"%[tok.text for tok in isolated_tokens])
       PRINT("\n-Trinity:rm_trigger:clean_request:",clean_request)
       return(" ".join(clean_request))


    orig_txt = txt
    nlp = spacy.load("fr_dep_news_trf")
    doc = nlp(txt)
    tokenizer = nlp.tokenizer

    trigtok = []
    isolated_wanabe = []

    for n,token in enumerate(doc):
        if token.text == ".":
              if token.is_punct and token.head.pos_ == "VERB" and len(isolated_wanabe) > 0:
                  print("\nBreakpoint")
                  break

        elif any(dep in token.dep_ for dep in ["obj", "obl"]) and token.dep_ not in ["iobj"] and token.head.pos_ == "VERB":

              PRINT(f"\nIsolate_Search:Texte: {token.text}")
              PRINT(f"Isolate_Search:Lemme: {token.lemma_}")
              PRINT(f"Isolate_Search:Token len: {len(token.text)}")
              PRINT(f"Isolate_Search:Token type (POS): {token.pos_}")
              PRINT(f"Isolate_Search:Tag de POS détaillé: {token.tag_}")
              PRINT(f"Isolate_Search:Dépendance: {token.dep_} - {spacy.explain(token.dep_)}")
              PRINT(f"Isolate_Search:Token principal (head): {token.head.text}")
              PRINT(f"Isolate_Search:token.head.pos_: {token.head.pos_}")
              PRINT(f"Isolate_Search:Entité nommée: {token.ent_type_}")
              PRINT(f"Isolate_Search:Est un stop word ? {token.is_stop}")
              PRINT(f"Isolate_Search:Est alphabétique ? {token.is_alpha}")
              PRINT(f"Isolate_Search:Est en minuscule ? {token.is_lower}")
              PRINT(f"Isolate_Search:Est en majuscule ? {token.is_upper}")
              PRINT(f"Isolate_Search:Est un nombre ? {token.like_num}")
              PRINT(f"Isolate_Search:Est une ponctuation ? {token.is_punct}")
              PRINT(f"Isolate_Search:Est un espace ? {token.is_space}")
              PRINT(f"Isolate_Search:Forme originale : {token.shape_}")

              PRINT(f"Isolate_Search:subtree: {[t.text for t in token.subtree]}")
              PRINT(f"Isolate_Search:Ancetres: {[t.text for t in token.ancestors]}")

              PRINT(f"Isolate_Search:left_edge: {token.left_edge}")
              PRINT(f"Isolate_Search:right_edge: {token.right_edge}")

              PRINT("Isolate_Search:Enfants du token :")
              for child in token.children:
                  PRINT(f"  Enfant : {child.text}, Dépendance : {child.dep_}")

              PRINT("Isolate_Search:Tokens à gauche :")
              for left in token.lefts:
                  PRINT(f"  Gauche : {left.text}, Dépendance : {left.dep_}")

              PRINT("Isolate_Search:Tokens à droite :")
              for right in token.rights:
                  PRINT(f"  Droite : {right.text}, Dépendance : {right.dep_}")

              PRINT("-------------------------------")


              if not token in isolated_wanabe:
                  for st in token.subtree:
                      if not st in isolated_wanabe:
                             isolated_wanabe.append(st)
                      else:
                            PRINT(f"Isolate_Search:token subtree {st.text} already in isolated_wanabe")
              else:
                  PRINT(f"Isolate_Search:token {token.text} already in isolated_wanabe")


    triggers = Check_Ambiguity(txt, to_get=function_name)
    try:
         if triggers:
              triggers = triggers[function_name][0][1]
              for trig in triggers:
                  trigtok.append([token.text for token in tokenizer(trig)])
         else:
              PRINT("\n-Trinity:Isolate_Search():Failed at triggers")
              return(" ".join([iw.text for iw in isolated_wanabe]))
    except Exception as e: 
         PRINT("\n-Trinity:Isolate_Search():Failed:Error:\n%s"%str(e))
         return(txt)



    return rm_trigger(trigtok,isolated_wanabe,doc)




def Reducto(txt):
    if len(txt) > 300:
        txt = txt[:300] + "(...)"
    return txt


def NbrToTts(number=None,timestamp=None):
    def nbrtowav(n):
         pathwav = []
         if n >= 1000:
             milliers_part = n // 1000
             n = n % 1000
             pathwav.append("./dates/milliers/"+milliers[milliers_part - 1].replace(" ","_")+".wav")
         if n >= 100:
             centaines_part = n // 100
             n = n % 100
             pathwav.append("./dates/centaines/"+centaines[centaines_part - 1].replace(" ","_")+".wav")
         if n > 0:
             pathwav.append("./dates/nombres/"+nombres[n - 1].replace(" ","_")+".wav")
         return(" ".join(pathwav))

    wavs = []
    if number and not timestamp:
        wavs = nbrtowav(number)
    elif timestamp and not number:
         dobject = datetime.fromtimestamp(timestamp)
         fdate = dobject.strftime("%A %d %B %Y")
         print("fdate:",fdate)

         daystr = dobject.strftime("%A")
         daynbr = dobject.day
         wavday = nbrtowav(daynbr)
         mnthstr = dobject.strftime("%B")
         yearnbr = dobject.year
         wavyear = nbrtowav(yearnbr)

         wavs.append("./dates/jours/"+daystr+".wav")
         wavs.append(wavday)
         wavs.append("./dates/mois/"+mnthstr+".wav")
         wavs.append(wavyear)

         print("wavs:",wavs)   

         aplay_cmd = " ".join(wavs)
         print("aplay_cmd:",aplay_cmd)
         os.system("aplay -q %s" % aplay_cmd)


def Read_Results(object):

   PRINT("\n-Trinity:Read_Results:object:%s"%object)
   pass


def Results_Hub(original_result,topx_res=None,from_function=None):

    Exit = False

    normalised_results = []
    fnc_rhub = []
    keys_to_function = {
                       "hist_input_full":["F_read_results"],
                       "hist_input_short":["F_read_results"],
                       "hist_input_wav":["F_play_audio"],
                       "hist_output_wav":["F_play_audio"],
                       "hist_urls":["F_read_link"],
                       "google_title":["F_read_results"],
                       "google_description":["F_read_results"],
                       "google_url":["F_read_link"],
                       }

#google_result.append({"google_title":title,"google_description":description, "google_url":url})

    if topx_res:
        PRINT("\n-Trinity:Results_Hub(original_result items nbr=%s,topx_res items nbr:%s,from_function=%s)\n"%(len(original_result),len(topx_res),str(from_function)))
        results_list = topx_res
    else:
        PRINT("\n-Trinity:Results_Hub(original_result items nbr=%s,from_function=%s)\n"%(len(original_result),str(from_function)))
        results_list = original_result


    if from_function == "Show_History":
          os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/history/show_history.wav")

    elif from_function == "Search_History":

         if len(results_list) == 1:
             os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/history/found_one.wav")
         elif len(results_list) == 2:
             os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/history/found_two.wav")
         elif len(results_list) == 3:
             os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/history/found_three.wav")
         elif len(results_list) == 4:
             os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/history/found_four.wav")
         elif len(results_list) >= 5 and topx_res:
             os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/history/found_five.wav")
         elif len(results_list) >= 5 and not topx_res:
             os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/history/found_all.wav")
         else:
             os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/history/no_result.wav")
             return ()

    elif from_function == "Google":
         os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/ok/googleres.wav")

    for n,res in enumerate(results_list,start=1):

       print("\n\n==Résultat: %s==\n"%str(n))

       bucket = {}

       for k,v in res.items():
           if k in keys_to_function:
               if v:
                   print("keys_to_function[%s]:%s v=%s"%(k,keys_to_function[k],v))
                   if type(keys_to_function[k]) == list:
                      for fnc in keys_to_function[k]:
                          tmpbucket = []
                          if fnc not in fnc_rhub:
                              fnc_rhub.append(fnc)
                              tmpbucket.append(fnc)
                          bucket[k] = tmpbucket
                   else:
                      if keys_to_function[k] not in fnc_rhub:
                         fnc_rhub.append(keys_to_function[k])
                         bucket[k]=keys_to_function[k]

#           print("-%s: %s"%(k,v))

       if bucket:
          bucket = {'r_nbr': n, **bucket}
          normalised_results.append(bucket)

    print("\nfnc_rhub:",fnc_rhub)
#    print("\nnormalised_results:")

    for n in normalised_results:
        print(n)

##
##
    cmd_from_prompt = Wait(self_launched=True,allowed_functions=fnc_rhub,from_function="Results_Hub")
##
##
    if cmd_from_prompt:
         if cmd_from_prompt == "no cmd":
              os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/history/err_cmd.wav")
         else:
             print("wait cmd_from_prompt:",cmd_from_prompt)
             input = input("wait")
    while True:
        time.sleep(0.5)

        if len(results_list) > 1:
            os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/question/search_history_cmds.wav")
        else:
            os.system("aplay -q  " + SCRIPT_PATH + "local_sounds/question/search_history_cmd.wav")

#        if not INTERPRETOR:
        Start_Thread_Record()

        if Wait_for("audio"):
            audio = audio_datas.get()
            transcripts, transcripts_confidence, words, words_confidence, Err_msg = Speech_To_Text(audio)
            txt, fconf = Check_Transcript(transcripts, transcripts_confidence, words, words_confidence, Err_msg)
            Exit = Commandes(txt=txt,allowed_functions=fnc_rhub,from_function="Results_Hub")
            #def Commandes(txt,allowed_functions=None,from_function=None)

        if Exit:
            Go_Back_To_Sleep(go_trinity=True)
            return ()
        else:
            Go_Back_To_Sleep(go_trinity=False)
            print("hey")

def Show_History():
    PRINT("\n-Trinity:Show_History()")
    if len(Loaded_History_List) == 0:
        os.system("aplay -q %s" % SCRIPT_PATH + "/local_sounds/errors/err_no_history.wav")
        return ()

    history_sort_asc = []

    for n,hitem in enumerate(Loaded_History_List):
        try:
            float(hitem["hist_epok"])
            history_sort_asc.append(hitem)
        except Exception as e:
            print("\n-Trinity:Show_History():Error Loaded_History_List[%s]['epok'] != float:"%n)
            print("\n-Trinity:Loaded_History_List[%s]:\n%s"%(n,hitem))


    return( Results_Hub(history_sort_asc,from_function="Show_History") )



def Search_History(to_search):
    Exit = False

    original_search = to_search

    to_search = Isolate_Search(to_search,"F_search_history")

    PRINT("\n-Trinity:Dans la fonction SearchHistory to_search %s in history." % to_search)

    MatchResults = []

    PRINT("\n-Trinity:Search_History:%s" % to_search)
    for args in Loaded_History_List:

        hist_file = args["hist_file"]
        hist_catws = args["hist_cats"]
        hist_input_full = args["hist_input_full"]
        hist_input_short = args["hist_input_short"]
        hist_input_wav = args["hist_input_wav"]
        hist_output = args["hist_output"]
        hist_output_wav = args["hist_output_wav"]
        hist_urls = args["hist_urls"]
        hist_epok = args["hist_epok"]
        hist_tstamp = args["hist_tstamp"]

        bingoat = 0
        if " " in to_search:
            for n, word in enumerate(to_search.split(" ")):

                if n == 0:
                    word = "%s " % word
                elif n == len(to_search.split(" ")) - 1:
                    word = " %s" % word
                else:
                    word = " %s " % word

                if word in hist_input_full.lower():
                    PRINT("\n-Trinity:Search_History:found partial result in hist_input_full:[%s]" % word)
                    bingoat += 1
                if word in hist_input_short.lower():
                    PRINT("\n-Trinity:Search_History:found partial result in hist_input_short:[%s]" % word)
                    bingoat += 1
                if word in hist_ouput.lower():
                    PRINT("\n-Trinity:Search_History:found partial result in hist_output:[%s]" % word)
                    bingoat += 1

            if to_search in hist_input_full.lower():
                PRINT("\n-Trinity:Search_History:full match in hist_input_full:[%s]" % to_search)
                bingoat += 5
            if to_search in hist_input_short.lower():
                PRINT("\n-Trinity:Search_History:full match in hist_input_short:[%s]" % to_search)
                bingoat += 5
            if to_search in hist_output.lower():
                PRINT("\n-Trinity:Search_History:full match in hist_output:[%s]" % to_search)
                bingoat += 5
        else:
            if to_search in hist_input_full.lower():
                PRINT("\n-Trinity:Search_History:full match in hist_input_full:[%s]" % to_search)
                bingoat += 1
            if to_search in hist_input_short.lower():
                PRINT("\n-Trinity:Search_History:full match in hist_input_short:[%s]" % to_search)
                bingoat += 1
            if to_search in hist_output.lower():
                PRINT("\n-Trinity:Search_History:full match in hist_output:[%s]" % to_search)
                bingoat += 1

        if bingoat > 0:
            MatchResults.append(
            {
                "hist_file":hist_file,
                "hist_cats":hist_cats,
                "hist_input_full":hist_input_full,
                "hist_input_short":hist_input_short,
                "hist_input_wav":hist_input_wav,
                "hist_output":hist_output,
                "hist_output_wav":hist_output_wav,
                "hist_urls":hist_urls,
                "hist_epok":hist_epok,
                "hist_tstamp":hist_tstamp,
                "hist_score":bingoat,
            }
            )

    if len(MatchResults) > 0:
        SortedMatched = sorted(MatchResults, key=lambda x: x["hist_score"], reverse=True)
        MatchedNbr = len(SortedMatched)
    else:
        SortedMatched = []
        MatchedNbr = 0

    if MatchedNbr > 5:
        MatchedNbr = 5

    TopFive = SortedMatched[:MatchedNbr]

    return(Results_Hub(SortedMatched,TopFive,from_function="Search_History"))


def Check_Time_Dialogue(time_to_substract=None,string=None):
    global LAST_DIALOG

    if not REMEMBER_LAST_15M:
        return string

    if len(LAST_DIALOG) == 0:
        return string


    try:
         last_string = LAST_DIALOG[0]
         last_stamp = LAST_DIALOG[1]
      
         time_difference = (time_to_substract - last_stamp).total_seconds()
         if time_difference > 1500:
              LAST_DIALOG = ()
              return string
         else:
              prompt = """La phrase commencant par "last_input=" représente la derniére phrase qu'un utilisateur t'a posé et tu y as dèja répondu même si tu ne t'en souviens pas.
La phrase commencant par "new_input=" représente une nouvelle interaction du même utilisateur avec toi tu devras répondre à ce que contient "new_input=".
La phrase commencant par "last_input=" peut n'avoir aucun rapport avec "new_input=" tu es donc libre de l'ignorer ou non en fonction de sa pertinence avec "new_input=".
Ne fais aucune mention dans ta réponse de cette consigne.
last_input='%s'
new_input='%s'"""%(last_string,string)
              return prompt
    except Exception as e:
         PRINT("\n-Trinity:Error:Check_Time_Dialogue:Error", str(e))
         LAST_DIALOG = ()
         return string

def Save_History(answer, no_audio=False):

    global Loaded_History_List
    global LAST_DIALOG

    PRINT("\n-Trinity:Dans la fonction History")

    if not answer:
        PRINT("\n-Trinity:No answer saved exiting History")
        return ()

    if last_sentence.empty():
        PRINT("\n-Trinity:No last_ sentence saved exiting History")
        return ()

    txt = last_sentence.get()

    PRINT("\n-Trinity:last sentence:", txt)

    if len(Current_Category) == 0:
        Classify(txt)

    Cat_File = (
        str(Current_Category[0])
        .replace("-", ".")
        .replace("&", "and")
        .replace(",", ".")
        .replace(")", ".")
        .replace("(", ".")
    )

    if Cat_File.startswith("."):
        Cat_File = Cat_File[1:]

    Cat_List = ".".join(Current_Category)
    if Cat_List.startswith("."):
        Cat_List = Cat_List[1:]

    Lemmatizer = preprocess(txt)

    PRINT("\n-Trinity:lemmatized last sentence:", Lemmatizer)

    if no_audio:

        new_wav = SCRIPT_PATH + "/local_sounds/errors/err_no_audio_saved.wav"

    else:

        rnd_name = str("".join(random.choice(string.ascii_letters + string.digits) for _ in range(16))) + ".wav"

        new_wav = SAVED_ANSWER + rnd_name
        current_wav = SCRIPT_PATH + "/tmp/current_answer.wav"

        os.system("cp %s %s" % (current_wav, new_wav))

    tformat = "%Y-%m-%d %H:%M:%S"
    now = datetime.now()

    LAST_DIALOG = (txt,now)

    hist_epok = now.timestamp()

    hist_tstamp = time.strftime(tformat, time.localtime(hist_epok))

    #  hist_file,hist_cats,hist_txt,hist_answer,hist_epok,hist_tstamp,hist_wav

    try:
        with open(SCRIPT_PATH + "/history/" + Cat_File, "a+", newline="") as csvfile:
            fieldnames = [
                "hist_file",
                "hist_cats",
                "hist_input_full",
                "hist_input_short",
                "hist_input_wav",
                "hist_output",
                "hist_output_wav",
                "hist_urls",
                "hist_epok",
                "hist_tstamp",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(
                {
                    "hist_file": Cat_File,
                    "hist_cats": Cat_List,
                    "hist_input_full": txt,
                    "hist_input_short": Lemmatizer,
                    "hist_input_wav":"",
                    "hist_output": answer,
                    "hist_output_wav": new_wav,
                    "hist_urls": URLExtract().find_urls(answer),
                    "hist_epok": hist_epok,
                    "hist_tstamp": hist_tstamp,
                }
            )

            PRINT("\n-Trinity:wrote history to:%s" % (SCRIPT_PATH + "/history/" + Cat_File))
            Loaded_History_List.append(

                {
                    "hist_file": Cat_File,
                    "hist_cats": Cat_List,
                    "hist_input_full": txt,
                    "hist_input_short": Lemmatizer,
                    "hist_input_wav":"",
                    "hist_output": answer,
                    "hist_output_wav": new_wav,
                    "hist_urls": URLExtract().find_urls(answer),
                    "hist_epok": hist_epok,
                    "hist_tstamp": hist_tstamp,
                }
            )
            PRINT("\n-Trinity:Loaded_History_List updated:%s" % len(Loaded_History_List))

    except Exception as e:
        print("\n-Trinity:Save_History:Error:%s" % str(e))


def Check_History(question):

    PRINT("\n-Trinity:Dans la fonction Check_History")

    PRINT("\n-Trinity:question:", question)

    lemmatized = preprocess(question)

    if len(Current_Category) == 0:
        Classify(question)
    else:
        Categories = Current_Category

    Cat_File = (
        str(Current_Category[0])
        .replace("-", ".")
        .replace("&", "and")
        .replace(",", ".")
        .replace(")", ".")
        .replace("(", ".")
    )
    if Cat_File.startswith("."):
        Cat_File = Cat_File[1:]

    Joined_Cat = ".".join(Current_Category)
    if Joined_Cat.startswith("."):
        Joined_Cat = Joined_Cat[1:]

    Best_Score = []
    Best_Txt = []
    Best_Answer = []
    Best_Wav = []

    for args in Loaded_History_List:

        hist_file = args["hist_file"]
        hist_cats = args["hist_cats"]
        hist_input_full = args["hist_input_full"]
        hist_input_short = args["hist_input_short"]
        hist_input_wav = args["hist_input_wav"]
        hist_output = args["hist_output"]
        hist_output_wav = args["hist_output_wav"]
        hist_urls = args["hist_urls"]
        hist_epok = args["hist_epok"]
        hist_tstamp = args["hist_tstamp"]



        if Cat_File == hist_file:
            if hist_cats == Joined_Cat:
                score = similar(lemmatized, hist_output)
                if "wikipedia" in hist_output:
                    if score > 0.85:

                        PRINT("\n-Trinity:hist_cats:", hist_cats)
                        PRINT("\n-Trinity:hist_input_full:", hist_input_full)
                        PRINT("\n-Trinity:hist_input_short:", hist_input_short)
                        PRINT("\n-Trinity:hist_answer:", hist_output)
                        PRINT("\n-Trinity:hist_wav:", hist_output_wav)
                        PRINT("\n-Trinity:Score:", score)

                        Best_Score.append(score)
                        if len(hist_input_full) > 0:
                            Best_Txt.append(hist_input_full)
                        else:
                            Best_Txt.append(hist_input_short)
                        Best_Answer(hist_output)
                        Best_Wav.append(hist_output_wav)

                else:
                    if score > 0.5:
                        PRINT("\n-Trinity:hist_cats:", hist_cats)
                        PRINT("\n-Trinity:hist_input_full:", hist_input_full)
                        PRINT("\n-Trinity:hist_input_short:", hist_input_short)
                        PRINT("\n-Trinity:hist_answer:", hist_output)
                        PRINT("\n-Trinity:hist_wav:", hist_output_wav)
                        PRINT("\n-Trinity:Score:", score)

                        Best_Score.append(score)
                        if len(hist_input_full) > 0:
                            Best_Txt.append(hist_input_full)
                        else:
                            Best_Txt.append(hist_input_short)
                        Best_Answer(hist_output)
                        Best_Wav.append(hist_output_wav)

    final_score = 0
    final_wav = ""
    for s in Best_Score:
        if s > final_score:
            final_score = s

    for s, t, w in zip(Best_Score, Best_Txt, Best_Answer, Best_Wav):
        if s == final_score:
            PRINT("\n-Trinity:Best matches :", t)
            if w != SAVED_ANSWER :
               print("DEBUG %s alors que %s"%(w,SAVED_ANSWER))
               sys.exit(1)
            final_wav = w

    if len(final_wav) > 0:

        os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/already/1.wav")
        os.system("aplay -q %s" % final_wav)
        os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/question/amigood.wav")

        Start_Thread_Record()

        if Wait_for("audio"):
            audio = audio_datas.get()
            transcripts, transcripts_confidence, words, words_confidence, Err_msg = Speech_To_Text(audio)
            txt, fconf = Check_Transcript(transcripts, transcripts_confidence, words, words_confidence, Err_msg)
            if len(txt) > 0:
                Question(txt)
                Wait_for("question")
            else:
                score_sentiment.put(False)
            opinion = score_sentiment.get()
            if opinion == None:
                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/notok/1.wav")
                return False
            elif opinion == False:
                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/notok/1.wav")
                return False
            else:
                os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/ok/1.wav")
                return True
    else:
        return False


def Classify(text_content):

    global Current_Category
    PRINT("\n-Trinity:Dans la fonction Classify")

    categories = []

    try:
        client = language_v1.LanguageServiceClient()

        type_ = language_v1.Document.Type.PLAIN_TEXT
        language = "fr"
        document = {"content": text_content, "type_": type_, "language": language}
        content_categories_version = language_v1.ClassificationModelOptions.V2Model.ContentCategoriesVersion.V2
        response = client.classify_text(
            request={
                "document": document,
                "classification_model_options": {
                    "v2_model": {"content_categories_version": content_categories_version}
                },
            }
        )

        for category in response.categories:
            categories.append(category.name.replace("/", "-").replace(" ", "-"))
    except Exception as e:
        PRINT("\n-Trinity:Error:", str(e))
        categories = ["nocat"]

    if len(categories) == 0:
        categories = ["nocat"]

    Current_Category = categories
    PRINT("\n-Trinity:Current_Category:\n", Current_Category)

    return ()


def Trinity(fname="WakeMe"):

    PRINT("\n-Trinity:")
    PRINT("\n-Trinity:fname:", fname)

    if INTERPRETOR:
      PRINT("\n-Trinity:INTERPRETOR TRUE")
      return Prompt()

    if fname == "WakeMe":

        wake_up()
        awake.put(True)
    else:

        if fname == "Speech_To_Text":
            Start_Thread_Record()
            if Wait_for("audio"):
                audio = audio_datas.get()
                (
                    transcripts,
                    transcripts_confidence,
                    words,
                    words_confidence,
                    Err_msg,
                ) = Speech_To_Text(audio)
                txt, fconf = Check_Transcript(
                    transcripts,
                    transcripts_confidence,
                    words,
                    words_confidence,
                    Err_msg,
                )

                if len(txt) > 0:
                    if fconf:
                        cmd = Commandes(txt)
                        if cmd:
                            return Go_Back_To_Sleep()
                        else:
                            To_Gpt(txt)

                    else:
                        return Bad_Confidence(txt)
                else:
                    return Go_Back_To_Sleep()
            else:
                return Go_Back_To_Sleep()

        elif fname == "Repeat":

            Start_Thread_Record()
            if Wait_for("audio"):
                audio = audio_datas.get()
                (
                    transcripts,
                    transcripts_confidence,
                    words,
                    words_confidence,
                    Err_msg,
                ) = Speech_To_Text(audio)
                txt, fconf = Check_Transcript(
                    transcripts,
                    transcripts_confidence,
                    words,
                    words_confidence,
                    Err_msg,
                )
                if len(txt) > 0:
                    Repeat(txt)
                else:
                    return Go_Back_To_Sleep()
            else:
                return Go_Back_To_Sleep()
        else:
            PRINT("\n-Trinity:TOUCHDOWN\n")
            return Go_Back_To_Sleep()


def GetConf():
    global DEBUG
    global XCB_ERROR_FIX
    global SAVED_ANSWER
    global GPT4FREE_SERVERS_LIST
    global GPT4FREE_SERVERS_STATUS
    global GPT4FREE_SERVERS_AUTH
    global INTERPRETOR
    global CHECK_UPDATE
    global CMD_DBG
    global SYNTAX_DBG
    global SEARCH_DBG

    options = [
        "DEBUG",
        "XCB_ERROR_FIX",
        "SAVED_ANSWER",
        "INTERPRETOR",
        "GPT4FREE_SERVERS_LIST",
        "GPT4FREE_SERVERS_STATUS",
        "GPT4FREE_SERVERS_AUTH",
        "CHECK_UPDATE",
        "CMD_DBG",
        "SYNTAX_DBG",
        "SEARCH_DBG",
    ]
    folder = False
    conf = False

    PRINT("\n-Trinity:GetConf()")

    if os.path.exists(SCRIPT_PATH + "/datas/conf.trinity"):
        with open(SCRIPT_PATH + "/datas/conf.trinity", "r") as f:
            f = f.readlines()

        for l in f:

            if "=" not in l:
                continue
            if l.startswith("#"):
               continue

            l = l.strip()

            if "#" in l:
                l = l.split("#")[0]

            option = next((r for r in options if r in l), "")

            #PRINT("L:",l)
            conf = l.split("=")[1]

            while conf.startswith(" "):
                conf = conf[1:]

            while conf.endswith(" "):
                conf = conf[:-1]

            conf = conf.replace("'", "").replace('"', "")


            if not option:
                PRINT("\n-Trinity:Error skipped line :", l)
                continue
#            else:
#                pass
#                print("Option:%s"%option)
#                print("conf:%s"%conf)
#                input("pause")

            if option == "SAVED_ANSWER":

                if conf.lower() == "default":
                    SAVED_ANSWER = SCRIPT_PATH + "/local_sounds/saved_answer/"
                else:
                    SAVED_ANSWER = conf

                if not os.path.exists(SAVED_ANSWER):
                    print("\n-Trinity:Error:GetConf:Le dossier:%s n'existe pas." % SAVED_ANSWER)
                    sys.exit()
                else:
                    saved_error = str(SAVED_ANSWER + "/saved_error").replace("//", "/")
                    if not os.path.exists(saved_error):
                        print("\n-Trinity:Error:GetConf:Le dossier:%s n'existe pas." % saved_error)
                        print("\n-Trinity:Création du dossier:", saved_error)
                        try:
                            os.makedirs(saved_error)
                        except Exception as e:
                            print("\n-Trinity:Error:Impossible de créer le dossier:%s :%s" % (saved_error, str(e)))
                            sys.exit()

            elif option == "INTERPRETOR":
                 if conf.lower() == "true":
                       INTERPRETOR = True
                 else:
                       INTERPRETOR = False

            elif option == "GPT4FREE_SERVERS_LIST":
                    if conf.lower() == "none":
                       GPT4FREE_SERVERS_LIST = None
                       continue
                    try:
                         if "[" in conf and "]" in conf:
#                               serv_list_tmp = serv_list_tmp.replace("'","").replace('"',"").replace(" ","")
                               serv_list_tmp = conf.split("]")[0].split("[")[1]
                               if "," in serv_list_tmp:
                                  serv_list_tmp = serv_list_tmp.split(",") 

                         if type(serv_list_tmp) == list:
                             GPT4FREE_SERVERS_LIST = [x for x in serv_list_tmp if "g4f.Provider." in x]
                         else:
                             if "g4f.Provider." in serv_list_tmp:
                                 GPT4FREE_SERVERS_LIST = [serv_list_tmp]

                    except Exception as e:
                         PRINT("\n-Trinity:getcong():Error:", str(e))

            elif option == "GPT4FREE_SERVERS_STATUS" and not GPT4FREE_SERVERS_LIST:
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

            elif option == "GPT4FREE_SERVERS_AUTH":
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

            elif option == "SYNTAX_DBG":
                if conf.lower() == "true":
                    SYNTAX_DBG = True
                elif conf.lower() == "false":
                    SYNTAX_DBG = False
                else:
                    print("-Trinity:Error SYNTAX_DBG has to be either True or False.")


            elif option == "CMD_DBG":
                if conf.lower() == "true":
                    CMD_DBG = True
                elif conf.lower() == "false":
                    CMD_DBG = False
                else:
                    print("-Trinity:Error CMD_DBG has to be either True or False.")

            elif option == "SEARCH_DBG":
                if conf.lower() == "true":
                    SEARCH_DBG = True
                elif conf.lower() == "false":
                    SEARCH_DBG = False
                else:
                    print("-Trinity:Error SEARCH_DBG has to be either True or False.")


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
        with open(SCRIPT_PATH + "conf.trinity", "w") as f:
            data = """SAVED_ANSWER = default
GPT4FREE_SERVERS_LIST = [g4f.Provider.you] #[g4f.Provider.PROVIDERNAME1,g4f.Provider.PROVIDERNAME2] or None
GPT4FREE_SERVERS_STATUS = Active #Active or Unknown or All or None
GPT4FREE_SERVERS_AUTH = False #True or False or All
INTERPRETOR = True # True or False
CHECK_UPDATE = True #Check update for Trinity or g4f
DEBUG = False #Print debug stuffs
CMD_DBG = False #Print commands results only for testing purpose
SYNTAX_DBG = False #Print output of Special syntax found in database at launch
SEARCH_DBG = False #Test output from Isolate_Search only .
XCB_ERROR_FIX = False #Fix Xcb error from popping due to DISPLAY env variable."""
            f.write(data)

        DEBUG = False
        CMD_DBG = False
        SYNTAX_DBG = False
        CHECK_UPDATE = True
        SEARCH_DBG = False
        INTERPRETOR = False
        GPT4FREE_SERVERS_LIST = None
        SEARCH_DBG = False
        SAVED_ANSWER = SCRIPT_PATH + "/local_sounds/saved_answer/"
        GPT4FREE_SERVERS_STATUS = "Active"
        GPT4FREE_SERVERS_AUTH = False
        XCB_ERROR_FIX = False


def Xcb_Fix(mode):
    global DISPLAY

    if mode == "unset":
        DISPLAY = os.getenv("DISPLAY")
        try:
            del os.environ["DISPLAY"]
        except:
            DISPLAY = ""
    if mode == "set":
        if len("DISPLAY") > 0:
            try:
                os.environ["DISPLAY"] = DISPLAY
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
        print("\n-Trinity:Error:Check_Update n'a pas pu déterminer la version de gpt4free:%s" % str(e))
        Gpt4free_Is_Up = True

    Trinity_Is_Up = False
    next_trinity = ""
    try:
        repo_trinity = gitobj.get_repo("on4r4p/Trinity")
        commits_trinity = repo_trinity.get_commits()
        last_trinity = commits_trinity[1].sha
        next_trinity = commits_trinity[0].sha

        if last_trinity == LAST_SHA:
            Trinity_Is_Up = True

    except Exception as e:
        print("\n-Trinity:Error:Check_Update n'a pas pu déterminer la version de Trinity:%s" % str(e))
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
        PRINT("\n-Trinity:Github SHA doesn't matched:\n%s=!%s\n" % (LAST_SHA, last_trinity))
    else:
        #       PRINT("\n-Trinity:Github SHA matched:\n%s==%s\n"%(LAST_SHA,last_trinity))
        PRINT("\n-Trinity:next_sha:%s\n" % (next_trinity))
        print("\n-Trinity:La version de Trinity est à jour .")

    if len(to_update) > 0:
        print(
            "\n-Trinity:Error:Une nouvelle version pour %s a été publiée.\n-Trinity:Mettez à jour votre version pour continuer.\n-Trinity:Ou changez CHECK_UPDATE à False dans datas/conf.trinity."
            % " et ".join(to_update)
        )
        sys.exit()


if __name__ == "__main__":

    SCRIPT_PATH = os.path.dirname(__file__)
    if SCRIPT_PATH.endswith("."):
        SCRIPT_PATH = SCRIPT_PATH[:-1]

    LAST_SHA = "203ba996734bb9288b60bc7eef12615b2c4fba06"

    NOMBRES = [
         "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix",
         "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf",
         "vingt", "vingt et un", "vingt-deux", "vingt-trois", "vingt-quatre", "vingt-cinq", "vingt-six", "vingt-sept", "vingt-huit", "vingt-neuf",
         "trente", "trente et un", "trente-deux", "trente-trois", "trente-quatre", "trente-cinq", "trente-six", "trente-sept", "trente-huit", "trente-neuf",
         "quarante", "quarante et un", "quarante-deux", "quarante-trois", "quarante-quatre", "quarante-cinq", "quarante-six", "quarante-sept", "quarante-huit", "quarante-neuf",
         "cinquante", "cinquante et un", "cinquante-deux", "cinquante-trois", "cinquante-quatre", "cinquante-cinq", "cinquante-six", "cinquante-sept", "cinquante-huit", "cinquante-neuf",
         "soixante", "soixante et un", "soixante-deux", "soixante-trois", "soixante-quatre", "soixante-cinq", "soixante-six", "soixante-sept", "soixante-huit", "soixante-neuf",
         "soixante-dix", "soixante et onze", "soixante-douze", "soixante-treize", "soixante-quatorze", "soixante-quinze", "soixante-seize", "soixante-dix-sept", "soixante-dix-huit", "soixante-dix-neuf",
         "quatre-vingts", "quatre-vingt-un", "quatre-vingt-deux", "quatre-vingt-trois", "quatre-vingt-quatre", "quatre-vingt-cinq", "quatre-vingt-six", "quatre-vingt-sept", "quatre-vingt-huit", "quatre-vingt-neuf",
         "quatre-vingt-dix", "quatre-vingt-onze", "quatre-vingt-douze", "quatre-vingt-treize", "quatre-vingt-quatorze", "quatre-vingt-quinze", "quatre-vingt-seize", "quatre-vingt-dix-sept", "quatre-vingt-dix-huit", "quatre-vingt-dix-neuf"
]

    CENTAINES = [
         "cent", "deux cents", "trois cents", "quatre cents", "cinq cents", 
         "six cents", "sept cents", "huit cents", "neuf cents"
     ]

    MILLIERS = [
         "mille", "deux mille", "trois mille", "quatre mille", "cinq mille", 
         "six mille", "sept mille", "huit mille", "neuf mille", "dix mille", 
         "onze mille", "douze mille", "treize mille", "quatorze mille", "quinze mille", 
         "seize mille", "dix-sept mille", "dix-huit mille", "dix-neuf mille", 
         "vingt mille", "vingt-et-un mille", "vingt-deux mille", "vingt-trois mille"
     ]

    JOURS = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]


    MOIS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]


    DISPLAY = ""
    Providers_To_Use = []
    LAST_DIALOG = ()
    REMEMBER_LAST_15M = False
    INTERPRETOR = False
    Providers_To_Use = None
    GPT4FREE_SERVERS_LIST = None
    GPT4FREE_SERVERS_STATUS = "Active"
    GPT4FREE_SERVERS_AUTH = False
    CHECK_UPDATE = True
    DEBUG = False
    CMD_DBG = False
    SYNTAX_DBG = False
    SEARCH_DBG = False
    XCB_ERROR_FIX = False
    SAVED_ANSWER = SCRIPT_PATH + "/local_sounds/saved_answer/"

    GetConf()


    if GPT4FREE_SERVERS_STATUS and not GPT4FREE_SERVERS_LIST:
        Providers_To_Use = Check_Free_Servers()
    if GPT4FREE_SERVERS_LIST:
       Providers_To_Use = GPT4FREE_SERVERS_LIST


    FRAME_DURATION = 480
    FRAME_RATE = 16000

    Loaded_History_List = []
    Current_Category = []
    Blacklisted = []

    PICO_KEY = PicoLoadKeys()
    GOOGLE_KEY, GOOGLE_ENGINE,GOOGLE_TRANSLATE = GoogleLoadKeys()
    DLANG_KEY = DetectLanguageLoadKeys()
    if DLANG_KEY:
        detectlanguage.configuration.api_key = DLANG_KEY
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
    Repeat_Last_One = ""
    Loaded_Trinity_Name_Requests = []
    Loaded_Trinity_Mean_Requests = []
    Loaded_Trinity_Dev_Requests = []
    Loaded_Trinity_Script_Requests = []
    Loaded_Trinity_Help_Requests = []
    Loaded_Prompt_Requests = []
    Loaded_Rnd_Requests = []
    Loaded_Read_Results = []
    Loaded_Repeat_Requests = []
    Loaded_Show_History_Requests = []
    Loaded_Search_History_Requests = []
    Loaded_Read_Link_Requests = []
    Loaded_Play_Audio_File_Requests = []
    Loaded_Search_Web_Requests = []
    Loaded_Wait_Words_Requests = []
    Loaded_Quit_Words_Requests = []
    Loaded_Sort_Results_Requests = []
    Loaded_Add_Triggers_Requests = []
    Loaded_Actions_Words_Requests = []
    Loaded_Mix_Actions_Functions = []
    Loaded_Alternatives_Triggers = []
    Loaded_Verbs_Words_List = []
    Loaded_Synonyms_Words_List = []
    Loaded_Mix_Functions_verbs = {}

    CMDFILE = SCRIPT_PATH + "/datas/cmd.trinity"
    ALTFILE = SCRIPT_PATH + "/datas/alt_cmd.trinity"
    TRIFILE = SCRIPT_PATH + "/datas/alt_trigger.trinity"
    ACTFILE = SCRIPT_PATH + "/datas/action.trinity"
    PREFILE = SCRIPT_PATH + "/datas/prefix.trinity"
    SYNFILE = SCRIPT_PATH + "/datas/synonym.trinity"


    COOKIES = SCRIPT_PATH + "/datas/har_and_cookies"
    set_cookies_dir(COOKIES)
    read_cookie_files(COOKIES)


    Load_Csv()

    if XCB_ERROR_FIX:
        Xcb_Fix("unset")

    os.system("aplay -q %s" % SCRIPT_PATH + "local_sounds/boot/psx.wav")
    signal.signal(signal.SIGINT, signal_handler)

    PRINT("\n-Trinity:CHECK_UPDATE:%s" % CHECK_UPDATE)
    PRINT("-Trinity:DEBUG:%s" % DEBUG)
    PRINT("-Trinity:CMD_DBG:%s" % CMD_DBG)
    PRINT("-Trinity:SYNTAX_DBG:%s" % SYNTAX_DBG)
    PRINT("-Trinity:SEARCH_DBG:%s" % SEARCH_DBG)
    PRINT("-Trinity:INTERPRETOR:%s" % INTERPRETOR)
    PRINT("-Trinity:GPT4FREE_SERVERS_LIST:%s" % GPT4FREE_SERVERS_LIST)
    PRINT("-Trinity:GPT4FREE_SERVERS_STATUS:%s" % GPT4FREE_SERVERS_STATUS)
    PRINT("-Trinity:GPT4FREE_SERVERS_AUTH:%s" % GPT4FREE_SERVERS_AUTH)
    PRINT("-Trinity:XCB_ERROR_FIX:%s" % XCB_ERROR_FIX)
    PRINT("-Trinity:SAVED_ANSWER:%s" % SAVED_ANSWER)
    PRINT("-Trinity:History categories loaded:%s" % len(Loaded_History_List))


    if Providers_To_Use:
        PRINT("-Trinity:Free Gpt servers to use:")
        Tmp_Providers = Providers_To_Use
        for i in Tmp_Providers:
            if GPT4FREE_SERVERS_STATUS != "All":
                try:
                   eval_provider = eval(i+".working")
                except Exception as e:
                    PRINT("-Trinity:eval_provider:%s"%e)
                    eval_provider = False
                if not eval_provider:
                    useit = input("-Trinity:Provider:%s does not seems to be working.Do you still want to use it?(Y/N):"%i)
                    while True:
                        if "y" not in useit.lower() and "n" not in useit.lower():
                            useit = input("-Trinity:Provider:%s does not seems to be working.Do you still want to use it?(Y/N):"%i)
                        else:
                            break
                    if "n" in useit.lower():
                        Providers_To_Use.remove(i)
                        PRINT("-Trinity:%s has been removed from servers to use"%i)
                    else:
                        PRINT("\t", i)
                else:
                     PRINT("\t%s is working."% i)
            else:
                    PRINT("\t", i)

    if CHECK_UPDATE:
        Check_Update()

    if SEARCH_DBG:
       Dbg_Search()

    if CMD_DBG:
        Dbg_Input()
    else:
#####
        Trinity()
#####

