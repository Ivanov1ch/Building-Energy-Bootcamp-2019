import sys
import numpy as np
import datetime as dt
import matplotlib
import matplotlib.pyplot as plt

# use ggplot style for more sophisticated visuals
plt.style.use('ggplot')

is_closed = False
panning_allowed = False


def enable_panning(event):
    global panning_allowed
    panning_allowed = True


def disable_panning(event):
    global panning_allowed
    panning_allowed = False


def has_been_closed():
    return is_closed


def window_closed(event):
    global is_closed
    is_closed = True


# Converts a numpy.datetime64 to a datetime.datetime object by converting dt64 to UTC time (for later use)
def datetime64_to_datetime(dt64):
    return dt.datetime.utcfromtimestamp((dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's'))


# Gets a list of x (time) and y (sensor reading) coordinates for the index-th column of data_df
# Also returns the labels for the x ticks (strings in HH:MM:SS) format
def get_coordinate_lists(data_df, index):
    time_list = data_df['Time'].tolist()
    value_list = data_df.iloc[:, index].tolist()

    time_list = [datetime64_to_datetime(time) for time in time_list]

    # Convert time_list to timedeltas, representing the time between each element of time_list and time_list[0]
    time_list = list(map(lambda time: time - time_list[0], time_list))

    # Convert the timedeltas to seconds
    time_list_seconds = list(map(lambda timedelta: round(timedelta.total_seconds()), time_list))

    # Convert the timedeltas to HH:MM:SS format
    time_list_strings = list(map(lambda timedelta: "%.2d:%.2d:%.2d" % (
        int(timedelta.seconds / 3600), (timedelta.seconds // 60) % 60, timedelta.seconds % 60), time_list))

    return time_list_seconds, value_list, time_list_strings


def live_plotter_init(data_df, lines, formats, labels, xlabel='X Label', ylabel='Y Label', title='Title'):
    plt.ion()
    fig = plt.figure(figsize=(13, 9))
    ax = fig.add_subplot(111)

    # Set window title
    gcf = plt.gcf()
    gcf.canvas.set_window_title(title)

    # Event bindings
    close_bind = fig.canvas.mpl_connect('close_event', window_closed)
    enter_bind = fig.canvas.mpl_connect('axes_enter_event', enable_panning)
    exit_bind = fig.canvas.mpl_connect('axes_leave_event', disable_panning)

    # Setup mouse wheel zooming
    def zoom_factory(ax, base_scale=2.):
        def zoom_fun(event):
            # get the current x and y limits
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0]) * .5
            cur_yrange = (cur_ylim[1] - cur_ylim[0]) * .5
            xdata = event.xdata  # get event x location
            ydata = event.ydata  # get event y location
            if event.button == 'up':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print
                event.button
            # set new limits
            ax.set_xlim([xdata - cur_xrange * scale_factor,
                         xdata + cur_xrange * scale_factor])
            ax.set_ylim([ydata - cur_yrange * scale_factor,
                         ydata + cur_yrange * scale_factor])
            plt.draw()  # force re-draw

        fi = ax.get_figure()  # get the figure of interest
        # attach the call back
        fi.canvas.mpl_connect('scroll_event', zoom_fun)

        # return the function
        return zoom_fun

    zoom = zoom_factory(ax)

    # Plot initial data
    for index in range(len(lines)):
        x_vec, y_vec, skip = get_coordinate_lists(data_df, index)
        lines[index] = ax.plot(x_vec, y_vec, formats[index], alpha=0.8, label=labels[index])

    ax.legend(loc='upper right')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.gcf().subplots_adjust(bottom=0.15)
    plt.show()


# Update the line graph
def live_plotter_update(data_df, lines, pause_time=0.01, max_points_to_show=10):
    # All x_vec and y_vec lists, used to set the bounds of the graph
    x_vecs = []
    y_vecs = []
    last_x_vec = None  # Store the last x_vec, in full (not only the last max_points_to_show points), for time labeling
    time_list_strings = None

    for index in range(len(lines)):
        x_vec, y_vec, list_strings = get_coordinate_lists(data_df, index)

        lines[index][0].set_data(x_vec, y_vec)

        # Add to x_vecs and y_vecs
        x_vecs.append(x_vec[-max_points_to_show:])
        y_vecs.append(y_vec[-max_points_to_show:])

        # Override time_list_strings
        time_list_strings = list_strings

        # Override last_x_vec, so the time labels are properly applied to all points, not just those visible
        last_x_vec = x_vec

        if has_been_closed():
            return  # Exit program early if closed

    # Do not adjust bounds if panning because it will send them back to the original view
    if not panning_allowed:
        # Adjust the bounds to fit all the lines on the screen and only show at most max_points_to_show at once

        # Find the smallest and largest x values (in the last max_points_to_show of each x_vec in x_vecs)
        smallest_x = np.min(x_vecs)
        largest_x = np.max(x_vecs)

        # Find the smallest and largest y values (in the last max_points_to_show of each y_vec in y_vecs)
        smallest_y = np.min(y_vecs)
        largest_y = np.max(y_vecs)

        # Update the x axis to use time_list_strings instead of values in seconds for easier reading (HH:MM:SS format)
        plt.xticks(last_x_vec, time_list_strings, rotation=-45, ha="left", rotation_mode="anchor")

        # Adjust the bounds to be a fraction of the standard deviation past the max and min points, to keep space
        # between the points and the borders
        plt.xlim(smallest_x - np.std(np.asarray(x_vecs).astype(np.float32)) / 3,
                 largest_x + np.std(np.asarray(x_vecs).astype(np.float32)) / 3)
        plt.ylim(smallest_y - np.std(np.asarray(y_vecs).astype(np.float32)) / 2,
                 largest_y + np.std(np.asarray(y_vecs).astype(np.float32)) / 2)

    if has_been_closed():
        return  # Exit program early if closed

    plt.pause(pause_time)
