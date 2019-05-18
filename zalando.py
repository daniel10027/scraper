#!/usr/bin/python

import connexion
import scarper
from bs4 import BeautifulSoup

"""
    Cette fonction permet de recuperer tous les articles d'une page zalendo
    Le parametre typ permet de savoir quelle categorie de personne est viser a savoir (homme, femme ou enfant)
    Le paremetre categorie permet de savoir la categorie d'article aue l'on recherche (chaussures, chemise, jeans, chaussettes, ...)
    Le parametre page nous permet de recuperer la page que l'on souhaite (1,2,3,....)
    Le parametre page est optionnel s'il n'est pas defini ce sera la premiere page qui sera recuperer
    return une list d'article
"""
def zalando(typ,categorie,page=1):
    ret = []
    url  = zalando_paginate(typ,categorie,page)

    articles = connexion.connexion(url,"z-grid-item","class","cat_articleCard-1r8nF",anonymous=True)
    
    for item in articles :
        res = {}
        
        if item.find('img',attrs={'class':'cat_image-1byrW'}):
            res['images'] = item.find('img',attrs={'class':'cat_image-1byrW'})['src'],
            res['nom'] = item.find('img',attrs={'class':'cat_image-1byrW'})['alt'],
            
            if item.find('div',attrs={'class':'cat_originalPrice-2Oy4G'}).find('span') :
                res['prix'] = item.find('div',attrs={'class':'cat_originalPrice-2Oy4G'}).find('span').text
        
        if res is not {} :
            ret.append(res)

    return ret    

"""
    cette fonction nous permet de retourner la page que l'on souhaite afficher
    return str url
"""
def zalando_paginate(typ,categorie,page=1):
    if page > 1:
        url = 'https://www.zalando.fr/{typ}/?q={categorie}&p={page}'.format(typ=typ,categorie=categorie,page=page)
    else:
        url = 'https://www.zalando.fr/{typ}/?q={categorie}'.format(typ=typ,categorie=categorie)
    
    return url

"""
    Pour tester le fonctionnement de chaque fonction decomment bloc par bloc 
"""
if __name__ == "__main__": 
    
    links = zalando_paginate('homme','chaussures')
    print(links)
    
    # links1 = zalando_paginate('homme','chaussures',3)
    # print(links1)
    
    new = zalando("homme",'montre')
    scarper.affichage(new)

    # new1 = zalando("homme",'montre',3)
    # scarper.affichage(new1)
