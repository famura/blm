import numpy as np
import pytest

import blm
from tests.conftest import needs_pyplot


@pytest.mark.parametrize("model_param", [dict(m_lo=1.1, m_up=0.9, c_lo=0.1, c_up=0.2)])
@pytest.mark.parametrize("x_init", [None, np.array(0.0)])
def test_constructor(model_param: dict, x_init: np.ndarray):
    bl_model = blm.BacklashModel(**model_param, x_init=x_init)
    print(bl_model)

    assert isinstance(bl_model, blm.BacklashModel)
    assert bl_model.m_lo == model_param["m_lo"]
    assert bl_model.m_up == model_param["m_up"]
    assert bl_model.c_lo == model_param["c_lo"]
    assert bl_model.c_up == model_param["c_up"]

    if x_init is not None:
        assert isinstance(bl_model.z_lo, np.ndarray)
        assert isinstance(bl_model.z_up, np.ndarray)


@pytest.mark.parametrize(
    "ctor_param",
    [
        dict(m_lo="invalid", m_up=1.0, c_lo=0.01, c_up=0.01, x_init=0),
        dict(m_lo=1.0, m_up="invalid", c_lo=0.01, c_up=0.01, x_init=0),
        dict(m_lo=1.0, m_up=1.0, c_lo="invalid", c_up=0.01, x_init=0),
        dict(m_lo=1.0, m_up=1.0, c_lo=0.01, c_up="invalid", x_init=0),
        dict(m_lo=1.0, m_up=1.0, c_lo=0.01, c_up=0.01, x_init="invalid"),
    ],
)
def test_nonfloat_ctor_params(ctor_param: dict):
    with pytest.raises(ValueError):
        blm.BacklashModel(**ctor_param)


@pytest.mark.parametrize(
    "ctor_param",
    [
        dict(m_lo=0, m_up=1.0, c_lo=0.01, c_up=0.01, x_init=0),
        dict(m_lo=1.0, m_up=0, c_lo=0.01, c_up=0.01, x_init=0),
        dict(m_lo=1.0, m_up=1.0, c_lo=-1, c_up=0.01, x_init=0),
        dict(m_lo=1.0, m_up=1.0, c_lo=0.01, c_up=-1, x_init=0),
    ],
)
def test_invalid_ctor_params(ctor_param: dict):
    with pytest.raises(ValueError):
        blm.BacklashModel(**ctor_param)


@pytest.mark.parametrize("plot", [pytest.param(True, marks=[needs_pyplot, pytest.mark.visual]), False])
@pytest.mark.parametrize("model_param", [dict(m_lo=2.0, m_up=1.9, c_lo=2.5, c_up=2.7)])
@pytest.mark.parametrize("apply_u_bl", [False])
def test_all(model_param: dict, apply_u_bl: bool, plot: bool):
    # Setup model
    dt = 0.002
    t_end = 4.0
    t_grid = np.linspace(0, t_end, int(t_end / dt))
    amp = 5.0
    freq = 1.0
    bl_model = blm.BacklashModel(**model_param, x_init=np.array(0.0))

    # Generate data
    x_hist = []
    x_bl_hist = []
    for t in t_grid:
        x = amp * (1 - t / t_end) * np.sin(2 * np.pi * freq * t)
        x_hist.append(x.copy())
        x_bl = bl_model(x)
        x_bl_hist.append(x_bl.copy())

    x_hist = np.expand_dims(np.stack(x_hist), axis=1)
    x_bl_hist = np.stack(x_bl_hist)
    if plot:
        from matplotlib import pyplot as plt

        plt.figure(figsize=(16, 8))
        plt.plot(x_hist)
        plt.plot(x_bl_hist)
        plt.grid()

        u_grid = np.linspace(-5, 5, 10001)
        u_grid_lo = model_param["m_lo"] * (u_grid + model_param["c_lo"])
        u_grid_up = model_param["m_up"] * (u_grid - model_param["c_up"])

        plt.figure(figsize=(8, 8))
        plt.plot(u_grid, u_grid_lo, label="lo")
        plt.plot(u_grid, u_grid_up, label="up")
        plt.fill_between(u_grid, u_grid_lo, u_grid_up, color="gray", alpha=0.3, label="backlash zone")
        plt.gca().axis("equal")
        plt.grid()
        plt.legend()
        plt.show()

    # Fit the model parameters
    bl_model.fit(u=x_hist[1:], x=x_bl_hist[1:], x_prev=x_bl_hist[:-1])

    # Catch invalid shapes
    with pytest.raises(ValueError):
        bl_model.fit(u=x_hist[2:], x=x_bl_hist[1:], x_prev=x_bl_hist[:-1])
