from peewee import *
import bcrypt
import web.auth as auth
mysql_db = MySQLDatabase("podcastmanager", host="localhost", port=3306, user="root", passwd="NvideA", threadlocals=True)
def getDb():
    """
    Returns the database connection object
    """
    return mysql_db

class MySqlModel(Model):
    """
    Base class that uses mysql
    """
    class Meta(object):
        database = mysql_db
    def __str__(self):
        r = {}
        for k in self._data.keys():
            try:
                r[k] = str(getattr(self, k))
            except:
                r[k] = json.dumps(getattr(self, k))
        return str(r)


class Groups(MySqlModel):
    groupname = CharField(unique = True)
    def getRoles(self):
        roles = []
        for gr in GroupsRoles.select().where(GroupsRoles.group == self):
            roles.append(gr.role)
        return roles

    def hasRole(self, rolename):
        role = None
        try:
            role = Roles.get(Roles.rolename == rolename)
        except Roles.DoesNotExist:
            return False
        roles = []
        for gr in GroupsRoles.select().where(GroupsRoles.group == self).where(GroupsRoles.role == role):
            roles.append(gr.role)
        if len(roles) == 1:
            return True
        return False


class Roles(MySqlModel):
    rolename = CharField(unique = True)

class GroupsRoles(MySqlModel):
    group = ForeignKeyField(Groups, related_name="groupsrole_groups")
    role = ForeignKeyField(Roles, related_name="groupsrole_role")
    class Meta:
        indexes = (
            (("group", "role"), True),
        )

class Users(MySqlModel):
    username = CharField(unique = True)
    email = CharField()
    password = CharField()
    group = ForeignKeyField(Groups, related_name="user_groups")
    def setPassword(self, password = None):
        if not password:
            return
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        self.password = hashed
        self.token = bcrypt.gensalt()
        self.save()

    def checkPassword(self, password = None):
        if not password:
            return False
        hashed = bcrypt.hashpw(password, self.password)
        return hashed == self.password

    def hasRole(self, role):
        if not self.group:
            return False
        return self.group.hasRole(role)

class Tokens(MySqlModel):
    token = CharField(unique=True)
    name = CharField()
    user = ForeignKeyField(Users, related_name="token_user")


def initTables():
    Groups.create_table(True)
    Roles.create_table(True)
    Users.create_table(True)
    GroupsRoles.create_table(True)
    Tokens.create_table(True)

def createTestData():
    g1 = Groups.create(groupname="admin")
    g2 = Groups.create(groupname="mod")
    g3 = Groups.create(groupname="user")
    u = Users.create(username = "test", email="some@test.xx", password = "", group = g3)
    u.setPassword("testpw")
    t = Tokens.create(token="aaaaaaaa", name="testtoken", user=u)
    print u.username + "  " + u.password + "  " + u.email
    r1 = Roles.create(rolename="ban")
    r2 = Roles.create(rolename="kick")
    r3 = Roles.create(rolename="read")
    GroupsRoles.create(group = g1, role = r1)
    GroupsRoles.create(group = g1, role = r2)
    GroupsRoles.create(group = g1, role = r3)
    GroupsRoles.create(group = g2, role = r2)
    GroupsRoles.create(group = g2, role = r3)
    GroupsRoles.create(group = g3, role = r3)

    print auth.getUserFromToken(t.token)
    print(g1.hasRole("kick"))
    print u.hasRole("read")
    

