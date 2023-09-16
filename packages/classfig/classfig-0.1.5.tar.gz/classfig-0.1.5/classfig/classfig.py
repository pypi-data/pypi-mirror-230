#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" classfig simplifies figure handling with matplotlib:
- predefinied templates
- figure instantiation in a class object
- simplified handling (e.g. plot with vectors)

from classfig import classfig
# very simple example
fig = classfig()
fig.plot()
fig.show()

# more complex example
fig = classfig('PPT',nrows=2) # create figure
fig.plot([1,2,3,1,2,3,4,1,1]) # plot first data set
fig.title('First data set') # set title for subplot
fig.subplot() # set focus to next subplot/axis
fig.plot([0,1,2,3,4],[0,1,1,2,3],label="random") # plot second data set
fig.legend() # generate legend
fig.grid() # show translucent grid to highlight major ticks
fig.xlabel('Data') # create xlabel for second axis
fig.save('fig1.png','pdf') # save figure to png and pdf

"""
# %%
import copy
import pathlib
import os
import numpy as np
from packaging import version
import matplotlib
import matplotlib.pyplot
from cycler import cycler


class classfig:
    """
    classfig simplifies figure handling with matplotlib

    Use as
    from classfig import classfig
    fig = classfig('PPT')
    fig.plot([0,1,2,3,4],[0,1,1,2,3])
    fig.save('test.png')

    @author: fstutzki

    """

    def __init__(
        self,
        template="PPT",
        nrows=1,
        ncols=1,
        isubplot=0,
        sharex=False,
        sharey=False,
        width=None,
        height=None,
        fontfamily=None,
        fontsize=None,
        linewidth=None,
        show=True,
        vspace=None,
        hspace=None,
    ):
        """Set default values and create figure: fig = classfig('OL',(2,2))"""
        # Initialize variables
        self.figshow = show  # show figure after saving
        self.axe_current = 0
        self.barH = None
        self.plotH = None
        self.surfaceH = None

        # color
        self.colorBlue = np.array([33, 101, 146]) / 255  # color "blue"
        self.colorRed = np.array([218, 4, 19]) / 255  # color "red"
        self.colorGreen = np.array([70, 173, 52]) / 255  # color "green"
        self.colorOrange = np.array([235, 149, 0]) / 255  # color "orange"
        self.colorYellow = np.array([255, 242, 0]) / 255  # color "yellow"
        self.colorGrey = np.array([64, 64, 64]) / 255  # color "black"

        if isinstance(template, int):
            ncols = copy.copy(nrows)
            nrows = copy.copy(template)
            template = "PPT"

        # default template
        tpl_width = 15
        tpl_height = 10
        tpl_fontfamily = "sans-serif"
        tpl_fontsize = 12
        tpl_linewidth = 2

        if template.lower() == "ppttwo":
            tpl_width = 10
            tpl_height = 8
            tpl_fontfamily = "sans-serif"
            tpl_fontsize = 12
            tpl_linewidth = 2
        elif template.lower() == "pptbig":
            tpl_width = 20
            tpl_height = 15
            tpl_fontfamily = "sans-serif"
            tpl_fontsize = 12
            tpl_linewidth = 3
        elif template.lower() == "ol":
            tpl_width = 8
            tpl_height = 6
            tpl_fontfamily = "serif"
            tpl_fontsize = 9
            tpl_linewidth = 1
        elif template.lower() == "oe":
            tpl_width = 12
            tpl_height = 8
            tpl_fontfamily = "serif"
            tpl_fontsize = 10
            tpl_linewidth = 1
        elif template.lower() == "square":
            tpl_width = 10
            tpl_height = 10
            tpl_fontfamily = "serif"
            tpl_fontsize = 10
            tpl_linewidth = 1

        if width is None:
            width = tpl_width
        if height is None:
            height = tpl_height
        if fontfamily is None:
            fontfamily = tpl_fontfamily
        if fontsize is None:
            fontsize = tpl_fontsize
        if linewidth is None:
            linewidth = tpl_linewidth
        self.linewidth = linewidth

        matplotlib.rc("font", size=fontsize)
        matplotlib.rc("font", family=fontfamily)
        matplotlib.rc("lines", linewidth=linewidth)

        color = [self.colorBlue, self.colorRed, self.colorGreen, self.colorOrange]
        linestyle = ["-", "--", ":", "-."]
        cyc_color = np.tile(color, (np.size(linestyle), 1))
        cyc_linestyle = np.repeat(linestyle, np.shape(color)[0])
        try:
            matplotlib.rc(
                "axes",
                prop_cycle=(
                    cycler("color", cyc_color) + cycler("linestyle", cyc_linestyle)
                ),
            )
        except Exception as e:
            print("classfig.__init__(): Cannot set cycle for color and linestyle")
            print(e)
        # if not self.figshow:
        #     matplotlib.use("Agg")
        self.figH = matplotlib.pyplot.figure()
        self.figH.set_size_inches(width / 2.54, height / 2.54)
        self.subplot(
            nrows,
            ncols,
            isubplot,
            sharex=sharex,
            sharey=sharey,
            vspace=vspace,
            hspace=hspace,
        )

    #        if template.lower() == 'square':
    #            self.axeC.margins(0)
    #            self.axeC.axis('off')
    #            self.axeC.set_position([0, 0, 1, 1])

    def subplot(
        self,
        *args,
        sharex=False,
        sharey=False,
        vspace=None,
        hspace=None,
    ):
        """
        Set current axis/subplot: fig.subplot(0) for first subplot
        or fig.subplot() for next subplot
        """
        num_args = len(args)

        if num_args == 0:
            # increase current axe handle by 1
            self.axe_current += 1
        elif num_args == 1:
            # define current axe handle
            self.axe_current = args[0]
        elif num_args == 2 or num_args == 3:
            # generate new subplot
            self.subplot_nrows = args[0]
            self.subplot_ncols = args[1]
            if num_args == 3:
                self.axe_current = args[2]
            else:
                self.axe_current = 0
            self.subplot_sharex = sharex
            self.subplot_sharey = sharey
            self.subplot_vspace = vspace
            self.subplot_hspace = hspace
            try:
                self.figH.clf()
                self.figH, self.axeH = matplotlib.pyplot.subplots(
                    nrows=self.subplot_nrows,
                    ncols=self.subplot_ncols,
                    num=self.figH.number,
                    sharex=self.subplot_sharex,
                    sharey=self.subplot_sharey,
                )
            except Exception as e:
                print("classfig.subplot(): Matplotlib cannot generate subplots.")
                print(e)
        else:
            raise ValueError("classfig.subplot() takes 0 to 3 unnamed arguments")

        # set current axe handle
        self.axe_current = self.axe_current % (self.subplot_nrows * self.subplot_ncols)
        if self.subplot_nrows == 1 and self.subplot_ncols == 1:
            self.axeC = self.axeH
        elif self.subplot_nrows > 1 and self.subplot_ncols > 1:
            isuby = self.axe_current // self.subplot_ncols
            isubx = self.axe_current % self.subplot_ncols
            self.axeC = self.axeH[isuby][isubx]
        else:
            self.axeC = self.axeH[self.axe_current]

    #        if np.size(self.figH.get_axes()) <= self.axe_current:
    # self.axeC = matplotlib.pyplot.subplot(
    #     self.subplot_nrows, self.subplot_ncols, self.axe_current
    # )  # ,True,False)

    #        else:
    #        print(self.figH.get_axes())
    #        self.axeC = self.figH.get_axes()[self.axe_current-1]
    #        return self.axeC
    def suptitle(self, *args, **kwargs):
        """Set super title for the whole figure"""
        self.figH.suptitle(*args, **kwargs)

    #    def plot(self,*args,**kwargs):
    #        """ Plot data """
    #        self.axeC.plot(*args,**kwargs)
    def bar(self, *args, **kwargs):
        """Generate bar plot"""
        self.barH = self.axeC.bar(*args, **kwargs)
        return self.barH

    def plot(
        self,
        *args,
        mat=np.array(
            [[1, 2, 3, 4, 5, 6, 7], np.random.randn(7), 2 * np.random.randn(7)]
        ),
        **kwargs,
    ):
        """Generate line plot"""
        if np.ndim(mat) > 1:
            if np.shape(mat)[0] > np.shape(mat)[1]:
                mat = mat.T
            for imat in mat[1:]:
                self.plotH = self.axeC.plot(mat[0, :], imat, *args, **kwargs)
                return self.plotH
        else:
            self.plotH = self.axeC.plot(mat, *args, **kwargs)
            return self.plotH

    def semilogx(self, *args, **kwargs):
        """Semi-log plot on x axis"""
        self.plot(*args, **kwargs)
        self.xscale("log")

    def semilogy(self, *args, **kwargs):
        """Semi-log plot on y axis"""
        self.plot(*args, **kwargs)
        self.yscale("log")

    def fill_between(self, *args, color=None, alpha=0.1, linewidth=0, **kwargs):
        """fill area below / between lines"""
        if color is None:
            color = self.colorLast()
        self.axeC.fill_between(
            *args, color=color, alpha=alpha, linewidth=linewidth, **kwargs
        )

    def colorLast(self):
        """returns the last color code used by plot"""
        return self.plotH[0].get_color()

    def pcolor(self, *args, logscale=False, **kwargs):
        """2D area plot"""
        if "cmap" not in kwargs:
            kwargs["cmap"] = "nipy_spectral"
        if logscale:
            kwargs["norm"] = matplotlib.colors.LogNorm()
        self.surfaceH = self.axeC.pcolormesh(*args, **kwargs)
        return self.surfaceH

    def pcolor_square(self, *args, **kwargs):
        """2D area plot with axis equal and off"""
        if "cmap" not in kwargs:
            kwargs["cmap"] = "nipy_spectral"
        self.surfaceH = self.axeC.pcolormesh(*args, **kwargs)
        self.axeC.axis("off")
        self.axeC.set_aspect("equal")
        self.axeC.set_xticks([])
        self.axeC.set_yticks([])
        return self.surfaceH

    def contour(self, *args, **kwargs):
        """2D contour plot"""
        self.surfaceH = self.axeC.contour(*args, **kwargs)
        return self.surfaceH

    def scatter(self, *args, **kwargs):
        """Plot scattered data"""
        self.surfaceH = self.axeC.scatter(*args, **kwargs)
        return self.surfaceH

    def colorbar(self, *args, **kwargs):
        """Add colorbar to figure"""
        self.figH.colorbar(*args, self.surfaceH, ax=self.axeC, **kwargs)

    #        self.axeC.colorbar(*args,**kwargs)
    def axis(self, *args, **kwargs):
        """Access axis properties such as 'off'"""
        self.axeC.axis(*args, **kwargs)

    def axis_aspect(self, *args, **kwargs):
        """Access axis aspect ration"""
        self.axeC.set_aspect(*args, **kwargs)

    def grid(self, *args, color="grey", alpha=0.2, **kwargs):
        """Access axis aspect ration"""
        self.axeC.grid(color=color, alpha=alpha, *args, **kwargs)

    def annotate(self, *args, **kwargs):
        """Annotation to figure"""
        self.axeC.annotate(*args, **kwargs)

    def text(self, *args, **kwargs):
        """Text to figure"""
        self.axeC.text(*args, **kwargs)

    def title(self, *args, **kwargs):
        """Set title for current axis"""
        self.axeC.set_title(*args, **kwargs)

    def xscale(self, *args, **kwargs):
        """Set x-axis scaling"""
        self.axeC.set_xscale(*args, **kwargs)

    def yscale(self, *args, **kwargs):
        """Set y-axis scaling"""
        self.axeC.set_yscale(*args, **kwargs)

    def xlabel(self, *args, **kwargs):
        """Set xlabel for current axis"""
        self.axeC.set_xlabel(*args, **kwargs)

    def ylabel(self, *args, **kwargs):
        """Set ylabel for current axis"""
        self.axeC.set_ylabel(*args, **kwargs)

    def xlim(self, xmin=np.inf, xmax=-np.inf):
        """Set limits for current x-axis: fig.xlim(0,1) or fig.xlim()"""
        try:
            if np.size(xmin) == 2:
                xmax = xmin[1]
                xmin = xmin[0]
            elif xmin == np.inf and xmax == -np.inf:
                for iline in self.axeC.lines:
                    xdata = iline.get_xdata()
                    xmin = np.minimum(xmin, np.nanmin(xdata))
                    xmax = np.maximum(xmax, np.nanmax(xdata))
            if version.parse(matplotlib.__version__) >= version.parse("3"):
                if np.isfinite(xmin):
                    self.axeC.set_xlim(left=xmin)
                if np.isfinite(xmax):
                    self.axeC.set_xlim(right=xmax)
            else:
                if np.isfinite(xmin):
                    self.axeC.set_xlim(xmin=xmin)
                if np.isfinite(xmax):
                    self.axeC.set_xlim(xmax=xmax)
        except Exception as e:
            print("classfig.xlim() throws exception:")
            print(e)
            # pass

    def ylim(self, ymin=np.inf, ymax=-np.inf):
        """Set limits for current y-axis: fig.ylim(0,1) or fig.ylim()"""
        try:
            if np.size(ymin) == 2:
                ymax = ymin[1]
                ymin = ymin[0]
            elif ymin == np.inf and ymax == -np.inf:
                for iline in self.axeC.lines:
                    ydata = iline.get_ydata()
                    ymin = np.minimum(ymin, np.nanmin(ydata))
                    ymax = np.maximum(ymax, np.nanmax(ydata))
            if version.parse(matplotlib.__version__) >= version.parse("3"):
                if np.isfinite(ymin):
                    self.axeC.set_ylim(bottom=ymin)
                if np.isfinite(ymax):
                    self.axeC.set_ylim(top=ymax)
            else:
                if np.isfinite(ymin):
                    self.axeC.set_ylim(ymin=ymin)
                if np.isfinite(ymax):
                    self.axeC.set_ylim(ymax=ymax)
        except Exception as e:
            print("classfig.ylim() throws exception:")
            print(e)
            # pass

    def legend(self, *args, labels=None, **kwargs):
        """insert legend to figure with plot(x,y,'label'='Test1')"""
        if labels is not None:
            ilabel = 0
            for iline in self.axeC.lines:
                iline.set_label(labels[ilabel])
                ilabel += 1
        handles, labels = self.axeC.get_legend_handles_labels()
        if np.size(self.axeC.lines) != 0 and len(labels) != 0:
            self.axeC.legend(*args, **kwargs)

    def legend_entries(self):
        """returns handle and labels of legend"""
        handles, labels = self.axeC.get_legend_handles_labels()
        return handles, labels

    def legend_count(self):
        """return number of legend entries"""
        handles, labels = self.axeC.get_legend_handles_labels()
        return np.size(handles)

    def set_cycle(self, color=False, linestyle=False):  # ,linewidth=False):
        """call to set color and linestyle cycle (will be used in this order)"""
        if color is False:
            color = [self.colorRed, self.colorBlue, self.colorGreen, self.colorOrange]
        if linestyle is False:
            linestyle = ["-", "--", ":", "-."]
        #        if linewidth is False:
        #            linewidth = self.linewidth
        if np.ndim(color) == 1:
            cyc_color = np.tile(color, (np.size(linestyle)))
        else:
            cyc_color = np.tile(color, (np.size(linestyle), 1))
        cyc_linestyle = np.repeat(linestyle, np.shape(color)[0])
        #        cyc_linewidth = np.ones(np.shape(cyc_color),dtype=float)*linewidth
        try:
            self.axeC.set_prop_cycle(
                cycler("color", cyc_color) + cycler("linestyle", cyc_linestyle)
            )  # +cycler('linewidth',cyc_linewidth))
        except Exception as e:
            print("classfig.set_cycle(): Cannot set cycle for color and linestyle:")
            print(e)
            print(np.shape(cyc_color))
            print(np.shape(cyc_linestyle))

    def set_parameters(self, hspace=False, vspace=False):
        """
        set useful figure parameters, called automatically by save
        and show function
        """
        # try:
        #     if (
        #         self.axeC.get_xscale() != "log"
        #     ):  # Otherwise xticks get missing on saving/showing- seems to be a bug
        #         self.axeH.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(7))
        # except:
        #     pass
        try:
            self.figH.tight_layout()
        except Exception as e:
            print("classfig.set_parameters(): Tight layout cannot be set!")
            print(e)

        if self.subplot_hspace is not None and self.subplot_nrows > 1:
            self.figH.subplots_adjust(hspace=self.subplot_hspace)
        if self.subplot_vspace is not None and self.subplot_ncols > 1:
            self.figH.subplots_adjust(vspace=self.subplot_vspace)

    def watermark(self, img, *args, xpos=100, ypos=100, alpha=0.15, zorder=1, **kwargs):
        """include watermark image to plot"""
        if os.path.isfile(img):
            self.figH.figimage(
                img, xpos, ypos, alpha=alpha, zorder=zorder, *args, **kwargs
            )
        else:
            print("classfig.watermark(): File not found")

    def show(self):
        """call in interactive console instead of save"""
        self.set_parameters()
        matplotlib.pyplot.show()  # block=False)

    def save(self, filename, *args, **kwargs):
        """Save figure to png, pdf: fig.save('test.png',600,'pdf')"""
        dpi = 300
        fileparts = filename.split(".")
        fileformat = set()
        fileformat.add(fileparts[-1])
        filename = filename.replace("." + fileparts[-1], "")
        for attribute in args:
            if isinstance(attribute, int):
                dpi = attribute
            else:
                fileformat.add(attribute)
        if "dpi" not in kwargs:
            kwargs["dpi"] = dpi

        self.set_parameters()
        for iformat in fileformat:
            try:
                pathlib.Path(os.path.dirname(filename)).mkdir(
                    parents=True, exist_ok=True
                )
                self.figH.savefig(filename + "." + iformat, **kwargs)
            except Exception as e:
                print(
                    f"classfig.save(): Figure cannot be saved to {filename}.{iformat}"
                )
                print(e)
        if self.figshow:
            matplotlib.pyplot.show()  # block=False)
        else:
            matplotlib.pyplot.draw()

    def clear(self, *args, **kwargs):
        """Clear figure content in order to reuse figure"""
        self.figH.clf(*args, **kwargs)

    def close(self, *args, **kwargs):
        """Close figure"""
        #        self.figH.close(*args,**kwargs)
        try:
            matplotlib.pyplot.close(self.figH)
        except Exception as e:
            print("classfig.close(): Figure cannot be closed")
            print(e)
