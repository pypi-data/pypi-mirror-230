import sys
import warnings
from datetime import datetime
from datetime import timedelta
from functools import partial

import pyqtgraph as pg
from PyQt5.QtCore import QDateTime
from PyQt5.QtCore import QRegExp
from PyQt5.QtCore import QTime
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QIntValidator
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure
from pyqtgraph import AxisItem
from pyqtgraph import PlotWidget

from egse.config import find_file
from egse.process import ProcessStatus
from egse.randomwalk import RandomWalk

warnings.filterwarnings("ignore")






def cut_range(x, y, interval):

    """
    Limit the elements in both lists such that the x-range is not larger
    than interval. The lists are shortened from the start.

    Given two lists of equal length, shorten the lists such that the elements
    in the x-list all fall within the range x[-1] - interval. The function is
    used to simulate a moving window of size interval.

    Args:
        - x: List of x-values in ascending order.
        - y: List of corresponding y-values.
        - interval: Range of x-value to crop to.

    Returns:
        - Cropped x-list.
        - Cropped y-list.
    """

    x_min = x[-1] - interval
    idx = next(a[0] for a in enumerate(x) if a[1] >= x_min)

    return x[idx:], y[idx:]

def cut_interval(x, y, start_time, end_time):

    """
    Limit the elements in both lists such that the x-values are in the given interval.

    Given two lists of equal lenght, shorten the lists such that the elements in the x-list
    are within the given interval.

    Args:
        - x: List of x-values in ascending order.
        - y: List of corresponding y-values.
        - start_time: Minimum x-value to include in the cropped lists.
        - end_time: Maximum x-value to include in the cropped lists.

    Returns:
        - Cropped x-list.
        - Cropped y-list.
    """

    print(type(start_time), type(end_time), type(x[0]))
    idx = next(a[0] for a in enumerate(x) if a[1] >= start_time and a[1] < end_time)

    return x[idx:], y[idx:]

def link(stripchart_widget, stripchart_controller):

    """
    Link the given stripchart widget with the given controller.  This means the
    following:

        - the stripchart widget "knows" about the stripchart controller and will update
          the information that is shown there;
        - the stripchart controller "knows" about the stripchart widget and controls what
          is shown.
    """

    stripchart_widget.controller = stripchart_controller
    stripchart_controller.stripcharts.append(stripchart_widget)

    if stripchart_controller.toolbar_mode:

        stripchart_controller.play_action.triggered.connect(stripchart_widget.play) # Action to put into the toolbar of the main GUI

    else:

        stripchart_controller.play_button.clicked.connect(stripchart_widget.play)   # Play button in the controller widget

