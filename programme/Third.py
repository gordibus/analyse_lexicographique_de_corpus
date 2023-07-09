#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 14:30:35 2023

@author: gordibus
"""
############# FOnctionne avec tout les fichiers !
import glob
import nltk
import spacy
from nltk.corpus import wordnet

nltk.download('punkt')
nlp = spacy.load('fr_core_news_sm')

def index_inverse_syntaxique(fichiers_texte):
    nlp = spacy.load('fr_core_news_sm')
    index_inverse = []

    for fichier_texte in fichiers_texte:
        with open(fichier_texte, 'r', encoding='utf-8') as f:
            text = f.read()
            doc = nlp(text)
            for sent in doc.sents:
                sent_text = sent.text.strip()
                for token in sent:
                    if token.dep_ in ['nsubj', 'ROOT']:
                        if token.dep_ == 'nsubj':
                            dep_label = 'SUJ'
                        else:
                            dep_label = 'V'
                        token_text = f'<{dep_label}>{token.text}</{dep_label}>'
                        index_inverse.append((fichier_texte, sent.text.strip(), token.text, token.lemma_, token.i + 1, dep_label, token.head.i + 1))

    return index_inverse

def index_inverse(fichiers_texte):
    inverted_index = {}

    for fichier_texte in fichiers_texte:
        with open(fichier_texte, 'r', encoding='utf-8') as f:
            for num_ligne, ligne in enumerate(f, start=1):
                for mot in ligne.strip().split():
                    if mot not in inverted_index:
                        inverted_index[mot] = {(fichier_texte, num_ligne)}
                    else:
                        inverted_index[mot].add((fichier_texte, num_ligne))

    return inverted_index

def print_results(results, sz=0, out=None, query_terms=None):
    if out:
        f = open(out, 'w', encoding='utf-8')
    for result in results:
        fichier_texte, num_ligne = result
        with open(fichier_texte, 'r', encoding='utf-8') as f:
            start_line = max(1, num_ligne - sz)
            end_line = num_ligne + sz + 1
            context_lines = [f'{i}: {line.strip()}' for i, line in enumerate(f, start=1) if start_line <= i < end_line]
            context_lines = [line for line in context_lines if any(term in line for term in query_terms)]
            context = ' '.join(context_lines)
            if query_terms:
                for i, term in enumerate(query_terms):
                    context = context.replace(term, f'<Q{i}>{term}</Q{i}>')
            if out:
                f.write(f'{fichier_texte} | {len(context)}, {len(query_terms)} | {context}\n')
            else:
                print(f'{fichier_texte} | {len(context)}, {len(query_terms)} | {context}\n')
    if out:
        f.close()

def get_synonyms(word):
    synonyms = []
    for syn in wordnet.synsets(word, lang='fra'):
        for lemma in syn.lemmas('fra'):
            synonyms.append(lemma.name())
    return synonyms

def SYNOREQET(index, query):
    query_terms = query.split()
    synonyms = []
    for word in query_terms:
        synonyms.extend(get_synonyms(word))
    query_postings = []
    for term in synonyms:
        if term not in index:
            print(f"No results found for term '{term}'")
            break
        else:
            query_postings.append(index[term])
    else:
        results = set.intersection(*query_postings)
        print_results(results, sz, out, synonyms)

def SYNOREQOU(index, query):
    query_terms = query.split()
    synonyms = []
    for word in query_terms:
        synonyms.extend(get_synonyms(word))
        results = set()
    for term in synonyms:
            if term in index:
                results.update(index[term])
            if len(results) > 0:
                print_results(results, sz, out, synonyms)
            else:
                 print(f"No results found for any of the terms: {', '.join(synonyms)}")

#fichiers_texte = ['JV80.txt', 'cinq_semaines_en_ballon.txt', 'de_la_terre_a_la_lune.txt', 'les_cinq_cents_millions_de_la_begum.txt', 'les_forceurs_de_blocus.txt', 'les_revoltes_de_la_bounty.txt', 'robur_le_conquerant.txt']
fichiers_texte=[]
path_corpora = "../DATA/*.txt"
for chemin in glob.glob(path_corpora):
    print(chemin)
    fichiers_texte.append(chemin)
inverted_index = index_inverse(fichiers_texte)
index_inverse_syntaxique = index_inverse_syntaxique(fichiers_texte)
sz = 0
out = None

while True:
    command = input('INTERO> ')
    
    if command.startswith('SRQET =') or command.startswith('SRQOU ='):
        query_terms = command.split('=')[1].strip().split(' ')
        query_terms = [(term.split('/')[0], term.split('/')[1]) for term in query_terms]
        results = []
        for item in index_inverse_syntaxique:
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
                formatted_sent = sent_text.replace(token_text, f"<{token_dep}{token_pos}>{token_text}</{token_dep}{token_pos}>")
                print(f"{file_name} | {len(line_num)} | {line_num} | {formatted_sent}")
    
    elif command.startswith('SZ ='):
        sz = int(command.split('=')[1].strip())
    elif command == 'SZ?':
        print(f"SZ = {sz}")
    elif command.startswith('OUT ='):
        out = command.split('=')[1].strip()
        if out.lower() == 'none':
            out = None
    elif command == 'OUT?':
        print(f"OUT = {out}")
    elif command.startswith('RQET ='):
        query_terms = command.split('=')[1].strip().split(',')
        query_terms = [term.strip() for term in query_terms]
        query_postings = []
        for term in query_terms:
            if term not in inverted_index:
                print(f"No results found for term '{term}'")
                break
            else:
                query_postings.append(inverted_index[term])
        else:
            results = set.intersection(*query_postings)
            print_results(results, sz, out, query_terms)
    elif command.startswith('RQOU ='):
        query_terms = command.split('=')[1].strip().split(',')
        query_terms = [term.strip() for term in query_terms]
        results = set()
        for term in query_terms:
            if term in inverted_index:
                results.update(inverted_index[term])
        if len(results) > 0:
            print_results(results, sz, out, query_terms)
        else:
            print(f"No results found for any of the terms: {', '.join(query_terms)}")
    elif command.startswith('SYNOREQET ='):
        query_terms = command.split('=')[1].strip()
        SYNOREQET(inverted_index, query_terms)
    elif command.startswith('SYNOREQOU ='):
        query_terms = command.split('=')[1].strip()
        SYNOREQOU(inverted_index, query_terms)
    elif command == 'QUIT':
        break
    else:
        print(f"Unrecognized command: '{command}'")




#################code qui fonctionne mais avec des problèmes########################
# import nltk
# import spacy
# from nltk.corpus import wordnet
# nltk.download('punkt')
# nlp = spacy.load('fr_core_news_sm')

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
#                     print(f"{file_name} | {line_num} | {formatted_sent}")
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
#                     print(f"{file_name} | {line_num} | {formatted_sent}")
#         elif command == 'QUIT':
#             break
#         else:
#             print("Invalid command")
            
# def index_inverse(fichier_texte):
#     inverted_index = {}
#     with open(fichier_texte, 'r', encoding='utf-8') as f:
#         for num_ligne, ligne in enumerate(f, start=1):
#             for mot in ligne.strip().split():
#                 if mot not in inverted_index:
#                     inverted_index[mot] = {num_ligne}
#                 else:
#                     inverted_index[mot].add(num_ligne)
#     return inverted_index



# def print_results(results, sz=0, out=None, query_terms=None):
#     if out:
#         f = open(out, 'w', encoding='utf-8')
#     for result in results:
#         with open(fichier_texte, 'r') as f:
#             start_line = max(1, result - sz)
#             end_line = result + sz + 1
#             context_lines = [f'{i}: {line.strip()}' for i, line in enumerate(f, start=1) if start_line <= i < end_line]
#             context_lines = [line for line in context_lines if any(term in line for term in query_terms)]
#             context = ' '.join(context_lines)
#             if query_terms:
#                 for i, term in enumerate(query_terms):
#                     context = context.replace(term, f'<Q{i}>{term}</Q{i}>')
#             if out:
#                 f.write(f'{fichier_texte} | {len(context)}, {len(query_terms)} | {context}\n')
#             else:
#                 print(f'{fichier_texte} | {len(context)}, {len(query_terms)} | {context}\n')
#     if out:
#         f.close()
        
# def get_synonyms(word):
#     synonyms = []
#     for syn in wordnet.synsets(word, lang='fra'):
#         for lemma in syn.lemmas('fra'):
#             synonyms.append(lemma.name())
#     return synonyms

# def SYNOREQET(index, query):
#     query_terms = query.split()
#     synonyms = []
#     for word in query_terms:
#         synonyms.extend(get_synonyms(word))
#     query_postings = []
#     for term in synonyms:
#         if term not in index:
#             print(f"No results found for term '{term}'")
#             break
#         else:
#             query_postings.append(index[term])
#     else:
#         results = set.intersection(*query_postings)
#         print_results(results, sz, out, synonyms)

# def SYNOREQOU(index, query):
#     query_terms = query.split()
#     synonyms = []
#     for word in query_terms:
#         synonyms.extend(get_synonyms(word))
#     results = set()
#     for term in synonyms:
#         if term in index:
#             results.update(index[term])
#     if len(results) > 0:
#         print_results(results, sz, out, synonyms)
#     else:
#         print(f"No results found for any of the terms: {', '.join(synonyms)}")


# fichier_texte = 'JV80.txt'
# inverted_index = index_inverse(fichier_texte)
# sz = 0
# out = None
# while True:
#     command = input('INTERO> ')

#     if command.startswith('SZ ='):
#         sz = int(command.split('=')[1].strip())
#     elif command == 'SZ?':
#         print(f"SZ = {sz}")
#     elif command.startswith('OUT ='):
#         out = command.split('=')[1].strip()
#         if out.lower() == 'none':
#             out = None
#     elif command == 'OUT?':
#         print(f"OUT = {out}")
#     elif command.startswith('RQET ='):
#         query_terms = command.split('=')[1].strip().split(',')
#         query_terms = [term.strip() for term in query_terms]
#         query_postings = []
#         for term in query_terms:
#             if term not in inverted_index:
#                 print(f"No results found for term '{term}'")
#                 break
#             else:
#                 query_postings.append(inverted_index[term])
#         else:
#             results = set.intersection(*query_postings)
#             print_results(results, sz, out, query_terms)
#     elif command.startswith('RQOU ='):
#         query_terms = command.split('=')[1].strip().split(',')
#         query_terms = [term.strip() for term in query_terms]
#         results = set()
#         for term in query_terms:
#             if term in inverted_index:
#                 results.update(inverted_index[term])
#         if len(results) > 0:
#             print_results(results, sz, out, query_terms)
#         else:
#             print(f"No results found for any of the terms: {', '.join(query_terms)}")
#     elif command.startswith('SYNOREQET ='):
#         query_terms = command.split('=')[1].strip()
#         SYNOREQET(inverted_index, query_terms)
#     elif command.startswith('SYNOREQOU ='):
#         query_terms = command.split('=')[1].strip()
#         SYNOREQOU(inverted_index, query_terms)
#     elif command == 'QUIT':
#         break
#     else:
#         print("Invalid command")



# fichier_texte = 'JV80.txt'

# # Index Inverse
# inverted_index = index_inverse(fichier_texte)

# # Index Inverse Syntaxique
# index_inverse_syntaxique = index_inverse_syntaxique(fichier_texte)

# # Interrogation de l'index inversé syntaxique
# interro_index_inverse_syntaxique(index_inverse_syntaxique)



##### FOnctionne avec un seul fichier =>



# import nltk
# import spacy
# from nltk.corpus import wordnet
# nltk.download('punkt')
# nlp = spacy.load('fr_core_news_sm')

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

# def index_inverse(fichier_texte):
#     inverted_index = {}
#     with open(fichier_texte, 'r', encoding='utf-8') as f:
#         for num_ligne, ligne in enumerate(f, start=1):
#             for mot in ligne.strip().split():
#                 if mot not in inverted_index:
#                     inverted_index[mot] = {num_ligne}
#                 else:
#                     inverted_index[mot].add(num_ligne)
#     return inverted_index

# def print_results(results, sz=0, out=None, query_terms=None):
#     if out:
#         f = open(out, 'w', encoding='utf-8')
#     for result in results:
#         with open(fichier_texte, 'r') as f:
#             start_line = max(1, result - sz)
#             end_line = result + sz + 1
#             context_lines = [f'{i}: {line.strip()}' for i, line in enumerate(f, start=1) if start_line <= i < end_line]
#             context_lines = [line for line in context_lines if any(term in line for term in query_terms)]
#             context = ' '.join(context_lines)
#             if query_terms:
#                 for i, term in enumerate(query_terms):
#                     context = context.replace(term, f'<Q{i}>{term}</Q{i}>')
#             if out:
#                 f.write(f'{fichier_texte} | {len(context)}, {len(query_terms)} | {context}\n')
#             else:
#                 print(f'{fichier_texte} | {len(context)}, {len(query_terms)} | {context}\n')
#     if out:
#         f.close()

# def get_synonyms(word):
#     synonyms = []
#     for syn in wordnet.synsets(word, lang='fra'):
#         for lemma in syn.lemmas('fra'):
#             synonyms.append(lemma.name())
#     return synonyms

# def SYNOREQET(index, query):
#     query_terms = query.split()
#     synonyms = []
#     for word in query_terms:
#         synonyms.extend(get_synonyms(word))
#     query_postings = []
#     for term in synonyms:
#         if term not in index:
#             print(f"No results found for term '{term}'")
#             break
#         else:
#             query_postings.append(index[term])
#     else:
#         results = set.intersection(*query_postings)
#         print_results(results, sz, out, synonyms)

# def SYNOREQOU(index, query):
#     query_terms = query.split()
#     synonyms = []
#     for word in query_terms:
#         synonyms.extend(get_synonyms(word))
#         results = set()
#     for term in synonyms:
#             if term in index:
#                 results.update(index[term])
#             if len(results) > 0:
#                 print_results(results, sz, out, synonyms)
#             else:
#                  print(f"No results found for any of the terms: {', '.join(synonyms)}")
# fichier_texte = 'JV80.txt'
# inverted_index = index_inverse(fichier_texte)
# index_inverse_syntaxique = index_inverse_syntaxique(fichier_texte)
# sz = 0
# out = None

# while True:
#     command = input('INTERO> ')
    
#     if command.startswith('SRQET =') or command.startswith('SRQOU ='):
#         query_terms = command.split('=')[1].strip().split(' ')
#         query_terms = [(term.split('/')[0], term.split('/')[1]) for term in query_terms]
#         results = []
#         for item in index_inverse_syntaxique:
#             file_name, line_num, sent_text, token_text, token_pos, token_dep, head_pos = item
#             for term, dep in query_terms:
#                 if term == token_text and dep == token_dep:
#                     results.append(item)
#                     break
#         if len(results) == 0:
#             print(f"No results found for terms '{' '.join([f'{term}/{dep}' for term, dep in query_terms])}'")
#         else:
#             for item in results:
#                 file_name, line_num, sent_text, token_text, token_pos, token_dep, head_pos = item
#                 formatted_sent = sent_text.replace(token_text, f"<{token_dep}{token_pos}>{token_text}</{token_dep}{token_pos}>")
#                 print(f"{file_name} | {line_num} | {formatted_sent}")
    
#     elif command.startswith('SZ ='):
#         sz = int(command.split('=')[1].strip())
#     elif command == 'SZ?':
#         print(f"SZ = {sz}")
#     elif command.startswith('OUT ='):
#         out = command.split('=')[1].strip()
#         if out.lower() == 'none':
#             out = None
#     elif command == 'OUT?':
#         print(f"OUT = {out}")
#     elif command.startswith('RQET ='):
#         query_terms = command.split('=')[1].strip().split(',')
#         query_terms = [term.strip() for term in query_terms]
#         query_postings = []
#         for term in query_terms:
#             if term not in inverted_index:
#                 print(f"No results found for term '{term}'")
#                 break
#             else:
#                 query_postings.append(inverted_index[term])
#         else:
#             results = set.intersection(*query_postings)
#             print_results(results, sz, out, query_terms)
#     elif command.startswith('RQOU ='):
#         query_terms = command.split('=')[1].strip().split(',')
#         query_terms = [term.strip() for term in query_terms]
#         results = set()
#         for term in query_terms:
#             if term in inverted_index:
#                 results.update(inverted_index[term])
#         if len(results) > 0:
#             print_results(results, sz, out, query_terms)
#         else:
#             print(f"No results found for any of the terms: {', '.join(query_terms)}")
#     elif command.startswith('SYNOREQET ='):
#         query_terms = command.split('=')[1].strip()
#         SYNOREQET(inverted_index, query_terms)
#     elif command.startswith('SYNOREQOU ='):
#         query_terms = command.split('=')[1].strip()
#         SYNOREQOU(inverted_index, query_terms)
#     elif command == 'QUIT':
#         break
#     else:
#         print(f"Unrecognized command: '{command}'")

