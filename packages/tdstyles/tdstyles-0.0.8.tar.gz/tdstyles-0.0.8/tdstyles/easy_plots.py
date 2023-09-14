import matplotlib.pyplot as plt
import matplotlib.lines as lines
from matplotlib.axes import Axes
from tdstyles.style_css import StyleNotebook
from tdstyles.exceptions import NotStyleNotebook, NotAnAxisObject


def check_grid_line_dictionary(dictionary):
    if dictionary.get('colors') is None:
        dictionary['color'] = 'black'
    if dictionary.get('linestyle') is None:
        dictionary['linestyle'] = 'dashed'
    if dictionary.get('linewidth') is None:
        dictionary['linewidth'] = 1
    if dictionary.get('alpha') is None:
        dictionary['alpha'] = 1

    return dictionary


class EasyPlot:
    def __init__(self, style_notebook=None):
        if style_notebook:
            if isinstance(style_notebook, StyleNotebook):
                self.style_notebook = style_notebook
            else:
                raise NotStyleNotebook(f"Expected an object of Type: '{type(StyleNotebook())}' as a second argument. "
                                       f"But instead got {type(style_notebook)}")
        else:
            self.style_notebook = StyleNotebook()

    def descriptive_plot(self, figsize=(8, 6), draw_line=False, line_pos_x_axis=1, background_color=None):

        if background_color is None:
            background_color = self.style_notebook.get_background_color()

        fig, ax = plt.subplots(1, 1, figsize=figsize, facecolor=background_color)

        ax.set_facecolor(background_color)

        if draw_line:
            line = lines.Line2D([line_pos_x_axis, line_pos_x_axis], [0, 1], transform=fig.transFigure, figure=fig,
                                color='black', lw=0.4)
            fig.lines.extend([line])

        return fig, ax

    def vertical_descriptive_plot(self, figsize=(6, 8), plots=3, plot_height=0.5, plot_width=0.75,
                                  background_color=None, draw_line=False):
        if plot_width > 1.4:
            raise Exception('Plot width cannot be greater than 1.5')

        if background_color is None:
            background_color = self.style_notebook.get_background_color()

        fig = plt.figure(figsize=figsize, facecolor=background_color)
        axes = []

        initial_axis = 0
        for _ in range(plots):
            axis = fig.add_axes([0, initial_axis, plot_width, plot_height])
            axis.set_facecolor(background_color)
            axes.append(axis)
            initial_axis += plot_height + 0.1

        if draw_line:
            line_length = (plot_height + 0.1) * plots
            line = lines.Line2D([plot_width + 0.1, plot_width + 0.1], [0 - 0.1, line_length], transform=fig.transFigure,
                                figure=fig, color='black', lw=0.4)
            fig.lines.extend([line])

        return fig, axes

    def horizontal_descriptive_plot(self, figsize=(8, 6), plots=3, plot_height=0.75, draw_line=False,
                                    line_pos_y_axis=-0.1, background_color=None):
        if plots not in [2, 3, 4]:
            raise Exception('Number of plots must be 2, 3 or 4')

        # Plot Position on X-axis
        increment = {2: 1, 3: 0.7, 4: 0.5}

        # Plot width based on number of plots required
        plot_width = {2: 0.9, 3: 0.6, 4: 0.43}

        if background_color is None:
            background_color = self.style_notebook.get_background_color()

        fig = plt.figure(figsize=figsize, facecolor=background_color)
        axes = []

        initial_axis = 0
        for _ in range(plots):
            axis = fig.add_axes([initial_axis, 0, plot_width[plots], plot_height])
            axis.set_facecolor(background_color)
            axes.append(axis)
            initial_axis += increment[plots]

        if draw_line:
            line_length = increment[plots] * (plots - 1) + plot_width[plots]
            line = lines.Line2D([0 - 0.1, line_length + 0.1], [line_pos_y_axis, line_pos_y_axis],
                                transform=fig.transFigure, figure=fig, color='black', lw=0.4)
            fig.lines.extend([line])

        return fig, axes


