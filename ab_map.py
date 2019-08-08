import numpy as np
import pandas as pd
import shapefile as shp
# from matplotlib import rcParams
# rcParams['font.family'] = 'sans-serif'
# rcParams['font.sans-serif'] = ['Lucida Grande']
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.ticker as tkr

output_dir = "output_16x9"

party_colors = {'Progressive Conservative': '#1F6ACD',
                'Social Credit': '#1FCD1F',
                'Liberal': '#CD301F',
                'United Farmers of Alberta': '#761FCD', #'#96CD1F',
                'New Democratic Party': '#CD611F',
                'Wildrose Party': '#1FCD76',
                'Other': '#8c8c8c'}

party_abbr = {"Progressive Conservative": "PC",
              "Social Credit": "SC",
              "Liberal": "Liberal",
              "United Farmers of Alberta": "UFA",
              "New Democratic Party": "NDP",
              "Wildrose Party": "WRP",
              "Other": "Other"}


def read_shapefile(sf):
    """
    Read a shapefile into a Pandas dataframe with a 'coords'
    column holding the geometry information. This uses the pyshp
    package
    """
    # https://towardsdatascience.com/mapping-geograph-data-in-python-610a963d2d7f
    fields = [x[0] for x in sf.fields][1:]
    records = [list(rec) for rec in sf.records()]
    shps = [s.points for s in sf.shapes()]

    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)

    return df

def millions(x, pos):
    'The two args are the value and tick position'
    return '{:3.0f}k'.format(x*1e-3)

def plot_map_fill(annotate_year, stats, pty_stats, df, colors, x_lim=None,
                  y_lim=None,
                  figsize=(11, 11)):
    '''
    Plot map with lim coordinates
    '''

    figure = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(4, 2, width_ratios=[1, 1], height_ratios=[1,10, 3, 2.5])
    ax1 = plt.subplot(gs[1,:])      # Province subplot
    ax2 = plt.subplot(gs[2,0])      # Edmonton subplot
    ax3 = plt.subplot(gs[2,1])      # Calgary subplot
    ax4 = plt.subplot(gs[0,:])      # Election stats
    ax5 = plt.subplot(gs[3,:])      # Party stats

    # Plot voter turnout
    ax4.fill_between(stats['Year'], 0, stats['Eligible Electors'], facecolor="#8c8c8c", alpha=0.5)
    ax4.fill_between(stats['Year'], 0, stats['Valid Received'], facecolor="#1FA4CD", alpha=0.8)

    if stats['Eligible Electors'].max() >= 900e3:
        ax4.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, loc: "{:3.0f}M".format(int(x*1e-6))))
    else:
        ax4.get_yaxis().set_major_formatter(tkr.FuncFormatter(lambda x, loc: "{:3.0f}k".format(int(x*1e-3))))

    #ax4.get_yaxis().set_major_formatter(plt.FuncFormatter(millions)) #lambda x, loc: "{0:g}".format(int(x/1000))))
    ax4.set_xlim(1900,2020)
    turnout = stats.iloc[-1,2]/stats.iloc[-1,6]*100
    txt_label = "{:3.0f}%".format(turnout)
    ax4.text(stats['Year'].iloc[-1]+1, stats['Valid Received'].iloc[-1]*0.75, txt_label, size="medium", fontweight='semibold')
    ax4.set_title("Turnout of Eligible Voters", fontsize=16, ha='center', fontweight='semibold')

    # Plot Electoral Divisions and fill with party colors
    for ed in range(df.shape[0]):
        shape_ex = np.array(df.coords[ed])
        x_lon = shape_ex[:,0]
        y_lat = shape_ex[:,1]
        ax1.fill(x_lon, y_lat, colors[df.EDNumber20[ed]-1])
        ax1.plot(x_lon, y_lat, 'w')

        # coord_x = int(0.5 * (np.min(x_lon) + np.max(x_lon)))
        # coord_y = int(0.5 * (np.min(y_lat) + np.max(y_lat)))

        if 27 <= df.EDNumber20[ed] and df.EDNumber20[ed] <= 46: # Edmonton subplot
            ax2.fill(x_lon, y_lat, colors[df.EDNumber20[ed]-1])
            ax2.plot(x_lon, y_lat, 'w')
            # ax2.text(coord_x, coord_y, df.EDNumber20[ed], fontsize=8, color="white", fontweight='bold')

        elif df.EDNumber20[ed] <= 26: # Calgary subplot
            ax3.fill(x_lon, y_lat, colors[df.EDNumber20[ed]-1])
            ax3.plot(x_lon, y_lat, 'w')
        #     ax3.text(coord_x, coord_y, df.EDNumber20[ed], fontsize=8, color="white", fontweight='bold')


    # Format legend for Alberta Plot
    legend_colors = []
    legend_labels = []
    color_list = []
    for key, value in party_colors.items():
        color_list.append(value)
        if key in party_abbr:
            legend_colors.insert(0, mpatches.Patch(color=value))
            legend_labels.insert(0, key)
        else:
            print("party missing", key, value)
    ax1.legend(legend_colors, legend_labels, loc=3, ncol=1, bbox_to_anchor=(0.03, 0.03), borderaxespad=0.)
    #ax1.legend(legend_colors, legend_labels, loc=8, ncol=4, bbox_to_anchor=(-0.05, -0.07, 1.05, .25), borderaxespad=0,
    #           mode='expand')


    #ax1.set_title('Vote on Tuesday, April 16!', fontsize=24)
    #ab_title = "Vote on Tuesday, April 16! \n" + \
    ab_title = "Alberta: {} MLAs".format(stats.iloc[-1,1])
    ab_title = "Divisions Won by Party: {} MLAs".format(stats.iloc[-1,1])
    ax1.set_title(ab_title, fontsize=16, fontweight='semibold', color='black')
    ax1.set_xlim(x_lim)
    ax1.set_ylim(y_lim)
    #ax1.text(100000, 5400000, "Alberta Overall: {} MLAs".format(stats.iloc[-1,1]), fontweight='semibold')
    text_args = {'size':'small', 'color':'gray', 'weight':'semibold'}
    #ax1.text(-330000, 5450000, "* Visualized with 2019 boundaries.", **text_args)
    ax1.text(55000, 5400000, "* Visualized with 2019 boundaries.", **text_args)

    # Format Calgary and Edmonton Plots
    ax2.set_title('Edmonton: {} MLAs'.format(stats.iloc[-1,9]), fontweight='semibold')
    ax3.set_title('Calgary: {} MLAs'.format(stats.iloc[-1,10]), fontweight='semibold')


    prior_sum = pty_stats.iloc[:-1,1:].sum(axis=0)
    current = pty_stats.iloc[-1,1:]
    ax5.barh(prior_sum.index, prior_sum, 0.75, color=color_list, alpha=0.5)
    ax5.barh(prior_sum.index, current, 0.75, left=prior_sum, color=color_list, alpha=1.0)
    ax5.set_xlim(0,850)
    temp_title = "Distribution of Seats by Political Affiliation"
    temp_title = "Members Elected in {}: {}".format(annotate_year, stats.iloc[-1,1])
    temp_title = "Sum of Divisions Won by Party"
    ax5.set_title(temp_title, fontsize=16, ha='center', fontweight='semibold')

    # txt_premier = "Premier: {} ({})".format(stats.iloc[-1,7], party_abbr[stats.iloc[-1,8]])
    txt_premier = "Premier: {}".format(stats.iloc[-1,7])
    txt_color = party_colors[stats.iloc[-1,8]]
    txt_idx = current.idxmax()
    txt_x = prior_sum[txt_idx] + current[txt_idx] + 20
    txt_align = "left"
    txt_alpha = 0.5

    if txt_x > 700:
        txt_x -= 40 #prior_sum[txt_idx] - 20
        txt_align = "right"
        txt_alpha = 0.5
        txt_idx = 1

    ax5.text(txt_x, txt_idx, txt_premier, fontweight='semibold', style='italic', size='small', ha=txt_align,
             bbox={'facecolor': txt_color, 'alpha': txt_alpha, 'pad': 5})

    # Add citations
    text_args = {'size':'small', 'color':'gray', 'weight':'semibold'}
    ax5.text(1, -4, "Source: elections.ab.ca", ha="left", **text_args)
    ax5.text(850, -4, "@jono_san", ha="right", **text_args)

    ax1.axis('off')
    ax2.axis('off')
    ax3.axis('off')

    # ax1.xaxis.set_major_locator(tkr.NullLocator())
    # ax1.yaxis.set_major_locator(tkr.NullLocator())
    # ax2.xaxis.set_major_locator(tkr.NullLocator())
    # ax2.yaxis.set_major_locator(tkr.NullLocator())
    # ax3.xaxis.set_major_locator(tkr.NullLocator())
    # ax3.yaxis.set_major_locator(tkr.NullLocator())


    figure.suptitle("ALBERTA'S ELECTION RESULTS: {}".format(annotate_year), fontsize=18, weight='semibold')
    plt.tight_layout(rect=[0, 0.0, 1, 0.97])
    print("saving: {}".format(annotate_year))
    plt.savefig(os.path.join(output_dir, "{}.png".format(annotate_year)))
    plt.close()

