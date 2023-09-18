from .rule_evaluator import evaluate_condition

class ExecutionFailed(Exception):
    pass

def get_function_by_name(name,actions):
    return actions.get(name, None)

def execute_actions(action_names, actions,context,**kwargs):
    status = {}
    for action_name in action_names:
        function = get_function_by_name(action_name, actions)
        if not function:
            status[str(action_name)] = "not found"
            continue  # Skip to the next action if this one is not found
        
        try:
            result,error = function(context=context,**kwargs)
            if error is None:  # If the function returns True, exit the function
                status[str(action_name)] = "successful execution"
                return result,status
            else :
                status[str(action_name)] = error
                continue
        except Exception as e:
            status[str(action_name)] = f'action execution failed with error : {e}'
            continue  # Continue to the next action if this one fails to execute

    return None,status

    # If we reach here, all actions have either failed to execute or returned False
    # failed_actions = ', '.join(action_names)
    # raise ExecutionFailed(f"All actions {failed_actions} failed to execute or returned False")