def pformat(d, indent=0, spaces=4, verbose=True):
    output = ''
    for key, value in d.items():
        output += f"{' ' * spaces * indent}'{str(key)}':\n"
        if isinstance(value, dict):
            output += f"{pformat(value, indent=indent+1, spaces=spaces, verbose=verbose)}\n"
        else:
            if not verbose:
                value = type(value)
            output += '\n'.join([f"{' ' * spaces * (indent+1)}{line}" for line in str(value).split('\n')]) + '\n'
    return output.rstrip('\n')

def pprint(d, **kwargs):
    print(pformat(d, **kwargs))
    
def pformat_english(*args):
    """
    Formats arguments in a way that follows English grammatical rules.
    """
    length = len(args)
    
    if length == 0:
        return ""
    
    if length == 1:
        return str(args[0])
    
    if length == 2:
        return f'{args[0]} and {args[1]}'
    
    return f"{', '.join(map(str, args[:-1]))}, and {args[-1]}"