class StripChartControllerWidget(QGroupBox):

    """
    Displays the begin and end of the time range that will be shown in the stripchart widgets
    that are linked to this stripchart controller (in the format "d hh:mm:ss"), and the corresponding
    interval length (in seconds).

    You can choose to display either:

        - the last interval (of given duration) of the time series
        - or a specific period in time (from the given start to end time).

    This can be chosen in two different way (you have to pick one):

        - via a button in the stripchart controller widget
        - or via a button/action that can be placed in the toolbar of the main GUI.

    If the button of choice is in "play" mode, the last time interval will be shown, the
    length of which can be specified (in seconds) in the text field in the controller widget. The
    start and end time of this time period is also displayed (but cannot be changed).
    Alternatively, if the button of choice is in "pause" mode, the plot is no longer updated
    in realtime, but you can specify which time period to inspect, by adapting the start and end
    time (in the format "d hh:mm:ss").  The interval lengths is also displayed (but cannot be
    changed).
    """

    def __init__(self, toolbar_mode=True):

        super(StripChartControllerWidget, self).__init__("")

        self.stripcharts = []
        self.realtime = True

        self.toolbar_mode = toolbar_mode

        if toolbar_mode:

            self.create_play_action()

        layout = QGridLayout()

        # Button: play/pause

        if not toolbar_mode:

            self.create_play_button()
            layout.addWidget(self.play_button, 0, 0)

        # From ... to ...

        self.create_start_end()

        layout.addWidget(QLabel("From"), 1, 1)
        layout.addWidget(self.start_time_label, 1, 2)
        layout.addWidget(QLabel("to"), 1, 3)
        layout.addWidget(self.end_time_label, 1, 4)

        # Interval length

        self.create_interval()

        layout.addWidget(QLabel("Interval [s]"), 2, 1)
        layout.addWidget(self.interval_label, 2, 2)

        self.setLayout(layout)


    def create_play_action(self):

        """
        Create play button/action that will be added to the toolbar of the main GUI.  When this button
        is pushed, the behaviour of the plots of the stripcharts changes accordingly.
        """

        play_pix = QPixmap(str(find_file("play.png", in_dir="images")))
        pause_pix = QPixmap(str(find_file("pause.png", in_dir="images")))
        play_icon = QIcon()
        play_icon.addPixmap(play_pix, QIcon.Normal, QIcon.On)
        play_icon.addPixmap(pause_pix, QIcon.Normal, QIcon.Off)

        self.play_action = QAction(play_icon, "Play", self)
        self.play_action.setToolTip("Sohw specific time interval / show last time interval")
        self.play_action.setCheckable(True)
        self.play_action.setChecked(False)
        self.play_action.triggered.connect(self.handle_play)

    def create_play_button(self):

        """
        Create play button that will be added to the stripchart controller.  When this button is
        pushed, the behaviour of the plots of the stripcharts changes accordingly.
        """

        self.play_icon  = QIcon(str(find_file("play.png", in_dir="images")))
        self.pause_icon = QIcon(str(find_file("pause.png", in_dir="images")))

        self.play_button = QPushButton("")
        self.play_button.setToolTip("Show specific time interval")
        self.play_button.setIcon(self.pause_icon)
        self.play_button.clicked.connect(self.play)

    def create_start_end(self):

        """
        Create the text fields (incl. validators) for the start and end time.

        Currently, the validator is not set for the text fields, as the values are not accepted then
        when you hit enter.  Still to figure out what the problem is.
        """

        time_regex = QRegExp('^([1-9]|[1-9]\d{1,}) ^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$')
        time_validator = QRegExpValidator(time_regex)

        # Start time

        self.start_time_label = QLineEdit(self)
        self.start_time_label.setReadOnly(True)

        # self.start_time_label.setValidator(time_validator)
        self.start_time_label.setPlaceholderText("d hh:mm:ss")
        self.start_time_label.returnPressed.connect(partial(self.update_start_time, self.start_time_label))

        self.end_time_label = QLineEdit(self)
        self.end_time_label.setReadOnly(True)

        # self.end_time_label.setValidator(time_validator)
        self.end_time_label.setPlaceholderText("d hh:mm:ss")
        self.end_time_label.returnPressed.connect(partial(self.update_end_time, self.end_time_label))

    def create_interval(self):

        """
        Create the text field for the interval length.
        """
        self.interval_label = QLineEdit(self)

        interval_validator = QIntValidator()
        interval_validator.setBottom(1)
        self.interval_label.setValidator(interval_validator)

        self.interval = timedelta(seconds=60)

        self.interval_label.setText(str(self.interval.seconds))
        self.interval_label.returnPressed.connect(partial(self.update_interval, self.interval_label))


    def handle_play(self):

        """
        When the play button in the toolbar of the main GUI is pushed (if any), the behaviour of the (plots in the)
        stripchart widget changes.

        In realtime mode (real stripchart):
            - the play-button in the stripchart controller (if any) should show the "pause" icon;
            - the plot is updated immediately when an extra datapoint is added to the time series;
            - the textfields in the stripchart controller (if any) with the start and end time cannot be
              changed by the user but will be updated automatically;
            - the interval length can be adapted via the dedicated text field in the stripchart controller (if any).

        In non-realtime mode (inspection of a specific time period):
            - the play-button in the stripchart controller (if any) should show the "play" icon;
            - the plot is no longer updated when an extra datapoint is added to the time series;
            - the start and end time can be adapted via the dedicated text fields in the stripchart
              controller (if any);
            - the textfield in the stripchart controller (if any) with the interval length cannot be
              changed by the user but will be updated automatically (when returning to realtime mode,
              this new interval length will be used).
        """

        self.play()

    def play(self):

        """
        When the play button is pushed in the stripchart controller (if any), the behaviour of the (plots in the)
        stripchart widget changes.

        In realtime mode (real stripchart):
            - the play-button in the stripchart controller (if any) should show the "pause" icon;
            - the plot is updated immediately when an extra datapoint is added to the time series;
            - the textfields in the stripchart controller (if any) with the start and end time cannot be
              changed by the user but will be updated automatically;
            - the interval length can be adapted via the dedicated text field in the stripchart controller (if any).

        In non-realtime mode (inspection of a specific time period):
            - the play-button in the stripchart controller (if any) should show the "play" icon;
            - the plot is no longer updated when an extra datapoint is added to the time series;
            - the start and end time can be adapted via the dedicated text fields in the stripchart
              controller (if any);
            - the textfield in the stripchart controller (if any) with the interval length cannot be
              changed by the user but will be updated automatically (when returning to realtime mode,
              this new interval length will be used).
        """

        self.realtime = not self.realtime

        # Realtime mode

        if self.realtime:

            if not self.toolbar_mode:

                self.play_button.setIcon(self.pause_icon)   # Change the icon on the play-button to "pause"
                self.play_button.setToolTip("Show specific time interval")
                self.play_button.repaint()

            self.start_time_label.setReadOnly(True)     # Disable changing the start time text field
            self.end_time_label.setReadOnly(True)       # Disable changing the start time text field
            self.interval_label.setReadOnly(False)      # Enable changing the interval length

        # Non-realtime mode

        else:

            if not self.toolbar_mode:

                self.play_button.setIcon(self.play_icon)   # Change the icon on the play-button to "play"
                self.play_button.setToolTip("Show last time interval")
                self.play_button.repaint()

            self.start_time_label.setReadOnly(False)   # Enable changing the start time text field
            self.end_time_label.setReadOnly(False)     # Enable changing the start time text field
            self.interval_label.setReadOnly(True)      # Disable changing the interval length


    def update_interval(self, interval_label):

        """
        If the text field with the interval length is updated, the plots in the stripchart
        widgets are updated.  Only applicable in realtime mode.

        Args:
            - interval_label: Text field where the interval length can be entered (in seconds).
        """

        self.interval = timedelta(seconds=int(interval_label.text()))

        # Update all stripchart widgets

        for stripchart in self.stripcharts:

            stripchart.update_interval(self.interval)

    def update_start_time(self, start_time_label):

        """
        If the text field with the start time is updated, the plots in the stripchart widgets
        are updated.  Only applicable in non-realtime mode.

        Args:
            - start_time_label: Text field where the start time can be entered (in format "d hh:mm:ss").
        """

        start_time = datetime.strptime(start_time_label.text(), "%j %H:%M:%S")
        start_time += timedelta(days=365.25*70-1, hours=12)         # 1900 -> 1970

        # Update all stripchart widgets

        for stripchart in self.stripcharts:

            stripchart.update_start_time(start_time)

    def update_end_time(self, end_time_label):

        """
        If the text field with the end time is updated, the plots in the stripchart widgets
        are updated.  Only applicable in non-realtime mode.

        Args:
            - end_time_label: Text field where the end time can be entered (in format "d hh:mm:ss").
        """

        end_time = datetime.strptime(end_time_label.text(), "%j %H:%M:%S")
        end_time += timedelta(days=365.25*70 - 1, hours=12)         # 1900 -> 1970

        # Update all stripchart widgets

        for stripchart in self.stripcharts:

            stripchart.update_end_time(end_time)

    def set_time(self, last_timepoint):

        """
        Update the content of the textfields with the start and end time (in realtime mode only).
        Only applicable in realtime mode.
        """

        self.end_time_label.setText(last_timepoint.strftime("%-d %H:%M:%S"))
        self.start_time_label.setText((last_timepoint - self.interval).strftime("%-d %H:%M:%S"))


