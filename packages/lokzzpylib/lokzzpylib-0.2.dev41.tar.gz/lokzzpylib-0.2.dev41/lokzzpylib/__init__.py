from clint.textui import puts, colored, indent
from pick import pick
import colorama
import keyboard
import random
import numpy
import time
try:
    import msvcrt
    windows = True
except:
    windows = False
    pass

colorama.init()

class Choice(object):
    def __init__(self, index, option):
        self.index = index
        self.option = option

def choose_from_list(title, options, indi = "*", minselcont = 1):
    option, index = pick(options, title, indi, min_selection_count=minselcont)
    index += 1
    return Choice(index, option)

def progress_bar(current, total, name="Progress", bar_length=50):
    fraction = current / total
    arrow = int(fraction * bar_length - 1) * '-' + '>'
    padding = int(bar_length - len(arrow)) * ' '
    ending = '\n' if current >= total else '\r'
    print(f'{name}: [{arrow}{padding}] {int(fraction*100)}%', end=ending)

def ask_bool(prompt):
    try:
        return {"true":True,"yes":True,"y":True,"false":False,"no":False,"n":False}[input(prompt).lower()]
    except KeyError:
        print("invalid input")

def ask_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("not a number")

def printc(n, d = '', f = False, sepL = 0, sepC = ' ', Beg = colored.green('//|'), BegL = 4, end = '\n'):
    sep = ''
    for i in range(sepL):
        sep =+ sepC
    with indent(BegL, quote=Beg):
        if f == False:
            puts(colored.blue(n) + sep + d + end, newline=False)
        else:
            puts(colored.blue(d) + sep + n + end, newline=False)

def stringc(n, d = '', f = False, sepL = 0, sepC = ' ', Beg = colored.green('//|'), BegL = 4, end = '\n'):
    sep, air = '', ''
    for i in range(sepL): sep =+ sepC
    BegL = BegL - len(Beg)
    for i in range(BegL): air =+ ' '
    if f == False:
        return str(Beg + air + colored.blue(n) + sep + d + end)
    else:
        return str(Beg + air + colored.blue(d) + sep + n + end)

def printd(n, d = '', f = False, A = False, sepL = 0, sepC = ' ', Beg = colored.red('>>|'), BegL = 4):
    if A == True:
        sep = ''
        for i in range(sepL):
            sep =+ sepC
        with indent(BegL, quote=Beg):
            if f == False:
                puts(colored.blue(n) + sep + d)
            else:
                puts(colored.blue(d) + sep + n)

def cool_spam(long, amount, lines = 1, delay = 0.01, normal = "-", unnormal = "#", reverse = False, c = True):
    long = int(numpy.floor(long))
    amount = int(numpy.floor(amount))
    if amount >= long: amount = long
    for i in range(lines):
        at = []
        txt = []
        if reverse: normalO = unnormal; unnormalO = normal
        else: normalO = normal; unnormalO = unnormal
        for i in range(long): txt.append(normalO)
        for i in range(amount): 
            add = random.randint(1, long)
            while True:
                try:
                    if add in at:
                        add = random.randint(1, long)
                    else:
                        at.append(add)
                        break
                except ValueError:
                    continue
        for i in at: txt[i - 1] = unnormalO
        if c: printc("".join(txt))
        else: print("".join(txt))
        time.sleep(delay)

def wind_getonekey(f = True):
    global windows
    if windows != True:
        return
    if f: out = str(msvcrt.getch(), 'utf-8')
    else: out = msvcrt.getch()
    return out

def clearsc(type=1):
    if type == 1:
        print('\033[2J')
    elif type == 2:
        for i in range(25):
            print('\n')

def clearinp(t = 25, e = False):
    for i in range(t):
        keyboard.press_and_release("\b")
        if e == True:
            printc("on the " + str(i + 1) + " backspace")

if __name__ == '__main__':
    exit()
