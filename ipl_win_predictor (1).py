# -*- coding: utf-8 -*-
"""IPL_Win_predictor

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Uvc9c_6JuRcdND5Mrh0CAe7uGayO0ihM
"""

import pandas as pd
import numpy as np
pd.set_option('display.max_columns',None)

deliveries=pd.read_csv('/content/delivery.csv')
matches=pd.read_csv('/content/matches.csv')

deliveries.head()

matches.head()

deliveries.columns

deliveries.groupby(['match_id','inning'])['total_runs'].sum().reset_index()

total_run_df=deliveries[deliveries['inning']==1].groupby(['match_id','inning'])['total_runs'].sum().apply(lambda x:x+1).reset_index()
total_run_df.head()

match_df=pd.merge(matches,total_run_df[['match_id','total_runs']],left_on='id',right_on='match_id')

match_df.head()

match_df['team1'].unique()

match_df.loc[match_df['team1']=='Delhi Daredevils','team1']='Delhi Capitals'
match_df.loc[match_df['team2']=='Delhi Daredevils','team2']='Delhi Capitals'

match_df.loc[match_df['team1']=='Deccan Chargers','team1']='Sunrisers Hyderabad'
match_df.loc[match_df['team2']=='Deccan Chargers','team2']='Sunrisers Hyderabad'

match_df.loc[match_df['team1']=='Rising Pune Supergiants','team1']='Rising Pune Supergiant'
match_df.loc[match_df['team2']=='Rising Pune Supergiants','team2']='Rising Pune Supergiant'

match_df.loc[match_df['team1']=='Royal Challengers Bengaluru','team1']='Royal Challengers Bangalore'

match_df.loc[match_df['team2']=='Royal Challengers Bengaluru','team2']='Royal Challengers Bangalore'

match_df[match_df['team2']=='Royal Challengers Bengaluru']

match_df.loc[match_df['team1']=='Kings XI Punjab','team1']='Punjab Kings'
match_df.loc[match_df['team2']=='Kings XI Punjab','team2']='Punjab Kings'

teams=['Royal Challengers Bangalore', 'Punjab Kings', 'Delhi Capitals',
       'Mumbai Indians', 'Sunrisers Hyderabad', 'Rajasthan Royals',
       'Chennai Super Kings', 'Kolkata Knight Riders']

match_df=match_df[match_df['team1'].isin(teams)]
match_df=match_df[match_df['team2'].isin(teams)]

match_df['team1'].unique()

match_df.shape

match_df[match_df['method']=='D/L'].style.background_gradient(cmap='plasma')

match_df['method'].unique()

match_df['method'].fillna(0,inplace=True)

match_df=match_df[match_df['method']==0]

match_df=match_df[['match_id','city','winner','total_runs']]
match_df.head()

delivery_df=pd.merge(match_df,deliveries,on='match_id')
delivery_df.head()

delivery_df=delivery_df[delivery_df['inning']==2]
delivery_df

# '''So by observation we can observe that in the matchdf we had taken
# firstinnings total runs,right and in the second case,that is in the
# delivery dataframe we considered second inning runs,as our main aim
# is to find the probability of either teams to win or loose,we need
# current runs and runrate,so for current runs,we can apply groupby
# on matchid and take the cummulative sum wrt total_runs_y,now,basically
# totalruns was present in matchdf as well as deliveries_df,but as we merged
# both the dataframes,it resulted in total_runs_x,and total_runs_y,
# so total_runs_x is the first innings runs and total_runs_y are the second
# innings runs,ball by ball,by applying cummulative sum,this becomes
# current score


# total_runs_y gives the run scored after each ball,so in the second innings,
# we want to get the total second innings runs,so we will groupby match id
# and will apply the cummulative sum'''

delivery_df['Current_score']=delivery_df.groupby('match_id')['total_runs_y'].cumsum()

delivery_df['runs_left']=delivery_df['total_runs_x']-delivery_df['Current_score']
delivery_df.head()

delivery_df['over'].unique()

# Map the over column from 0-19 to 1-20
delivery_df['over'] = delivery_df['over'] + 1

delivery_df['remaining_balls'] = 126- (delivery_df['over'] * 6+delivery_df['ball'])

delivery_df.head(10)

delivery_df['player_dismissed'].fillna(0,inplace=True)

delivery_df['player_dismissed']=delivery_df['player_dismissed'].apply(lambda x:x if x==0 else 1)

delivery_df['player_dismissed']=delivery_df['player_dismissed'].astype(int)

delivery_df['player_dismissed'].unique()

wickets=delivery_df.groupby('match_id')['player_dismissed'].cumsum().values

delivery_df['wickets']=10-wickets

((delivery_df['Current_score']*6)/(120-delivery_df['remaining_balls']))

delivery_df['Current_run_rate']=((delivery_df['Current_score']*6)/(120-delivery_df['remaining_balls']))

((delivery_df['runs_left']*6)/(delivery_df['remaining_balls']))

delivery_df['required_run_rate']=((delivery_df['Current_score']*6)/(delivery_df['remaining_balls']))

