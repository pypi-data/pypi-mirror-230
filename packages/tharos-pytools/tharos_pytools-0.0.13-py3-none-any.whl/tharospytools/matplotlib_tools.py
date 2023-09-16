'Tools to assist with graphs creation'
import matplotlib as mpl
from matplotlib.colors import rgb2hex, hex2color
from mycolorpy import colorlist


def get_palette(number_of_colors: int, cmap_name: str = 'viridis', as_hex: bool = False) -> list:
    """Returns a number_of_colors-sized palette, as a list,
    that one can access with colors[i].

    Args:
        number_of_colors (int): number of colors needed
        cmap_name (str, optionnal) : name of the matplotlib colormap. Defaults to viridis.
        hex (bool) : specifies if colors shall be returned by rgb values (False, default) or hex (True)

    Returns:
        list: palette of colors
    """
    try:
        colormap = mpl.colormaps[cmap_name].resampled(number_of_colors)
    except Exception as exc:
        raise ValueError(
            f"The colormap {cmap_name} is not a valid colormap") from exc    
    return [
        rgb2hex(colormap(int(x/number_of_colors))) if as_hex
        else colormap(int(x/number_of_colors)) for x in range(number_of_colors)
    ]


def get_palette_from_list(data_array: list, cmap_name: str = 'viridis', as_hex: bool = False) -> list:
    """Returns a number_of_colors-sized palette, as a list,
    that one can access with colors[i].

    Args:
        data_array (list): array of data to be normalized
        cmap_name (str, optional): matplotlib cmap to use. Defaults to 'viridis'.
        as_hex (bool, optional): if value shoud be hex or rgba. Defaults to False.

    Returns:
        list: list of colors, one per value
    """
    colormap: list = colorlist.gen_color_normalized(
        cmap=cmap_name, data_arr=[i/max(data_array) for i in data_array])
    return [hex2color(color) if as_hex else color for color in colormap]
