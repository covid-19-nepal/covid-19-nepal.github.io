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


plt.rcParams["axes.labelsize"] = 12
plt.rcParams["axes.titlesize"] = 14
sns.set_style("whitegrid")

# 2018 Projected net Population

population = {

                "Province 1"	: 4621467,
                "Province 2"	: 5507253,
                "Province 3"	: 5634950,
                "Province 4"	: 2449619,
                "Province 5"	: 4585115,
                "Province 6"	: 1600381,
                "Province 7"	: 2601218,
                "National"	    : 27000000,
                }

ylabels = {
    "Infected": "Projected infected population (in thousand)", 
    "Recovered": "Cumulative projected recovered (in thousand)",     
    "Deaths": "Cumulative projected deaths",
    "DeathsPerDay": "Projected deaths/day", 
    "Infected_threshold": "Projected symptomatic infected population (in thousand)"
    }
    

ylims = {
        "Infected": [0, 8000], 
        "Recovered": [0, 14000], 
        "Deaths": [0, 70000], 
        "DeathsPerDay": [0, 3000]
        }

# Setting up environment
workdir = os.getcwd()
plotdir = os.path.join(workdir, "plots2")
datadir = os.path.join(workdir, "data2")
measure = "Recovered"

# Make sure directories exist, otherwise create
for dir in [plotdir, datadir]:
    if not os.path.exists(dir):
        os.makedirs(dir)


projectedInfectionRate = {"Low Infection":0.1, "Medium Infection": 0.3, "High Infection": 0.5}
projectedInfxn = 0.3
projChilam = 0.005
currentInfected = 5
totalRecovered = 0
gamma = 1/14
Ro = 4.0
oldBeta = [0.4, 0.2, 0.13, 0.105]
allBeta = [0.4, 0.2, 0.13, 0.105]
Sfactor = 1+14/365000

startdate = date(2020, 4, 1)


treats = [
    "No", 
    "50", 
    "75", 
    "90"
    ]
colors = ['red', 'blue', 'green', 'cyan']
linestyles = ["--", "-", "-."]

#Looping through the provinces
for province, popn in population.items():

    fig = plt.figure(figsize=(19,7))
    plotno = 130
    for infectionKey, projInfxn in projectedInfectionRate.items(): 
        ns = popn * projInfxn
        plotno += 1
        #print(plotno)
        # Initializing the general plot parameters
        ax = fig.add_subplot(plotno)
        ax.set_xlim([0,600])
        #dateFmt = mdates.DateFormatter('%b-%Y')
        #ax.xaxis.set_major_formatter(dateFmt)
        ax.xaxis.set_major_locator(plt.MultipleLocator(90))
        
        # Looping through beta for each province
        for n, beta in enumerate(allBeta): 
            
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
            days = range(800)
            for day in days:
                #print (f"{day}, {int(prevSusceptible)}, {int(prevInfected)}, {int(prevRecovered)}")
                susceptible = (prevSusceptible - (prevSusceptible/ns)*(beta*prevInfected)) * Sfactor
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
            totalInfected = df.infected.sum()
            df['symptomatic'] = df.infected/2
            df['percentOfTotalInfected'] = df.infected/totalInfected*100
            
            if (province == "National"):
                cumInfected = df.infected.max()
                cumRecovered = df.recovered.max()
                cumDeaths = df.chilam.max()
            
            
            # Plot generation
            if measure == "Infected":
                ydata = df.infected/1000 
            if measure == "Recovered":
                ydata = df.recovered/1000 
            if measure == "Deaths":
                ydata = df.chilam 
            if measure == "DeathsPerDay":
                ydata = df.chilamPerDay 
            if measure == "Infected_threshold":
                ydata = df.infected/2000
            

            ax.plot(df.day, ydata, color=colors[n], linewidth= 2, label=treats[n])
            ax.set_xlabel("Days from first infection")
            ax.set_ylim(ylims[measure])
            if plotno == 131:
                ax.set_ylabel(ylabels[measure])
            
            plt.legend()

            #plt.tight_layout(pad=32)            
            # Text and image outputs
            ax.set_title(infectionKey)
            outfilename = f"{measure}_{province}.png"
            plt.savefig(os.path.join(plotdir, outfilename), 
                    format='png', bbox_inches='tight')
            csvFileName = f"{province.replace(' ', '-')}_{treats[n]}_{projInfxn}.csv"
            df.to_csv(os.path.join(datadir, csvFileName), 
                    sep=',', index=False)
                    
    plt.close()