class StyleAxis:
    def __init__(self, axis):
        if not isinstance(axis, Axes):
            raise NotAnAxisObject(f"Expected an {Axes} Object instead got {type(axis)} Object")

        self.axis = axis

    def despine_axis(self, *args):
        if len(args) == 0:
            args = ['top', 'right']
        if len(args) <= 4:
            for side in args:
                if side not in ['top', 'bottom', 'left', 'right']:
                    raise Exception(f"Only ['top', 'bottom', 'left', 'right'] are allowed in list. But got {side}.")

            if 'top' in args:
                self.axis.spines['top'].set_visible(False)
            if 'bottom' in args:
                self.axis.spines['bottom'].set_visible(False)
            if 'left' in args:
                self.axis.spines['left'].set_visible(False)
            if 'right' in args:
                self.axis.spines['right'].set_visible(False)
        else:
            raise Exception(f"'despine_axis' requires a minimum of 1 and maximum of 4 elements in the list. But got "
                            f"{len(args)} instead.")

    def alter_axis_spine(self, spines=None, color=None, linewidth=None):
        if spines is None:
            spines = ['left', 'bottom']

        if not isinstance(spines, str) and not isinstance(spines, list):
            raise Exception(f"'spines' argument takes either a string or list of strings as spines."
                            f"Example: 'top' or ['left', 'right']")

        if isinstance(spines, str):
            string_spine = spines
            spines = list()
            spines.append(string_spine)

        for spine in spines:
            if spine not in ['top', 'bottom', 'left', 'right']:
                raise Exception(f"Only 'top', 'bottom', 'left' or 'right' are allowed. But got '{spine}'.")
            if color is None and linewidth is None:
                raise Exception("At least Need color or linewidth parameter to bring change to the axis.")
            if color:
                self.axis.spines[spine].set_color(color)
            if linewidth:
                self.axis.spines[spine].set_linewidth(linewidth)

    def draw_grid_lines(self, x_axis=False, y_axis=True, x_axis_dict=None, y_axis_dict=None):
        if x_axis or y_axis:
            self.axis.set_axisbelow(True)
            if x_axis:
                if x_axis_dict is None:
                    x_axis_dict = {'color': 'white', 'linestyle': 'dashed', 'linewidth': 1, 'alpha': 1}
                x_axis_dict = check_grid_line_dictionary(x_axis_dict)
                self.axis.xaxis.grid(color=x_axis_dict.get('color'), linestyle=x_axis_dict.get('linestyle'),
                                     linewidth=x_axis_dict.get('linewidth'), alpha=x_axis_dict.get('alpha'))
            if y_axis:
                if y_axis_dict is None:
                    y_axis_dict = {'color': 'white', 'linestyle': 'dashed', 'linewidth': 1, 'alpha': 1}
                y_axis_dict = check_grid_line_dictionary(y_axis_dict)
                self.axis.yaxis.grid(color=y_axis_dict.get('color'), linestyle=y_axis_dict.get('linestyle'),
                                     linewidth=y_axis_dict.get('linewidth'), alpha=y_axis_dict.get('alpha'))

    def alter_axis_ticks(self, axis='both', **kwargs):
        """
        Change the appearance of ticks, tick labels, and gridlines.

        Tick properties that are not explicitly set using the keyword
        arguments remain unchanged unless *reset* is True.

        Parameters
        ----------
        axis : {'x', 'y', 'both'}, default: 'both'
            The axis to which the parameters are applied.

        Other Parameters
        ----------------
        direction : {'in', 'out', 'inout'}
            Puts ticks inside the axes, outside the axes, or both.
        length : float
            Tick length in points.
        width : float
            Tick width in points.
        color : color
            Tick color.
        pad : float
            Distance in points between tick and label.
        labelsize : float or str
            Tick label font size in points or as a string (e.g., 'large').
        labelcolor : color
            Tick label color.
        colors : color
            Tick color and label color.
        zorder : float
            Tick and label zorder.
        bottom, top, left, right : bool
            Whether to draw the respective ticks.
        labelbottom, labeltop, labelleft, labelright : bool
            Whether to draw the respective tick labels.
        labelrotation : float
            Tick label rotation
        grid_color : color
            Gridline color.
        grid_alpha : float
            Transparency of gridlines: 0 (transparent) to 1 (opaque).
        grid_linewidth : float
            Width of gridlines in points.
        grid_linestyle : str
            Any valid `.Line2D` line style spec.

        Examples
        --------
        ax.tick_params(direction='out', length=6, width=2, colors='r',
                       grid_color='r', grid_alpha=0.5)

        This will make all major ticks be red, pointing out of the box,
        and with dimensions 6 points by 2 points.  Tick labels will
        also be red.  Gridlines will be red and translucent.
        """

        self.axis.tick_params(axis=axis, **kwargs)
