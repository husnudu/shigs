import time
import os
import requests
import telebot
import datetime
import jsons
import json
from colored import fore, style
from tqdm import tqdm

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning)

bot = telebot.TeleBot("",
                      parse_mode="HTML")  # You can set parse_mode by default. HTML or MARKDOWN


def log(message):
    today = datetime.datetime.now()
    date_time = today.strftime("%m/%d/%Y, %H:%M:%S")
    print(fore.MAGENTA + "[ " + date_time + " ] New Message From : " + str(message.chat.first_name) + " => " + str(
        message.text) + style.RESET,
          end='\n', flush=True)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    log(message)
    bot.reply_to(message, "Hello " + message.chat.first_name + " Welcome To Tiktok Downloader Bot\n\n"
                                                               "How To Use :\n"
                                                               "1. Send Your link Video,\n"
                                                               "2. Waiting and Bot sent to you Video\n\n"
                                                               "Author : <a href='https://t.me/Sandroputraaa'>Sandro Putraa</a>",
                 disable_web_page_preview=True)


@bot.message_handler(regexp="tiktok")
def handle_message(message):
    messageChatID = message.message_id
    today = datetime.datetime.now()
    date_time = today.strftime("%m/%d/%Y, %H:%M:%S")
    log(message)

    url = "http://sandroputraa.my.id/API/tiktok.php"

    querystring = {"url": ""}

    callApi = requests.request("GET", url, params=querystring)
    JsonResponse = callApi.json()

    if JsonResponse['status']:
        print(fore.GREEN + "[ " + date_time + " ] [ Success ] Username : " + JsonResponse['author'] + " | Aweme ID : " + JsonResponse['aweme_id'] + style.RESET, flush=True)
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, "Success Get Video Information\nPlease Wait Bot send Video",
                         reply_to_message_id=messageChatID)
        download = requests.request("GET", JsonResponse['url_vid'], verify=False)

        total_size_in_bytes = int(download.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(str(JsonResponse['aweme_id'] + ".mp4"), 'wb') as file:
            for data in download.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
                progress_bar.refresh()
        progress_bar.close()

        videoFile = open(str(JsonResponse['aweme_id'] + ".mp4"), 'rb')

        dataCaption = "Username : " + JsonResponse['author'] + "\nDesc : " + JsonResponse['desc'] + "\n"
        bot.send_chat_action(message.chat.id, 'upload_video')
        print(fore.YELLOW + "[ " + date_time + " ] Send Video to User : " + message.chat.first_name + "" + style.RESET,
              flush=True, end="\n")
        try:

            videoSent = bot.send_video(message.chat.id, videoFile, caption=dataCaption,
                                       reply_to_message_id=messageChatID)
            videoFile.close()
            jsonsDump = jsons.dumps(videoSent)
            decodeResult = json.loads(jsonsDump)
            if not decodeResult['video']['file_id']:
                print(
                    fore.RED + "[ " + date_time + " ] [ Failed ] Failed Send Video To Username : " + message.chat.first_name + " | Aweme ID : " + str(
                        JsonResponse['item']['aweme_id']) + style.RESET,
                    flush=True, end="\n")
            else:
                print(
                    fore.GREEN + "[ " + date_time + " ] [ Success ] Success Send Video To Username : " + message.chat.first_name + " | Aweme ID : " + str(
                        JsonResponse['item']['aweme_id']) + style.RESET,
                    flush=True, end="\n")

                os.remove(str(JsonResponse['aweme_id'] + ".mp4"))

        except Exception as ex:
            bot.send_chat_action(message.chat.id, 'typing')
            bot.send_message(message.chat.id, "Failed sent video\nTry again later", reply_to_message_id=messageChatID)
            print("Error : " + str(ex))

    else:
        bot.send_chat_action(message.chat.id, 'typing')
        bot.send_message(message.chat.id, "Failed get Information Video\nPlease Wait or change another Link")
        print(JsonResponse, end="\n", flush=True)


@bot.message_handler(content_types=['text'])
def command_default(message):
    log(message)
    bot.send_chat_action(message.chat.id, 'typing')
    bot.send_message(message.chat.id, "I don't understand \"" + message.text + "\"\nMaybe try the help page at /help")


try:
    print("Bot Running", end="\n", flush=True)
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

except Exception as ex:
    print("Error : " + str(ex))
    bot.stop_polling()
    time.sleep(10)
    print("Bot Running Again", end="\n", flush=True)
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
