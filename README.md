Detects the x,y position of GSPro buttons on screen. It captures an image of the GSPro window and runs that image through tesseract OCR to locate buttons. Useful for automating mouse clicks for button boxes. Check out [gspro-button-box](https://github.com/dudewheresmycode/gspro-button-box) to see how it's used.

## Usage

```powershell
GSPButtonDetect.exe --xpos 0 --ypos 0 --width 800 --height 600 --debug
```

### Options
| Option | Values | Description |
| ------ | ------ | ----------- |
| `--xpos` | The x position (in pixels) of the screen area to capture |
| `--ypos` | The y position (in pixels) of the screen area to capture |
| `--width` | The width (in pixels) of the screen area to capture |
| `--height` | The height (in pixels) of the screen area to capture |
| `--debug` | Open a window displaying the processed image and text boxes |

## Development

First clone the repo and change to it's directory
```powershell
git clone https://github.com/dudewheresmycode/gspro-button-detect.git
cd gspro-button-detect
```

Create a local python3 virtual environment:

```powershell
python3 -m venv venv
```

Install the dependencies into the virtual environment:
```powershell
venv\Scripts\pip.exe install -r requirements.txt
```

You can test the script run the following command. It will look at a 800x600 area of the top left of the screen. When using with GSPro, you should set these values to GSPro's window position and size.

```powershell
venv\Scripts\python.exe detect.py --xpos 0 --ypos 0 --width 800 --height 600 --debug
```

## Building the EXE
Create pyinstaller spec file (with image asset)
```powershell
venv\Scripts\pyi-makespec.exe detect.py
```

Compile executable file:
```powershell
venv\Scripts\pyinstaller.exe detect.spec
```