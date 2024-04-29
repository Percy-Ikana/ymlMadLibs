import random
import os
import copy
import argparse
import pyperclip
import yaml
import time

#this code is bad, and I do feel bad about it, but I also don't care enough to make it better =)

def replaceName(string, nameNum, name):
    return string.replace(nameNum, name)

def replace(string, str, newStr):
    return string.replace(str, newStr, 1)

def parseNameEntry(line, number):
    return {'['+entry.split(',')[0]+str(number)+']':entry.split(',')[1] for \
            entry in line.split(';')}

def processSubElems(subElems, parentKey, parent):
    if not isinstance(subElems, dict):
        if len(parentKey) > 1:
            parent[parentKey[1] + parentKey[0] + ''.join(parentKey[2:])] = subElems
    if isinstance(subElems, dict):
        for subSubElem in list(subElems.keys()):
            newPar = copy.deepcopy(parentKey)
            newPar.append(subSubElem)
            processSubElems(subElems[subSubElem], newPar, parent)

def processLists(wordList):
    if isinstance(wordList,dict):
        for key in wordList.keys():
            processLists(wordList[key])
    if isinstance(wordList,list):
        if isinstance(wordList[0], dict):
            for each in wordList:
                processLists(each)
        if isinstance(wordList[0], str):
            newList = []
            for entry in wordList:
                if "[num" in entry[:5]:
                    repeats = int(entry.split(']')[0][4:])
                    baseString = entry[len("[num"+str(repeats)+"]"):]
                    for x in range (repeats):
                        newList.append(baseString)
                else:
                    newList.append(entry)
            del wordList[:len(wordList)]
            wordList.extend(newList)

        

def main(file, numGen, baseNum, customBase):
    fics = []
    OGwords = []
    for passedFile in file.split(","):
        with open(passedFile.strip(), 'r') as file:
            OGwords.append(yaml.safe_load(file))
    
    for elem in OGwords:
        processLists(OGwords)
    NewWordList = {}
    for elem in OGwords:
        for key in elem.keys():
            if key not in NewWordList:
                NewWordList[key] = elem[key]
            else:
                #Combine the lists
                NewWordList[key].extend(elem[key])
    OGwords = NewWordList
    for i in range(numGen):
        words = copy.deepcopy(OGwords)

        for key in words:
            if isinstance(words[key], list) and key != "bases":
                random.shuffle(words[key])

        for elem in list(words.keys()):
            replaced = False

            for num in range(len(words[elem])):
                if isinstance(words[elem][num], dict):
                    processSubElems(words[elem][num], [str(num)], words)
                    replaced = True
            if replaced:
                del words[elem]
        if customBase is None:
            if baseNum is not None:
                base = copy.deepcopy(words["bases"][int(baseNum)])
            else:                
                base = copy.deepcopy(random.choice(words["bases"]))
        else:
            base = customBase
        done = False
        for key in words:
            if isinstance(words[key], list):
                random.shuffle(words[key])
        

        while not done:
            done = True
            for key in words.keys():
                tag = '['+key+']'
                while tag in base:
                    if isinstance(words[key], list):
                        base = replace(base, tag, random.choice(words[key]))
                    else:
                        base = replace(base, tag, words[key])
                    done = False
            for key in words:
                for elem in range(len(words[key])):
                    tag = '['+key+'-'+str(elem)+']'
                    if tag in base:
                        if isinstance(words[key], list):
                            base = replaceName(base, tag, words[key][elem])
                            done = False
                        else:
                            base = replaceName(base, tag, words[key])
                            done = False
        fics.append(base)
    return '\n\n'.join(fics)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', 
                        help='the full path to all yaml files needed for the madlib, split by commas.', 
                        required=True)
    parser.add_argument('-n', '--number', 
                        help='how many strings to generate', 
                        required=True)
    parser.add_argument('-p', '--pause', 
                        help='pause the program after generation', 
                        action='store_true',
                        required=False)
    parser.add_argument('-c', '--copy', 
                        help='Copy generated text to clipboard', 
                        action='store_true',
                        required=False)
    parser.add_argument('-b', '--base', 
                        help='What base to use', 
                        required=False)
    parser.add_argument('--customBase', 
                        help='a custom base in the format [text]', 
                        required=False)
    args = parser.parse_args()
    start_time = time.time()
    fics = main(args.dir,int(args.number), args.base, args.customBase)
    
    print(fics)

    if args.copy:
        pyperclip.copy(fics)
    print("--- %s seconds ---" % (time.time() - start_time))
    if args.pause:
        print("Press Enter to Exit...")
        input()
    