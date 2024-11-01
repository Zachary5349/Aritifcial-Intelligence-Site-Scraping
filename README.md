# Site Scraping

## A fully functional site scraping program that uses twikit to obtain information, a SQL server to store information, and then visualizes the information with Tableau.

### Disclaimer 
This application is for informational purposes only.

Welcome to the Site Scraping Program, an AI application mdae to get data from other websites. 
This program uses a twitter scraping API called twikit to obtain data from specific Twitter Handles.
This program is current getting data from HP's offical account and tracks and visualizes it through Tableau Public. 
The program can be expanded to any twitter account, and using a different API than twikit, the program can be used on different applications, other than twitter, as well.

## For Developers: Comments are included in the code explaining functions and chunks of code. These will help explain how the program works.

## For Users and Developers: To run the program, many packages are required. Packages include: 

import datetime

import pandas as pd

import asyncio

import pypyodbc as odbc


After importing the latest versions of the packages, you should be able to run the code without errors. 

You will also need a twitter account, a SQL Database, and a Tablaeu public account if you want to visually display the data.


## If you find a bug or a possible improvement to this project, please submit an issue in the issues tab above. Thank you!
