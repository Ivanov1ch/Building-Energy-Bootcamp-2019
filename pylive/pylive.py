import matplotlib.pyplot as plt
import numpy as np

# use ggplot style for more sophisticated visuals
plt.style.use('ggplot')


def live_plotter_init(x_vec, y_vec, lines, formats, labels, xlabel='X Label', ylabel='Y Label', title='Title'):
    plt.ion()
    fig = plt.figure(figsize=(13, 6))
    ax = fig.add_subplot(111)

    # Only plot the first points
    for index in range(len(lines)):
        lines[index] = ax.plot(x_vec[index][:1], y_vec[index][:1], formats[index], alpha=0.8, label=labels[index])

    ax.legend()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.show()


# the function below is for updating both x and y values (great for updating dates on the x-axis)
def live_plotter_xy(x_vec, y_vec, lines, stop_index, pause_time=0.01):
    for index in range(len(lines)):
        lines[index][0].set_data(x_vec[index][:stop_index], y_vec[index][:stop_index])
        plt.xlim(np.min(x_vec[index][:stop_index]), np.max(x_vec[index][:stop_index]))
        if np.min(y_vec[index][:stop_index]) <= lines[index][0].axes.get_ylim()[0] or np.max(
                y_vec[index][:stop_index]) >= lines[index][0].axes.get_ylim()[1]:
            plt.ylim([np.min(y_vec[index][:stop_index]) - np.std(y_vec[index][:stop_index]),
                      np.max(y_vec[index][:stop_index]) + np.std(y_vec[index][:stop_index])])

    plt.pause(pause_time)
