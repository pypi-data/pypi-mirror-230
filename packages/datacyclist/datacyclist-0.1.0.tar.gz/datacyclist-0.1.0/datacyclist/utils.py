

def plot_frame(ax):
    ax.set_facecolor('#292525')
    ax.spines['bottom'].set_color('w')
    ax.tick_params(axis='x', colors='w')
    ax.xaxis.label.set_color('w')
    ax.spines['left'].set_color('w')
    ax.tick_params(axis='y', colors='w')
    ax.yaxis.label.set_color('w')
    return ax
