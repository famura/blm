"""
This scripts allows to play with the 4 parameters of the backlash model.

Based on matplotlib's interactive slider demo

.. seealso::
    https://matplotlib.org/3.1.1/gallery/widgets/slider_demo.html
"""

from typing import Union

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button, Slider

from blm import BacklashModel


def lin_dec_sin(t: np.ndarray, t_end: float, amp: float, freq: float):
    """Linearly decaying sinus wave."""
    return amp * (1 - t / t_end) * np.cos(2 * np.pi * freq * t)


def update(val):
    """Core callback function."""
    reset_lbm_from_slider_values(x_init=lin_dec_sin(t_grid[0], t_end, amp, freq))

    # Generate backlash data
    x_hist = []
    for t in t_grid:
        x = lin_dec_sin(t, t_end, amp, freq)
        x_hist.append(G_bl_model(x).copy())
    x_hist = np.expand_dims(np.stack(x_hist), axis=1)

    # Update the curve the data
    G_lines.set_ydata(x_hist)

    # Update the zone data
    u_grid = np.linspace(-5, 5, 2001)
    u_grid_lo = G_slider_m_lo.val * (u_grid + G_slider_c_lo.val)
    u_grid_up = G_slider_m_up.val * (u_grid - G_slider_c_up.val)
    G_bound_lo.set_ydata(u_grid_lo)
    G_bound_up.set_ydata(u_grid_up)
    axs[1].collections.clear()
    axs[1].fill_between(u_grid, u_grid_lo, u_grid_up, color="gray", alpha=0.3, label="backlash zone")

    fig.canvas.draw_idle()


def reset(event):
    """Reset the sliders."""
    G_slider_m_lo.reset()
    G_slider_m_up.reset()
    G_slider_c_lo.reset()
    G_slider_c_up.reset()


def reset_lbm_from_slider_values(x_init: Union[float, int, list, np.ndarray]):
    """Use the global slider values to create a new linear backlash model."""
    # Catch infeasible values
    if G_slider_m_lo.val == 0:
        G_slider_m_lo.val = 1e-4
    if G_slider_m_up.val == 0:
        G_slider_m_up.val = 1e-4

    # Set values
    G_bl_model.reset(G_slider_m_lo.val, G_slider_m_up.val, G_slider_c_lo.val, G_slider_c_up.val, x_init=x_init)


if __name__ == "__main__":
    # Setup
    dt = 0.002
    t_end = 5.0
    t_grid = np.linspace(0.0, t_end, int(t_end / dt))
    amp = 4.0
    freq = 1.0
    x = lin_dec_sin(t_grid, t_end, amp, freq)

    # Create figure
    mpl.style.use("seaborn")
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(16, 9))
    plt.subplots_adjust(left=0.05, bottom=0.3)

    # Create sliders
    lim_m = 5.0
    lim_c = 10.0
    delta_m = 0.02
    delta_c = 0.01
    ax_m_lo = plt.axes([0.05, 0.10, 0.7, 0.03])
    ax_m_up = plt.axes([0.05, 0.05, 0.7, 0.03])
    ax_c_lo = plt.axes([0.05, 0.20, 0.7, 0.03])
    ax_c_up = plt.axes([0.05, 0.15, 0.7, 0.03])
    G_slider_m_lo = Slider(ax_m_lo, "m_lo", -lim_m, lim_m, valinit=1.0, valstep=delta_m)
    G_slider_m_up = Slider(ax_m_up, "m_up", -lim_m, lim_m, valinit=1.0, valstep=delta_m)
    G_slider_c_lo = Slider(ax_c_lo, "c_lo", 0.0, lim_c, valinit=0.0, valstep=delta_c)
    G_slider_c_up = Slider(ax_c_up, "c_up", 0.0, lim_c, valinit=0.0, valstep=delta_c)
    G_slider_m_lo.on_changed(update)
    G_slider_m_up.on_changed(update)
    G_slider_c_lo.on_changed(update)
    G_slider_c_up.on_changed(update)

    # Create reset button
    resetax = plt.axes([0.8, 0.115, 0.1, 0.05])
    button_reset = Button(resetax, "reset", hovercolor="0.975")
    button_reset.on_clicked(reset)

    # Initial plotting of the curve
    axs[0].plot(t_grid, x, lw=2, label="original", color="C0")
    (G_lines,) = axs[0].plot(t_grid, x, lw=2, label="backlash", color="C2")

    # Plot the backlash decision boundaries
    u_grid = np.linspace(-5, 5, 2001)
    u_grid_lo = G_slider_m_lo.val * (u_grid + G_slider_c_lo.val)
    u_grid_up = G_slider_m_up.val * (u_grid - G_slider_c_up.val)
    (G_bound_lo,) = axs[1].plot(u_grid, u_grid_lo, label="bound lo", color="C1")
    (G_bound_up,) = axs[1].plot(u_grid, u_grid_up, label="bound up", color="C3")
    axs[1].fill_between(u_grid, u_grid_lo, u_grid_up, color="gray", alpha=0.3, label="backlash zone")

    # Annotate
    axs[0].set_xlabel("time [s]")
    axs[0].set_ylabel("output (with and without backlash)")
    axs[0].set_ylim([-6, 6])
    axs[0].legend(
        bbox_to_anchor=(0.2, 1.02, 0.6, 0.102),
        loc="lower left",
        ncol=2,
        mode="expand",
        borderaxespad=0.0,
        frameon=False,
    )
    axs[1].axis("equal")
    axs[1].legend(
        bbox_to_anchor=(0.1, 1.02, 0.8, 0.102),
        loc="lower left",
        ncol=3,
        mode="expand",
        borderaxespad=0.0,
        frameon=False,
    )

    # Backlash model
    G_bl_model = BacklashModel(G_slider_m_lo.val, G_slider_m_up.val, G_slider_c_lo.val, G_slider_c_up.val)

    plt.show()
