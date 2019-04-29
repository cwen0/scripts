#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import numpy as np


def analysis(values):
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    lo = q1 - 1.5 * (q3 - q1)
    hi = q3 + 1.5 * (q3 - q1)

    r_values = []

    for v in values:
        if lo <= v and v <= hi:
            r_values.append(v)

    return {
        "min": np.min(r_values),
        "max": np.max(r_values),
        "mean": np.mean(r_values)
    }


def main():
    values = []
    with open('tps.all') as fp:
        for line in fp:
            values.append(float(line))

    a_data = analysis(values)
    print(a_data)
    print(a_data["max"]/a_data["mean"] - 1)
    print(1 - a_data["min"]/a_data["mean"])


if __name__ == "__main__":
    main()
