# Based on https://stackoverflow.com/a/3041990
def query_yes_no(question, default='yes'):
    '''Ask a yes/no question via input() and return their answer.
    'question' is a string that is presented to the user.
    'default' is the presumed answer if the user just hits <Enter>.
        It must be 'yes' (the default), 'no' or None (meaning
        an answer is required of the user).
    The 'answer' return value is True for 'yes' or False for 'no'.
    '''
    valid = {'yes': True, 'y': True, 'ye': True, 'no': False, 'n': False}
    if default is None: prompt = ' [y/n] '
    elif default == 'yes': prompt = ' [Y/n] '
    elif default == 'no': prompt = ' [y/N] '
    else: raise ValueError('invalid default answer: "%s"' % default)
    while True:
        print(question + prompt, end='')
        choice = input().lower()
        if default is not None and choice == '': return valid[default]
        elif choice in valid: return valid[choice]
        else: print('Please respond with "yes" or "no" '
            '(or "y" or "n").\n')

# Not based on anything
def query_string(question, default=None):
    ''' Present a qusetion to the user via input() and return their answer as a
    string. If a default is provided, then it is returned if the user just hits
    <Enter>. The default can be an empty string, and even none-string values
    (except None). It will always be wrapped in str() before it is returned,
    however. '''
    if default == None: prompt = ' '
    else: prompt = ' (def: "{}") '.format(default)
    while True:
        print(question + prompt, end='')
        answer = input()
        if answer: return answer
        if not answer and default != None: return str(default)
