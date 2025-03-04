import inspect

def debug_info(variable):
    # Get the current frame and the caller frame
    current_frame = inspect.currentframe()
    caller_frame = current_frame.f_back
    
    # Get the name of the function or method from the caller frame
    function_name = caller_frame.f_code.co_name
    
    # Get the local variables of the caller frame
    local_vars = caller_frame.f_locals
    
    # Print debugging information
    print(f"[DEBUG] Function/Method: {function_name}")
    print(f"[DEBUG] Data passed: {variable}")
    # print(f"[DEBUG] Caller locals: {local_vars}")
