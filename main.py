import cognitive_face as CF
import os
import requests
import time
from config import faceURI, faceKey, botId
from io import BytesIO
from PIL import Image, ImageDraw
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

CF.BaseUrl.set(faceURI)
CF.Key.set(faceKey)

def start(update, context):
    update.message.reply_text('The bot has started')

def help(update, context):
    update.message.reply_text('Send two different facial images to compare')

class ImgHandler():
    def __init__(self):
        self.prevFace = {}

    def handle(self, update, context):
        update.message.reply_text('Image received')
        imgUrl = update.message.photo[-1].get_file().file_path
        result = CF.face.detect(imgUrl)
        response = requests.get(imgUrl)
        img = Image.open(BytesIO(response.content))
        color="blue"
        if result is not None:
            draw = ImageDraw.Draw(img) 
            for currFace in result:
                faceRectangle = currFace['faceRectangle']
                left = faceRectangle['left']
                top = faceRectangle['top']
                width = faceRectangle['width']
                height = faceRectangle['height']
                draw.line([(left,top),(left+width,top)],fill=color, width=5)
                draw.line([(left+width,top),(left+width,top+height)],fill=color , width=5)
                draw.line([(left+width,top+height),(left, top+height)],fill=color , width=5)
                draw.line([(left,top+height),(left, top)],fill=color , width=5)

        currentTime = time.time()
        filePath = str(currentTime) + '.jpg'
        img.save(filePath)
        update.message.reply_photo(photo=open(filePath, 'rb'))
        os.remove(filePath)

        currFace = result[0]['faceId']
        chat_id = update.message.chat_id
        if self.prevFace.get(chat_id) is None:
            self.prevFace[chat_id] = currFace
            update.message.reply_text('First image processed')
        else:
            verify = CF.face.verify(self.prevFace[chat_id], currFace)
            update.message.reply_text('Confidence Level: ' + str(verify['confidence']))
            self.prevFace[chat_id] = None

    def cancel(self, update, context):
        chat_id = update.message.chat_id
        self.prevFace[chat_id] = None
        update.message.reply_text('Process cancelled')

def main():
    updater = Updater(botId, use_context=True)
    imgHandler = ImgHandler()
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(MessageHandler(Filters.photo, imgHandler.handle))
    dispatcher.add_handler(CommandHandler("cancel", imgHandler.cancel))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()