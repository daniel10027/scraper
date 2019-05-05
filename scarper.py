#!/usr/bin/python

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


base = 'https://www.amazon.fr'
categorie = 'https://www.amazon.fr/gp/site-directory?pf_rd_p=c5273c8d-4caa-4cd7-bc78-0035916feb89&pf_rd_r=MC70K3AW297B2PYMPZQB'

def connexion(url, selected = None, attr = None, attrsValue = None):
    page = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(page.content, 'html.parser')

    if selected != None and attr is None and attrsValue is None :
        return soup.select(selected)

    elif selected != None and attr != None and attrsValue != None :
        return soup.findAll(selected,attrs={attr:attrsValue})
    elif selected == None and attr == None and attrsValue == None :
        return soup
    else:
        raise Exception('Veuillez entrer convenablement les parametres de la fonction')

def get_website_categorie(url):
    results = []
    categories = connexion(url,'div',"class","popover-grouping")
    for categorie in categories :
        result = {
            "nom":categorie.find('h2',attrs={"class":"popover-category-name"}).text,
            "sousCategories": [{sousCat.text:sousCat['href']} for sousCat in categorie.findAll('a',attrs={"class":"nav_a"})]
        }
        results.append(result)
  
    return results

def get_website_data(url) :
    results = []
    sections = connexion(url,'li',"class","octopus-pc-item")
    
    for section in sections :
        results.append(section)
    
    return results

def get_octopus_data(url):
    datas = get_website_data(url)
    result = []
    
    for data in datas :
        result.append(get_website_data_detail(data))

    return list(filter(lambda x: x is not None, result))
    
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

def get_all_page_url_suffix(url) :
    uris = []
    uri = get_website_categorie(url)
    for item in uri :
        for extend in item["sousCategories"] :
            for values in extend.values() :
                uris.append(values)
    return uris

def get_all_key_uri() :
    result = []
    urls = get_website_categorie(categorie)
    for url in urls :
        dir = [d.keys() for i,d in enumerate(url["sousCategories"])]
        result.append(dir)
    return result

def get_all_uri(url):
    urls = get_all_page_url_suffix(url)
    return [urljoin(base,uri) for uri in urls]

def check_key_exist(key) :
    result = []
    urls = get_website_categorie(categorie)
    for url in urls :
        dir = any([d[key] for i,d in enumerate(url["sousCategories"]) if key in d])
        result.append(dir)
    return any(result)

def get_key_uri(key) :
    result = []
    urls = get_website_categorie(categorie)
    for url in urls :
        dir = [d[key] for i,d in enumerate(url["sousCategories"]) if key in d]
        result.append(dir)

    new = list(filter(lambda x: x != [], result))
    return urljoin(base, new[0][0])

def conversion(entier=0, decimal= 0, symbol='€') :
    prix = round(float("{entier}.{decimal}".format(entier=entier,decimal=decimal)))
    if symbol == '€' :
        return 655 * prix
    else :
        return 587 * prix

def paginate_uri(uri, page=1) :
    if isinstance(page,int) and page < 1 :
        raise Exception("La page recherche n'existe pas et ne peux etre inferieur a 1")
    elif isinstance(page,str) :
        raise Exception("Veullez entrer une valeur entier")
    elif isinstance(page,int) :
        if uri in get_all_uri(categorie) :
            return connexion("{uri}&page={page}".format(uri=uri,page=page))
        elif check_key_exist(uri) :
            return connexion("{uri}&page={page}".format(uri=get_key_uri(uri),page=page))
        else :
            raise Exception("L'url taper n'existe pas")
    else :
        raise Exception("Erreur non reconnu")

def ikea_main():
    result = []
    items = connexion('https://www.ikea.com/fr/fr/','li',"class","desktop-menu__item")
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

def ikea_lien() :
    link = []
    result = ikea_main()

    for el in result:
        for it in el["souscat"] :
            link.append(it['lien'])
    return link

def ikea_categorie() :
    link = []
    result = ikea_main()

    for el in result:
        for it in el["souscat"] :
            link.append(it['nom'])
    return link


def ikea_get_key_uri(key) :
    if key in ikea_categorie() :
        for el in ikea_main():
            for it in el["souscat"] :
                if it["nom"] == key :
                    return it["lien"]
    else :
        raise Exception('Veuillez entrer un bon mot clé')

if __name__ == "__main__": 
    
    links = connexion('http://cursus.nan.ci')
    # print(links)
    for link in links:
        print(link)
        print()
   
   

        