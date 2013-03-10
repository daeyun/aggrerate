def validateUser(username, password):
    return username == password

def addUser(username, password):
        db = MySQLdb.connect(host='ec2-174-129-96-104.compute-1.amazonaws.com',
        user='matt',
        passwd='matt',
        db='aggrerate')
