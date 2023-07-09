#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 15 01:44:06 2023

@author: gordibus
"""
###### Fonctionne avec les 7 textes 
import glob
import spacy

def index_inverse_syntaxique(fichiers_texte):
    nlp = spacy.load('fr_core_news_sm')  # Charger le modèle de langue française de SpaCy
    index_inverse = []

    for fichier_texte in fichiers_texte:
        with open(fichier_texte, 'r', encoding='utf-8') as f:
            text = f.read()
            doc = nlp(text)  # Traiter le texte avec SpaCy
            for sent in doc.sents:
                sent_text = sent.text.strip()
                for token in sent:
                    if token.dep_ in ['nsubj', 'ROOT']:
                        if token.dep_ == 'nsubj':
                            dep_label = 'SUJ'
                        else:
                            dep_label = 'V'
                        token_text = f'<{dep_label}>{token.text}</{dep_label}>'
                        index_inverse.append((fichier_texte, sent.text.strip(), token_text, token.lemma_, token.i + 1, dep_label, token.head.i + 1))
    return index_inverse

#fichiers_texte = ['JV80.txt', 'cinq_semaines_en_ballon.txt', 'de_la_terre_a_la_lune.txt', 'les_cinq_cents_millions_de_la_begum.txt', 'les_forceurs_de_blocus.txt', 'les_revoltes_de_la_bounty.txt', 'robur_le_conquerant.txt']   # Remplacez par les noms de vos fichiers 
fichiers_texte=[]
path_corpora = "../DATA/*.txt"
for chemin in glob.glob(path_corpora):
    print(chemin)
    fichiers_texte.append(chemin)
index_inverse = index_inverse_syntaxique(fichiers_texte)

for item in index_inverse:
    print(' | '.join(map(str, item)))

def interro_index_inverse_syntaxique(index_inverse):
    sz = 0
    while True:
        command = input('INTERO> ')
        if command.startswith('SZ ='):
            sz = int(command.split('=')[1].strip())
        elif command == 'SZ?':
            print(f"SZ = {sz}")
        elif command.startswith('SRQET ='):
            query_terms = command.split('=')[1].strip().split(' ')
            query_terms = [(term.split('/')[0], term.split('/')[1]) for term in query_terms]
            results = []
            for item in index_inverse:
                file_name, line_num, sent_text, token_text, token_pos, token_dep, head_pos = item
                for term, dep in query_terms:
                    if term == token_text and dep == token_dep:
                        results.append(item)
                        break
            if len(results) == 0:
                print(f"No results found for terms '{' '.join([f'{term}/{dep}' for term, dep in query_terms])}'")
            else:
                for item in results:
                    file_name, line_num, sent_text, token_text, token_pos, token_dep, head_pos = item
                    formatted_sent = sent_text[max(0, token_pos - sz):min(len(sent_text), token_pos + sz)]
                    print(f"{file_name} |{len(line_num)}| {line_num} | {formatted_sent}")
        elif command.startswith('SRQOU ='):
            query_terms = command.split('=')[1].strip().split(' ')
            query_terms = [(term.split('/')[0], term.split('/')[1]) for term in query_terms]
            results = []
            for item in index_inverse:
                file_name, line_num, sent_text, token_text, token_pos, token_dep, head_pos = item
                for term, dep in query_terms:
                    if term == token_text and dep == token_dep:
                        results.append(item)
                        break
            if len(results) == 0:
                print(f"No results found for any of the terms: {' '.join([f'{term}/{dep}' for term, dep in query_terms])}")
            else:
                for item in results:
                    file_name, line_num, sent_text, token_text, token_pos, token_dep, head_pos = item
                    formatted_sent = sent_text[max(0, token_pos - sz):min(len(sent_text), token_pos + sz)]
                    print(f"{file_name} |{len(line_num)}|{line_num}| {formatted_sent}")
        elif command == 'QUIT':
            break
        else:
            print("Invalid command")


#fichiers_texte = ['JV80.txt', 'cinq_semaines_en_ballon.txt', 'de_la_terre_a_la_lune.txt', 'les_cinq_cents_millions_de_la_begum.txt', 'les_forceurs_de_blocus.txt', 'les_revoltes_de_la_bounty.txt', 'robur_le_conquerant.txt']   # Remplacez par les noms de vos fichiers 
fichiers_texte=[]
path_corpora = "../DATA/*.txt"
for chemin in glob.glob(path_corpora):
    print(chemin)
    fichiers_texte.append(chemin)
index_inverse = index_inverse_syntaxique(fichiers_texte)
interro_index_inverse_syntaxique(index_inverse)





###### Fonctionne avec un seul texte:
# import spacy

# def index_inverse_syntaxique(fichier_texte):
#     nlp = spacy.load('fr_core_news_sm')  # Charger le modèle de langue française de SpaCy
#     index_inverse = []

#     with open(fichier_texte, 'r', encoding='utf-8') as f:
#         text = f.read()
#         doc = nlp(text)  # Traiter le texte avec SpaCy
#         for sent in doc.sents:
#             sent_text = sent.text.strip()
#             for token in sent:
#                 if token.dep_ in ['nsubj', 'ROOT']:
#                     if token.dep_ == 'nsubj':
#                         dep_label = 'SUJ'
#                     else:
#                         dep_label = 'V'
#                     token_text = f'<{dep_label}>{token.text}</{dep_label}>'
#                     index_inverse.append((fichier_texte, sent.text.strip(), token.text, token.lemma_, token.i + 1, dep_label, token.head.i + 1))

#     return index_inverse

# fichier_texte = 'JV80.txt'
# index_inverse = index_inverse_syntaxique(fichier_texte)

# for item in index_inverse:
#     print(' | '.join(map(str, item)))

# def interro_index_inverse_syntaxique(index_inverse):
#     while True:
#         command = input('INTERO> ')
#         if command.startswith('SRQET ='):
#             query_terms = command.split('=')[1].strip().split(' ')
#             query_terms = [(term.split('/')[0], term.split('/')[1]) for term in query_terms]
#             results = []
#             for item in index_inverse:
#                 file_name, line_num, sent_text, token_text, token_pos, token_dep, head_pos = item
#                 for term, dep in query_terms:
#                     if term == token_text and dep == token_dep:
#                         results.append(item)
#                         break
#             if len(results) == 0:
#                 print(f"No results found for terms '{' '.join([f'{term}/{dep}' for term, dep in query_terms])}'")
#             else:
#                 for item in results:
#                     file_name, line_num, sent_text, token_text, token_pos, token_dep, head_pos = item
#                     formatted_sent = sent_text.replace(token_text, f"<{token_dep}{token_pos}>{token_text}</{token_dep}{token_pos}>")
#                     print(f"{file_name} |{len(line_num)}| {line_num} | {formatted_sent}")
#         elif command.startswith('SRQOU ='):
#             query_terms = command.split('=')[1].strip().split(' ')
#             query_terms = [(term.split('/')[0], term.split('/')[1]) for term in query_terms]
#             results = []
#             for item in index_inverse:
#                 file_name, line_num, sent_text, token_text, token_pos, token_dep, head_pos = item
#                 for term, dep in query_terms:
#                     if term == token_text and dep == token_dep:
#                         results.append(item)
#                         break
#             if len(results) == 0:
#                 print(f"No results found for any of the terms: {' '.join([f'{term}/{dep}' for term, dep in query_terms])}")
#             else:
#                 for item in results:
#                     file_name, line_num, sent_text, token_text, token_pos, token_dep, head_pos = item
#                     formatted_sent = sent_text.replace(token_text, f"<{token_dep}{token_pos}>{token_text}</{token_dep}{token_pos}>")
#                     print(f"{file_name} |{len(line_num)}|{line_num}| {formatted_sent}")
#         elif command == 'QUIT':
#             break
#         else:
#             print("Invalid command")

# fichier_texte = 'JV80.txt'
# index_inverse = index_inverse_syntaxique(fichier_texte)
# interro_index_inverse_syntaxique(index_inverse)


### Fonctionne avec les 7 textes de Jules Vernes