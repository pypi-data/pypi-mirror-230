from datetime import datetime

def greet():
    """
    target: greets user based on time of the day
    return: greetings (str)
    """ 
    time = datetime.now().hour
    if time < 11:
        return "Good Morning!"
    elif time < 15:
        return "Good Afternoon!"
    elif time < 18:
        return "Good Evening!"
    else:
        return "Good Night!"