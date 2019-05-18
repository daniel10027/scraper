#!/usr/bin/python

import connexion
import scarper
from bs4 import BeautifulSoup


"""
    Permet de lister l'ensemble des categories et liens associes
    list dict
"""
def ikea_main():
    result = []
    items = connexion.connexion('https://www.ikea.com/fr/fr/','li',"class","desktop-menu__item")
    for item in items :
        obj = {}
        obj["titre"] = item.find('span',attrs={'class':'desktop-menu__title'}).text
        obj["souscat"] = []
        if item.find('ul', attrs={'class':'desktop-menu__level1'}) :
            sousCat = item.findAll('li', attrs={'class':'desktop-menu__level1__item'})
            for cat in sousCat :
                if cat.find('ul',attrs={"class":"desktop-menu__level2"}):
                    links = cat.findAll('a') 
                    for link in links :
                        l = {}
                        l["nom"] = link.text
                        l["lien"] = link['href']
                        obj["souscat"].append(l)
                        result.append(obj)
                else:
                    continue
    
    return result

"""
    Permet de lister l'ensemble des liens
    list
"""
def ikea_lien() :
    link = []
    result = ikea_main()

    for el in result:
        for it in el["souscat"] :
            link.append(it['lien'])
    return link

"""
    Permet de lister l'ensemble des categories
    list
"""
def ikea_categorie() :
    link = []
    result = ikea_main()

    for el in result:
        for it in el["souscat"] :
            link.append(it['nom'])
    return link

    
"""
    Cette fonction sera implementer quand je vais finir la fonction connexion
"""
# def ikea_click_paginate(url) :
#     results = []
#     driver = webdriver.Chrome("/Users/armelreal/Downloads/chromedriver")
#     liens = ikea_lien()
#     if url in liens :
#         links = driver.get(url)
#     elif ikea_get_key_uri(url) in liens:
#         links = driver.get(ikea_get_key_uri(url))
#     else:
#         raise Exception("Erreur mauvaise url")

#     html = connexion(driver.page_source,"div","class","catalog-product-list__total-count")
#     print(driver.current_url)
#     # end = int(int(html[-1]) / int(html[1])) - 1
#     wait(driver,'div.product-compact__spacer')
    
#     if driver.find_element_by_css_selector('button.range-btn.catalog-product-list__load-more-button.range-btn--filled.js-load-more__button') and end > 0:      
#         button = driver.find_element_by_css_selector('button.range-btn.catalog-product-list__load-more-button.range-btn--filled.js-load-more__button')
#         for i in end:
#             button.click()
#             wait(driver,'div.product-compact__spacer')
#             driver.implicitly_wait(5)
#             if button.is_displayed() :
#                 continue
#             else :
#                 break
    
#     links = connexion(driver.current_url,"div","class","product-compact__spacer")

#     for link in links:
#         obj = {}
        
#         if link.find('img') : 
#             obj["image"] = link.find('img')['src']
        
#         if link.find('span',attrs={'class':"product-compact__name"}) :     
#             obj["nom"] = link.find('span',attrs={'class':"product-compact__name"}).text.strip()
        
#         if link.find('span',attrs={'class':"product-compact__type"}) :             
#             obj["type"] = link.find('span',attrs={'class':"product-compact__type"}).text.strip()
        
#         if link.find('span',attrs={'class':"product-compact__description"}) :                     
#             obj["description"] = link.find('span',attrs={'class':"product-compact__description"}).text.strip()
        
#         if link.find('span',attrs={'class':"product-compact__price"}) :                             
#             obj["prix"] = link.find('span',attrs={'class':"product-compact__price"}).text.strip()

#         if link.find('span',attrs={'class':"product-compact__ratings"}) :                                 
#             obj["avis"] = link.find('span',attrs={'class':"product-compact__ratings"}).text.strip()
        
#         results.append(obj)
#     driver.quit()
#     return results

"""
    list des articles de la page
    list dict
"""
def ikea_get_article(url) :
    
    results = []
    liens = ikea_lien()

    if url in liens :
        links = connexion.connexion(url,"div","class","product-compact__spacer")
    elif ikea_get_key_uri(url) in liens:
        links = connexion.connexion(ikea_get_key_uri(url),"div","class","product-compact__spacer")
    else :
        raise Exception("L'url recherche n'existe pas")
    
    for link in links:
        obj = {}
        
        if link.find('img') : 
            obj["image"] = link.find('img')['src']
        
        if link.find('span',attrs={'class':"product-compact__name"}) :     
            obj["nom"] = link.find('span',attrs={'class':"product-compact__name"}).text.strip()
        
        if link.find('span',attrs={'class':"product-compact__type"}) :             
            obj["type"] = link.find('span',attrs={'class':"product-compact__type"}).text.strip()
        
        if link.find('span',attrs={'class':"product-compact__description"}) :                     
            obj["description"] = link.find('span',attrs={'class':"product-compact__description"}).text.strip()
        
        if link.find('span',attrs={'class':"product-compact__price"}) :                             
            obj["prix"] = link.find('span',attrs={'class':"product-compact__price"}).text.strip()

        if link.find('span',attrs={'class':"product-compact__ratings"}) :                                 
            obj["avis"] = link.find('span',attrs={'class':"product-compact__ratings"}).text.strip()
        
        results.append(obj)

    return results

"""
    Permet de generer l'url associe a un mot clef
"""
def ikea_get_key_uri(key) :
    if key in ikea_categorie() :
        for el in ikea_main():
            for it in el["souscat"] :
                if it["nom"] == key :
                    return it["lien"]
    else :
        raise Exception('Veuillez entrer un bon mot clé')

""" 
    A venir un exple de chaque fonction 
"""