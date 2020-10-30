import numpy as np

_HYPER_PARAMS = {
    0: {
        "adam_beta_1": np.power(10., -1.891),
        "adam_beta_2": np.power(10., -0.628),
        "adam_eps": np.power(10., -7.962),
        "adam_wd": np.power(10., -3.985),
        "max_lr": np.power(10., -3.352),
        "cycle_peak": 0.32,
    },
    1: {
        "adam_beta_1": np.power(10., -2.279),
        "adam_beta_2": np.power(10., -1.179),
        "adam_eps": np.power(10., -8.279),
        "adam_wd": np.power(10., -3.921),
        "max_lr": np.power(10., -3.33),
        "cycle_peak": 0.38,
    },
    2: {
        "adam_beta_1": np.power(10., -2.252),
        "adam_beta_2": np.power(10., -1.079),
        "adam_eps": np.power(10., -7.949),
        "adam_wd": np.power(10., -3.923),
        "max_lr": np.power(10., -3.316),
        "cycle_peak": 0.42,
    },
    3: {
        "adam_beta_1": np.power(10., -2.152),
        "adam_beta_2": np.power(10., -1.158),
        "adam_eps": np.power(10., -8.025),
        "adam_wd": np.power(10., -4.065),
        "max_lr": np.power(10., -3.326),
        "cycle_peak": 0.36,
    },
    4: {
        "adam_beta_1": np.power(10., -2.294),
        "adam_beta_2": np.power(10., -1.112),
        "adam_eps": np.power(10., -8.357),
        "adam_wd": np.power(10., -3.936),
        "max_lr": np.power(10., -3.357),
        "cycle_peak": 0.35,
    },
    5: {
        "adam_beta_1": np.power(10., -2.081),
        "adam_beta_2": np.power(10., -0.759),
        "adam_eps": np.power(10., -7.939),
        "adam_wd": np.power(10., -3.91),
        "max_lr": np.power(10., -3.372),
        "cycle_peak": 0.37,
    },
    6: {
        "adam_beta_1": np.power(10., -2.068),
        "adam_beta_2": np.power(10., -1.125),
        "adam_eps": np.power(10., -8.13),
        "adam_wd": np.power(10., -4.022),
        "max_lr": np.power(10., -3.22),
        "cycle_peak": 0.4,
    },
    7: {
        "adam_beta_1": np.power(10., -1.709),
        "adam_beta_2": np.power(10., -1.793),
        "adam_eps": np.power(10., -7.909),
        "adam_wd": np.power(10., -4.086),
        "max_lr": np.power(10., -3.223),
        "cycle_peak": 0.32,
    },
    8: {
        "adam_beta_1": np.power(10., -1.906),
        "adam_beta_2": np.power(10., -0.865),
        "adam_eps": np.power(10., -8.285),
        "adam_wd": np.power(10., -4.044),
        "max_lr": np.power(10., -3.31),
        "cycle_peak": 0.38,
    },
    9: {
        "adam_beta_1": np.power(10., -2.142),
        "adam_beta_2": np.power(10., -0.718),
        "adam_eps": np.power(10., -8.066),
        "adam_wd": np.power(10., -3.874),
        "max_lr": np.power(10., -3.334),
        "cycle_peak": 0.44,
    },
    10: {
        "adam_beta_1": np.power(10., -1.6402),
        "adam_beta_2": np.power(10., -0.9021),
        "adam_eps": np.power(10., -8.4447),
        "adam_wd": np.power(10., -4.171),
        "max_lr": np.power(10., -3.4708),
        "cycle_peak": 0.293,
    },
    11: {
        "adam_beta_1": np.power(10., -1.091),
        "adam_beta_2": np.power(10., -0.88),
        "adam_eps": np.power(10., -8.605),
        "adam_wd": np.power(10., -3.792),
        "max_lr": np.power(10., -3.564),
        "cycle_peak": 0.23,
    },
    12: {
        "adam_beta_1": np.power(10., -0.39),
        "adam_beta_2": np.power(10., -1.253),
        "adam_eps": np.power(10., -8.885),
        "adam_wd": np.power(10., -5.256),
        "max_lr": np.power(10., -3.944),
        "cycle_peak": 0.15,
    },
    13: {
        "adam_beta_1": np.power(10., -0.603),
        "adam_beta_2": np.power(10., -0.588),
        "adam_eps": np.power(10., -9.036),
        "adam_wd": np.power(10., -5.207),
        "max_lr": np.power(10., -3.569),
        "cycle_peak": 0.22,
    },
    14: {
        "adam_beta_1": np.power(10., -1.902),
        "adam_beta_2": np.power(10., -0.554),
        "adam_eps": np.power(10., -8.439),
        "adam_wd": np.power(10., -4.137),
        "max_lr": np.power(10., -3.617),
        "cycle_peak": 0.24,
    },
    15: {
        "adam_beta_1": np.power(10., -0.853),
        "adam_beta_2": np.power(10., -0.57),
        "adam_eps": np.power(10., -8.928),
        "adam_wd": np.power(10., -4.647),
        "max_lr": np.power(10., -3.585),
        "cycle_peak": 0.22,
    },
    16: {
        "adam_beta_1": np.power(10., -0.854),
        "adam_beta_2": np.power(10., -0.787),
        "adam_eps": np.power(10., -8.971),
        "adam_wd": np.power(10., -4.379),
        "max_lr": np.power(10., -3.611),
        "cycle_peak": 0.21,
    },
    17: {
        "adam_beta_1": np.power(10., -1.969),
        "adam_beta_2": np.power(10., -0.895),
        "adam_eps": np.power(10., -8.622),
        "adam_wd": np.power(10., -4.043),
        "max_lr": np.power(10., -3.574),
        "cycle_peak": 0.23,
    },
    18: {
        "adam_beta_1": np.power(10., -1.244),
        "adam_beta_2": np.power(10., -0.736),
        "adam_eps": np.power(10., -8.698),
        "adam_wd": np.power(10., -4.397),
        "max_lr": np.power(10., -3.604),
        "cycle_peak": 0.2,
    },
    19: {
        "adam_beta_1": np.power(10., -1.617),
        "adam_beta_2": np.power(10., -0.608),
        "adam_eps": np.power(10., -8.876),
        "adam_wd": np.power(10., -4.475),
        "max_lr": np.power(10., -3.588),
        "cycle_peak": 0.2,
    },
    20: {
        "adam_beta_1": np.power(10., -1.507),
        "adam_beta_2": np.power(10., -0.755),
        "adam_eps": np.power(10., -8.933),
        "adam_wd": np.power(10., -3.953),
        "max_lr": np.power(10., -3.619),
        "cycle_peak": 0.22,
    },
}

def get_hyper_params(grid_id):
    return _HYPER_PARAMS[grid_id]
