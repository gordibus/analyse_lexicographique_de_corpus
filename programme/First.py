#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 15 16:42:47 2023

@author: gordibus
"""
import glob
import nltk
nltk.download('punkt')

def index_inverse(fichiers_texte):
    inverted_indexes = {}
    for fichier_texte in fichiers_texte:
        inverted_index = {}
        with open(fichier_texte, 'r', encoding='utf-8') as f:
            for num_ligne, ligne in enumerate(f, start=1):
                for mot in ligne.strip().split():
                    if mot not in inverted_index:
                        inverted_index[mot] = {num_ligne}
                    else:
                        inverted_index[mot].add(num_ligne)
        inverted_indexes[fichier_texte] = inverted_index
    return inverted_indexes

def print_results(fichier_texte, results, sz=0, out=None, query_terms=None):
    if out:
        f = open(out, 'w', encoding='utf-8')
    for result in results:
        with open(fichier_texte, 'r', encoding='utf-8') as f:
            start_line = max(1, result - sz)
            end_line = result + sz + 1
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


#fichiers_texte = ['JV80.txt', 'cinq_semaines_en_ballon.txt', 'de_la_terre_a_la_lune.txt', 'les_cinq_cents_millions_de_la_begum.txt', 'les_forceurs_de_blocus.txt', 'les_revoltes_de_la_bounty.txt', 'robur_le_conquerant.txt'] 
fichiers_texte=[]
path_corpora = "../DATA/*.txt"
for chemin in glob.glob(path_corpora):
    print(chemin)
    fichiers_texte.append(chemin)
inverted_indexes = index_inverse(fichiers_texte)

sz = 0
out = None
while True:
    command = input('INTERO> ')
    if command.startswith('SZ ='):
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
        for fichier_texte, inverted_index in inverted_indexes.items():
            query_postings = []
            for term in query_terms:
                if term not in inverted_index:
                    print(f"No results found for term '{term}'")
                    break
                else:
                    query_postings.append(inverted_index[term])
            else:
                results = set.intersection(*query_postings)
                print_results(fichier_texte, results, sz, out, query_terms)
    elif command.startswith('RQOU ='):
        query_terms = command.split('=')[1].strip().split(',')
        query_terms = [term.strip() for term in query_terms]
        for fichier_texte, inverted_index in inverted_indexes.items():
            results = set()
            for term in query_terms:
                if term in inverted_index:
                    results.update(inverted_index[term])
            if len(results) > 0:
                print_results(fichier_texte, results, sz, out, query_terms)
            else:
                print(f"No results found for any of the terms: {', '.join(query_terms)}")
    elif command == 'QUIT':
        break
    else:
        print("Invalid command")
