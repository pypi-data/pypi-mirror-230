# Package for appstatpy for the applied statistics course at the University of
Copenhagen 

Below is documentations for all relevant functions in the ExternalFunctions
subpackage. Remember that to load all of these functions load the library as 
$from appstatpy.ExternalFunctions import *


## format\_value(value, decimals)
    Formats a value based on its type.

    This function takes a value and a 'decimals' parameter and formats the value
    according to its type. If the value is a float or an integer, it will be
    formatted with the specified number of decimals. Otherwise, the value will
    be returned as-is.

    ### Args:
        value (float, int, or any): The value to be formatted.
        decimals (int): The number of decimals to be used when formatting
            float or integer values. Ignored for other types.

    ### Returns:
        str: The formatted value as a string.

    ### Examples:
        >>> format\_value(3.14159, 2)
        '3.14'
        >>> format\_value(42, 0)
        '42'


## values\_to\_string(values, decimals):
    Converts a list of values to formatted strings.

    This function takes a list of values and a 'decimals' parameter and converts
    each value in the list to a formatted string using the 'format\_value'
    function. If a value within the list is itself a list (e.g., representing a
    value with uncertainty), it will be formatted as "value +/- uncertainty".

    ### Args:
        values (list): A list of values to be converted to strings.
        decimals (int): The number of decimals to be used when formatting
            float or integer values. Ignored for other types.

    ### Returns:
        list of str: A list of formatted strings corresponding to the input values.

    ### Examples:
        >>> values\_to\_string([3.14159, 42, 'Hello'], 2)
        ['3.14', '42', 'Hello']
        >>> values\_to\_string([[2.0, 0.1], 1.5], 1)
        ['2.0 +/- 0.1', '1.5']

    ### Note:
        This function relies on the 'format\_value' function for value formatting.


## len\_of\_longest\_string(strings):
    Returns the length of the longest string in a list of strings.

    This function takes a list of strings as input and returns the length of the
    longest string in the list.

    ### Args:
        strings (list of str): A list of strings for which the longest length
            is to be determined.

    ### Returns:
        int: The length of the longest string in the input list of strings.

    ### Examples:
        >>> len\_of\_longest\_string(['apple', 'banana', 'cherry'])
        6
        >>> len\_of\_longest\_string(['Hello', 'world'])
        5

## nice\_string\_output(d, extra\_spacing=5, decimals=3):
    Formats and outputs a dictionary with aligned names and values.

    This function takes a dictionary 'd' containing names and corresponding values
    to be properly formatted. It ensures that the distance between the names and
    the values in the printed output has a minimum distance of 'extra\_spacing'.
    The number of decimals used for formatting can be specified using the 'decimals'
    keyword.

    ### Args:
        d (dict): A dictionary containing names (keys) and values to be formatted
            and displayed.
        extra\_spacing (int, optional): The minimum additional spacing between names
            and values in the printed output. Default is 5.
        decimals (int, optional): The number of decimals to be used when formatting
            float or integer values. Ignored for other types. Default is 3.

    ### Returns:
        str: A formatted string representation of the dictionary with aligned names
            and values.

    ### Examples:
        >>> data = {'apple': 3.14159, 'banana': 42, 'cherry': 1.618}
        >>> nice\_string\_output(data, extra\_spacing=4, decimals=2)
        'apple   3.14    \nbanana  42      \ncherry   1.62'

    ### Note:
        This function relies on the 'len\_of\_longest\_string' and 'values\_to\_string'
        functions for value formatting.

## add\_text\_to\_ax(x\_coord, y\_coord, string, ax, fontsize=12, color='k'):
    Adds text to a matplotlib axes with specified properties.

    This function is a shortcut to add text to a Matplotlib axes with proper font
    settings. The text is positioned using relative coordinates with respect to
    the axes.

    ### Args:
        x\_coord (float): The x-coordinate of the text, relative to the axes.
        y\_coord (float): The y-coordinate of the text, relative to the axes.
        string (str): The text to be added to the axes.
        ax (matplotlib.axes.Axes): The Matplotlib axes to which the text will be added.
        fontsize (int, optional): The font size of the text. Default is 12.
        color (str or tuple, optional): The color of the text. Default is 'k' (black).

    ### Returns:
        None

    ### Examples:
        >>> import matplotlib.pyplot as plt
        >>> fig, ax = plt.subplots()
        >>> add\_text\_to\_ax(0.5, 0.5, 'Hello, World!', ax, fontsize=16, color='blue')

    ### Note:
        This function uses Matplotlib's `text` function for adding the text to the axes.

## Chi2Regression:
    Chi-square regression class for fitting data to a model using chi-square statistics.

    This class represents a chi-square regression for fitting data to a model.
    It computes the chi-square value for the provided data and model prediction.

    ### Args:
        f (callable): A callable function representing the model.
        x (numpy.ndarray): An array of input values for the model.
        y (numpy.ndarray): An array of observed data values.
        sy (numpy.ndarray or None, optional): An array of uncertainties in the observed data.
            If None, an array of ones\_like 'x' will be used. Default is None.
        weights (numpy.ndarray or None, optional): An array of weights for the data points.
            If None, an array of ones\_like 'x' will be used. Default is None.
        bound (tuple or None, optional): A tuple representing the lower and upper bounds for 'x'.
            Data outside this bound will be excluded from the computation. Default is None.

## simpson38(f, edges, bw, \*arg):
    Numerical integration using Simpson's 3/8 rule.

    This function performs numerical integration using Simpson's 3/8 rule.
    It takes a function 'f', bin edges 'edges', a bin width 'bw', and variable arguments '*arg'.
    The integration is performed using the function values at the edges and intermediate points.

    ### Args:
        f (callable): A callable function for which integration is to be performed.
        edges (numpy.ndarray): An array of bin edges.
        bw (float): The bin width.
        *arg: Variable arguments to be passed to the function 'f'.

    ### Returns:
        float: The result of the numerical integration using Simpson's 3/8 rule.

## integrate1d(f, bound, nint, \*arg):
    Compute 1D integral using numerical integration.

    This function computes the 1D integral of a function using numerical integration.
    It takes a callable function 'f', a bound 'bound', a number of intervals 'nint',
    and variable arguments '*arg'. The function values are evaluated at the bin edges
    and integrated using Simpson's 3/8 rule.

    ### Args:
        f (callable): A callable function for which integration is to be performed.
        bound (tuple): A tuple representing the lower and upper bounds of integration.
        nint (int): The number of intervals for numerical integration.
        *arg: Variable arguments to be passed to the function 'f'.

    ### Returns:
        float: The result of the 1D numerical integration.
