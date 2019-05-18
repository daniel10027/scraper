#!/usr/bin/python

import connexion
import scarper
from bs4 import BeautifulSoup

"""
    cette fonction nous permet de retourner la page que l'on souhaite afficher
    return str url
"""
def ali_baba_paginate(categorie,page=1):
    if page > 1:
        url = 'https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText={categorie}&page={page}'.format(categorie=categorie,page=page)
    else:
        url = 'https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText={categorie}'.format(categorie=categorie)
    
    return url

"""
    Cette fonction permet de recuperer tous les articles d'une page ali-baba
    Le paremetre categorie permet de savoir la categorie d'article aue l'on recherche (chaussures, chemise, jeans, chaussettes, ...)
    Le parametre page nous permet de recuperer la page que l'on souhaite (1,2,3,....)
    Le parametre page est optionnel s'il n'est pas defini ce sera la premiere page qui sera recuperer
    return une list d'article
"""
def ali_baba_article(categorie,page=1) :
    els = []
    url = ali_baba_paginate(categorie,page)

    articles = connexion(url,"div","class","m-gallery-product-item-wrap")
    for item in articles  :
        result = {}
        result["image"] = item.find("img")['src']
        result["libelle"] = item.find("img")['alt']
        result["prix"] = item.find("b")
        els.append(result)
    return els

"""
    Pour tester le fonctionnement de chaque fonction decomment bloc par bloc 
"""
# if __name__ == "__main__": 
    
    # links = ali_baba_paginate('chaussures')
    # print(links)
    
    # links1 = ali_baba_paginate('chaussures',3)
    # print(links1)
    
    # new = ali_baba_article('montre')
    # scarper.affichage(new)

    # new1 = ali_baba_article('montre',3)
    # scarper.affichage(new1)