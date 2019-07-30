import matplotlib.pyplot as plt
import numpy as np

# use ggplot style for more sophisticated visuals
plt.style.use('ggplot')


def live_plotter(x_vec, y1_data, line1, identifier='', pause_time=0.1):
    if line1 == []:
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        fig = plt.figure(figsize=(13, 6))
        ax = fig.add_subplot(111)
        # create a variable for the line so we can later update it
        line1, = ax.plot(x_vec, y1_data, '-o', alpha=0.8)
        # update plot label/title
        plt.ylabel('Y Label')
        plt.title('Title: {}'.format(identifier))
        plt.show()

    # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    # adjust limits if new data goes beyond bounds
    if np.min(y1_data) <= line1.axes.get_ylim()[0] or np.max(y1_data) >= line1.axes.get_ylim()[1]:
        plt.ylim([np.min(y1_data) - np.std(y1_data), np.max(y1_data) + np.std(y1_data)])
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)

    # return line so we can update it again in the next iteration
    return line1


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
        if np.min(y_vec[index][:stop_index]) <= lines[index][0].axes.get_ylim()[0] or np.max(y_vec[index][:stop_index]) >= lines[index][0].axes.get_ylim()[1]:
            plt.ylim([np.min(y_vec[index][:stop_index]) - np.std(y_vec[index][:stop_index]), np.max(y_vec[index][:stop_index]) + np.std(y_vec[index][:stop_index])])

    plt.pause(pause_time)
