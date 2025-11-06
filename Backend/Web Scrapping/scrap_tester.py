from urllib.robotparser import RobotFileParser

def check_robots(base_url="https://npino.com/robots.txt", user_agent="*"):
    rp = RobotFileParser()
    rp.set_url(base_url)
    rp.read()
    return rp.can_fetch(user_agent, "https://npino.com/")
