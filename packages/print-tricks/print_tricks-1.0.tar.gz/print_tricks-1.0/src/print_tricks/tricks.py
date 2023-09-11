import time


def typewrite(text, speed=0.2, end='\n'):
    text = text + end
    
    for char in text:
        time.sleep(speed)
        print(char, end='', flush=True)


def slidetext(text, speed=0.03):
    s = ''

    for x in text[::-1]:
        s = x + s
        print(s, end='\r')
        time.sleep(speed)
    print(s)

        