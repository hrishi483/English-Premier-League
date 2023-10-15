import time  # to simulate a real time data, time loop
import plotly.graph_objects as go
import numpy as np  # np mean, np random
import pandas as pd  # read csv, df manipulation
import plotly.express as px  # interactive charts
import streamlit as st  # 🎈 data web app development
from streamlit_option_menu  import option_menu
import plotly.subplots as sp
# from helper import*
from PIL import Image
import regex as reg
import numpy as np
import pandas as pd
import requests as re
from bs4 import BeautifulSoup as bs

def get_team_link_prev(name):
    website=re.get("https://fbref.com/en/comps/9/2022-2023/2022-2023-Premier-League-Stats").text
    soup = bs(website,"lxml")
    team_links=dict()
    for body in soup.find_all("tbody"):
        for row in body.find_all("tr"):
            for a_tag in row.find('td').find_all('a'):
                if a_tag is not None:
                    team_link="https://fbref.com/"+a_tag["href"]
                    team_name=reg.search(r'/([^/]+)-Stats$',team_link)
                    if team_name:
                        team_name = team_name.group(1)
                        # print(result)
                        temp=team_link.split('/')[:-1]
                        temp.append('2022-2023')
                        temp.append(team_name)
                        team_link='/'.join(temp)
                    team_links[team_name]=team_link
    if name in team_links.keys():
        return team_links[name]
    print("Incorrect name ,Recheck the team Name, ")

def get_team_statistics(name,table_name=""):
    team_link=get_team_link_prev(name)
    #Standard Stats
    # individual_team = bs(re.get(get_team_link_prev(name)).text)
    if table_name=='Standard Stats':
        individual_team_standard_stats = pd.read_html(team_link,match="Standard Stats")[0]
        individual_team_standard_stats.columns = [col[1] for col in individual_team_standard_stats.columns]
        individual_team_standard_stats = individual_team_standard_stats.drop(columns="Matches")
        individual_team_standard_stats = individual_team_standard_stats.iloc[:-2,:]
        # print(individual_team_standard_stats.head(5))
        return(individual_team_standard_stats)

    #Goalkeeping Statistics
    if table_name=='Goalkeeping Stats':
        goalkeeping_table = pd.read_html(team_link,match="Advanced Goalkeeping ")[0]
        goalkeeping = goalkeeping_table.iloc[:-2,:]
        goalkeeping.columns=goalkeeping.columns.droplevel(0)
        # print(goalkeeping.head(5))
        return goalkeeping

    #Shooting stats
    if table_name=="shooting":
        Shooting_table = pd.read_html(team_link,match="Shooting ")[0]
        Shooting = Shooting_table.iloc[:-2,:]
        Shooting.columns=Shooting.columns.droplevel(0)
        # print(Shooting.head(5))
        return Shooting
    
    if table_name=="Scores & Fixtures":
        scores_fixtures= pd.read_html(team_link,match="Scores & Fixtures")[0]
        # scores_fixtures.columns = scores_fixtures.columns.droplevel(0)
        # print(scores_fixtures.head(5))
        return scores_fixtures
    
    #Passibg stats
    if table_name=="passing":      
        website=re.get(team_link).text

        soup = bs(website)
        poss =soup.find_all(class_="")
        passing_stats_bool = False
        for log in soup.find_all('a'):
            try:
                if 'passing' in log["href"] and "Premier-League" in log['href']:
                    new_link="https://fbref.com/"+log['href']
                    passing_stats=pd.read_html(new_link,match="Passing")[0]
                    passing_stats.columns=passing_stats.columns.droplevel()
                    passing_stats=passing_stats.iloc[:,:14]                   
                    passing_stats['Cmp%']=passing_stats["Cmp%"].astype('float')
                    passing_stats_bool =True
                    break
            except:
                passing_stats_bool=False
        if passing_stats_bool==True:
            return passing_stats
    else:
        print("Table Not Found")
    
    
#Page configuration
st.set_page_config(
    page_title="Real-Time Data Science Dashboard",
    page_icon="⚽",
    layout="wide",
)


st.title("⚽English Premier League Dashboard📊")

#Hortizontal Navigation bar
selected=option_menu(
    menu_title=None,
    options=["Home","Players","Current Season Fixtures"],
    default_index=0,
    orientation='horizontal',
)


#************************************************************************************************



#Home Page


if selected=="Home":
    with st.sidebar:
        regular_season_stats=pd.read_html("https://fbref.com/en/comps/9/2022-2023/2022-2023-Premier-League-Stats")[0]
        squads = regular_season_stats['Squad']
        print(squads)
        options=["All Teams"]
        with st.sidebar:
            add_radio = st.radio(
                "Choose to view Team Statistics",
                (["All Teams"]+list(squads))
            )
    with st.spinner("Loading..."):
        time.sleep(3)

    if add_radio == "All Teams":
        st.download_button(
            label="2022-2023 Premier League Stats",
            data="csv",
            file_name='large_df.csv',
            mime='text/csv',
        )
        #Regular Season Stats
        st.dataframe(regular_season_stats)
        new_df=regular_season_stats.copy()
        new_df["Top Team Scorer"] = regular_season_stats["Top Team Scorer"].apply(lambda x: x.split("-")[0])
        new_df["Top_Team_Scorer_goals"]=regular_season_stats['Top Team Scorer'].apply(lambda x:x.split('-')[1])
        
        colors = ['#1f77b4', '#ff7f0e'] 
        col1,col2=st.columns(2)
        #Bar Chart of top goal scorers
        with col1:
            # new_df=new_df.sort_values(by='Top_Team_Scorer_goals',ascending=True)
            fig = px.bar(new_df, x='Top Team Scorer', y='Top_Team_Scorer_goals', title='Top Team Scorers',text_auto=True,color_discrete_sequence=[colors[0]])
            fig.update_xaxes(tickangle= -90)  
            st.plotly_chart(fig)

        with col2:
            new_df=new_df.sort_values(by='Attendance',ascending=False)
            fig = px.bar(new_df, x='Squad', y='Attendance', title='EPL Season Attendance by Team', color_discrete_sequence=[colors[1]])
            st.plotly_chart(fig)

        col3,col4=st.columns(2)
        with col3:
            new_df=new_df.sort_values(by='GF', ascending=True)
            fig = px.bar(new_df, x='Squad', y=['xG', 'GF'], title='Expected vs Actual Goals Scored: Attacking performance of Team', barmode='group',color_discrete_map={'xGA':' #ff3333','GA':'#ff9999'})
            fig.update_layout(legend=dict(orientation="h", y=1.1, x=0.5))
            st.plotly_chart(fig)
        with col4:
            new_df=new_df.sort_values(by='GA',ascending=False)
            fig = px.bar(new_df, x='Squad', y=['xGA', 'GA'], title='Expected vs Actual Goals Conceded: Defensive performance of Team', barmode='group',color_discrete_map={'xGA':'#00ff00','GA':'#99ffcc'})
            fig.update_layout(legend=dict(orientation="h", y=1.1, x=0.5))
            st.plotly_chart(fig)
    
    st.write('Team :',add_radio)
    Standard_Stats=get_team_statistics(add_radio,'Standard Stats')
    print(Standard_Stats)
    st.download_button(
            label="Standard Stats",
            data="csv",
            file_name="csv",
            mime='text/csv',
        )
    st.dataframe(Standard_Stats)



#
if selected=="Players":
    st.write("Players")








#Teams Page Display the teams as icons
if selected=="Teams":
    st.write("Teams")

if selected=="Current Season Fixtures":
    st.write("Current Season Fixtures")