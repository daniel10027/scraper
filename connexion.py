#!/usr/bin/python

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from random import shuffle

"""
    anonymous connexion anonyme
    brow affichage du navigateur
    configuration de notre navigateur
"""
def build_chrome_options(anonymous = False, brow = False):
    PROXY = get_proxy_value()
    chrome_options = webdriver.ChromeOptions()
    
    if anonymous is True :
        chrome_options.add_argument("--proxy-server={proxy}".format(proxy=PROXY))
    if brow is False :
        chrome_options.add_argument("headless")

    return chrome_options

"""
    link url de la page
    generateur de proxy
"""
def get_proxies(link):
    
    soup = connexion(link,lxml=True)
    https_proxies = filter(lambda item: "yes" in item.text, soup.select("table.table tr"))
    
    for item in https_proxies:
        yield "{}:{}".format(item.select_one("td").text, item.select_one("td:nth-of-type(2)").text)

"""
    retourne une liste de proxy ranger aleatoirement
"""
def get_random_proxies_iter():
    proxies = list(get_proxies('https://www.sslproxies.org/'))
    shuffle(proxies)
    return iter(proxies)

"""
    retourne un proxy sans verification du fonctionnement a notre navigateur
"""
def get_proxy_value():
    proxies = list(get_proxies('https://www.sslproxies.org/'))
    shuffle(proxies)
    return proxies[0]

"""
    permet de recuperer un proxy valide
    session de connexion
    proxies de connexion
    validated validation du proxy
    retourne la reponse de la page pour le proxy utiliser
"""
def get_proxy(session, proxies, validated=False):
    session.proxies = {'https': 'https://{}'.format(next(proxies))}
    if validated:
        while True:
            try:
                return session.get('https://httpbin.org/ip').json()
            except Exception:
                session.proxies = {'https': 'https://{}'.format(next(proxies))}

"""
    retourne la reponse de la page pour le proxy utiliser
"""
def get_response(url):
    session = requests.Session()
    ua = UserAgent()
    proxies = get_random_proxies_iter()
    while True:
        try:
            session.headers = {'User-Agent': ua.random}
            print(get_proxy(session, proxies, validated=True))
            return session.get(url)
        except StopIteration:
            raise
        except Exception:
            pass

"""
    retourne le nombre de page
"""
def get_page_number(url, selected = None, attr = None, attrsValue = None,position=-1):
    pages = connexion(url,selected,attr,attrsValue)
    text = pages[0].text
    element = text.split()
    return element[position]

"""
    Attend que la page recharge son ajax
    driver de la page
    selement qu'on recherche
"""
def wait(driver,selector) :
    WebDriverWait(driver, 3).until( 
        expected_conditions.presence_of_all_elements_located( 
            (By.CSS_SELECTOR, selector)
        ) 
    )

"""
    interagir avec la page
    selected element a cliquer
"""
def click(driver = '', selected  = '',selectedWait = ''):
    if driver is not '' and selected  is not '':
        if driver.find_element_by_css_selector(selected):      
            button = driver.find_element_by_css_selector(selected)
            button.click()
            if selectedWait is not '':
                wait(driver,selectedWait)
            
            driver.implicitly_wait(5)
    else:
        raise Exception("Entrer le driver et l'element a selectionner")

"""
    Permet de me connecter a une url
    url c'est l'url de la page rechercher
    selected c'est l'element que je cherche a selectionner
    attr c'est la propriete que je recherche
    attrsValue c'est la valeur de la propriete
    anonymous connexion anonyme
    selenium utilisation de navigateur
    brow utilisation de navigateur en arriere plan ou non
    retourne la page ou la liste d'element selectionner
    lxml permet de choisir le parser de la page
    Pour le moment je n'ai pas encore integrer l'interaction avec ajax et navigateur
    il est lies aux fonctions click, wait, get_page_number
"""
def connexion(url, selected = None, attr = None, attrsValue = None,selenium=False,anonymous = False,brow=False,lxml=False): 
    
    if selenium == False:
        if anonymous == True:
            response = get_response(url)
            soup = BeautifulSoup(response.text, 'lxml')
        else:
            page = requests.get(url, allow_redirects=True)
            if lxml :
                soup = BeautifulSoup(page.text, 'lxml')
            else:
                soup = BeautifulSoup(page.content, 'html.parser')
    else:
        if brow is True and anonymous == False:
            driver = webdriver.Chrome("/Users/armelreal/Downloads/chromedriver")
        elif brow is True and anonymous == True:
            driver = webdriver.Chrome("/Users/armelreal/Downloads/chromedriver",chrome_options=build_chrome_options(True,False))            
        elif anonymous == True:
            driver = webdriver.Chrome("/Users/armelreal/Downloads/chromedriver",chrome_options=build_chrome_options(True))
        else:
            driver = webdriver.Chrome("/Users/armelreal/Downloads/chromedriver",chrome_options=build_chrome_options())
        
        links = driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.close()

    if selected != None and attr is None and attrsValue is None :
        return soup.select(selected)

    elif selected != None and attr != None and attrsValue != None :
        return soup.findAll(selected,attrs={attr:attrsValue})
    elif selected == None and attr == None and attrsValue == None :
        return soup
    else:
        raise Exception('Veuillez entrer convenablement les parametres de la fonction')
