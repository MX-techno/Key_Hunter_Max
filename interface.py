import hashlib
import binascii
import sys
import os
from tkinter import *
import re
from tkinter import filedialog
from threading import Thread, Lock
from collections import Counter
from words import WORDLIST
import docx



result_file = "result.txt"
capture_next_200_symbols = True
THREAD_COUNT = 10
TRASH_THRESHOLD = 25 #percents

MIN_WORD_COUNT = 12
MAX_WORD_COUNT = 24

root = Tk()
have_results = False
lock = Lock()


ex = {
#   'bitcoin-address': r'[13][a-km-zA-HJ-NP-Z1-9]{25,34}',
#   'base58 private key': r'[5KL][1-9A-HJ-NP-Za-km-z]{50,51}',
    'torn extended private key': r'xprv[\S\s]{0,200}',
    'zprv': r'zprv[\S\s]{0,200}',
    'yprv': r'yprv[\S\s]{0,200}',
    'extended private key': r'xprv[a-km-zA-HJ-NP-Z1-9]{107}',
    'zprv': r'zprv[a-km-zA-HJ-NP-Z1-9]{107}',
    'yprv': r'yprv[a-km-zA-HJ-NP-Z1-9]{107}',
    'extended public key (bitcoin-xpub-key)': r"(xpub[a-km-zA-HJ-NP-Z1-9]{100,108})(\\?c=\\d*&h=bip\\d{2,3})?",
}


#    'possible seed phrase': r'[a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10} [a-z]{2,10}'
one_word_ex = r'[a-z]{2,10}'
base_seed_ex = ''
for i in range(MIN_WORD_COUNT):
    base_seed_ex += fr'{one_word_ex} '
print(base_seed_ex)

for i in range(MAX_WORD_COUNT - MIN_WORD_COUNT):
    ex.update({f'possible seed phrase ({MIN_WORD_COUNT+i})': base_seed_ex[:-1]})
    base_seed_ex += fr'{one_word_ex} '
for reg in ex:
    continue
    print(reg, ex[reg])


def procces_string(string):
    string = re.sub("^\s+|\n|\r|\s+$", '', string)
    out = {}
    for item in ex:
        x1 = re.findall(ex[item], string)
        # print(x1)
        x1 = list(set(x1))
        for match in x1:
            while type(match) != str:
                match = match[0]
            out[match] = item
    return out


def get_string_ignore(path):
    string = open(path, 'r', errors='ignore', encoding='utf8').read()
    out = ''
    for char in string:
        try:
            if ord(char.lower()) > 0 or ord(char.lower()) < -100:
                out += char
        except Exception as e:
            continue
    return out


def is_wallet_file(text):
    walletdescriptor_count = len(re.findall('walletdescriptorcache', text))
    if walletdescriptor_count > 5:
        return True
    key_ckey = len(re.findall('ckey!', text))
    if key_ckey > 10:
        return True

    key_count = len(re.findall('key', text))
    pool_count = len(re.findall('pool', text))
    keymeta_count = len(re.findall('keymeta', text))
    if key_count > 5 and pool_count > 5 and keymeta_count > 5:
        return True
    return False


def find_keys(string):
    out_data = {}
    # get_string(path)
    # out_data.update(procces_string(get_string(file_path)))
    out_data.update(procces_string(string))
    return out_data


def save_result(data, filename):
    global have_results
    have_results = True
    lock.acquire()
    print(f'{data} {filename}')
    f = open(result_file, 'a', errors='ignore')
    f.write(data + " - " + filename + "\n")
    f.close()
    lock.release()

def is_trahs(key):
    items = dict(Counter(key))
    for item in items:
        percent = (items[item]/len(key))*100
        if percent > TRASH_THRESHOLD:
        #    print(percent, item, items[item])
            return True
        #print(percent, item, items[item])
    return False

def click():
    path = filedialog.askdirectory()
    # path = path_input.get()

    dir_filenames = [os.path.join(dirpath, f) for (
        dirpath, dirnames, filenames) in os.walk(path) for f in filenames]

    def worker(i):
        while True:
            lock.acquire()
            if len(dir_filenames) <= 0:
                print(f'Thread {i} exit')
                lock.release()
                return
            file = dir_filenames.pop(0)
            print(f'Thread {i} file {file}')
            lock.release()
            # try:
            print("Ищу в файле " + file)

            try:
                doc = docx.Document(file)
                fullText = []
                for para in doc.paragraphs:
                    fullText.append(para.text)
                text = '\n'.join(fullText)
            except:
                text = get_string_ignore(file)

            #open(f'{file}111', 'w', encoding='utf8').write(text)

            if is_wallet_file(text):
                save_result(f'possible wallet.dat file', file)
            keys = find_keys(text)
            for key in keys:
                if ex[keys[key]][:4] not in ['xprv', 'yprv', 'zprv'] and is_trahs(key): 
                    print(f'trash: {keys[key]} {key}')
                    continue
         
                if 'possible seed phrase' in keys[key]:
                    #print(key)
                    seed_words = key.split(' ')
                    #print(seed_words)
                    correct_seed = True
                    for seed_word in seed_words:
                        word_finded = False
                        for word in WORDLIST:
                            if word in seed_word:
                                word_finded = True
                                break
                        if word_finded == False:
                            correct_seed = False
                            break
                    if not correct_seed:
                        continue
                    

                save_result(f'{keys[key]} {key}', file)
            # except Exception as e:
            #    save_result(f'Ошибка {e}', file)

    threads = []
    for i in range(THREAD_COUNT):
        threads.append(Thread(target=worker, args=(i,)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    global have_results
    if not have_results:
        f = open(result_file, 'a', errors='ignore')
        f.write("работа завершена, ничего не найдено. \n")
        f.close()
    print('Работа завершена.')
    #root.destroy()


def startWindow():
    root.title("Поиск ключей")
    root.geometry("450x150")
    root.resizable(width=False, height=False)

    button_frame = Frame(root)
    button_frame.place(relx=0.03, rely=0.4, relwidth=0.5, relheight=0.5)
    btn = Button(button_frame, text="Open", command=click)
    btn.pack()

    root.mainloop()


if __name__ == "__main__":
    startWindow()
