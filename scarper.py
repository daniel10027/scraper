#!/usr/bin/python

import itertools

"""
    Cette fonction permet de transformer les list de list en une list
    merge_list est la list de list passer en parametres
    return une list
"""
def list_merge(merge_list):
    return list(itertools.chain.from_iterable(merge_list))


"""
    Cette fonction permet de faire l'affichage du contenu d'une liste
"""
def affichage(lst):
    i = 0
    for item in lst :
        print(item)
        print()
        i+=1
    print(i)