class StripChartWidget(QGroupBox):

    def __init__(self, quantity, unit):

        """
        Initialisation of a plot of the focal plane, with a blue circle indicating the
        field-of-view.  Below the plot you can find a spinner to choose the coordinate
        system to be used in the plot.

        Args:
            - quantity: Physical quantity shown by the strip chart.
            - unit: Unit of the physical quantity shown by the strip chart.
        """

        super(StripChartWidget, self).__init__("")

        self.interval = timedelta(seconds=60)

        self.realtime = True
        self.controller = None

        self.timepoints = []
        self.values = []

        # Plot window

        layout = QGridLayout()

        self.stripchart = TimeSeriesCanvas(quantity, unit)

        layout.addWidget(self.stripchart)

        self.setLayout(layout)

    def update(self, time, value):

        """
        Update the plot when the given datapoint is added to the time series, only when in realtime
        mode.

        Args:
            - time: Time [ms].
            - value: Value.
        """

        # Convert from double to datetime

        time = datetime.fromtimestamp(time / 1000.0)

        # Append to the time series

        self.timepoints.append(time)
        self.values.append(value)

        # Update the plot (only in realtime mode)

        if self.realtime:

            self.end_time = self.timepoints[-1]                 # New point = new end time
            self.start_time = self.end_time - self.interval     # Update start time

            last_timepoints, last_values = cut_range(self.timepoints, self.values, self.interval)   # Cut out the requested range
            self.stripchart.plot(last_timepoints, last_values, interval=self.interval)              # Update the plot

            if not self.controller is None:

                self.controller.set_time(last_timepoints[-1])       # Update the text fields in the stripchart controller (begin and end time)



    def update_interval(self, interval):

        """
        When the text field with the interval is updated in the stripchart controller (if any),
        the range on the x-axis of the plot is adapted accordingly.

        Args:
            - interval: Length of the time period to be displayed in the plot [s].
        """

        self.interval = interval

        last_timepoints, lastvalues = cut_range(self.timepoints, self.values, self.interval)
        self.stripchart.plot(last_timepoints, lastvalues, interval=self.interval)

    def update_start_time(self, start_time):

        """
        When the text field with the start time is updated in the stripchart controller (if any),
        the range on the x-axis of the plot is adapted accordingly.

        Args:
            - start_time: First timepoint to be displayed in the plot (in the format "d hh:mm:ss").
        """

        self.start_time = start_time

        self.interval = self.end_time.replace(microsecond=0) - self.start_time.replace(microsecond=0)

        self.controller.interval_label.setText(str(self.interval.seconds))

        t, v = cut_interval(self.timepoints, self.values, self.start_time, self.end_time)
        self.stripchart.plot(t, v, min_time=self.start_time, max_time=self.end_time)



    def update_end_time(self, end_time):

        """
        When the text field with the end time is updated in the stripchart controller (if any),
        the range on the x-axis of the plot is adapted accordingly.

        Args:
            - end_time: Last timepoint to be displayed in the plot (in the format "d hh:mm:ss").
        """

        self.end_time = end_time

        self.interval = self.end_time.replace(microsecond=0) - self.start_time.replace(microsecond=0)

        self.controller.interval_label.setText(str(self.interval.seconds))

        t, v = cut_interval(self.timepoints, self.values, self.start_time, self.end_time)
        self.stripchart.plot(t, v, min_time=self.start_time, max_time=self.end_time)

    def play(self):

        """
        When the play button from the stripchart controller (if any) is pushed, the widget is notified
        that the display behaviour (realtime update of the last interval vs. inspecting specific period)
        must change.
        """

        self.realtime = not self.realtime





