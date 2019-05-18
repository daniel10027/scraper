#!/usr/bin/python

import connexion
import scarper
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base = 'https://www.amazon.fr'
categorie = 'https://www.amazon.fr/gp/site-directory?pf_rd_p=c5273c8d-4caa-4cd7-bc78-0035916feb89&pf_rd_r=MC70K3AW297B2PYMPZQB'

"""
    retourne une liste de categorie
    list
"""
def get_website_categorie(url):
    results = []
    categories = connexion.connexion(url,'div',"class","popover-grouping")
    for categorie in categories :
        result = {
            "nom":categorie.find('h2',attrs={"class":"popover-category-name"}).text,
            "sousCategories": [{sousCat.text:sousCat['href']} for sousCat in categorie.findAll('a',attrs={"class":"nav_a"})]
        }
        results.append(result)
  
    return results

"""
    retourne une liste des bloc articles
    list
"""
def get_website_data(url) :
    results = []
    sections = connexion.connexion(url,'li',"class","octopus-pc-item")
    
    for section in sections :
        results.append(section)
    
    return results

"""
    list epurer des articles
    retourne une liste des bloc articles
    list
"""
def get_octopus_data(url):
    datas = get_website_data(url)
    result = []
    
    for data in datas :
        result.append(get_website_data_detail(data))

    return list(filter(lambda x: x is not None, result))

"""
    Formatage d'un bloc de page
    retourne les details du bloc
    dict
"""
def get_website_data_detail(row) :
    result = {}
    
    if row.find('a',attrs={"class":"octopus-pc-item-link"}) :
        result["titre"] = row.find('a',attrs={"class":"octopus-pc-item-link"})['title'].strip()
    if row.find('img',attrs={"class":"octopus-pc-item-image"}) :
        result["image"] = row.find('img',attrs={"class":"octopus-pc-item-image"})['src'].strip()
    if row.find('span',attrs={"class":"a-price-whole"}) :
        result["prix-entier"] = row.find('span',attrs={"class":"a-price-whole"}).text.strip().rstrip(',')
    if row.find('span',attrs={"class":"a-price-fraction"}) :
        result["prix-decimal"] = row.find('span',attrs={"class":"a-price-fraction"}).text
    if row.find('span',attrs={"class":"a-price-symbol"}) :
        result["prix-symbole"] = row.find('span',attrs={"class":"a-price-symbol"}).text.strip() 
    if row.find('span',attrs={"class":"a-text-strike"}) :
        result["prix-barre"] = row.find('span',attrs={"class":"a-text-strike"}).text.strip()
    
    if "prix-symbole" in result :
        if "prix-entier" in result.keys() and "prix-decimal" not in result.keys() :
            result["cfa"] = conversion(entier=int(result["prix-entier"]), symbol=result["prix-symbole"])
        elif "prix-entier" not in result.keys() and "prix-decimal" in result.keys() :
            result["cfa"] = conversion(decimal=int(result["prix-decimal"]), symbol=result["prix-symbole"])
        elif "prix-entier" in result.keys() and "prix-decimal" in result.keys() :
            result["cfa"] = conversion(entier=int(result["prix-entier"]), decimal=int(result["prix-decimal"]), symbol=result["prix-symbole"])
    else :
        if "prix-entier" in result.keys() and "prix-decimal" not in result.keys() :
            result["cfa"] = conversion(entier=int(result["prix-entier"]))
        elif "prix-entier" not in result.keys() and "prix-decimal" in result.keys() :
            result["cfa"] = conversion(decimal=int(result["prix-decimal"]))
        elif "prix-entier" in result.keys() and "prix-decimal" in result.keys() :
            result["cfa"] = conversion(entier=int(result["prix-entier"]), decimal=int(result["prix-decimal"]))
    
    if result != {} :
        return result 

"""
    retourne toutes les urls de amazon sans la base
    list
"""
def get_all_page_url_suffix(url) :
    uris = []
    uri = get_website_categorie(url)
    for item in uri :
        for extend in item["sousCategories"] :
            for values in extend.values() :
                uris.append(values)
    return uris

"""
    retourne toutes les mots clef (nom des categories) de amazon
    list
"""
def get_all_key_uri() :
    result = []
    urls = get_website_categorie(categorie)
    for url in urls :
        dir = [d.keys() for i,d in enumerate(url["sousCategories"])]
        result.append(dir)
    return result

"""
    retourne toutes les urls de amazon sans la base
    list
"""
def get_all_uri(url):
    urls = get_all_page_url_suffix(categorie)
    return [urljoin(base,uri) for uri in urls]

"""
    retourne bool
    verifie si l'url de la categorie d'article (un mot clef) existe
"""
def check_key_exist(key) :
    result = []
    urls = get_website_categorie(categorie)
    for url in urls :
        dir = any([d[key] for i,d in enumerate(url["sousCategories"]) if key in d])
        result.append(dir)
    return any(result)

"""
    retourne str
    l'url de la categorie d'article (un mot clef) existe
"""
def get_key_uri(key) :
    result = []
    urls = get_website_categorie(categorie)
    for url in urls :
        dir = [d[key] for i,d in enumerate(url["sousCategories"]) if key in d]
        result.append(dir)

    new = list(filter(lambda x: x != [], result))
    return urljoin(base, new[0][0])

"""
    retourne prix en cfa de la page
"""
def conversion(entier=0, decimal= 0, symbol='€') :
    prix = round(float("{entier}.{decimal}".format(entier=entier,decimal=decimal)))
    if symbol == '€' :
        return 655 * prix
    else :
        return 587 * prix

"""
    permet de faire la pagination d'url
    retourne egalement tous les articles de la page
    si un mot clef est passe on verifie qu'il existe puis on genere l'url associe a ce mot
    puis on fait sa pagination et enfin on cherche a recuperer les articles de la pages
    si une  url est passe on verifie on fait sa pagination et enfin on cherche a recuperer les articles de la pages
"""
def paginate_uri(uri, page=1) :
    if isinstance(page,int) and page < 1 :
        raise Exception("La page recherche n'existe pas et ne peux etre inferieur a 1")
    elif isinstance(page,str) :
        raise Exception("Veullez entrer une valeur entier")
    elif isinstance(page,int) :
        if uri in get_all_uri(categorie) :
            return get_octopus_data("{uri}&page={page}".format(uri=uri,page=page))
        elif check_key_exist(uri) :
            return get_octopus_data("{uri}&page={page}".format(uri=get_key_uri(uri),page=page))
        else :
            raise Exception("L'url taper n'existe pas")
    else :
        raise Exception("Erreur non reconnu")

"""
    Pour tester le fonctionnement de chaque fonction decomment bloc par bloc 
"""
# if __name__ == "__main__":

#     articles = paginate_uri('Films')
#     scarper.affichage(articles)

#     articles = paginate_uri('https://www.amazon.fr/gp/site-directory?pf_rd_p=f8890209-8271-489b-85ec-08d76ec9a128&pf_rd_r=EE5JXG1RGDKG8GRWAGJQ')
#     scarper.affichage(articles)

#     articles = paginate_uri('Films',2)
#     scarper.affichage(articles)

#     articles = paginate_uri('https://www.amazon.fr/gp/site-directory?pf_rd_p=f8890209-8271-489b-85ec-08d76ec9a128&pf_rd_r=EE5JXG1RGDKG8GRWAGJQ',2)
#     scarper.affichage(articles)

#     url = get_key_uri('Films')
#     print(url)

#     url = check_key_exist('Films')
#     print(url)

#     url = get_all_key_uri()
#     scarper.affichage(url)