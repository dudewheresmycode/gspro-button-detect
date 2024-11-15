#! /usr/bin/env python3

import argparse
import sys
import time
import pytesseract
from pytesseract import Output
import numpy
from PIL import Image, ImageGrab, ImageOps
import cv2
import json 


pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract.exe'


ap = argparse.ArgumentParser(
    prog='GSPButtonDetect',
    description='Detects the position of buttons in GSPro',
    epilog='https://github.com/dudewheresmycode/gspro-button-detect')

ap.add_argument("-x", "--xpos", type=int, default=0, help="X position of screen to capture")
ap.add_argument("-y", "--ypos", type=int, default=0, help="Y position of screen to capture")
ap.add_argument("-w", "--width", type=int, default=640, help="Width of screen to capture")
ap.add_argument("-t", "--height", type=int, default=480, help="Height of screen to capture")
ap.add_argument("-d", "--debug", help="Show debug window")
# ap.add_argument("-d", "--debug", help="Show help message")
args = vars(ap.parse_args())

x      = args["xpos"]
y      = args["ypos"]
width  = args["width"]
height = args["height"]

# Import ImageGrab if possible, might fail on Linux
try:
    from PIL import ImageGrab
    use_grab = True
except Exception as ex:
    # Some older versions of pillow don't support ImageGrab on Linux
    # In which case we will use XLib 
    if ( sys.platform == 'linux' ):
        from Xlib import display, X   
        use_grab = False
    else:
        raise ex


def screenGrab( rect ):
    """ Given a rectangle, return a PIL Image of that part of the screen.
        Handles a Linux installation with and older Pillow by falling-back
        to using XLib """
    global use_grab
    x, y, width, height = rect
    if ( use_grab ):
        image = ImageGrab.grab( bbox=[ x, y, x+width, y+height ], all_screens=True )
    else:
        # ImageGrab can be missing under Linux
        dsp  = display.Display()
        root = dsp.screen().root
        raw_image = root.get_image( x, y, width, height, X.ZPixmap, 0xffffffff )
        image = Image.frombuffer( "RGB", ( width, height ), raw_image.data, "raw", "BGRX", 0, 1 )
        # DEBUG image.save( '/tmp/screen_grab.png', 'PNG' )
    
    return convert_pil_to_cv(image)

def convert_pil_to_cv(img):
    # Convert PIL to OpenCV image
    converted = numpy.array(img)
    # Convert RGB to BGR
    converted = converted[:, :, ::-1].copy()
    return converted

def change_contrast(img, level):
  factor = (259 * (level + 255)) / (255 * (259 - level))
  def contrast(c):
      return 128 + factor * (c - 128)
  return img.point(contrast)


def find_lowest_ypos(candidates):
    lowest = candidates[0]
    for i in range(len(candidates)):
        candidate = candidates[i]
        if (lowest["position"][1] < candidate["position"][1]):
            lowest = candidate
    return lowest

    
# Area of screen to monitor
screen_rect = [ x, y, width, height ]  
# print( EXE + ": watching " + str( screen_rect ) )


time.sleep(0.5)

image = screenGrab( screen_rect )              # Grab the area of the screen

# test images
# image = cv2.imread('images/drop-option-flag.png')
# image = cv2.imread('images/drop-option-lateral.png')
# image = cv2.imread('images/out-of-bounds.png')
# image = cv2.imread('images/rehit-option.png')

# image = image[y:y+height, x:x+width]

# tweaks the color of the image to make it more readable to tesseract
color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   
pil_image = Image.fromarray(color_coverted) 
greyscaled = ImageOps.colorize(ImageOps.grayscale(pil_image), black="black", white="white")
posterized_greyscaled = ImageOps.posterize(greyscaled, 2)
high_contrast = change_contrast(posterized_greyscaled, 100)

open_cv_image = convert_pil_to_cv(high_contrast)

found = None

# make 3 attempts to detect the button text
for attempt in range(3):
    # feed the image to Tesseract OCR
    datas = pytesseract.image_to_data(open_cv_image, output_type=Output.DICT)

    # set some default values
    text_position = (-1, -1)
    centery = -1
    text = -1
    candidates = []
    # number of data points returned
    n_datas = len(datas['level'])

    print("Attempt " + str(attempt + 1) + " of 3", file=sys.stderr)
    # loop through text groups
    for i in range(n_datas):
        (tx, ty, tw, th, text) = (datas['left'][i], datas['top'][i], datas['width'][i], datas['height'][i], datas['text'][i])
        if len(text.strip()) > 1:
            lowercase = text.lower()
            cv2.rectangle(open_cv_image, (tx, ty), (tx + tw, ty + th), (0, 255, 0), 2)
            if (lowercase == "drop") or (lowercase == "rehit"):
                text_position = (x + tx + round(tw / 2), y + ty + round(th / 2))
                candidates.append({ "text": lowercase, "position": text_position })


    if (len(candidates) > 0):
        found = find_lowest_ypos(candidates)
        if found != None:
            cv2.circle(open_cv_image, found["position"], 2, (0,0,255), -1)
        
    if found != None:
        break
    time.sleep(0.1)

if found:
    print(str(found["position"][0]) + " " + str(found["position"][1]), file=sys.stdout)
else:
    print("No matching button was found", file=sys.stderr)

# pass --debug option to show detected text in image
if args.get("debug", False):
    windowName = "GSPRO Button Detection (press q to quit)"
    cv2.namedWindow(windowName)
    cv2.resizeWindow(windowName, width, height)
    cv2.imshow(windowName, open_cv_image)

    ### TODO: Loop for a time and monitor the screen for the text?
    while ( True ): 
        # boxes  = pytesseract.image_to_boxes( image )   # OCR the image
        # print(boxes)

        # text  = pytesseract.image_to_string( image )   # OCR the image
        # for box in boxes:
        # IF the OCR found anything, write it to stdout.
        # text = text.strip()
        # if ( len( text ) > 0 ):
        #     print( text )
        key = cv2.waitKey(1) & 0xFF
        # if the 'q' key is pressed, stop the loop
        if key == ord("q"):
            break
        
        # print("Waiting...")
        # time.sleep(0.5)
