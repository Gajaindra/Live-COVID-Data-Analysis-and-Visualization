#!/usr/bin/env python
# coding: utf-8

# In[30]:


from bs4 import BeautifulSoup as soup
from datetime import date,datetime
from urllib.request import Request,urlopen
import pandas as pd
import numpy as np


# In[31]:


import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import plotly.offline as py
import seaborn as sns
import gc
import warnings
warnings.filterwarnings("ignore")

from pandas_profiling import ProfileReport


# In[32]:


today= datetime.now()
yesterday_str ="%s %d %d" %(date.today().strftime("%b"),today.day-1,today.year)
yesterday_str


# In[33]:


url="https://www.worldometers.info/coronavirus/#countries"
req= Request (url , headers ={'User-Agent':"Mozilla/5.0"})
webpage = urlopen(req)
page_soup =soup(webpage,"html.parser")


# In[34]:


table= page_soup.findAll("table",{"id":"main_table_countries_yesterday"})
table


# In[38]:


containers= table[0].findAll("tr",{"style":""})
title = containers[0]
del containers[0]
all_data =[]
clean = True
for country in containers:
  country_data=[]
  country_container=country.findAll("td")
  if country_container[1].text=="China":
    continue
  for i in range(1,len(country_container)):
    final_feature = country_container[i].text
    if clean:
      if i!=1 and i!=len(country_container)-1:
        final_feature=final_feature.replace(",","")

        if final_feature.find('+')!=-1:
          final_feature=final_feature.replace("+","")
          final_feature=float(final_feature)
        elif final_feature.find('-')!=-1:
          final_feature=final_feature.replace("-","")
          final_feature=float(final_feature)*-1
    if final_feature=='N/A':
      final_feature=0
    elif final_feature == "" or final_feature ==" ":
      final_feature=-1

    country_data.append(final_feature)
  all_data.append(country_data)


# In[36]:


all_data


# In[37]:


df=pd.DataFrame(all_data)
df.drop([15,16,17],inplace =True,axis=1)
df.drop([18,19,20],inplace =True,axis=1)
df.head()


# In[9]:


column_labels=["Country","Total cases","New cases","Total Deaths","New Deaths","Total Recovered","New Recovered","Active Cases","Serious/Critical","Total Cases/1M","Deaths/1M","Total Teasts","Test/1M","Population","Continent"]


# In[10]:


df.columns=column_labels


# In[11]:


df


# In[12]:


for label in df.columns:
    if label != 'Country' and label!="Continent":
        df[label]=pd.to_numeric(df[label])


# In[13]:


df["%Inc Cases"] = df["New cases"]/df["Total cases"]*100
df["%Inc Deaths"] = df["New Deaths"]/df["Total Deaths"]*100
df["%Inc Recovered"] = df["New Recovered"]/df["Total Recovered"]*100


# In[14]:


df.head()


# In[15]:


cases =df[["Total Recovered","Active Cases","Total Deaths"]].loc[0]
cases_df=pd.DataFrame(cases).reset_index()
cases_df


# In[16]:


cases_df.columns=["Type","Total"]
cases_df["percentage"] = np.round(100*cases_df['Total']/np.sum(cases_df["Total"]),2)
cases_df


# In[17]:


cases_df["Virus"]=["COVID-19" for i in range(len(cases_df))]
cases_df


# In[18]:


fig=px.bar(cases_df, x="Virus", y ="percentage",color="Type", hover_data=["Total"])
fig.show()


# In[19]:


cases =df[["New cases","New Recovered","New Deaths"]].loc[0]
cases_df=pd.DataFrame(cases).reset_index()
cases_df.columns=["Type","Total"]
cases_df["percentage"] = np.round(100*cases_df['Total']/np.sum(cases_df["Total"]),2)
cases_df["Virus"]=["COVID-19" for i in range(len(cases_df))]
fig=px.bar(cases_df, x="Virus", y ="percentage",color="Type", hover_data=["Total"])
fig.show()


# In[20]:


per= np.round(df[["%Inc Cases",	"%Inc Deaths","%Inc Recovered"]].loc[0],2)
per_df=pd.DataFrame(per)
per_df.columns=["percentage"]
fig=go.Figure()
fig.add_trace(go.Bar(x=per_df.index,y=per_df['percentage'],marker_color=["yellow","blue","red"]))
fig.show()


# In[21]:


continent_df = df.groupby("Continent").sum().drop("All")
continent_df


# In[22]:


continent_df=continent_df.reset_index()
continent_df


# In[23]:


def continent_visualization(vis_list):
    for label in vis_list:
        c_df=continent_df[['Continent',label]]
        c_df['percentage']=np.round(100*c_df[label]/np.sum(c_df[label]),2)
        c_df["Virus"]=["COVID-19" for i in range(len(c_df))]
        fig=px.bar(c_df, x="Virus", y ="percentage",color="Continent", hover_data=[label])
        fig.update_layout(title={"text": f"{label}"})
        fig.show()
        gc.collect()


# In[24]:


cases_list=["Total cases","Active Cases","New cases","Serious/Critical","Total Cases/1M"]

deaths_list=["Total Deaths","New Deaths","Deaths/1M"]

recovered_list =["Total Recovered","New Recovered","%Inc Recovered"]


# In[25]:


continent_visualization(cases_list)


# In[26]:


df=df.drop([len(df)-1])
country_df=df.drop([0])
country_df


# In[27]:


LOOT_AT =10
country=country_df.columns[1:14]
fig=go.Figure()
c=0
for i in country_df.index:
    if c< LOOT_AT:
        fig.add_trace(go.Bar(name=country_df['Country'][i], x= country,y=country_df.loc[i][1:14]))
    else:
        break
    c+=1

fig.update_layout(title={"text":f'{LOOT_AT}'})
fig.show()


# In[28]:


fig.update_layout(title={"text":f'top {LOOT_AT} countries affected'},yaxis_type="log")
fig.show()