def main():
    sns.set(style="whitegrid", palette="deep", color_codes=True)
    sns.mpl.rc("figure", figsize=(11,6))

    shp_path = "./2019Boundaries_ED-Shapefiles/EDS_ENACTED_BILL33_15DEC2017.shp"
    sf = shp.Reader(shp_path)

    ed_df = read_shapefile(sf)

    # Alberta limits
    y_lim = (5415000, 6675000)  # lat
    x_lim = (-400000, 400000)  # long
    figsize = (9, 16)

    election_stats = pd.read_csv('election_stats.csv')

    election_winners = pd.read_csv('election_winners.csv', na_values=['nan', ' '])
    election_winners = election_winners.fillna(method='bfill')
    winner_colors = election_winners.copy()
    for i in range(election_winners.shape[0]):
        for j in range(2,election_winners.shape[1]):
            if election_winners.iloc[i, j] in party_colors:
                winner_colors.iloc[i,j] = party_colors[election_winners.iloc[i, j]]
            else:
                winner_colors.iloc[i,j] = 'grey'

    party_stats = pd.read_csv("party_wins.csv", skiprows=1)

    for ind, year in election_stats.iterrows():
        stats = election_stats.iloc[:ind+1,:]
        pty_stats = party_stats.iloc[:ind+1,:]
        colors = winner_colors.iloc[:,ind+2]
        plot_map_fill(int(year.values[0]), stats, pty_stats, ed_df, colors, x_lim, y_lim, figsize)
        break


if __name__ == "__main__":
    main()