class TimeSeriesCanvas(FigureCanvas):

    def __init__(self, quantity, unit, parent=None, dpi=100):

        """
        Initialisation of the plot window, that will be used to plot time series.

        Args:
            - quantity: Physical quantity that will be shown on the y-axis.
            - unit: Unit of the physical quantity that will be shown on the y-axis.
        """

        self.quantity = quantity
        self.unit = unit

        self.figure = Figure()
        self.ax = self.figure.add_subplot(111)

        FigureCanvas.__init__(self, self.figure)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    def plot(self, timepoints, values, interval=None, min_time = None, max_time = None):

        """
        Remove the current content (if any) and plot the given data.

        Args:
            - timepoints: Timepoints as datatime objects.
            - values: Values corresponding to the timepoints.
            - interval: Range of the x-axis (up to the last timepoints) as timedelta object.  If this
                        is None, the x-range will not be set.
            - min_time: Lower end of the interval to show on the x-axis.
            - max_time: Upper end of the interval to show on the x-axis.
        """

        # Remove old content (if any)

        try:
            del self.ax.lines[-1]
        except:
            pass

        # Plot the new data

        self.ax.plot(timepoints, values, "b")

        # On the x-axis: time

        if not interval is None:

            self.ax.set_xlim([timepoints[-1] - interval, timepoints[-1]])

        if not min_time is None and not max_time is None:

            self.ax.set_xlim([min_time, max_time])

        self.ax.set_xlabel("Time [d hh:mm:ss]", fontsize=10)
        formatter = DateFormatter("%-d %H:%M:%S")
        self.ax.xaxis.set_major_formatter(formatter)
        self.figure.autofmt_xdate()

        # On the y-axis: physical quantity (specified at initialisation)

        self.ax.set_ylabel(self.quantity + " [" + self.unit + "]", fontsize=10)

        self.draw()




