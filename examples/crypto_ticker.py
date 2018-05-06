# Author: Jason Wong
# Modified from matrix8x16_test.py by Carter Nelson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.7

import sys
import time
import requests
import threading

from PIL import Image
from PIL import ImageDraw

from Adafruit_LED_Backpack import Matrix8x16

prices_eur = {"btc": 0, "eth": 0, "ltc": 0, "xmr": 0}
ticker_url = {"btc": "https://api.coinmarketcap.com/v1/ticker/bitcoin/?convert=EUR", \
              "eth": "https://api.coinmarketcap.com/v1/ticker/ethereum/?convert=EUR", \
              "ltc": "https://api.coinmarketcap.com/v1/ticker/litecoin/?convert=EUR", \
              "xmr": "https://api.coinmarketcap.com/v1/ticker/monero/?convert=EUR"}

# raw data from https://xantorohara.github.io/led-matrix-editor/
raw_digits = [["00111000", "01000100", "01000100", "01000100", "01000100", "01000100", "01000100", "00111000"], \
        ["00010000", "00110000", "00010000", "00010000", "00010000", "00010000", "00010000", "00111000"], \
        ["00111000", "01000100", "00000100", "00000100", "00001000", "00010000", "00100000", "01111100"], \
        ["00111000", "01000100", "00000100", "00011000", "00000100", "00000100", "01000100", "00111000"], \
        ["00000100", "00001100", "00010100", "00100100", "01000100", "01111100", "00000100", "00000100"], \
        ["01111100", "01000000", "01000000", "01111000", "00000100", "00000100", "01000100", "00111000"], \
        ["00111000", "01000100", "01000000", "01111000", "01000100", "01000100", "01000100", "00111000"], \
        ["01111100", "00000100", "00000100", "00001000", "00010000", "00100000", "00100000", "00100000"], \
        ["00111000", "01000100", "01000100", "00111000", "01000100", "01000100", "01000100", "00111000"], \
        ["00111000", "01000100", "01000100", "01000100", "00111100", "00000100", "01000100", "00111000"]]

raw_btc = ["00011000", "11111100", "01100110", "01100110", "01111100", "01100110", "01100110", "11111100"]

raw_eth = ["00010000", "00111000", "01111100", "11111110", "01111100", "00111000", "00010000", "00000000"]

raw_ltc = ["01100000", "01100000", "01100000", "11111110", "11111110", "01100000", "01100000", "01111110"]

raw_xmr = ["11000110", "11101110", "11111110", "11111110", "11010110", "11000110", "11000110", "00000000"]

raw_space = ["00000000", "00000000", "00000000", "00000000", "00000000", "00000000", "00000000", "00000000"]


def price_worker(currency):
    global prices_eur
    global ticker_url
    url = ticker_url[currency]
    tcp_session = requests.Session()
    while(1):
        try:
            response = tcp_session.get(url)
        except requests.exceptions.RequestException as e:
            print(currency + e)
        if (response.ok):
            prices_eur[currency] = int(float(response.json()[0]['price_eur']))
            print(currency + ": " + str(prices_eur[currency]))
        else:
            print(currency + ": " + response.status_code)
        time.sleep(5);

def makeImageFromRaw(raw):
    image = Image.new('1', (8, 8))
    draw = ImageDraw.Draw(image)
    for x in range(0, 8):
        for y in  range(0, 8):
            if(raw[x][y] == "1"):
                draw.point((7-x,y), fill=255)
    return image

image_btc = makeImageFromRaw(raw_btc)
image_eth = makeImageFromRaw(raw_eth)
image_ltc = makeImageFromRaw(raw_ltc)
image_xmr = makeImageFromRaw(raw_xmr)
image_space = makeImageFromRaw(raw_space)
image_digits = []
for raw in raw_digits:
    image_digits.append(makeImageFromRaw(raw))

# start threads to fetch cryptocurrency price
t_btc = threading.Thread(target=price_worker, args=["btc"])
t_btc.daemon = True
t_btc.start()

t_eth = threading.Thread(target=price_worker, args=["eth"])
t_eth.daemon = True
t_eth.start()

t_ltc = threading.Thread(target=price_worker, args=["ltc"])
t_ltc.daemon = True
t_ltc.start()

t_xmr = threading.Thread(target=price_worker, args=["xmr"])
t_xmr.daemon = True
t_xmr.start()


time.sleep(2);

# Create display instance on default I2C address (0x70) and bus number.
display = Matrix8x16.Matrix8x16()

# Initialize the display. Must be called once before using the display.
display.begin()

while(1):
    display.clear()
    display.set_brightness(1)
    msg = time.strftime("%H%M", time.localtime())
    msg+= " B" + (str(prices_eur["btc"]))
    msg+= " E" + (str(prices_eur["eth"]))
    msg+= " L" + (str(prices_eur["ltc"]))
    msg+= " M" + (str(prices_eur["xmr"]))

    print("msg: " + msg)

    image = Image.new('1', (8, len(msg)*8))
    for i in range(0, len(msg)):
        if(msg[i] == "B"):
            image.paste(image_btc, (0, i*8, 8, (i+1)*8))
        elif(msg[i] == "E"):
            image.paste(image_eth, (0, i*8, 8, (i+1)*8))
        elif(msg[i] == "L"):
            image.paste(image_ltc, (0, i*8, 8, (i+1)*8))
        elif(msg[i] == "M"):
            image.paste(image_xmr, (0, i*8, 8, (i+1)*8))
        elif(msg[i] == " "):
            image.paste(image_space, (0, i*8, 8, (i+1)*8))
        else:
            image.paste(image_digits[int(msg[i])], (0, i*8, 8, (i+1)*8))
    images = display.vertical_scroll(image,True)
    display.animate(images, delay=0.07)

