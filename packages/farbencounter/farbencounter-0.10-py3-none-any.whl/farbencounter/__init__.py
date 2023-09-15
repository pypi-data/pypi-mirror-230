import numexpr  # Import the 'numexpr' library for efficient numerical expression evaluation (up to 10x faster than numpy).
import numpy as np
import pandas as pd
from a_cv_imwrite_imread_plus import open_image_in_cv


def count_colors(img, sort=True, get_color_coords=True):
    """
    Count the unique colors in an image and return a DataFrame with color counts and optional color coordinates.

    Parameters:
        img (numpy.ndarray): Input image as a NumPy array with shape (height, width, 3).
        sort (bool, optional): Whether to sort the resulting DataFrame by color count. Default is True.
        get_color_coords (bool, optional): Whether to retrieve color coordinates. Default is True.

    Returns:
        pandas.DataFrame: A DataFrame containing color information with columns 'r', 'g', 'b', and 'c' (count).
        dict: A dictionary containing color coordinates if 'get_color_coords' is True.
    """

    # Open the image and ensure it has 3 color channels.
    img = open_image_in_cv(img, channels_in_output=3)

    # Extract the red, green, and blue color channels from the image.
    r, g, b = (
        img[..., 2],
        img[..., 1],
        img[..., 0],
    )

    # Use 'numexpr' to efficiently calculate a unique numerical representation for each color.
    absnum = numexpr.evaluate(
        "(r << 16) + (g << 8) + b",
        global_dict={},
        local_dict={"r": r, "g": g, "b": b},
    )

    # Find unique values and their counts in the 'absnum' array.
    npunique = np.unique(absnum, return_counts=True)

    # Merge DataFrames to combine color information and color counts.
    df = pd.merge(
        pd.DataFrame(
            {
                "r": r.ravel(),
                "g": g.ravel(),
                "b": b.ravel(),
                "a": absnum.ravel(),
            }
        )
        .drop_duplicates()  # Remove duplicate rows based on the unique numerical representation 'a'.
        .reset_index(drop=True)  # Reset the DataFrame index after dropping duplicates.
        .set_index("a"),  # Set the 'a' column as the index of the DataFrame.
        pd.DataFrame({"a": npunique[0], "c": npunique[1]}).set_index("a"),
        left_index=True,  # Merge DataFrames using the index of the left DataFrame ('a' column).
        right_index=True,  # Merge DataFrames using the index of the right DataFrame ('a' column).
        sort=sort,  # Sort the resulting DataFrame by color count if 'sort' is True.
    ).reset_index(drop=False)

    allresults = {}

    if get_color_coords:
        bb = np.ascontiguousarray(absnum.flatten())
        aa = np.ascontiguousarray(df.a.__array__())
        aa2 = [tuple(map(int, [r, g, b])) for r, g, b in zip(df.r, df.g, df.b)]
        a = np.lib.stride_tricks.as_strided(aa, (len(aa), len(bb)), (aa.itemsize, 0))
        boollist = numexpr.evaluate(
            "a==bb", global_dict={}, local_dict={"a": a, "bb": bb}
        )
        for ini, color in enumerate(aa2):
            try:
                allresults[color] = (
                    np.dstack(
                        np.divmod(np.where(boollist[ini])[0], absnum.shape[1])
                    ).squeeze()
                )[:, [1, 0]]
            except Exception:
                ga = (
                    np.dstack(
                        np.divmod(np.where(boollist[ini])[0], absnum.shape[1])
                    ).squeeze()
                ).tolist()
                allresults[color] = np.array([[ga[1], ga[0]]])

    return df, allresults

