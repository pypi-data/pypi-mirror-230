import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import minimize
from typing import Iterable, List, Tuple, Literal
from collections import namedtuple


def mse(a: np.ndarray, b: np.ndarray) -> float:
    return ((a-b)**2).sum()


def quantiles_and_probabilities(values: np.ndarray) -> Tuple[np.ndarray]:

    quantiles = np.sort(values)
    ranks = np.arange(1, quantiles.size+1)
    probs = (ranks - 0.28)/(quantiles.size + 0.28)

    return quantiles, probs


def poisson(P: np.ndarray, loc: float, scale: float, shape: float):
    if shape == 0:
        return loc - scale*np.log(-np.log(P))
    else:
        return loc - scale/shape * (1-(-np.log(P))**-shape)


def default_xi_bounds(quantiles,
                      lower_xi=-float("inf"),
                      upper_xi=float("inf")) -> List[Tuple[float, float]]:
    max = quantiles.max()
    min = quantiles.min()
    return [(min, max),
            (0.0, 2*(max-min)),
            (lower_xi, upper_xi)]


def fit_annual_maxima(
    values: np.ndarray,
    kind: Literal["gumbel", "weibull", "frechet"] = None,
    **optkwargs
):

    if (
        kind == "gumbel" or
        "bounds" in optkwargs and tuple(optkwargs["bounds"]) == (.0, .0)
    ):
        return *fit_gumbel(values), 0
    if "bounds" not in optkwargs:
        optkwargs["bounds"] = default_xi_bounds(
            values,
            lower_xi=0 if kind == "frechet" else -float("inf"),
            upper_xi=-0 if kind == "weibull" else float("inf")
        )
    if kind == "frechet":
        assert tuple(optkwargs["bounds"][2]) >= (0, 0)
    elif kind == "weibull":
        assert tuple(optkwargs["bounds"][2]) <= (0, 0)
    if "x0" not in optkwargs:
        optkwargs["x0"] = *fit_gumbel(values), 0

    return fit_poisson(values, **optkwargs)


def fit_poisson(quantiles,
                probs: np.ndarray = None,
                error_func=mse,
                **optkwargs):

    if probs is None:
        quantiles, probs = quantiles_and_probabilities(quantiles)
    solution = minimize(
        lambda params: error_func(poisson(probs, *params), quantiles),
        **optkwargs
    )

    return solution.x, solution.fun


def fit_frechet(values,
                probs: np.ndarray = None,
                upper_xi=float("inf"),
                lower_xi=0, **optkwargs):

    if "bounds" not in optkwargs:
        optkwargs["bounds"] = default_xi_bounds(
            values,
            lower_xi=lower_xi,
            upper_xi=upper_xi
        )
    assert lower_xi >= 0 and (upper_xi is None or upper_xi > 0)
    if "x0" not in optkwargs:
        optkwargs["x0"] = *fit_gumbel(values)[0], 0

    return fit_poisson(values, probs, **optkwargs)


def fit_gumbel(values: np.ndarray, probs=None, error_func=mse):

    scale = np.sqrt(6)*values.std()/np.pi
    loc = values.mean() - 0.577*scale

    if probs is None:
        _, probs = quantiles_and_probabilities(values)
    error = error_func(poisson(probs, loc, scale, 0), values)

    return (loc, scale), error


def fit_weibull(values,
                probs: np.ndarray = None,
                lower_xi=-float("inf"),
                upper_xi=-0, **optkwargs):

    if "bounds" not in optkwargs:
        optkwargs["bounds"] = default_xi_bounds(
            values,
            lower_xi=lower_xi,
            upper_xi=upper_xi
        )
    if "x0" not in optkwargs:
        optkwargs["x0"] = *fit_gumbel(values)[0], 0
    assert upper_xi <= 0 and (lower_xi is None or lower_xi < 0)

    return fit_poisson(values, probs, **optkwargs)


_Fit = namedtuple('Fit', 'name params error')


