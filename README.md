# Scraping-openfoodfacts

## Résumé
Ce projet a pour but de scraper les données du site [openfoodfacts](https://fr.openfoodfacts.org/). Pour chaque produit, on souhaite récupérer l'ensemble des informations permettant d'évaluer l'impact sur la santé et l'environnement.    

## Description 

Le fichier opfoodfact.py contient les fonctions permettant de parcourir chaque page produit et de scraper les informations voulues : teneurs en sucres, énérgie, nutri-score, écoscore ... Les données sont répertoriées dans data.csv.  
Le fichier projet_celine_mendola.ipynb lance l'exécution du scraping puis nettoie les données récupérées (data_cleaned.csv). Enfin quelques analyses de données sont effectuées. 
