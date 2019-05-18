#!/usr/bin/python

import connexion
import scarper
from bs4 import BeautifulSoup

"""
    Cette fonciton nous permet de recuperer le blog des categorie du site https://fr.aliexpress.com
    return list categories
"""
def ali_express_init():
    url = "https://fr.aliexpress.com"
    categories = connexion.connexion(url,"dl","class","cl-item")
    return categories

""" 
    Cette fonction prend en parametre une url et retourne les articles concernant cette url
    Mais il peut arriver qu'aucun article ne soit retourner tous simplement parce que ali express vous black-list au bout d'un certains nombre de requete et vous demande de vous connecte pour acceder a cette page
    Je n'ai pas encore compris comment contourner leur redirection
    Pour ne pas etre black-lister deh le debut il est preferable de lancer le scrap de facon anonyme et avec un navigateur 
    return list article
"""
def ali_express_article(url) :
    els = []
    """
        Ali express possede deux formatage de ses articles selon la page
        pour certaines item d'autre list-item
        donc je verifie les deux condition si la premiere ne me retourne rien je passe au second
    """

    # articles = connexion.connexion(url,"div","class","item") etablir une connexion a la page de facon normale 
    articles = connexion.connexion(url,"div","class","item",True,True) # connexion anonyme et avec un navigateur
    
    if articles == []:
        # articles = connexion.connexion(url,"li","class","list-item") etablir une connexion a la page de facon normale 
        articles = connexion.connexion(url,"li","class","list-item",True,True) # connexion anonyme et avec un navigateur
    
    if articles is not []:
        for item in articles  :
            result = {}
            
            if item.find("img") :
                result["image"] = item.find("img")['src']
                result["libelle"] = item.find("img")['alt']
                
                if item.find("div",attrs={"class":"info"}).find("span",attrs={"class":"value"}):
                    result["prix"] = item.find("div",attrs={"class":"info"}).find("span",attrs={"class":"value"}).text
            
            print(result)
            els.append(result)

        return els

"""
    cette fonction me permet de formater les categories que je retrouve sur ali-express
    prend en parametre une list de categorie en html
    return une list dict de categorie
"""
def ali_express_format_categorie(categorieHtml) :
    name = categorieHtml.find('dt',attrs={"class":"cate-name"}).find('a')
    if name :
        result = {
            'nom': name.text,
            'lien': name['href']
        }
        return result

"""
    cette fonction me permet de formater les sous-categories que je retrouve sur ali-express
    prend en parametre une list de categorie en html
    return une list dict de sous-categorie
"""
def ali_express_format_souscategorie(categorieHtml) :
    els = []
    names = categorieHtml.find('dd',attrs={"class":"sub-cate"}).find('dt').findAll('a')
    if names :
        for name in names:
            if name.text :
                result = {
                    'nom': name.text,
                    'lien': name['href']
                }
                els.append(result)
        return els

"""
    cette fonction me permet de formater chaque element retrouver dans chaque sous-categorie que je retrouve sur ali-express
    prend en parametre une list de categorie en html
    return une list dict de sous-sous-categorie
"""
def ali_express_format_items(categorieHtml) :
    els = []
    names = categorieHtml.find('dd',attrs={"class":"sub-cate"}).find('dd').findAll('a')
    if names :
        for name in names:
            if name.text :
                result = {
                    'nom': name.text,
                    'lien': name['href']
                }
                els.append(result)
        return els
"""
    retourne les categorie de ali express
"""
def ali_express_categorie() :
    return ali_express_categorie_function_caller(1)

"""
    retourne les sous-categorie de ali express
"""
def ali_express_souscategorie() :
    return ali_express_categorie_function_caller(2)

"""
    retourne les sous-sous-categorie de ali express
"""
def ali_express_items() :
    return ali_express_categorie_function_caller(3)

"""
    Fonction de traitement elle permet de nous retourner(categorie, sous-categorie ou sous-sous-categorie)
"""
def ali_express_categorie_function_caller(n = 1) :
    els = []
    for item in ali_express_init() :
        if n == 1 :
            result = ali_express_format_souscategorie(item)
        elif n == 2 :
            result = ali_express_format_categorie(item)
        elif n == 3 :
            result = ali_express_format_items(item)

        if result :
            els.append(result)
    return els

"""
    return list all categories mot clef plus lien
"""
def ali_express_all():
    return scarper.list_merge(ali_express_items()) + ali_express_souscategorie() + scarper.list_merge(ali_express_categorie())

"""
    Traitement fonction pour recuperer les nom des mot clef ou les liens de toutes les categories du site
    Les liens et les mots clefs sont uniques 
"""
def ali_express_fns(var):
    result = []
    for item in ali_express_all() :
        if item['nom'] not in result :
            result.append(item[var])
    return result

"""
    Liste des mots clef de toutes les categories
"""
def ali_express_keys():
    return ali_express_fns('nom')

"""
    Liste des liens de toutes les categories
"""
def ali_express_links():
    return ali_express_fns('lien')

"""
    Le parametres key est une categorie d'article
    permet de nous donner l'url correspond a la categorie du mot clef
"""
def ali_express_get_url(key):
    alls = ali_express_all()
    for item in alls :
        if key == item['nom']:
            return item['lien']

"""
    cette fonction nous permet de retourner la page que l'on souhaite afficher
    return str url
"""
def url_paginate_ali_express(url, page = 1):
    if page > 1:
        idx = url.index('.html')
        newUri = "{un}/{page}{deux}".format(un=url[:idx],page=page,deux=".html?site=fra&tag=")
        return newUri
    return url

"""
    Pour tester le fonctionnement de chaque fonction decomment bloc par bloc 
"""
# if __name__ == "__main__":

    # items =  ali_express_items()
    # scarper.affichage(items)

    # sous-categories =  ali_express_souscategorie()
    # scarper.affichage(sous-categories)
    
    # categories =  ali_express_categorie()
    # scarper.affichage(categories)
    
    # all = ali_express_all()
    # scarper.affichage(all)

    # clef = ali_express_keys()
    # scarper.affichage(clef)

    # links = ali_express_links()
    # scarper.affichage(clef)

    # chemise = ali_express_get_url('Chemises')
    # print(chemise)

    # chemise = url_paginate_ali_express(ali_express_get_url('Chemises'),2)
    # print(chemise)

    # electronic = url_paginate_ali_express('https://fr.aliexpress.com/category/205000021/consumer-electronics.html?ltype=wholesale&',2)
    # print(electronic)

    # categories = ali_express_init()
    # scarper.affichage(categories)

    # articles = ali_express_article('https://fr.aliexpress.com/category/205000021/consumer-electronics.html?ltype=wholesale&')
    # scarper.affichage(articles)

    # articles = ali_express_article(ali_express_get_url('Chemises'))
    # scarper.affichage(articles)

    # articles = ali_express_article(url_paginate_ali_express(ali_express_get_url('Chemises'),2))
    # scarper.affichage(articles)

    # articles = ali_express_article(url_paginate_ali_express('https://fr.aliexpress.com/category/205000021/consumer-electronics.html?ltype=wholesale&',2))
    # scarper.affichage(articles) 