class YearlyMaxima:

    def __init__(self,
                 values: Iterable,
                 error_func=mse) -> None:
        quantiles, probs = quantiles_and_probabilities(
            np.array(values)
        )

        # Gumbel
        gumbel_params, gumbel_error = fit_gumbel(values)
        self.gumbel = _Fit(name="Gumbel", params=gumbel_params, error=gumbel_error)

        bounds = default_xi_bounds(quantiles, lower_xi=0)
        x0 = *gumbel_params, 0
        # Fréchet
        params, error = fit_frechet(
            quantiles,
            probs,
            x0=x0,
            bounds=bounds,
            error_func=error_func
        )
        self.frechet = _Fit(name="Fréchet", params=params, error=error)
        # Weibull
        bounds[2] = (-float("inf"), -0)
        params, error = fit_poisson(
            quantiles,
            probs,
            x0=x0,
            bounds=bounds,
            error_func=error_func
        )
        self.weibull = _Fit(name="Weibull", params=params, error=error)

    def __repr__(self) -> str:
        s = f"Best fit: {self.best}"
        for name, object in self.__dict__.items():
            params = [f"\n\t\t\t{p}" for p in object.params]
            s = (
                f"{s}\n\t{name.capitalize()}:\n\t\tloss: {object.error}"
                f"\n\t\tparams:{''.join(params)}"
            )
        return s

    @property
    def best(self):
        errors = {name: error for name, _, error in self.__dict__.values()}
        return min(errors, key=errors.get)

    @property
    def params(self):
        return self.best.params

    def predict(self, array, kind: Literal["return period", "probability", "reduced gummbel"]):

        if kind == "return period":
            P = 1 - 1/array
        elif kind == "reduced gumbel":
            P = np.exp(-np.exp(-array))
        elif kind != "probability":
            raise ValueError(f"{kind} is not known")

        return poisson(array, poisson(P, self.params))


_xaxis_transformation = {
    "gumbel": lambda p: -np.log(-np.log(p)),
    "probability": lambda p: p,
    "return period": lambda p: 1/(1-p)
}

_xaxis_label = {
    "gumbel": "Variable réduite de Gumbel "
              rf"$u=-\log\left(-\log\left(1-\frac{{1}}{{T}}\right)\right)$",
    "probability": "Probabilité de non-dépassement",
    "return period": "Période de retour (années)"
}


def analyse(annual_maxima,
            xaxis: Literal[
                "probability",
                "return period",
                "gumbel"
            ] = "gumbel",
            show=True, tight_layout=True,
            style="ggplot", font="monospace",
            _base_functions=True, **figkwargs):

    with plt.style.context(style):
        with plt.style.context({'font.family': font}):
            fig, ax = plt.subplots(**figkwargs)

            C, P = quantiles_and_probabilities(annual_maxima)
            if _base_functions:
                xg = 0
                (lg, sg), _ = fit_gumbel(annual_maxima)
                (lf, sf, xf), _ = fit_frechet(annual_maxima)
                (lw, sw, xw), _ = fit_weibull(annual_maxima)
            else:
                (lg, sg), _ = fit_annual_maxima(annual_maxima, kind="gumbel")
                (lf, sf, xf), _ = fit_annual_maxima(annual_maxima, kind="frechet")
                (lw, sw, xw), _ = fit_annual_maxima(annual_maxima, kind="weibull")

            _P = np.linspace(P.min(), P.max(), num=1000)
            x, _x = map(_xaxis_transformation[xaxis], (P, _P))

            ax.plot(x, C, 'ok', label="Empirique", ms=2)
            ax.plot(x, lg-sg*np.log(-np.log(P)), label=rf"Gumbel  $\mu={lg:.1f}$ $\sigma={sg:.1f}$ $\xi={xg:.2f}$")
            ax.plot(_x, poisson(_P, lf, sf, xf), label=rf"Fréchet $\mu={lf:.1f}$ $\sigma={sf:.1f}$ $\xi={xf:+.2f}$")
            ax.plot(_x, poisson(_P, lw, sw, xw), label=rf"Weibull $\mu={lw:.1f}$ $\sigma={sw:.1f}$ $\xi={xw:+.2f}$")

            if xaxis == "probability":
                xt = ax.get_xticks()
                ax.set_xticks(xt)
                ax.set_xticklabels([f"{t:.0%}" for t in xt])
                ax.set_xlim(0, 1)
            ax.set_xlabel(_xaxis_label[xaxis])
            ax.set_ylabel(f"Quantiles des maxima\nannuels du débit (m$^3$/s)")
            ax.legend()
            if tight_layout:
                plt.tight_layout()

    return plt.show() if show else fig, ax


if __name__ == "__main__":
    rainfall = np.array((
        55.6, 72.8, 58.2, 127.0, 60.6, 75.6, 32.6, 46.5, 47.5, 20.8, 42.0,
        40.5, 40.0, 58.2, 48.6, 44.0, 74.4, 37.5, 14.8, 72.6, 16.0, 107.0,
        65.4, 37.0, 84.6, 59.4, 18.1, 54.6, 99.9, 11.1, 60.3, 37.3, 36.5,
        42.1, 94.3, 6.92, 14.3, 94.2, 56.7, 67.0, 66.3, 143.0, 86.2, 213.0,
        53.4, 14.8, 119.0, 390.0, 19.7, 16.3, 10.9, 9.55
    ))
    analyse(rainfall, _base_functions=True)
    print(YearlyMaxima(rainfall))
