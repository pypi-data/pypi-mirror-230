import math


def test_adjacent_points(points, row_idx, point_idx, num) -> bool:
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        r, c = row_idx + dr, point_idx + dc
        if is_valid_coord(r, c, len(points), len(points[0])) and (points[r][c] == num):
            return True
    return False


def is_valid_coord(row_idx, col_idx, rows, cols) -> bool:
    return 0 <= row_idx < rows and 0 <= col_idx < cols


def calc_hum(temp, dew):
    return round(math.exp(17.625 * dew / (243.04 + dew)) / math.exp(17.625 * temp / (243.04 + temp)), 2)
