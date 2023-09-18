import sys

def _get_answer(max_choice: int)->int:
    while True:
        val = input('Your choice: ')
        if val.isdigit() and 0 <= int(val) <= max_choice:
            break
    return int(val)

def _print_screen(params_stack: list) -> list:
    params = params_stack[-1]
    details_func = params.get('details_function')
    title, body, options = details_func(params)
    root_screen_flag = True if params.get('root_screen_flag') == 'yes' else False
    zero_title = 'go back' if not root_screen_flag else 'exit'

    print('********************************************************************************')
    print('********************************************************************************')
    print(title)
    if body:
        print('********************************************************************************')
        print(body)
    print('********************************************************************************')
    for no in range(len(options)):
        print(f"({no+1}) {options[no]['title']}")
    print(f'(0) {zero_title}')
    ans = _get_answer(len(options))
    if root_screen_flag and ans == 0: # exit root screen
        return None
    if not root_screen_flag and ans == 0: # go back to te previous screen
        params_stack.pop()
        return params_stack
    #prepare for going into chosen option
    params_stack.append(options[ans-1])
    return params_stack
        
def start_walking(welcome: str, byebye: str, root_params: dict) -> None:
    root_params['root_screen_flag'] = 'yes'
    print(welcome)
    print('')
    params_stack = [root_params]
    while True:
        params_stack = _print_screen(params_stack)
        if params_stack == None:
            break
    print('')
    print(byebye)
    print('')
    
def main () -> int:
    try:
        return 0
    except Exception as e:
        print(str(e))
        return 1
    
if __name__ == "__main__":
    sys.exit (main ())
