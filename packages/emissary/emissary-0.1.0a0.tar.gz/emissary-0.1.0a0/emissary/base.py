

class base():
    """
    Description for class.

    :ivar target_dict: Argument mapping for target arguments
    :ivar option_dict: Argument mapping for option arguments
    :ivar command_seq: Sequence of commands to execute
    """
    
    _command_seq = []
    _target_dict = {}
    _option_dict = {}
    
    def __init__(self):
        pass