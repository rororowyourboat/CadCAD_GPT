def plan_parser(plan):
    # if plan has ### then split by ### else dont split
    if '###' in plan:
        plan = plan.split('###')[1]
        plans = plan.split('\n')
        return plans
    else:
        return []


# print with colors
def print_color(string, color):
    print("\033["+color+"m"+string+"\033[0m")


