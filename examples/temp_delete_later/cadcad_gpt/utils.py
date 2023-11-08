def plan_parser(plan: str) -> list:
    """
    Splits the given plan from planner agent into multiple sub-plans using ``` as a delimiter.

    Parameters:
    plan (str): Plan string which may contain ``` delimiter to break it into sub-plans.

    Returns:
    list: A list of sub-plans. Returns an empty list if no ``` delimiter is found.
    """
    if '```' not in plan:
        return []

    # Split plan into sub-plans using ``` as a delimiter and remove the first element (reasoning step)
    plans = plan.split('```')[1]
    # remove brackets and split into list
    plans = plans.replace('\n','').replace('[','').replace(']','').replace('python','').split(',')
    plan_list = [plan.strip() for plan in plans]
    return plan_list



def color(text: str, style: str) -> str:
    """
    Prints the given text in the specified color style.

    Args:
        text (str): The text to be printed.
        style (str): The color style to be applied to the text. Must be one of the following:
            'blue_bold', 'blue_underline', 'green_bold', 'green_underline', 'cyan_bold', 'cyan_underline',
            'red_bold', 'red_underline', 'magenta_bold', 'magenta_underline', 'yellow_bold', 'yellow_underline',
            'white'

    Raises:
        ValueError: If an invalid style is provided.

    Returns:
        str: The text wrapped in the specified color style.
    """
    styles = {
        'blue': '\033[0;34m',
        'blue_bold': '\033[1;34m',
        'blue_underline': '\033[4;34m',
        'green_bold': '\033[1;32m',
        'green_underline': '\033[4;32m',
        'cyan': '\033[0;36m',
        'cyan_bold': '\033[1;36m',
        'cyan_underline': '\033[4;36m',
        'red_bold': '\033[1;31m',
        'red_underline': '\033[4;31m',
        'magenta_bold': '\033[1;35m',
        'magenta_underline': '\033[4;35m',
        'yellow_bold': '\033[1;33m',
        'yellow_underline': '\033[4;33m',
        'white': '\033[0m'
    }

    if style not in styles:
        raise ValueError('Invalid style')

    return styles[style] + text + '\033[0m'