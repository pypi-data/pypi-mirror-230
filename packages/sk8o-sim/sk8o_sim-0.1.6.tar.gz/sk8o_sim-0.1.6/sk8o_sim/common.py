from dataclasses import dataclass

import numpy as np


def randomize_parameter(
    mean, param_noise_percent_std: float, affine: float = 0
) -> float:
    """A utility function to generate "noisy" physical paramers, used in domain randomization.

    The resulting value will be sampled from a normal distribution N(mean, (mean + affine) * param_noise_percent_std / 100).



    Parameters
    ----------
    mean : float
        The mean of the value of the parameter.
    param_noise_percent_std : float
        mean*param_noise_percent_std is the % std deviation from the mean (if affine is zero).
    affine : float, optional
        Since the std is proportional to the mean, this is a way to make the parameter randomized even if mean is zero. This option is used when randomizing the position of COM of bodies in MuJoCo, by default 0

    Returns
    -------
    float
        The randomized parameter.
    """
    if isinstance(mean, np.ndarray):
        shape = mean.shape
    else:
        shape = [1]
    ret = (
        np.random.randn(*shape) * (mean + affine) * param_noise_percent_std / 100 + mean
    )
    if ret.shape == (1,):
        return ret[0]
    else:
        return ret
