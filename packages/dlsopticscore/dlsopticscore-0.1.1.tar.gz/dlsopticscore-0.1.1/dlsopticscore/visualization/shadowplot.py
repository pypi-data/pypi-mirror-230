import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import cm
from lmfit.models import GaussianModel


major_alpha = 0.2
minor_alpha = 0.1
grid_color = 'gray'

cmap = cm.viridis
line_colour = cmap(0.3)
fit_colour = cmap(0.8)
image_text_colour = cmap(0.9)
hist_text_colour = cmap(0.2)
centre_colour = cmap(0.6)


def plot_image(shadow, scale=1e4, bins=75, rotateimage=False):
    if rotateimage:
        x = shadow.z
        y = shadow.x

    else:
        x = shadow.x
        y = shadow.z

    x_min = np.min(x)
    x_max = np.max(x)
    y_min = np.min(y)
    y_max = np.max(y)

    (image_hist, image_xedges,
        image_yedges) = np.histogram2d(x, y, bins=bins,
                                       range=((x_min, x_max), (y_min, y_max)))
    image_hist = image_hist.T

    x_hist, x_bins = np.histogram(x, bins=bins)
    x_centres = (x_bins[:-1] + x_bins[1:]) / 2

    y_hist, y_bins = np.histogram(y, bins=bins)
    y_centres = (y_bins[:-1] + y_bins[1:]) / 2

    gauss = GaussianModel()
    x_result = gauss.fit(x_hist, x=x_centres)
    y_result = gauss.fit(y_hist, x=y_centres)

    fwhm_x = x_result.best_values['sigma']*2.355
    fwhm_y = y_result.best_values['sigma']*2.355

    centre_x = x_result.best_values['center']
    centre_y = y_result.best_values['center']

    fig = plt.figure(figsize=(8, 8))
    spec = gridspec.GridSpec(ncols=4, nrows=4)

    ax_histx = fig.add_subplot(spec[0, 0:3])
    ax_histx.hist(x*scale, bins=bins, histtype='step',
                  fill=False, color=line_colour)
    ax_histx.plot(x_centres*scale, x_result.best_fit, color=fit_colour,
                  linestyle='--')
    ax_histx.plot([centre_x*scale, centre_x*scale],
                  np.asarray(ax_histx.get_ylim()),
                  color=centre_colour, linestyle='--')

    ax_image = fig.add_subplot(spec[1:4, 0:3])
    plt.pcolormesh(image_xedges*scale, image_yedges*scale,
                   image_hist, cmap=cmap)

    ax_histy = fig.add_subplot(spec[1:4, 3])
    ax_histy.hist(y*scale, bins=bins, orientation="horizontal",
                  histtype='step', fill=False, color=line_colour)
    ax_histy.plot(y_result.best_fit, y_centres*scale,
                  color=fit_colour, linestyle='--')
    ax_histy.plot(np.asarray(ax_histy.get_xlim()),
                  [centre_y*scale, centre_y*scale],
                  color=centre_colour, linestyle='--')

    ax_histx.axes.xaxis.set_ticklabels([])
    ax_histy.axes.yaxis.set_ticklabels([])

    ax_histx.axes.set_xlim(ax_image.axes.get_xlim())
    ax_histy.axes.set_ylim(ax_image.axes.get_ylim())

    ax_image.grid(True, which='major', color=grid_color, alpha=major_alpha)
    ax_image.grid(True, which='minor', color=grid_color, alpha=minor_alpha)

    ax_histx.grid(True, which='major', axis='x',
                  color=grid_color, alpha=major_alpha)
    ax_histx.grid(True, which='minor', axis='x',
                  color=grid_color, alpha=minor_alpha)
    ax_histx.grid(True, which='major', axis='y',
                  color=grid_color, alpha=major_alpha)

    ax_histy.grid(True, which='major', axis='y',
                  color=grid_color, alpha=major_alpha)
    ax_histy.grid(True, which='minor', axis='y',
                  color=grid_color, alpha=minor_alpha)
    ax_histy.grid(True, which='major', axis='x',
                  color=grid_color, alpha=major_alpha)

    ax_image.minorticks_on()
    ax_histx.minorticks_on()
    ax_histx.tick_params(which='minor', left=False)
    ax_histy.minorticks_on()
    ax_histy.tick_params(which='minor', bottom=False)

    ax_image.set_xlabel(r'x [$\mu$m]')
    ax_image.set_ylabel(r'y [$\mu$m]')

    image_label = r'FWHM$_x$ = {:.2f} $\mu$m'.format(fwhm_x*scale)
    image_label += '\n'
    image_label += r'FWHM$_y$ = {:.2f} $\mu$m'.format(fwhm_y*scale)
    ax_image.annotate(image_label, xycoords='axes fraction',
                      xy=(0.05, 0.05), color=image_text_colour)

    histx_label = r'x$_0$ = {:.2f} $\mu$m'.format(centre_x*scale)
    ax_histx.annotate(histx_label, xycoords='axes fraction',
                      xy=(0.05, 0.8), color=hist_text_colour)

    histy_label = r'y$_0$ = {:.2f} $\mu$m'.format(centre_y*scale)
    ax_histy.annotate(histy_label, xycoords='axes fraction',
                      xy=(0.1, 0.95), color=hist_text_colour)

    plt.show()


def plot_energy(shadow, bins=75):
    energy = shadow.energy

    hist, bin_edges = np.histogram(energy, bins=bins)
    centres = (bin_edges[:-1] + bin_edges[1:]) / 2

    gauss = GaussianModel()
    pars = gauss.guess(hist, x=centres)
    result = gauss.fit(hist, x=centres, params=pars)

    result.fit_report(min_correl=0.25)

    fwhm = result.best_values['sigma']*2.355
    centre = result.best_values['center']

    fig = plt.figure(figsize=(8, 8))

    ax = fig.add_subplot(111)
    ax.hist(energy, bins=bins, histtype='step',
            fill=False, color=line_colour)
    ax.plot(centres, result.best_fit,
            color=fit_colour, linestyle='--')
    ax.plot([centre, centre], np.asarray(ax.get_ylim()),
            color=centre_colour, linestyle='--')

    ax.grid(True, which='major', color=grid_color, alpha=major_alpha)
    ax.grid(True, which='minor', color=grid_color, alpha=minor_alpha)
    ax.minorticks_on()

    ax.set_xlabel('Energy [eV]')
    ax.set_ylabel('Rays')

    label = r'$\Delta$E$_{FWHM}$ = ' + '{:.4f} eV'.format(fwhm)
    label += '\n'
    label += r'E$_0$ = {:.2f} eV'.format(centre)
    ax.annotate(label, xycoords='axes fraction',
                xy=(0.05, 0.90), color=hist_text_colour)

    plt.show()