def result(row):
  return 1 if row['batting_team']==row['winner'] else 0

delivery_df['result']=delivery_df.apply(result,axis=1)
delivery_df.head()

import seaborn as sns
# Correct usage of sns.countplot with the 'x' parameter
sns.countplot(x='result', data=delivery_df,palette='magma')

temp_df=delivery_df['result'].value_counts().reset_index()

import plotly.express as px
px.bar(temp_df,x='result',y='count')

delivery_df.columns

final_df=delivery_df[['batting_team','bowling_team','city','runs_left',
                        'remaining_balls','wickets','total_runs_x','Current_run_rate',
                        'required_run_rate','result']]

final_df.shape

final_df.isna().sum()

final_df=final_df.dropna(subset='city')

final_df=final_df[final_df['remaining_balls']!=0]

final_df.head()

data=final_df.copy()

test=data['result']

train=data.drop('result',axis=1)

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(train,test,test_size=0.2,random_state=1)

X_train.shape,X_test.shape

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn import metrics

"""##`To convert cat variable to int`"""

cf=ColumnTransformer([('trf',OneHotEncoder(sparse=False,drop='first'),['batting_team','bowling_team','city'])],remainder='passthrough')

import warnings
warnings.filterwarnings('ignore')
pipe=Pipeline(steps=[('step1',cf),('step2',LogisticRegression(solver='liblinear'))])
pipe.fit(X_train,y_train)

y_pred=pipe.predict(X_test)
print(metrics.accuracy_score(y_test,y_pred))

pipe.predict_proba(X_test)[10]

import warnings
warnings.filterwarnings('ignore')
pipe1=Pipeline(steps=[('step1',cf),('step2',RandomForestClassifier())])
pipe1.fit(X_train,y_train)

y_pred=pipe1.predict(X_test)
print(metrics.accuracy_score(y_test,y_pred))

pipe1.predict_proba(X_test)[:10]

X_train.head(10)

# I will go with Logistic Regression because i need to
# showcase the probability right,even though Random Forest is
# giving much accurate result,but RandomForest is being baised
# at one side,as you can observe the prob of winning for 7th and 8th   sample
# is shown as 0% and 100% loose prob,this is kind of tooo strong or may
# be sometimes unrealistic,so its better to use a model which gives equal
# justice towards both side,as we also don't know which team will outperform
# and win the game!

import pickle
pickle.dump(pipe,open('pipe.pkl','wb'))

# !pip install -q streamlit

!wget -q -O - ipv4.icanhazip.com

# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py
# import streamlit as st
# import pandas as pd
# import pickle
# teams = ['Sunrisers Hyderabad',
#          'Mumbai Indians',
#          'Royal Challengers Bangalore',
#          'Kolkata Knight Riders',
#          'Kings XI Punjab',
#          'Chennai Super Kings',
#          'Rajasthan Royals',
#          'Delhi Capitals']
# 
# # declaring the venues
# 
# cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
#           'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
#           'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
#           'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
#           'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
#           'Sharjah', 'Mohali', 'Bengaluru']
# 
# 
# pipe = pickle.load(open('pipe.pkl', 'rb'))
# st.title('IPL Win Predictor')
# 
# 
# col1, col2 = st.columns(2)
# 
# with col1:
#     battingteam = st.selectbox('Select the batting team', sorted(teams))
# 
# with col2:
# 
#     bowlingteam = st.selectbox('Select the bowling team', sorted(teams))
# 
# 
# city = st.selectbox(
#     'Select the city where the match is being played', sorted(cities))
# 
# 
# target = st.number_input('Target')
# 
# col3, col4, col5 = st.columns(3)
# 
# with col3:
#     score = st.number_input('Score')
# 
# with col4:
#     overs = st.number_input('Overs Completed')
# 
# with col5:
#     wickets = st.number_input('Wickets Fallen')
# 
# 
# if st.button('Predict Probability'):
# 
#     runs_left = target-score
#     balls_left = 120-(overs*6)
#     wickets = 10-wickets
#     currentrunrate = score/overs
#     requiredrunrate = (runs_left*6)/balls_left
# 
#     input_df = pd.DataFrame({'batting_team': [battingteam], 'bowling_team': [bowlingteam], 'city': [city], 'runs_left': [runs_left], 'remaining_balls': [
#                             balls_left], 'wickets': [wickets], 'total_runs_x': [target], 'Current_run_rate': [currentrunrate], 'required_run_rate': [requiredrunrate]})
# 
#     result = pipe.predict_proba(input_df)
#     lossprob = result[0][0]
#     winprob = result[0][1]
# 
#     st.header(battingteam+"- "+str(round(winprob*100))+"%")
# 
#     st.header(bowlingteam+"- "+str(round(lossprob*100))+"%")



!streamlit run app.py & npx localtunnel --port 8501

import subprocess

# Run the shell command using subprocess
subprocess.run(["wget", "-q", "-O", "-", "ipv4.icanhazip.com"])

