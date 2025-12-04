import numpy as np


Matrix_Ktu = (
    (0.0, 1.26, 1.26, 0.435, 0.76, 0.55, 0.55, 0.35, 0.435, 0.35, 0.0 , 0.35, 0.4, 0.23, 0.09),
    (0.0, 1.525, 1.525, 0.53, 1.0, 0.595, 0.595, 0.35, 0.53, 0.35, 0.0, 0.385, 0.365, 0.235, 0.09),
    (0.0, 1.59, 1.545, 0.98, 1.07, 0.947, 0.93, 0.77, 0.665, 0.57, 0.185, 0.49, 0.45, 0.31, 0.135),
    (0.0, 1.65, 1.555, 1.275, 1.1, 1.122, 1.106, 1.045, 0.68, 0.62, 0.8, 0.515, 0.477, 0.325, 0.14)
)
def compute_K_tu(A_av, Material_Number):
    X1 = Matrix_Ktu[0][Material_Number]
    Y1 = Matrix_Ktu[1][Material_Number]
    Y2 = Matrix_Ktu[2][Material_Number]
    Y3 = Matrix_Ktu[3][Material_Number]

    D1 = X1/2 - 0.7
    D2 = X1/2 + 0.7

    A_av = np.asarray(A_av)

    cond = A_av < X1

    part1 = (Y1 / X1) * A_av

    part2 = (((Y1 * (A_av - D2)) / D1) * ((A_av - 1.4) / (2*D1))) \
          - (((Y2 * (A_av - X1)) / D1) * ((A_av - 1.4) / D1))   \
          + (((Y3 * (A_av - D2)) / (2*D1)) * ((A_av - X1) / D1))

    return np.where(cond, part1, part2)


def compute_K_ty(A_av):
    K_ty = compute_K_tu(A_av, 3)
    return K_ty

Matrix_Kt = (
    (0.0, 2.91, 2.5, 2.91, 2.2, 1.7, 2.2, 1.0),
    (0.0, 0.922, 0.9, 0.922, 0.877, 0.877, 0.65, 0.675),
    (0.0, 0.896, 0.826, 0.842, 0.755, 0.68, 0.37, 0.503),
    (0.0, 0.755, 0.73, 0.5, 0.683, 0.525, 0.115, 0.339)
)
def compute_K_t(W_D, Material_Number):
    X1 = Matrix_Kt[0][Material_Number]
    Y1 = Matrix_Kt[1][Material_Number]
    Y2 = Matrix_Kt[2][Material_Number]
    Y3 = Matrix_Kt[3][Material_Number]

    D1 = X1/2 - 2.5
    D2 = X1/2 + 2.5

    W_D = np.asarray(W_D)

    cond = W_D < X1

    part1 = ( (Y1 - 1) / (X1 - 1) ) * (W_D - 1) + 1

    part2 = (((Y1 * (W_D - D2)) / D1) * ((W_D - 5.0) / (2*D1))) \
          - (((Y2 * (W_D - X1)) / D1) * ((W_D - 5.0) / D1))     \
          + (((Y3 * (W_D - D2)) / (2*D1)) * ((W_D - X1) / D1))

    return np.where(cond, part1, part2)
