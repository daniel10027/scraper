#!/usr/bin/python

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import selenium.webdriver.chrome.service as service
import itertools


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
            return get_octopus_data("{uri}&page={page}".format(uri=uri,page=page))
        elif check_key_exist(uri) :
            return get_octopus_data("{uri}&page={page}".format(uri=get_key_uri(uri),page=page))
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

def wait(driver,selector) :
    WebDriverWait(driver, 3).until( 
        expected_conditions.presence_of_all_elements_located( 
            (By.CSS_SELECTOR, selector)
        ) 
    )
    

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

def ikea_get_article(url) :
    
    results = []
    liens = ikea_lien()

    if url in liens :
        links = connexion(url,"div","class","product-compact__spacer")
    elif ikea_get_key_uri(url) in liens:
        links = connexion(ikea_get_key_uri(url),"div","class","product-compact__spacer")
    else :
        raise Exception("L'url recherche n'existe pas")
    
    # ikea_click_paginate(url)

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

def ikea_get_key_uri(key) :
    if key in ikea_categorie() :
        for el in ikea_main():
            for it in el["souscat"] :
                if it["nom"] == key :
                    return it["lien"]
    else :
        raise Exception('Veuillez entrer un bon mot clé')

def ali_express_init():
    url = "https://fr.aliexpress.com"
    categories = connexion(url,"dl","class","cl-item")
    return categories

def ali_baba_search_article(categorie,page=1) :
    els = []
    url = "https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText={categorie}&page={page}".format(categorie=categorie,page=page)
    articles = connexion(url,"div","class","m-gallery-product-item-wrap")
    for item in articles  :
        result = {}
        result["image"] = item.find("img")['src']
        result["libelle"] = item.find("img")['alt']
        result["prix"] = item.find("b")
        els.append(result)
    return els

def ali_express_article(url) :
    els = []
    articles = connexion(url,"div","class","item")
    
    if articles == []:
        articles = connexion(url,"li","class","list-item")
    
    for item in articles  :
        result = {}
        result["image"] = item.find("img")['src']
        result["libelle"] = item.find("img")['alt']
        result["prix"] = item.find("div",attrs={"class":"info"}).find("span",attrs={"class":"value"}).text
        print(result)
        els.append(result)
    return els

def ali_express_format_categorie(categorieHtml) :
    name = categorieHtml.find('dt',attrs={"class":"cate-name"}).find('a')
    if name :
        result = {
            'nom': name.text,
            'lien': name['href']
        }
        return result

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

def ali_express_categorie() :
    return ali_express_categorie_function_caller(1)


def ali_express_souscategorie() :
    return ali_express_categorie_function_caller(2)


def ali_express_items() :
    return ali_express_categorie_function_caller(3)

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

def list_merge(merge_list):
    return list(itertools.chain.from_iterable(merge_list))

def ali_express_all():
    return list_merge(ali_express_items()) + ali_express_souscategorie() + list_merge(ali_express_categorie())

def ali_express_fns(var):
    result = []
    for item in ali_express_all() :
        if item['nom'] not in result :
            result.append(item[var])
    return result

def ali_express_keys():
    return ali_express_fns('nom')

def ali_express_links():
    return ali_express_fns('lien')

def ali_express_get_url(key):
    alls = ali_express_all()
    for item in alls :
        if key == item['nom']:
            return item['lien']

def url_paginate_ali_express(url, page = 1):
    if page > 1:
        idx = url.index('.html')
        newUri = "{un}/{page}{deux}".format(un=url[:idx],page=page,deux=".html?site=fra&tag=")
        return newUri
    return url


def zalando(typ,categorie,page=1):
    ret = []
    if page > 1:
        url = 'https://www.zalando.fr/{typ}/?q={categorie}&p={page}'.format(typ=typ,categorie=categorie,page=page)
    else:
        url = 'https://www.zalando.fr/{typ}/?q={categorie}'.format(typ=typ,categorie=categorie)
    
    articles = connexion(url,"z-grid-item","class","cat_articleCard-1r8nF")
    
    for item in articles :
        res = {
            'images': item.find('img',attrs={'class':'cat_image-1byrW'})['src'],
            'nom': item.find('img',attrs={'class':'cat_image-1byrW'})['alt'],
            'prix': item.find('div',attrs={'class':'cat_originalPrice-2Oy4G'}).find('span').text
        }
        ret.append(res)

    return ret    

if __name__ == "__main__": 
    
    # print(zalando("enfant",'jouet fille'))
    # print(connexion("https://www.alibaba.com/trade/search?fsb=y&IndexArea=product_en&CatId=&SearchText=table&page=1","b"))
    # for link in new :
    #     print(link)
    
