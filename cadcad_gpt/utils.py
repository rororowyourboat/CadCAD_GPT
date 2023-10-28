def plan_parser(plan: str) -> list:
    """
    Splits the given plan from planner agent into multiple sub-plans using ``` as a delimiter.
    
    Parameters:
    plan (str): Plan string which may contain ``` delimiter to break it into sub-plans.

    Returns:
    list: A list of sub-plans. Returns an empty list if no ``` delimiter is found.
    """
    # Split plan into sub-plans using ``` as a delimiter
    plans = plan.split('```')
    #remove the '[' ']' symbols from all the elements
    plans = [plan.replace('[', '').replace(']', '') for plan in plans]
    #remove the extra spaces from all the elements
    plans = [plan.strip() for plan in plans]
    plan_list = plans[1].split(', ')
    return plan_list




def print_color(string: str, color: str) -> None:
    """
    Prints a string on console in a given color.

    Parameters:
    string (str): The string to be printed on console
    color (str): The color code for the string to be printed in

    Returns:
    None
    """
    # Print string with the given color and reset console color to default afterwards
    print("\033["+color+"m"+string+"\033[0m")
