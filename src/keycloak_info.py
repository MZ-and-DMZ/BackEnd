from keycloak import KeycloakAdmin
from keycloak import KeycloakOpenIDConnection
from pprint import pprint

from database import db_client
from src.config import conf


# 환경 설정 ----------------------------------------------------------------------------------
# MongoDB 연결
client = db_client.mongoClient(conf["DB_server"])

# keycloak 초기 연결
def connect_keycloak(realm) :
# Configure client
    keycloak_connection = KeycloakOpenIDConnection(
                        server_url="http://www.mia7a.store:8080/",
                        username="admin",
                        password="admin",
                        realm_name="master",
                        verify=True)
    # test = KeycloakAdmin(realm_name="myrealm")
    # keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
    keycloak_admin = KeycloakAdmin(connection=keycloak_connection)
    if realm == "master" :
        pass
    else :
        keycloak_admin = KeycloakAdmin(realm_name=realm, connection=keycloak_connection)
    return keycloak_admin

# -------------------------------------------------------------------------------------------


# Realm 목록 가져오기
def get_realms(keycloak_account) :
    realms = []
    for realm in keycloak_account.get_realms() :
        realms.append(realm['realm'])
    return realms

# 특정 realm의 Users, Roles, Groups, Clients 목록 가져오기
def get_info(category="users", realm="master") -> list:
    keycloak_admin = connect_keycloak(realm)
    if category == "clients" : # Client 목록 조회
        info = keycloak_admin.get_clients()
    elif category == "users" : # Users 목록 조회
        info = keycloak_admin.get_users()
    elif category == "groups" : # Groups 목록 조회
        info = keycloak_admin.get_groups()
    return info

# AWS의 클라이언트 ID 가져오기
# Client ID = 'a507f7f0-6555-405f-bb8e-0e5848dc748d'
def aws_get_client_id(realm="master") :
    keycloak_connection = KeycloakOpenIDConnection(
                server_url="http://www.mia7a.store:8080/",
                username="admin",
                password="admin",
                realm_name="master",
                verify=True)
    keycloak_admin = KeycloakAdmin(realm_name=realm, connection=keycloak_connection)
    # keycloak_admin = connect_keycloak(realm)
    aws_client = keycloak_admin.get_client_id("urn:amazon:webservices")
    pprint(aws_client)
    return aws_client

# Group ID 가져오기
def get_group_id_list(realm="master") -> list:
    group_list = get_info("groups")
    group_id_list = []
    for group in group_list :
        group_id = group['id']
        group_id_list.append(group_id)
    pprint(group_id_list)
    return group_id_list

# User ID 가져오기
def get_user_id_list(realm="master") -> list :
    user_list = get_info("users")
    user_id_list = []
    for user in user_list :
        user_id = user['id']
        user_id_list.append(user_id)
    pprint(user_id_list)
    return(user_id_list)

# Group에 부여되어 있는 Client Role 정보
def get_group_role(group_id, client_id='a507f7f0-6555-405f-bb8e-0e5848dc748d', realm="master") :
    keycloak_admin = connect_keycloak(realm)
    # group_id = 'ed19e655-eed1-498a-958a-2a23e0ba8a1c' # Group ID
    # client_id = 'a507f7f0-6555-405f-bb8e-0e5848dc748d' # AWS Client ID
    group_roles = keycloak_admin.get_group_client_roles(group_id=group_id, client_id=client_id)
    print(group_roles)
    return group_roles

# User에 부여되어 있는 Client Role 정보
def get_user_role(user_id, client_id, realm="master") :
    keycloak_admin = connect_keycloak(realm)
    user_id = 'b5121619-61fa-4d2a-a49e-aa143ed351e0' # User ID, 함수 정상 동작 확인용(alice, backend leader)
    client_id = 'a507f7f0-6555-405f-bb8e-0e5848dc748d' # AWS Client ID
    user_roles = keycloak_admin.get_client_roles_of_user(user_id=user_id, client_id=client_id)
    # print(user_roles)
    return user_roles

