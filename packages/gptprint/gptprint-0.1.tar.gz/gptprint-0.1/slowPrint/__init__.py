import random, time

def gptprint(text, delay=0.01):
    for word in text.split(' '):
        print(word, end=' ')
        time.sleep(delay + random.uniform(0, delay/2))
        
