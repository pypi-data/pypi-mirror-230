# Counts the unique colors in an image and returns a DataFrame with color counts and optional color coordinates.

## Tested against Windows 10 / Python 3.11 / Anaconda

### pip install farbencounter


```python

# Example usage
from farbencounter import count_colors
pic = r"https://www.python.org/static/img/python-logo.png"
img = open_image_in_cv(pic, channels_in_output=3)
df, colorcoords = count_colors(img=img, sort=True, get_color_coords=True)

# df: DataFrame containing color information and counts
# colorcoords: Dictionary containing color coordinates


# df
# Out[3]:
#             a    r    g    b      c
# 0           0    0    0    0    456
# 1          26    0    0   26      2
# 2        3612    0   14   28      2
# 3        3619    0   14   35      1
# 4        3870    0   15   30      9
# ..        ...  ...  ...  ...    ...
# 849  16776316  255  252  124      2
# 850  16776431  255  252  239      1
# 851  16776432  255  252  240      1
# 852  16776830  255  254  126      1
# 853  16777215  255  255  255  18608
# [854 rows x 5 columns]


# colorcoords
# ....
# (44, 99, 147): array([[48, 32]]),
#  (45,
#   45,
#   45): array([[230,  28],
#         [170,  32],
#         [189,  52]], dtype=int64),
#  (45, 86, 119): array([[12, 25]]),
#  (45, 94, 133): array([[ 8, 30]]),
#  (45, 96, 139): array([[20, 43]]),
#  (45, 101, 150): array([[45, 36]]),
#  (46, 35, 12): array([[36, 53]]),
#  (46,
#   46,
#   46): array([[239,  14],
#         [143,  23],
#         [143,  28],
#         [170,  34],
#         [185,  34],
#         [ 84,  45],
#         [ 90,  48],
#         [118,  48],
#         [119,  48],
#         [201,  48],
#         [194,  52]], dtype=int64)
# ....


```