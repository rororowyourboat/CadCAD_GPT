from pydantic import create_model
import inspect
from inspect import Parameter

def schema(f):
    kw = {n:(o.annotation, ... if o.default==Parameter.empty else o.default)
        for n,o in inspect.signature(f).parameters.items()}
    s = create_model(f'Input for `{f.__name__}`', **kw).schema()
    return dict(name=f.__name__, description=f.__doc__, parameters=s)


def plan_parser(plan):
    # if plan has ### then split by ### else dont split
    if '###' in plan:
        plan = plan.split('###')[1]
        plans = plan.split('\n')
        return plans
    else:
        return []


# pritn with colors
def print_color(string, color):
    print("\033["+color+"m"+string+"\033[0m")


