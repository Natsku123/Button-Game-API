import pymysql
from modules.utils import get_config

config = get_config()['database']


def insert(sql):
    """
    Insert data into database.
    :param sql:
    :return:
    """
    db = pymysql.connect(
        config['host'],
        config['username'],
        config['password'],
        config['name'],
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with db.cursor() as cursor:
            cursor.execute(sql)

        db.commit()
        db.close()
        return True
    except pymysql.MySQLError as e:
        db.rollback()
        db.close()
        print(e, e.args)
        return False


def get(sql, everything=True):
    """
    Get data from database.
    :param sql:
    :param everything:
    :return:
    """
    db = pymysql.connect(
        config['host'],
        config['username'],
        config['password'],
        config['name'],
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with db.cursor() as cursor:
            cursor.execute(sql)

            if everything:
                data = cursor.fetchall()
            else:
                data = cursor.fetchone()

        db.close()
        return data
    except pymysql.MySQLError:
        db.close()
        return None


def add_click(username):
    """
    Add click to clicker and check if got any goal
    :param username:
    :return:
    """

    # Get existing player
    player_sql = "SELECT * FROM players WHERE `username`='{0}';".format(username)
    player = get(player_sql, False)
    new_player = False

    # Prepare for creation of a new player if doesn't exits
    if player is None:
        player = {
            "username": username,
            "clicks": 0,
            "bronze": 0,
            "silver": 0,
            "gold": 0
        }
        new_player = True

    # Get clicker
    clicker_sql = "SELECT * FROM clickers WHERE `id`=1;"

    clicker = get(clicker_sql, False)

    # Add this click
    clicker['clicked'] = clicker['clicked'] + 1
    player['clicks'] = player['clicks'] + 1

    # Check if any goals were reached.
    if clicker['clicked'] % 500 == 0:
        player['gold'] = player['gold'] + 1
        status = "gold"
    elif clicker['clicked'] % 200 == 0:
        player['silver'] = player['silver'] + 1
        status = "silver"
    elif clicker['clicked'] % 100 == 0:
        player['bronze'] = player['bronze'] + 1
        status = "bronze"
    else:
        status = "default"

    # Create a player or update player
    if new_player:
        new_sql = "INSERT INTO players (`username`, `clicks`, `bronze`, `silver`, `gold`) VALUES ('{0}', '{1}','{2}', '{3}', '{4}');".format(
                        player['username'],
                        player['clicks'],
                        player['bronze'],
                        player['silver'],
                        player['gold']
                    )
        if not insert(new_sql):
            return {'status': "error", "error": "Cannot create " + str(username) + "."}
    else:
        update_sql = "UPDATE players SET `clicks`='{0}', " \
                     "`bronze`='{1}', `silver`='{2}', `gold`='{3}' " \
                     "WHERE `username`='{4}';".format(
                            player['clicks'],
                            player['bronze'],
                            player['silver'],
                            player['gold'],
                            player['username']
                        )
        if not insert(update_sql):
            return {'status': "error", "error": "Cannot update " + str(username) + "."}
    return {'status': status}


def get_players():
    """
    Get all existing players.
    :return:
    """
    sql = "SELECT * FROM players;"
    return get(sql)


def get_needed():
    """
    Calculate next goal and amount of clicks needed.
    :return:
    """
    sql = "SELECT * FROM clickers WHERE `id`=1;"
    clicker = get(sql, False)

    # Calculation for needed clicks per goal type
    needed_gold = (clicker['clicked'] // 500 + 1) * 500 - clicker['clicked']
    needed_silver = (clicker['clicked'] // 200 + 1) * 200 - clicker['clicked']
    needed_bronze = (clicker['clicked'] // 100 + 1) * 100 - clicker['clicked']

    # Return only the highest goal type.
    if needed_gold <= needed_silver and needed_gold <= needed_bronze:
        return {'next': "gold", "amount": needed_gold}
    elif needed_silver < needed_gold and needed_silver <= needed_bronze:
        return {'next': "silver", "amount": needed_silver}
    elif needed_bronze < needed_gold and needed_bronze < needed_silver:
        return {'next': "bronze", "amount": needed_bronze}
    else:
        return {'next': "error", "amount": -1}
