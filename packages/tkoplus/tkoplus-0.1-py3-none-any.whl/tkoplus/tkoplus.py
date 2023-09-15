"""change titlebar color in windows 11 with tkinter\n
widgets:{\"colors\" for print and show all colors name ,\n
\"wind11\" for windows 11 \n
wind11.titlebar.bg(master,color)
}"""

from ctypes import windll, byref, sizeof, c_int
from tkinter import *

#name colors

colors = {
    "white", "black", "blue and blue1-blue18", "red and red1-red18", "yellow and yellow1-yellow18",
    "cyan and cyan1-cyan18", "pink", "purole", "orange and orange1-orange18", "green and green1-green18", "gray and gray1-gray10"
}

#colors hex code

COLORS_HEX  ={
    "white":0x00ffffff, "black":0x00000000,
    "blue":0x00FF0000, "blue1":0x00000000, "blue2":0x001C0000, "blue3":0x00380000, "blue4":0x00550000, "blue5":0x00710000,
    "blue6":0x008D0000, "blue7":0x00AA0000, "blue8":0x00C60000, "blue9":0x00E20000, "blue10":0x00FF0000, "blue11":0x00FF1C1C,
    "blue12":0x00FF3838, "blue13":0x00FF5454, "blue14":0x00FF7171, "blue15":0x00FF8D8D, "blue16":0x00FFAAAA, "blue17":0x00FFC6C6, "blue18":0x00FFE2E2,
    "red":0x000000FF, "red1":0x00000000, "red2":0x0000001C, "red3":0x00000038, "red4":0x00000055, "red5":0x00000071, "red6":0x0000008D,
    "red7": 0x000000AA, "red8": 0x000000C6, "red9": 0x000000E2, "red10": 0x000000FF, "red11": 0x001C1CFF, "red12": 0x003838FF, "red13": 0x005454FF, "red14": 0x007171FF,
    "red15": 0x008D8DFF, "red16": 0x00AAAAFF, "red17": 0x00C6C6FF, "red18": 0x00E2E2FF,
    "yellow": 0x0000FFFF, "yellow1": 0x00000000, "yellow2": 0x00001C1C, "yellow3": 0x00003838, "yellow4": 0x00005555, "yellow5": 0x00007171, "yellow6": 0x00008D8D, "yellow7": 0x0000AAAA,
    "yellow8": 0x0000C6C6, "yellow9": 0x0000E2E2, "yellow10": 0x0000FFFF, "yellow11": 0x001CFFFF, "yellow12":0x0038FFFF, "yellow13": 0x0054FFFF, "yellow14": 0x0071FFFF, "yellow15": 0x008DFFFF,
    "yellow16": 0x00AAFFFF, "yellow17": 0x00C6FFFF, "yellow18": 0x00E2FFFF,
    "cyan": 0x00FFFF00, "cyan1": 0x00000000, "cyan2": 0x001C1C00, "cyan3": 0x00383800, "cyan4": 0x00555500, "cyan5": 0x00717100, "cyan6": 0x008D8D00, 
    "cyan7": 0x00AAAA00, "cyan8": 0x00C6C600 ,"cyan9": 0x00E2E200 ,"cyan10": 0x00FFFF00, "cyan11": 0x00FFFF1C , "cyan12": 0x00FFFF38 , "cyan13": 0x00FFFF54,
    "cyan14": 0x00FFFF71 , "cyan15": 0x00FFFF8D,"cyan16": 0x00FFFFAA , "cyan17": 0x00FFFFC6 , "cyan18": 0x00FFFFE2,
    "purple":0x00FF5BC3, "pink": 0x00DBAAFF, "green": 0x0004E400, "green1": 0x0000000, "green2": 0x00011800, "green3": 0x00023101, "green4": 0x00044902, "green5": 0x00056203,
    "green6": 0x00067B04, "green7": 0x00089305, "green8": 0x0009AC06, "green9": 0x000BC507, "green10": 0x000CDD08, "green11": 0x0024E121, "green12": 0x003CE53A, "green13": 0x0056E853,
    "green14" : 0x0070EC6E, "green15": 0x008BF089, "green16": 0x00A7F3A5, "green17": 0x00C3F7C2, "green18": 0x00E0FBE0,
    "orange": 0x00308CE8, "orange1": 0x00000000, "orange2": 0x00050F19, "orange3": 0x000A1F33, "orange4": 0x00102E4D, "orange5":0x00153E67, "orange6": 0x001B4D80, "orange7": 0x00205D9A, 
    "orange8": 0x00256DB4, "orange9": 0x002B7CCE, "orange10": 0x00308CE8, "orange11": 0x004598EA, "orange12": 0x005BA4ED, "orange13": 0x0071B0EF, "orange14": 0x0087BDF2, "orange15": 0x009EC9F4,
    "orange16": 0x00B6D6F7, "orange17": 0x00CEE3F9, "orange18": 0x00E6F1FC,
    "gray": 0x00717171, "gray1": 0x00000000, "gray2": 0x001C1C1C, "gray3": 0x00383838, "gray4": 0x00545454, "gray5": 0x00717171, "gray6": 0x008D8D8D, "gray7": 0x00A9A9A9, "gray8": 0x00C6C6C6, 
    "gray9": 0x00E2E2E2, "gray10": 0x00FFFFFF
    }

