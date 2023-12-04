import random
import os
import copy
import argparse
import pyperclip
import yaml

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

def main(file, numGen):
    fics = []
    OGwords = {}
    with open(file, 'r') as file:
        OGwords = yaml.safe_load(file)
    for i in range(numGen):
        words = copy.deepcopy(OGwords)

        for key in words:
            if isinstance(words[key], list):
                random.shuffle(words[key])

        for elem in list(words.keys()):
            replaced = False

            for num in range(len(words[elem])):
                if isinstance(words[elem][num], dict):
                    processSubElems(words[elem][num], [str(num)], words)
                    replaced = True
            if replaced:
                del words[elem]
        base = copy.deepcopy(random.choice(words["bases"]))
        done = False
        for key in words:
            if isinstance(words[key], list):
                random.shuffle(words[key])
        for key in words:
            for elem in range(len(words[key])):
                tag = '['+key+'-'+str(elem)+']'
                if tag in base:
                    if isinstance(words[key], list):
                        base = replaceName(base, tag, random.choice(words[key]))
                    else:
                        base = replaceName(base, tag, words[key])

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
        fics.append(base)
    return '\n\n'.join(fics)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dir', 
                        help='the full path to the yml used for the madlib', 
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
    args = parser.parse_args()

    fics = main(args.dir,int(args.number))

    print(fics)

    if args.copy:
        pyperclip.copy(fics)

    if args.pause:
        print("Press Enter to Exit...")
        input()