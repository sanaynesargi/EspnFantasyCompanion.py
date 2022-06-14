import matplotlib.pyplot as plt
import seaborn as sns

colors = [
    "red",
    "orange",
    "yellow",
    "green",
    "blue",
    "grey",
    "teal",
    "magenta"
]


def reshape_array(scores):
    new_scores = []
    for i in range(len(scores[0])):
        new_scores.append([])
        for j in range(len(scores)):
            new_scores[-1].append(scores[j][i])

    return new_scores

def plot_data(scores, mids, teams):
    data = reshape_array(scores)

    sns.set_style("dark")
    _, ax4 = plt.subplots()

    # plot the boxplot
    ax4.boxplot(data, showfliers=False, usermedians=mids, boxprops={"linewidth": 2},
     medianprops={"linewidth": 2, "color": "red"},
     capprops={"linewidth": 2})
    
    # setup graph
    ax4.set_title("Player Performance By Week")
    ax4.set_xlabel("Week #")
    ax4.set_ylabel("Points Scored")

    # plot points according to player points scored
    keys = list(teams.keys())
    used_labels = []
    marker = "o"
    x = 1
    c = 0

    print(data)
    for scores_per_week in data:
        c = 0
        least_y = scores_per_week[0]
        for score in scores_per_week:
            if least_y > score:
                least_y = score
            label = teams[keys[c]]

            if label in used_labels:
                label = None
            else:
                used_labels.append(label)
            
            ax4.plot([x], [score], marker=marker, markerfacecolor=colors[c], markeredgecolor=colors[c], label=label)

            c += 1
        x += 1
        

    ax4.legend(bbox_to_anchor=(1, 1.0), loc="upper left")
    plt.show()
    plt.close()

