# -*- coding: utf-8 -*-'

"""
Created on Wed Apr  1 15:29:47 2020

@author: SereneWizard
"""
import os
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
import seaborn as sns


plt.rcParams["axes.labelsize"] = 14
plt.rcParams["axes.titlesize"] = 15
sns.set_style("whitegrid")


# All key value pairs

# 2011 actual population
population = {
                "National": 26494504,
                "Province 1": 4534943, 
                "Province 2": 5404145, 
                "Province 3": 5529452,
                "Province 4": 2403757, 
                "Province 5": 4499272,
                "Province 6": 1570418,
                "Province 7": 2552517,
                }

# 2018 Projected Population
population = {
                "National"   :	30124251.05,
                "Province 1" :	5156230.191,
                "Province 2" :	6144512.865,
                "Province 3" :	6286986.924,
                "Province 4" :	2733071.709,
                "Province 5" :	5115672.264,
                "Province 6" :	1785565.266,
                "Province 7" :	2902211.829,
                }

ylabels = {
    "Infected": "Projected infected population (in thousand)", 
    "Recovered": "Cumulative projected recovered (in thousand)",     
    "Deaths": "Cumulative projected deaths (in thousand)",
    "DeathsPerDay": "Projected deaths/day"
    }


# Setting up environment
workdir = os.getcwd()
plotdir = os.path.join(workdir, "plots")
datadir = os.path.join(workdir, "data")
outfileprefix = "Recovered"

# Make sure directories exist, otherwise create
for dir in [plotdir, datadir]:
    if not os.path.exists(dir):
        os.makedirs(dir)

projInfxn = 0.3
projChilam = 0.005
currentInfected = 5
totalRecovered = 0
allBeta = [0.4, 0.2, 0.13, 0.105]
gamma = 0.071429
startdate = date(2020, 4, 1)


treats = [
    "No", 
    "50", 
    "75", 
    "90"
    ]
colors = ['red', 'blue', 'cyan', 'green']

#Looping through the provinces
for province, popn in population.items():
    # Initializing the general plot parameters
    fig = plt.figure(figsize=(12,7))
    ax = fig.add_subplot(111)
    ax.set_xlim([0,600])
    #dateFmt = mdates.DateFormatter('%b-%Y')
    #ax.xaxis.set_major_formatter(dateFmt)
    ax.xaxis.set_major_locator(plt.MultipleLocator(90))
    
    # Looping through beta for each province
    for n, beta in enumerate(allBeta): 
        ns = popn * projInfxn
        prevSusceptible = int(ns)
        prevInfected = currentInfected
        prevRecovered = totalRecovered
        prevChilams = 0
        outputDict = {
            "day": [0],
            "susceptible": [prevSusceptible], 
            "infected": [prevInfected], 
            "recovered": [prevRecovered],
            "chilam": [0],
            "chilamPerDay": [0]
            }
        days = range(600)
        for day in days:
            susceptible = prevSusceptible - (prevSusceptible/ns)*(beta*prevInfected)
            infected = prevInfected + (prevSusceptible/ns) * (beta*prevInfected) - (prevInfected*gamma)
            recovered = prevRecovered + (prevInfected * gamma)
            chilams = recovered*projChilam
            chilamsPerDay = chilams-prevChilams
            
            outputDict["day"].append(day+1)
            outputDict["susceptible"].append(int(susceptible))
            outputDict["infected"].append(int(infected))
            outputDict["recovered"].append(int(recovered))
            outputDict["chilam"].append(int(chilams))
            outputDict["chilamPerDay"].append(int(chilamsPerDay))
                
            prevSusceptible = susceptible
            prevInfected = infected
            prevRecovered = recovered
            prevChilams = chilams

            
        datelist = pd.date_range(startdate, periods=(max(days)+2))
        df = pd.DataFrame.from_dict(outputDict, orient='columns')
        print(df.tail())
        
        
        # Plot generation
        if outfileprefix == "Infected":
            ydata = df.infected/1000 
        if outfileprefix == "Recovered":
            ydata = df.recovered/1000 
        if outfileprefix == "Deaths":
            ydata = df.chilam/1000 
        if outfileprefix == "DeathsPerDay":
            ydata = df.chilamPerDay 
        
        ax.plot(df.day, ydata, color=colors[n], linewidth= 2, label=treats[n]+' Mitigation')
        ax.set_xlabel("Days from first infection")
        ax.set_ylabel(ylabels[outfileprefix])
        plt.legend()
        #plt.tight_layout(pad=32)
        
        # Save csv
        df.to_csv(os.path.join(datadir, province.replace(' ', '-'))+'_'+treats[n]+'.csv', 
                  sep=',', index=False)
    
    # Save plot figure
    if (province != "National"):
        plt.title(province)
        outfilename = f"{outfileprefix}_{province.split(' ')[1]}.png"
    else: 
        outfilename = f"{outfileprefix}_{province}.png"
    
    plt.savefig(os.path.join(plotdir, outfilename), 
                format='png', bbox_inches='tight')
