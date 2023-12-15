from google.oauth2 import service_account

from .config import settings


gcp_credentials = service_account.Credentials.from_service_account_info(
    settings.get("gcp_credentials"), scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
gcp_project_id = settings["gcp_credentials"]["project_id"]
gcp_organization_id = settings["gcp_organization_id"]
# key_path_file = settings["google_application_credentials"]
# gcp_credentials = service_account.Credentials.from_service_account_file(key_path_file, scopes=["https://www.googleapis.com/auth/cloud-platform"])
# gcp_project_id = settings["project_id"]


async def get_all_roles_for_member(cloudresourcemanager_service, project_id, member):
    policy = cloudresourcemanager_service.projects().getIamPolicy(resource=project_id, body={}).execute()
    roles_for_member = []

    for binding in policy['bindings']:
        if member in binding['members']:
            roles_for_member.append(binding['role'])

    return roles_for_member


async def remove_role_binding(cloudresourcemanager_service, project_id, member, role):
    policy = cloudresourcemanager_service.projects().getIamPolicy(resource=project_id, body={}).execute()

    for binding in policy['bindings']:
        if binding['role'] == role and member in binding['members']:
            binding['members'].remove(member)
            break

    cloudresourcemanager_service.projects().setIamPolicy(
        resource=project_id,
        body={
            'policy': policy
        }).execute()


async def add_role_binding(cloudresourcemanager_service, project_id, member, role):
    policy = cloudresourcemanager_service.projects().getIamPolicy(resource=project_id, body={}).execute()
    bindings = policy.get("bindings", [])
    binding = next((b for b in bindings if b["role"] == role), None)

    if binding:
        if member not in binding["members"]:
            binding["members"].append(member)
    else:
        bindings.append({"role": role, "members": [member]})
    
    cloudresourcemanager_service.projects().setIamPolicy(
        resource=project_id,
        body={
            "policy": {"bindings": bindings}
        }).execute()


async def create_and_assign_role(iam_service, cloudresourcemanager_service, project_id, member, current_time, permissions):
    member_type, member_email = member.split(':')
    member_name = member_email.split('@')[0]
    role_id = 'boch_' + member_name + '_1'

    # 역할 생성
    iam_service.projects().roles().create(
        parent=f'projects/{project_id}',
        body={
            'roleId': role_id,
            'role': {
                'title': 'Optimization Role - Boch_' + member_name,
                'description': 'Optimization role for ' + member_name + '(' + current_time.strftime('%Y-%m-%d') + ')',
                'includedPermissions': permissions,
                'stage': 'GA'
            }
        }).execute()

    # 역할 부여
    policy = cloudresourcemanager_service.projects().getIamPolicy(resource=project_id, body={}).execute()
    policy['bindings'].append({
        'role': f'projects/{project_id}/roles/{role_id}',
        'members': [member]
    })
    cloudresourcemanager_service.projects().setIamPolicy(
        resource=project_id,
        body={
            'policy': policy
        }).execute()


async def update_optimization_role(iam_service, project_id, member_name, current_time, permissions, role_id):
    role = iam_service.projects().roles().get(name=f"projects/{project_id}/roles/{role_id}").execute()
    role["description"] = 'Optimization role for ' + member_name + '(' + current_time.strftime('%Y-%m-%d') + ')'
    role["includedPermissions"] = permissions
    iam_service.projects().roles().patch(
        name=f"projects/{project_id}/roles/{role_id}",
        body=role
    ).execute()


async def create_customer_role(iam_service, project_id, role_id, history):
    iam_service.projects().roles().create(
        parent=f'projects/{project_id}',
        body={
            'roleId': role_id,
            'role': {
                'title': history["title"],
                'description': history["description"],
                'includedPermissions': history["includedPermissions"],
                'stage': 'GA'
            }
        }).execute()


async def get_project_role_list(iam_service, project_id):
    roles_list = iam_service.projects().roles().list(parent=f'projects/{project_id}').execute()

    return roles_list