class TimeAxisItem(AxisItem):
    def __init__(self, *args, **kwargs):
        AxisItem.__init__(self, *args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [QDateTime.fromMSecsSinceEpoch(value).toString('d HH:mm:ss') for value in values]


class StripChart(PlotWidget):
    """
    A PlotWidget that represents a StripChart (scatter plot).
    By default the bottom axis is a time axis in milliseconds resolution, but
    the labels are 'hh:mm:ss' since midnight.
    By default the left axis is a Position in degrees.
    The default can be changed by using the `axisItems` and `labels` arguments
    as in the following example:
    ```
    stripchart = StripChart(
        axisItems={'bottom': AxisItem(orientation='bottom')},
        labels={'left'  : ('Position', 'millimeter'),
                'bottom': ('Index', None)})
    ```
    """
    def __init__(self, **kwargs):
        if 'axisItems' not in kwargs:
            bottom_axis = TimeAxisItem(orientation='bottom')
            left_axis = AxisItem(orientation='left')

            # Disable automatic prefix for SI units and axis scaling
            bottom_axis.enableAutoSIPrefix(enable=False)
            left_axis.enableAutoSIPrefix(enable=False)

            kwargs['axisItems'] = {'bottom': bottom_axis, 'left': left_axis}

        PlotWidget.__init__(self, **kwargs)

        if 'labels' not in kwargs:
            self.setLabel('left', 'Position', units='degrees')
            self.setLabel('bottom', 'Time', units='d hh:mm:ss')

        self._plot = self.plot(pen=pg.mkPen(width=4))
        self._x_time = []
        self._y_data = []
        self._interval = 60 * 60   # [s] number of seconds on the bottom axis

    def setInterval(self, interval):
        """
        Set the interval for the x-axis.
        Time intervals are in seconds.
        """
        self._interval = interval

    def setData(self, *args, **kwargs):
        self._plot.setData(*args, **kwargs)

    def set_yrange(self, ymin, ymax):
        self.setYRange(ymax, ymin)

    def update(self, time, value):

        self._x_time.append(time)
        self._y_data.append(value)

        # We are not cutting the original data, that keeps on growing for the
        # lifetime of the stripchart object. The reason is because we might want
        # to implement panning back and forth in time at some point.
        #
        # x is in milliseconds, so interval shall also be in miliseconds

        x, y = cut_range(self._x_time, self._y_data, self._interval * 1000)

        self._plot.setData(x, y)


if __name__ == "__main__":

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.stripchart = StripChart()
            self.random_walk = RandomWalk(scale=0.1, count=0)
            self.process_status = ProcessStatus()

            self.setCentralWidget(self.stripchart)

            self.stripchart_timer = QTimer()
            self.stripchart_timer.timeout.connect(self.update_stripchart)
            self.stripchart_timer.setInterval(100)
            self.stripchart_timer.start()

            self.reporting_timer = QTimer()
            self.reporting_timer.timeout.connect(self.report_system_resources)
            self.reporting_timer.setInterval(10_000)
            self.reporting_timer.start()

        def update_stripchart(self):
            # current_time = datetime.now()
            current_time = QTime.currentTime().msecsSinceStartOfDay()
            value = next(self.random_walk)
            self.stripchart.update(current_time, value)

        def report_system_resources(self):
            print(self.process_status)

    app = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
