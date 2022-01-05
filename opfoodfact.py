# -*- coding: utf-8 -*-
"""
Created on Wed May 19 15:24:18 2021

@author: celine
"""

#Import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import concurrent.futures



def getURL(nbpage=1):
    
  """
  Récupérer la liste des URL de chaque produit pour l'ensemble des pages
  Entrée: Nombre de pages
  Sortie: Liste des URL 
  
  """
  liste_URL=[]
  #Pour chaque page du site, récupérer son adresse url
  for p in range(1,1+nbpage):
    r=requests.get('https://fr.openfoodfacts.org/'+str(p))
    soup=BeautifulSoup(r.text,'html.parser')
    
    # puis récupérer l'adresse url de l'ensemble des produits
    for i in range(75,185):
        s=soup.find_all('a')[i]['href']
        if s.startswith('/produit/'):
            liste_URL.append('https://fr.openfoodfacts.org/'+s) 
            
  return liste_URL


def ahref(nom,soup):
    """ récupère le texte dans la balise dont l'attribut href contient la chaine de charactère
        saisie dans la variable nom
        Entrée : soup correspondant à la page d'un produit, 
                 nom correspondant au mot recherché dans l'attribut href
        sortie : textes de toutes les balises correspondantes séparés par une virgule """
    try:
        elt=''
        for a in soup.findAll(href=re.compile(nom)):
            elt+=a.text+', '
    except:
        elt="xxx"
    
    if elt=='':
        elt="xxx"
    return elt.strip()


liste_info=[]  #liste_info contiendra une liste de tupple, chaque tupple contiendra 
    #l'ensemble des caractériques scrappées d'un produit 

def scrape(url):   
    """ scrape les différents champs de la page d'un url donné 
    entrée : url
    sortie: un tuple avec tous les champs recherché ajouté à liste_info """
    
    r= requests.get(url)
    soup=BeautifulSoup(r.text,'html.parser')
    
    # récupérer le nom du produit
    try:
        nom=soup.find_all('h1',attrs={'property':'food:name'})[0].text.strip().replace("\xa0"," ")
    except :
        nom='xxx'

    
    # récupérer le code bar
    try:
        code_bar=soup.find_all('span',attrs={'property':'food:code'})[0].text
    except: 
        code_bar='xxx'
    
    # récupérer le nutri-score
    try:
        s=soup.find_all('script',attrs={"type":"text/javascript"})[0].contents[0].index("Nutri-Score ")
        nutrisc=soup.find_all('script',attrs={"type":"text/javascript"})[0].contents[0][s+12:s+13].strip().replace('n','xxx')
    except:
        nutrisc='xxx'
        
    # récupérer le score NOVA
    try:
        s=soup.find_all('script',attrs={"type":"text/javascript"})[0].contents[0].index("NOVA ")
        novasc=soup.find_all('script',attrs={"type":"text/javascript"})[0].contents[0][s+4:s+6].strip().replace('n','xxx')
    except:
        novasc='xxx'
    
    # récupérer l'Eco-score
    try:
        s=soup.find_all('script',attrs={"type":"text/javascript"})[0].contents[0].index("Eco-Score ")
        ecosc=soup.find_all('script',attrs={"type":"text/javascript"})[0].contents[0][s+10:s+11].strip().replace('n','xxx')
    except :
        try:
            s=soup.find_all('script',attrs={"type":"text/javascript"})[0].contents[0].index("Éco-Score ")
            ecosc=soup.find_all('script',attrs={"type":"text/javascript"})[0].contents[0][s+10:s+11].strip().replace('n','xxx')
        except:
            ecosc='xxx'

    #récupérer la quantité
    qu='xxx'
    for i in range(8,15):
        try:
            if soup.find_all('p')[i].text.strip().startswith('Quantité'):
                qu=soup.find_all('p')[i].contents[-1].strip()
        except :
            pass

    #récupérer le conditionnement
    cond=ahref('/conditionnement',soup)
    
    #récupérer les marques
    mar=ahref('/marque',soup)
    
    #Catégorie 
    cat=ahref('/categorie',soup)
    
    #récupérer le label 
    label=ahref('/label',soup)

    #récupérer l'origine des ingrédients
    origine=ahref('/origine',soup)
    
    #le lieux de fabrication et de transformation 
    fab=ahref('/lieu-de-fabrication|/commune',soup)

    #code de traçabilité
    tr=ahref('/code-emballeur|/commune',soup)
    
    #lien vers la page du produit sur le site officiel du fabricant
    liste_marque=re.split('; |, | & | - | ',mar.lower())
    mail=['@','.fr','.com','http://', 'www','https://']
    site="xxx"
    for i in range(0,len(soup.find_all('a'))):
        try:
            lien=soup.find_all('a')[i]['href']
            if any(ele in lien for ele in mail) and any(ele in lien for ele in liste_marque):
                site=soup.find_all('a')[i]['href']    
                break
        except KeyError:
            pass
    #magasins
    mag=ahref('/magasin',soup)
    
    #pays de vente
    pv=ahref('/pays',soup)
    
    
    #Additifs
    additifs=''
    for i in range(len(soup.find_all('a'))):
        try:
            elt=soup.find_all('a')[i]['href']
            if elt.startswith('/additif') and 'Risque' not in soup.find_all('a')[i].text:
                additifs+=soup.find_all('a')[i].text.strip('\n') +', '
        except:
            pass
    if additifs=='':
        additifs='xxx'
    additifs=additifs.strip()
        
    
    #ingrédients issus de l'huile de palme    
    hp=ahref('^/ingredients-',soup).replace('\r','')
    