#class Control for place and config all widgets

class Control():
    
    """This class is for Active and Config all widget."""

    class wind11():
        class titlebar():
            class bg():
                def draw(self):
                    try:
                        WindowsName.update()
                    except:
                        return
                    HWND = windll.user32.GetParent(WindowsName.winfo_id())
                    DWMWA_CAPTION_COLOR = 35
                    try:
                        COLOR_1 = COLORS_HEX[ColorName]
                    except:
                        print(f"name '{ColorName}' is not defined\n",f"KeyError: '{ColorName}'\n\n",f"NameError: name '{ColorName}' is not defined")
                        return
                    windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_CAPTION_COLOR, byref(c_int(COLOR_1)), sizeof(c_int))

                def config(self,color):
                    ColorName = color
                    try:
                        WindowsName.update()
                    except:
                        return
                    HWND = windll.user32.GetParent(WindowsName.winfo_id())
                    DWMWA_CAPTION_COLOR = 35
                    try:
                        COLOR_1 = COLORS_HEX[color]
                    except:
                        print(f"name '{color}' is not defined\n",f"KeyError: '{color}'\n\n",f"NameError: name '{ColorName}' is not defined")
                        return
                    windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_CAPTION_COLOR, byref(c_int(COLOR_1)), sizeof(c_int))
            class title():
                def draw(self):
                    try:
                        WindowsName.update()
                    except:
                        return
                    HWND = windll.user32.GetParent(WindowsName.winfo_id())
                    DWMWA_TITLE_COLOR = 36
                    try:
                        COLOR_2 = COLORS_HEX[ColorName]
                    except:
                        print(f"name '{ColorName}' is not defined\n",f"KeyError: '{ColorName}'\n\n",f"NameError: name '{ColorName}' is not defined")
                        return
                    windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_TITLE_COLOR, byref(c_int(COLOR_2)), sizeof(c_int))   
                def config(self,color):
                    ColorName = color
                    try:
                        WindowsName.update()
                    except:
                        return
                    HWND = windll.user32.GetParent(WindowsName.winfo_id())
                    DWMWA_TITLE_COLOR = 36
                    try:
                        COLOR_2 = COLORS_HEX[ColorName]
                    except:
                        print(f"name '{ColorName}' is not defined\n",f"KeyError: '{ColorName}'\n\n",f"NameError: name '{ColorName}' is not defined")
                        return
                    windll.dwmapi.DwmSetWindowAttribute(HWND, DWMWA_TITLE_COLOR, byref(c_int(COLOR_2)), sizeof(c_int))   

class wind11():

    """Widgets Windows 11"""

    class titlebar():

        """Change titlebar color"""

        class bg(Control.wind11.titlebar.bg): #for Active and Config titlebar color

            """Get master and color for draw in the titlebar."""

            def __init__(self,master,color):
                global WindowsName,ColorName
                WindowsName = master
                ColorName = color

        class title(Control.wind11.titlebar.title): #for Active and Config titlebar color

            """Get master and color for draw in the titlebar"""

            def __init__(self,master,color):
                global WindowsName,ColorName
                WindowsName = master
                ColorName = color