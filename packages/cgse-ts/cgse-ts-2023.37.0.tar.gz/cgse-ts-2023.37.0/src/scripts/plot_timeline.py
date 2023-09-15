import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime


timings = {
    "2022-10-13T16:53:10.278": ("Send N-FEE to STANDBY mode on frame 3.", 2),
    "2022-10-13T16:53:19.905": ("TIMECODE 1", -1),
    "2022-10-13T16:53:19.906": ("HK FN 1", -2),
    "2022-10-13T16:53:26.155": ("TIMECODE 2", -1),
    "2022-10-13T16:53:26.156": ("HK FN 2", -2),
    "2022-10-13T16:53:32.406": ("TIMECODE 3", -1),
    "2022-10-13T16:53:32.407": ("HK FN 3", -2),
    "2022-10-13T16:53:32.518": ("Send N-FEE to internal sync on frame 3.", 2),
    "2022-10-13T16:53:38.656": ("TIMECODE 4", -1),
    "2022-10-13T16:53:38.657": ("HK FN 0", -2),
    "2022-10-13T16:53:44.906": ("TIMECODE 5", -1),
    "2022-10-13T16:53:44.907": ("HK FN 1", -2),
    "2022-10-13T16:53:51.156": ("TIMECODE 6", -1),
    "2022-10-13T16:53:51.157": ("HK FN 2", -2),
    "2022-10-13T16:53:57.406": ("TIMECODE 7", -1),
    "2022-10-13T16:53:57.407": ("HK FN 3", -2),
    "2022-10-13T16:53:57.526": ("Send n_cam_partial_ccd_int_sync on frame 0", 1),
    "2022-10-13T16:54:03.545": ("TIMECODE 8", -1),
    "2022-10-13T16:54:03.546": ("HK FN 0", -2),
    "2022-10-13T16:54:03.669": ("Commanding N-FEE FULL IMAGE mode", 2),
    "2022-10-13T16:54:03.684": ("Wait 2 cycle...", -3),
    "2022-10-13T16:54:05.892": ("TIMECODE 9", -1),
    "2022-10-13T16:54:05.893": ("HK FN 0", -2),
    "2022-10-13T16:54:07.049": ("TIMECODE 10", -1),
    "2022-10-13T16:54:07.050": ("HK FN 0", -2),
    "2022-10-13T16:54:07.360": ("Execute puna.move_relative_user(0, 0, 10, 0, 0, 0.) immediately", 1),
    "2022-10-13T16:54:07.431": ("Wait 2 cycle...", -3),
    "2022-10-13T16:54:08.206": ("TIMECODE 11", -1),
    "2022-10-13T16:54:08.207": ("HK FN 0", -2),
    "2022-10-13T16:54:09.363": ("TIMECODE 12", -1),
    "2022-10-13T16:54:09.364": ("HK FN 0", -2),
    "2022-10-13T16:54:09.651": ("Execute puna.move_relative_user(0, 0, 10, 0, 0, 0.) immediately", 1),
    "2022-10-13T16:54:09.728": ("Wait 2 cycle...", -3),
    "2022-10-13T16:54:10.520": ("TIMECODE 13", -1),
    "2022-10-13T16:54:10.521": ("HK FN 0", -2),
    "2022-10-13T16:54:11.677": ("TIMECODE 14", -1),
    "2022-10-13T16:54:11.678": ("HK FN 0", -2),
    "2022-10-13T16:54:11.970": ("Execute puna.move_relative_user(0, 0, 10, 0, 0, 0.) immediately", 1),
    "2022-10-13T16:54:12.055": ("Wait 2 cycle...", -3),
    "2022-10-13T16:54:12.834": ("TIMECODE 15", -1),
    "2022-10-13T16:54:12.835": ("HK FN 0", -2),
    "2022-10-13T16:54:13.991": ("TIMECODE 16", -1),
    "2022-10-13T16:54:13.992": ("HK FN 0", -2),
    "2022-10-13T16:54:14.295": ("Send N-FEE to DUMP mode immediately.", 2),
    "2022-10-13T16:54:14.407": ("Commanding N-FEE DUMP mode", 2),
    "2022-10-13T16:54:14.409": ("Send N-FEE to STANDBY mode on frame 3.", 2),
    "2022-10-13T16:54:20.241": ("TIMECODE 17", -1),
    "2022-10-13T16:54:20.242": ("HK FN 0", -2),
    "2022-10-13T16:54:39.099": ("Commanding N-FEE STANDBY mode", 2),
    "2022-10-13T16:54:39.104": ("Send N-FEE to ON mode on frame 3.", 2),
    "2022-10-13T16:55:04.105": ("Commanding N-FEE ON mode", 2),
}

# Choose some nice levels

levels = [x[1] for x in timings.values()]
times = [datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%f") for x in timings]
descr = [x[0] for x in timings.values()]

# Create figure and plot a stem plot with the date
fig, ax = plt.subplots(figsize=(6, 12), constrained_layout=True)
ax.set(title="Timing movement test")

ax.hlines(times, 0, levels, color="tab:red")  # The vertical stems.
ax.plot(np.zeros_like(times), times, "-o",
        color="k", markerfacecolor="w")  # Baseline and markers on it.

# annotate lines
for time, level, d in zip(times, levels, descr):
    ax.annotate(d, xy=(level, time),
                xytext=(np.sign(level)*3, 3), textcoords="offset points",
                horizontalalignment="left" if level > 0 else "right",
                verticalalignment="top")

ax.yaxis.set_major_locator(mdates.SecondLocator(interval=5))
ax.yaxis.set_major_formatter(mdates.DateFormatter("%S"))
ax.set_ylabel("Seconds")
plt.setp(ax.get_yticklabels(), rotation=0, ha="right")

# remove y axis and spines

ax.xaxis.set_visible(False)
ax.spines[["left", "top", "right"]].set_visible(False)

ax.margins(x=0.1)
plt.show()