#https://fr.openfoodfacts.org/ingredients-issus-de-l-huile-de-palme

    #Repères nnutritionels pour 100 g 
    #MG/lipides pour 100g
    try:
        mg=soup.find_all('div',attrs={"class":"small-12 xlarge-6 columns"})[-1].contents[4].strip()
    except:
        mg='xxx'
    
    #acides gras saturés pour 100g
    try:
        ag=soup.find_all('div',attrs={"class":"small-12 xlarge-6 columns"})[-1].contents[10].strip()
    except:
        ag='xxx'
    
    #sucres pour 100g
    try:
        sqe=soup.find_all('div',attrs={"class":"small-12 xlarge-6 columns"})[-1].contents[16].strip()
    except:
        sqe='xxx'
    
    #sel pour 100g
    try:
        sfq=soup.find_all('div',attrs={"class":"small-12 xlarge-6 columns"})[-1].contents[22].strip()
    except:
        sfq='xxx'
        
    #Comparaison avec les valeurs moyennes des produits de même catégorie (catégories cochées)
    forminput = soup.find_all("input",attrs={"checked":"checked"})
    vmcat=''
    for item in forminput:
        try:
            vmcat += item.next_sibling.strip()+ ', '
        except:
            pass
    vmcat=vmcat.strip()
    if vmcat=='':
        vmcat='xxx'

    #Energie en kj
    try:
        ekj=soup.find_all('tr',attrs={'id': "nutriment_energy-kj_tr", 'class':"nutriment_main"})[0].contents[3].text.strip().replace("\r|\n|\t", " ")
    except:
        ekj='xxx'
    
        
    #Energie en kcal
    try:
        ekcal=soup.find_all('tr',attrs={'id': "nutriment_energy-kcal_tr", 'class':"nutriment_main"})[0].contents[3].text.strip().replace("\r|\n|\t", " ").replace("?","xxx")
    except:
        ekcal='xxx'
        
    #Analyse des ingrédients
    #libellés rouge : avec huile de palme, non végétarien, non végétalien
    redlib=''
    r=soup.find_all('span',attrs={"class":"alert round label ingredients_analysis red"})
    for i in range(len(r)):
        try:
            redlib+=r[i].text.strip()+', '
        except:
            pass
    if redlib=='':
        redlib='xxx'
        
    #libellés verts : sans huile de palme, végétarien, végétalien
    greenlib=''
    g=soup.find_all('span',attrs={"class":"alert round label ingredients_analysis green"})
    for i in range(len(g)):
        try:
            greenlib+=g[i].text.strip()+', '
        except:
            pass
    if greenlib=='':
        greenlib='xxx'
    
    #libellés orange : pourrait contenir de l'huile de palme, peut être végétarien, peut être végétalien
    orangelib=''
    o=soup.find_all('span',attrs={"class":"alert round label ingredients_analysis orange"})
    for i in range(len(o)):
        try:
            orangelib+=o[i].text.strip()+', '
        except:
            pass
    if orangelib=='':
        orangelib='xxx'
        
    #vitamines ajoutées
    va=ahref('/vitamine',soup)
    #minéraux ajoutés
    ma=ahref('/mineral',soup)
            
    liste_info.append((nom,url,code_bar,nutrisc,novasc,ecosc,qu,cond,mar,cat,label,origine,fab,tr,site,mag,pv,additifs,hp,va,ma,mg,ag,sqe,sfq,vmcat,ekj,ekcal,\
                       greenlib,orangelib,redlib))
    return 
    

def scrap_opfoodfacts(nbpage):
    """fonction qui permet de scrapper les pages(de 1 à nbpage) du site openfoodfacts
    entrée : le nombre de pages
    sortie: le dataset data des données scrappées"""
    start=time.time()
    liste_URL=getURL(nbpage)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(scrape,liste_URL)
    TEMPS_EXEC=time.time()-start
    data=pd.DataFrame(liste_info,columns=['nom','URL','code bar','nutrtri-score','nova','ecoscore','quantite','conditionnement',"marques","categorie",'label,certifications,récompenses','origine',\
                                      'lieu de fabrication','code de traçabilité','lien vers la page du produit','magasins','pays de vente','additifs','ingrédients issus de l\'huile de palme', \
                                          'vitamines ajoutées','minéraux ajoutés', 'matières grasses/lipides pour 100g','acides gras saturés pour 100g', 'sucres pour 100g','sel pour 100g',\
                                              'catégories aux repères nutritionels similaires','énergie en kj','énergie en kcal','libellés vert','libellés orange','libellés rouge'])
    print('temps d\'exécution: ', TEMPS_EXEC,' sec')
    return data




