import itertools
import warnings

import pyxu.abc as pxa
import pyxu.info.ptype as pxt
import pyxu.info.warning as pxuw
import pyxu.operator.func as pxof
import pyxu.runtime as pxrt
import pyxu.util as pxu

__all__ = [
    "GradientDescent",
]


class GradientDescent(pxa.Solver):
    r"""
    Gradient Descent (GD) solver.

    GradientDescent solves minimization problems of the form

    .. math::

       {\min_{\mathbf{x}\in\mathbb{R}^N} \;\mathcal{F}(\mathbf{x}),

    where:

    * :math:`\mathcal{F}:\mathbb{R}^N\rightarrow \mathbb{R}` is *convex* and *differentiable*, with
      :math:`\beta`-*Lipschitz continuous* gradient, for some :math:`\beta\in[0,+\infty[`.

    **Remark 1:**
    The convergence is guaranteed for step sizes :math:`\tau\leq 1/\beta`.

    **Remark 2:**
    GradientDescent achieves the following (optimal) *convergence rate* with the implemented acceleration scheme
    from Nesterov [Nesterov]_.

    .. math::

       \mathcal{F}(\mathbf{x}_{k}) - \mathcal{F}^{*} \leq O\bigl(\frac{\Vert x_{0} - x^{*}\Vert}^{2}_{2}{\tau k^2}\bigr)


    **Remark 3:**
    The relative norm change of the primal variable is used as the default stopping criterion.
    By default, the algorithm stops when the norm of the difference between two consecutive GradientDescent
    iterates :math:`\{\mathbf{x}_n\}_{n\in\mathbb{N}}` is smaller than 1e-4.
    Different stopping criteria can be used. (see :py:mod:`~pyxu.opt.solver.stop`.)

    ``GradientDescent.fit()`` **Parameterization**

    x0: pxt.NDArray
        (..., N) initial point(s).
    tau: pxt.Real
        Gradient step size.
        Defaults to :math:`1 / \beta` if unspecified.
    acceleration: bool
        If True (default), then use Nesterov acceleration scheme.

    References
    ----------
    .. [1] [Nesterov] Nesterov, Yurii Evgen'evich.
           "A method of solving a convex programming problem with convergence rate O\bigl(k^2\bigr)."
           Doklady Akademii Nauk. Vol. 269. No. 3. Russian Academy of Sciences, 1983.
    """

    def __init__(
        self,
        f: pxa.DiffFunc = None,
        **kwargs,
    ):
        kwargs.update(
            log_var=kwargs.get("log_var", ("x",)),
        )
        super().__init__(**kwargs)

        if f is None:
            msg = " ".join(
                [
                    "Cannot minimize always-0 functional.",
                    "Parameter f must be specified.",
                ]
            )
            raise ValueError(msg)
        else:
            self._f = f

    @pxrt.enforce_precision(i=("x0", "tau"))
    def m_init(
        self,
        x0: pxt.NDArray,
        tau: pxt.Real = None,
        acceleration: bool = True,
    ):
        mst = self._mstate  # shorthand
        mst["x"] = mst["x_prev"] = x0

        if tau is None:
            try:
                mst["tau"] = pxrt.coerce(1 / self._f.estimate_diff_lipschitz(method="svd", tol=0.1))
            except ZeroDivisionError as exc:
                # _f is constant-valued: \tau is a free parameter.
                mst["tau"] = 1
                msg = "\n".join(
                    [
                        rf"The gradient step size \tau is auto-set to {mst['tau']}.",
                        r"Choosing \tau manually may lead to faster convergence.",
                    ]
                )
                warnings.warn(msg, pxuw.AutoInferenceWarning)
        else:
            try:
                assert tau > 0
                mst["tau"] = tau
            except:
                raise ValueError(f"tau must be positive, got {tau}.")

        if acceleration:
            mst["a"] = (pxrt.coerce(k / (k + 3)) for k in itertools.count(start=0))
        else:
            mst["a"] = itertools.repeat(pxrt.coerce(0))

    def m_step(self):
        mst = self._mstate  # shorthand
        a = next(mst["a"])

        # In-place implementation of -----------------
        #   y = (1 + a) * mst["x"] - a * mst["x_prev"]
        y = mst["x"] - mst["x_prev"]
        y *= a
        y += mst["x"]
        # --------------------------------------------

        # In-place implementation of -----------------
        #   z = y - mst["tau"] * self._f.grad(y)
        z = pxu.copy_if_unsafe(self._f.grad(y))
        z *= -mst["tau"]
        z += y
        # --------------------------------------------

        mst["x_prev"], mst["x"] = mst["x"], z

    def default_stop_crit(self) -> pxa.StoppingCriterion:
        from pyxu.opt.stop import RelError

        stop_crit = RelError(
            eps=1e-4,
            var="x",
            f=None,
            norm=2,
            satisfy_all=True,
        )
        return stop_crit

    def objective_func(self) -> pxt.NDArray:
        func = lambda x: self._f.apply(x)

        y = func(self._mstate["x"])
        return y

    def solution(self) -> pxt.NDArray:
        """
        Returns
        -------
        x: pxt.NDArray
            (..., N) solution.
        """
        data, _ = self.stats()
        return data.get("x")
