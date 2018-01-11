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

# Remaining functions are not based on anything

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

def query_int(question, default=None):
    while True:
        answer = query_string(question, default)
        try: _ = int(answer)
        except ValueError as e: continue
        else: return int(answer)

def query_list(question, choices, default=None):
    ''' Present a list of choices to the user and return the one they picked.
    If a default is provided, then it is returned if the user just hits
    <Enter>. The default must be an index into the choices list.
    '''
    assert len(choices) > 0
    if default != None:
        assert isinstance(default, int)
        assert default < len(choices)
        question += ' (def: {})'.format(default)
    print(question)
    for i, choice in enumerate(choices): print('{:3d} {}'.format(i, choice))
    while True:
        print(question, end=' ')
        answer = input()
        try: answer = int(answer)
        except ValueError as e:
            if answer == '' and default != None: return choices[default]
            continue
        if answer < 0 or answer > len(choices)-1: continue
        return choices[answer]
