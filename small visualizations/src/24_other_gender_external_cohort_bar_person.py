#!/usr/bin/env python
# coding: utf-8

# Last edited on 12/18/2020 by Mara Hubelbank

# PURPOSE: Produce the "Gender of other External Team Members across Cohorts 1‐9, Person-Level" figure.
# INPUT: CSV files for awards, individual awards, and demographics.
# OUTPUT: A bar chart representing the gender distribution of external team members (person-level) across the cohorts.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Specify the in- and out- file locations 
inp = '../../data_master/'
outp = '../figures/'

# Specify whether the level is 'role' or 'person'
level = 'person'

# Set the cohorts
MIN = 1
MAX = 9

# Read in awards CSV and demographics CSV
df_awards_i = pd.read_csv(inp + 'individual_awards.csv')
df_awards = pd.read_csv(inp + 'awards.csv')
df_dems = pd.read_csv(inp + 'individual_demographics.csv')

df_awards = df_awards[['award_id', 'cohort']]
df_dems = df_dems[['person_id', 'gender']]

TITLE = 'Gender of other External Team Members across Cohorts ' + str(MIN) + '-' + str(MAX) + ',\n' + level.title() + '-Level'
COLORS = ['#1A85FF', '#D41159'] # blue (men), red (women)
GRID_COLOR = '#d9d9d8' # light gray
TEXT_COLOR = '#404040' # dark gray

# DATASET ---------------------------------------------------------------------------------------------------------

# Filter award type to keep only "it"
df_awards_i = df_awards_i[df_awards_i['award_type'] == "it"] 

# Filter award role to keep only non-pi internals
df_awards_i = df_awards_i[(df_awards_i['award_role'] != "pi") & (df_awards_i['award_role'] != "co-pi")
                    & (df_awards_i['award_role'] != "former pi") & (df_awards_i['award_role'] != "former co-pi")
                    & ~(df_awards_i['award_role'].str.contains("internal"))] 

# Drop duplicates of the same person for the same award
level_cols = ['person_id'] if level == 'person' else ['person_id', 'award_id']
df_awards_i = df_awards_i.drop_duplicates(level_cols)

# Initialize the master dataframe
# Add person_id and award_start_year from awards df
df_master = df_awards_i[['person_id', 'award_id', 'award_start_year', 'award_role']].copy() 

# Merge with the awards csv on award_id
df_master = pd.merge(df_master, df_awards, on = 'award_id', how='left')
df_master = df_master.astype({'cohort': int})
    
# Filter out by cohort data
df_master = df_master[(df_master['cohort'] >= MIN) & (df_master['cohort'] <= MAX)]

# add the gender column by merging in demographic column (inner join since we can't count unspecified gender ids)
df_master = pd.merge(df_master, df_dems, on = 'person_id')

# VISUALIZATION ----------------------------------------------------------------------------------------------------

# Create a new dataframe to store the quantities of each subbar
df_q = pd.DataFrame(columns=['cohort', 'men', 'women'])

# Get the size of the intersection of the given parameters
def get_q(cohort, gender):
    return len(df_master[(df_master['cohort'] == cohort) & (df_master['gender'] == gender)])

# Filter nan values 
def no_nans(elem):
    return str(elem) != 'nan'

# Get unique cohortss
cohorts = df_master['cohort'].unique()
cohorts = sorted(list(filter(no_nans, cohorts)))

# Get unique genders
genders = df_master['gender'].unique() 
genders = sorted(list(filter(no_nans, genders)))

# Add the quantity of each combination to the quantity dataframe
for cohort in cohorts:
    df_q = df_q.append({'cohort': cohort, 'men': get_q(cohort, 'man'), 
                        'women': get_q(cohort, 'woman')}, ignore_index=True)

# Some constants for the bar chart
NUM_X = len(cohorts)
BAR_WIDTH = 0.35 # width of each bar

df_q = df_q.set_index(['cohort'])

# Get the bar values for the given cohort as an array (percentages and raw)
def get_vals(cohort): 
    men_raw = df_q.loc[cohort, 'men']
    women_raw = df_q.loc[cohort, 'women']
    sum_raw = men_raw + women_raw
    cum_sums.append(sum_raw) 
    
    if (sum_raw != 0):
        men_perc = round(men_raw * 100 / sum_raw)
        women_perc = round(women_raw * 100 / sum_raw)
        return np.array([men_perc, women_perc, men_raw, women_raw])
    return np.array([0, 0, 0, 0])

# Plot a bar with the given values
def plot_bar(index, values):
    values_perc = values[:2]
    values_raw = values[2:]
    indices = np.repeat(index,repeats=len(values)) 
    cumsum_bottom_values = np.concatenate([np.zeros(1), np.cumsum(values)[:-1]], axis=0)     
    for ind, perc, raw, bottom, color in zip(indices, values_perc, values_raw, cumsum_bottom_values, COLORS):
        plt.bar(ind, perc, bottom=bottom, color=color, width=BAR_WIDTH)
        plt.text(ind, bottom+perc/2, raw, ha="center", va="center", fontsize=16)

plt.figure(figsize=(NUM_X * 1.6, 6)) # size of bar chart figure

x = np.arange(1, NUM_X + 1, 1)

cum_sums = []
job_N_dict = {}
i = 1
for cohort in cohorts:
    values = get_vals(cohort)
    plot_bar(i, values)
    i += 1   
        
# Get the axis attribute.
ax = plt.gca()

# Title the graph, calculating the sum of cumulative sums.        
total = str(sum(cum_sums))
plt.title(TITLE + ' (n=' + total + ')', fontsize=26, pad=15, color=TEXT_COLOR)

# Label the bars on x-axis with the cohort nums
plt.xticks(x, cohorts, fontsize=18, color=TEXT_COLOR)

# Label the y-axis with percentages
y_vals = np.arange(0, 110, 20)
y_labels = [(str(y) + '%') for y in y_vals] # min 0%, max 100%, step 10%
plt.yticks(y_vals, y_labels, fontsize=16, color=TEXT_COLOR) # y-ticks (min, max, step)

# Add the horizontal grid lines and remove the top and side borders.
plt.grid(color=GRID_COLOR, which='major', axis='y', linestyle='solid', linewidth=2)
ax.set_axisbelow(True)
ax.spines['bottom'].set_color(GRID_COLOR)
ax.spines['top'].set_color('none')
ax.spines['left'].set_color('none')
ax.spines['right'].set_color('none')

# Make the legend (bottom center).
l_labels = ['men', 'women']
custom_lines = [Line2D([0], [0], color=c, marker="s", markersize=10, linewidth=0, label=lab) for c, lab in zip(COLORS, l_labels)]
leg = ax.legend(handles=custom_lines, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=len(l_labels), framealpha=0, prop={'size': 16})
for text in leg.get_texts():
    plt.setp(text, color = TEXT_COLOR, fontsize=18)
    
plt.tight_layout(pad=2)
plt.savefig(outp + 'fig_24_' + level + '.png')