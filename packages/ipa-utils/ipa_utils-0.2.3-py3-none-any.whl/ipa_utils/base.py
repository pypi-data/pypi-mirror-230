import json
import logging

import ldap3

LDAP_MAX_ENTRIES = 10 * 10000
USER_BASE_DN_TEMPLATE = u"cn=users,cn=accounts,{base_dn}"
USER_SEARCH_TEMPLATE = u"(&(objectclass=person)(uid={username}))"
USERS_SEARCH_TEMPLATE = u"(objectclass=person)"
USER_OBJECT_CLASSES = [
    "top",
    "person",
    "organizationalPerson",
    "inetOrgPerson",
    "inetUser",
    "posixAccount",
    "krbPrincipalAux",
    "krbTicketPolicyAux",
    "ipaObject",
    "ipaSshUser",
    "ipaSshGroupOfPubKeys",
    "mepOriginEntry",
]

logger = logging.getLogger(__name__)

class IpaService(object):

    def __init__(self, host=u"127.0.0.1", port=389, base_dn=None, username=None, password=None, server_params=None, connection_params=None):
        connection_params = connection_params or {}
        server_params = server_params or {}
        self.host = host
        self.port = port
        self.base_dn = base_dn
        self.server_params = {
            "get_info": ldap3.ALL,
        }
        self.connection_params = {
            "auto_referrals": True,
            "fast_decoder": True,
        }
        self.server_params.update(server_params)
        self.connection_params.update(connection_params)
        if username:
            self.connection_params["user"] = username
        if password:
            self.connection_params["password"] = password
        if not base_dn:
            self.base_dn = self.auto_get_base_dn()
            if not self.base_dn:
                raise RuntimeError(u"ERROR: no BaseDN provides and fetch the BaseDN failed.")

    def auto_get_base_dn(self):
        connection = self.get_connection()
        base_dns = [x for x in connection.server.info.naming_contexts if u"dc=" in x]
        if base_dns:
            return base_dns[0]
        else:
            return None

    @property
    def user_base_dn(self):
        return USER_BASE_DN_TEMPLATE.format(base_dn=self.base_dn)

    def get_connection(self):
        server = ldap3.Server(self.host, self.port, **self.server_params)
        connection = ldap3.Connection(server, **self.connection_params)
        connection.bind()
        connection.start_tls()
        connection.bind()
        return connection

    def get_user_dn(self, username):
        return "uid={},{}".format(username, self.user_base_dn)

    def get_user_detail_from_entry(self, user_entry):
        user_detail = json.loads(user_entry.entry_to_json())
        data = {
            u"dn": user_detail[u"dn"],
        }
        data.update(user_detail[u"attributes"])
        for key in data.keys():
            value = data[key]
            if isinstance(value, list) and len(value) == 1:
                data[key] = value[0]
        return data

    def get_user_detail(self, username, connection=None):
        user_entry = self.get_user_entry(username, connection)
        if not user_entry:
            return None
        return self.get_user_detail_from_entry(user_entry)

    def get_user_entry(self, username, connection=None):
        connection = connection or self.get_connection()
        connection.search(
            search_base=self.user_base_dn,
            search_filter=USER_SEARCH_TEMPLATE.format(username=username),
            attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES],
            )
        if len(connection.entries):
            return connection.entries[0]
        else:
            return None

    def get_user_entries(self, connection=None, paged_size=200):
        entries = []
        connection = connection or self.get_connection()
        extra_params = {}
        counter = 0
        while True:
            counter += 1
            if counter > LDAP_MAX_ENTRIES / paged_size:
                raise RuntimeError("IpaService.get_user_entries hit the max limit: {0}".format(LDAP_MAX_ENTRIES))
            connection.search(
                search_base=self.user_base_dn,
                search_filter=USERS_SEARCH_TEMPLATE,
                attributes=[ldap3.ALL_ATTRIBUTES, ldap3.ALL_OPERATIONAL_ATTRIBUTES],
                paged_size=paged_size,
                **extra_params
                )
            entries += connection.entries
            paged_cookie = connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
            if paged_cookie:
                extra_params["paged_cookie"] = paged_cookie
            else:
                break
        return entries

    def add_user_entry(self, username, user_detail, user_object_classes=None, connection=None):
        dn = self.get_user_dn(username)
        connection = connection or self.get_connection()
        user_object_classes = user_object_classes or USER_OBJECT_CLASSES
        logger.info("add user entry: dn={0}, connection={1}, user_object_classes={2}, user_detail={3}".format(dn, connection, user_object_classes, user_detail))
        success = connection.add(dn, user_object_classes, user_detail)
        logger.info("add user entry: dn={0}, success={1}, result={2}".format(dn, success, connection.result))
        if success:
            return True
        else:
            raise RuntimeError(connection.result)

    def update_user_entry(self, username, user_changes, connection=None):
        dn = self.get_user_dn(username)
        connection = connection or self.get_connection()
        changes = {}
        for key, value in user_changes.items():
            if isinstance(value, (list, set, tuple)):
                values = list(value)
            else:
                values = [value]
            changes[key] = [(ldap3.MODIFY_REPLACE, values)]
        logger.info("update user entry: dn={0}, connection={1}, changes={2}".format(dn, connection, changes))
        success = connection.modify(dn, changes)
        logger.info("update user entry: dn={0}, success={1}, result={2}".format(dn, success, connection.result))
        if success:
            return True
        else:
            raise RuntimeError(connection.result)

    def delete_user_entry(self, username, connection=None):
        dn = self.get_user_dn(username)
        connection = connection or self.get_connection()
        logger.info("delete user entry: dn={0}, connection={1}".format(dn, connection))
        success = connection.delete(dn)
        logger.info("delete user entry: dn={0}, success={1}, result={2}".format(dn, success, connection.result))
        if success:
            return True
        else:
            raise RuntimeError(connection.result)

    def modify_user_password(self, username, new_password, connection=None):
        dn = self.get_user_dn(username)
        connection = connection or self.get_connection()
        logger.info("modify user password: dn={0}, connection={1}".format(dn, connection))
        success = connection.extend.standard.modify_password(user=dn, new_password=new_password)
        logger.info("modify user password: dn={0}, success={1}, result={2}".format(dn, success, connection.result))
        if success:
            return True
        else:
            raise RuntimeError(connection.result)