# User에 부여되어 있는 모든 role 가져오기
def get_user_all_role(user_id, client_id='a507f7f0-6555-405f-bb8e-0e5848dc748d', realm="master") :
    keycloak_admin = connect_keycloak(realm)
    client_roles = get_user_role(user_id, client_id)
    realm_roles = keycloak_admin.get_realm_roles_of_user(user_id)
    roles = []
    for client_role in client_roles :
        role = {}
        role['name'] = client_role['name']
        role['type'] = 'client'
        roles.append(role)
    for realm_role in realm_roles :
        role = {}
        role['name'] = realm_role['name']
        role['type'] = 'realm'
        roles.append(role)
    return roles



# API 서버에서 사용하는 값들을 정리해서 DB에 입력하는 함수들 ---------------------------------------------
# (API 연결) [Users] 사용자 정보 조회 -  사용자명, 부서 이름, 역할 이름 가져오기
# /idp/keycloak/users
def get_users_info_for_api(realm="master") :
    keycloak_admin = connect_keycloak(realm)
    users = []
    for user_info in get_info('users') :
        user = {}
        user['name'] = user_info['username']
        user['id'] = user_info['id']
        user['roles'] = get_user_all_role(user['id'])
        user['groups'] = list()
        for group in  keycloak_admin.get_user_groups(user_id=user['id']) :
            user['groups'].append(group['name'])
        users.append(user)
    pprint(users)
    return users

# (API 연결) [Groups] 전체 그룹 대상, 그룹별 들어있는 사용자 정보, 인원 수 출력
# /idp/keycloak/groups
def get_groups_members(realm="master", client_id='a507f7f0-6555-405f-bb8e-0e5848dc748d') -> list:
    keycloak_admin = connect_keycloak(realm)
    groups = []
    for group in get_info("groups") :
        group_info = {}
        group_info['name'] = group['name']
        group_info['id'] = group['id']
        roles = []
        for role in keycloak_admin.get_group_client_roles(group_id=group['id'], client_id=client_id) :
            roles.append(role['name'])
        group_info['client_roles'] = roles
        members = keycloak_admin.get_group_members(group['id'])
        usernames = []
        for member in members :
            usernames.append(member['username'])
        group_info['members'] = usernames
        group_info['num'] = len(usernames)
        groups.append(group_info)
        pprint(groups)

    return groups

# (API 연결) [Roles] Realm, 각 Client의 role 들을 모두 가져온다.
# /idp/keycloak/roles
def get_all_roles(realm="master") :
    keycloak_admin = connect_keycloak(realm="master")
    roles = list()
    ## for문을 한 번 더 돌려서 각 client의 id를 가져오고 해당 id를 기반으로 role 검색하는 걸로 수정

    # client role 추가
    for client in get_client_info_summary() :
        client_id = client['id']
        for client_role in keycloak_admin.get_client_roles(client_id=client_id) :
            role = {}
            role['name'] = client_role['name']
            role['id'] = client_role['id']
            role['type'] = 'client'
            role['client'] = client['clientId']
            roles.append(role)
    
    # realm role 추가
    for realm_role in keycloak_admin.get_realm_roles() :
        role = {}
        role['name'] = realm_role['name']
        role['id'] = realm_role['id']
        role['type'] = 'realm'
        role['client'] = None
        roles.append(role)
    pprint(roles)
    return roles

# (API 연결) [Client] Client의 id, clientid, name 등의 정보를 출력
# /idp/keycloak/clients
def get_client_info_summary(realm="master") :
    clients = list()
    for client_info in get_info("clients") :
        client = dict()
        client['clientId'] = client_info['clientId']
        client['name'] = client_info['name']
        client['id'] = client_info['id']
        try :
            client['baseUrl'] = client_info['baseUrl']
            client['rootUrl'] = client_info['rootUrl']
            client['protocol'] = client_info['protocol']
        except KeyError as e :
            client['baseUrl'] = ""
            client['rootUrl'] = ""
            client['protocol'] = ""
        clients.append(client)
    pprint(clients)
    return clients


if __name__ == "__main__" :
    client.keycloak_clients_summary_col.insert_many(get_client_info_summary())