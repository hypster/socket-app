import MessageType.Request

def check_enough_balance(fromAcc, amount, db):
    return db[fromAcc]['balance'] >= amount

def check_acc_exists(acc, db):
    if acc in db:
        return True
    else:
        return False

def substract(acc, amount, db):
    db[acc]['balance'] -= amount
    return True

def add(acc, amount, db):
    db[acc]['balance'] += amount
    return True

def check_permission(user_id, acc, db):
    _id = get_user_id(acc, db)
    return _id == user_id

def get_balance(acc, db):
    return db[acc]['balance']

def get_user_id(acc, db):
    return db[acc]['user_id']