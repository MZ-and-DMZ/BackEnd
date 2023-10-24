import boto3

from .config import conf


class awsSdk:
    def __init__(self):
        self.client = boto3.client(
            "iam",
            aws_access_key_id=conf["aws_access_key"],
            aws_secret_access_key=conf["aws_secret_access_key"],
        )

    def add_role_to_instance_profile(self, instance_profile_name, role_name):
        return self.client.add_role_to_instance_profile(
            InstanceProfileName=instance_profile_name, RoleName=role_name
        )

    def add_user_to_group(self, user_name, group_name):
        """
        특정 IAM 사용자를 그룹에 추가합니다.
        Args:
            user_name (str): 추가할 IAM 사용자의 이름.
            group_name (str): 사용자를 추가할 그룹의 이름.
        """
        return self.client.add_user_to_group(UserName=user_name, GroupName=group_name)

    def attach_group_policy(self, group_name, policy_arn):
        """
        특정 IAM 그룹에 정책을 연결합니다.
        Args:
            group_name (str): 정책을 연결할 IAM 그룹의 이름.
            policy_arn (str): 연결할 정책의 Amazon 리소스 이름 (ARN).
        """
        return self.client.attach_group_policy(
            GroupName=group_name, PolicyArn=policy_arn
        )

    def attach_role_policy(self, role_name, policy_arn):
        """
        특정 IAM 역할에 정책을 연결합니다.
        Args:
            role_name (str): 정책을 연결할 IAM 역할의 이름.
            policy_arn (str): 연결할 정책의 Amazon 리소스 이름 (ARN).
        """
        return self.client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

    def attach_user_policy(self, user_name, policy_arn):
        """
        특정 IAM 사용자에게 정책을 연결합니다.
        Args:
            user_name (str): 정책을 연결할 IAM 사용자의 이름.
            policy_arn (str): 연결할 정책의 Amazon 리소스 이름 (ARN).
        """
        return self.client.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)

    def can_paginate(self, operation_name):
        """
        지정한 작업 이름으로 페이징이 가능한지 여부를 확인합니다.
        Args:
            operation_name (str): 확인할 작업 이름.
        """
        return self.client.can_paginate(operation_name)

    def change_password(self, old_password, new_password):
        """
        IAM 사용자의 비밀번호를 변경합니다.
        Args:
            old_password (str): 현재 비밀번호.
            new_password (str): 새로운 비밀번호.
        """
        return self.client.change_password(
            OldPassword=old_password, NewPassword=new_password
        )

    def close(self):
        """
        IAM 클라이언트를 닫습니다.
        """
        self.client.close()

    def create_access_key(self, user_name):
        """
        특정 IAM 사용자에게 액세스 키를 생성합니다.
        Args:
            user_name (str): 액세스 키를 생성할 IAM 사용자의 이름.
        """
        return self.client.create_access_key(UserName=user_name)

    def create_account_alias(self, account_alias):
        """
        AWS 계정에 별칭을 추가합니다.
        Args:
            account_alias (str): 추가할 계정 별칭.
        """
        return self.client.create_account_alias(AccountAlias=account_alias)

    def create_group(self, group_name):
        """
        새로운 IAM 그룹을 생성합니다.
        Args:
            group_name (str): 생성할 IAM 그룹의 이름.
        """
        return self.client.create_group(GroupName=group_name)

    def create_instance_profile(self, instance_profile_name):
        """
        새로운 IAM 인스턴스 프로필을 생성합니다.
        Args:
            instance_profile_name (str): 생성할 IAM 인스턴스 프로필의 이름.
        """
        return self.client.create_instance_profile(
            InstanceProfileName=instance_profile_name
        )

    def create_login_profile(self, user_name, password):
        """
        특정 IAM 사용자의 로그인 프로필을 생성합니다.
        Args:
            user_name (str): 로그인 프로필을 생성할 IAM 사용자의 이름.
            password (str): 사용자의 비밀번호.
        """
        return self.client.create_login_profile(UserName=user_name, Password=password)

    def create_open_id_connect_provider(self, url, thumbprint_list):
        """
        새로운 OpenID Connect 공급자를 생성합니다.
        Args:
            url (str): OpenID Connect 공급자의 URL.
            thumbprint_list (list): OpenID Connect 공급자의 지문 목록.
        """
        return self.client.create_open_id_connect_provider(
            Url=url, ThumbprintList=thumbprint_list
        )

    def create_policy(self, policy_name, policy_document):
        """
        새로운 IAM 정책을 생성합니다.
        Args:
            policy_name (str): 생성할 IAM 정책의 이름.
            policy_document (str): 정책 문서(JSON 형식).
        """
        return self.client.create_policy(
            PolicyName=policy_name, PolicyDocument=policy_document
        )

    def create_policy_version(self, policy_arn, policy_document, set_as_default=False):
        """
        IAM 정책의 새로운 버전을 생성합니다.
        Args:
            policy_arn (str): 새로운 버전을 생성할 IAM 정책의 Amazon 리소스 이름 (ARN).
            policy_document (str): 정책 문서(JSON 형식).
            set_as_default (bool): 새로운 버전을 기본 버전으로 설정할지 여부 (기본값: False).
        """
        return self.client.create_policy_version(
            PolicyArn=policy_arn,
            PolicyDocument=policy_document,
            SetAsDefault=set_as_default,
        )

    def create_role(self, role_name, assume_role_policy_document):
        """
        새로운 IAM 역할을 생성합니다.
        Args:
            role_name (str): 생성할 IAM 역할의 이름.
            assume_role_policy_document (str): 역할을 수행하는 데 사용될 정책 문서(JSON 형식).
        """
        return self.client.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=assume_role_policy_document
        )

    def create_saml_provider(self, saml_metadata_document):
        """
        새로운 SAML 공급자를 생성합니다.
        Args:
            saml_metadata_document (str): SAML 공급자의 메타데이터 문서(XML 형식).
        """
        return self.client.create_saml_provider(
            SAMLMetadataDocument=saml_metadata_document
        )

    def create_service_linked_role(self, aws_service_name, description):
        """
        서비스 링크된 역할을 생성합니다.
        Args:
            aws_service_name (str): 생성할 서비스 링크된 역할의 서비스 이름.
            description (str): 역할에 대한 설명.
        """
        return self.client.create_service_linked_role(
            AWSServiceName=aws_service_name, Description=description
        )

    def create_service_specific_credential(self, user_name, service_name):
        """
        서비스별 자격 증명을 생성합니다.
        Args:
            user_name (str): 서비스별 자격 증명을 생성할 IAM 사용자의 이름.
            service_name (str): 서비스별 자격 증명을 생성할 서비스 이름.
        """
        return self.client.create_service_specific_credential(
            UserName=user_name, ServiceName=service_name
        )

    def create_user(self, user_name):
        """
        새로운 IAM 사용자를 생성합니다.
        Args:
            user_name (str): 생성할 IAM 사용자의 이름.
        """
        return self.client.create_user(UserName=user_name)

    def create_virtual_mfa_device(self, virtual_mfa_device_name):
        """
        가상 MFA 장치를 생성합니다.
        Args:
            virtual_mfa_device_name (str): 생성할 가상 MFA 장치의 이름.
        """
        return self.client.create_virtual_mfa_device(
            VirtualMFADeviceName=virtual_mfa_device_name
        )

        def deactivate_mfa_device(self, user_name, serial_number):
            """
            특정 IAM 사용자의 MFA 장치를 비활성화합니다.
            Args:
                user_name (str): MFA 장치를 비활성화할 IAM 사용자의 이름.
                serial_number (str): 비활성화할 MFA 장치의 일련 번호.
            """

        return self.client.deactivate_mfa_device(
            UserName=user_name, SerialNumber=serial_number
        )

    def delete_access_key(self, user_name, access_key_id):
        """
        특정 IAM 사용자의 액세스 키를 삭제합니다.
        Args:
            user_name (str): 액세스 키를 삭제할 IAM 사용자의 이름.
            access_key_id (str): 삭제할 액세스 키의 ID.
        """
        return self.client.delete_access_key(
            UserName=user_name, AccessKeyId=access_key_id
        )

    def delete_account_alias(self, account_alias):
        """
        AWS 계정에서 계정 별칭을 제거합니다.
        Args:
            account_alias (str): 제거할 계정 별칭.
        """
        return self.client.delete_account_alias(AccountAlias=account_alias)

    def delete_account_password_policy(self):
        """
        AWS 계정에서 비밀번호 정책을 제거합니다.
        """
        return self.client.delete_account_password_policy()

    def delete_group(self, group_name):
        """
        특정 IAM 그룹을 삭제합니다.
        Args:
            group_name (str): 삭제할 IAM 그룹의 이름.
        """
        return self.client.delete_group(GroupName=group_name)

    def delete_group_policy(self, group_name, policy_name):
        """
        특정 IAM 그룹의 정책을 삭제합니다.
        Args:
            group_name (str): 정책을 삭제할 IAM 그룹의 이름.
            policy_name (str): 삭제할 정책의 이름.
        """
        return self.client.delete_group_policy(
            GroupName=group_name, PolicyName=policy_name
        )

    def delete_instance_profile(self, instance_profile_name):
        """
        특정 IAM 인스턴스 프로필을 삭제합니다.
        Args:
            instance_profile_name (str): 삭제할 IAM 인스턴스 프로필의 이름.
        """
        return self.client.delete_instance_profile(
            InstanceProfileName=instance_profile_name
        )

    def delete_login_profile(self, user_name):
        """
        특정 IAM 사용자의 로그인 프로필을 삭제합니다.
        Args:
            user_name (str): 삭제할 IAM 사용자의 이름.
        """
        return self.client.delete_login_profile(UserName=user_name)

    def delete_open_id_connect_provider(self, open_id_connect_provider_arn):
        """
        특정 OpenID Connect 공급자를 삭제합니다.
        Args:
            open_id_connect_provider_arn (str): 삭제할 OpenID Connect 공급자의 ARN.
        """
        return self.client.delete_open_id_connect_provider(
            OpenIDConnectProviderArn=open_id_connect_provider_arn
        )

    def delete_policy(self, policy_arn):
        """
        특정 IAM 정책을 삭제합니다.
        Args:
            policy_arn (str): 삭제할 IAM 정책의 Amazon 리소스 이름 (ARN).
        """
        return self.client.delete_policy(PolicyArn=policy_arn)

    def delete_policy_version(self, policy_arn, version_id):
        """
        특정 IAM 정책의 버전을 삭제합니다.
        Args:
            policy_arn (str): 버전을 삭제할 IAM 정책의 Amazon 리소스 이름 (ARN).
            version_id (str): 삭제할 정책 버전의 ID.
        """
        return self.client.delete_policy_version(
            PolicyArn=policy_arn, VersionId=version_id
        )

    def delete_role(self, role_name):
        """
        특정 IAM 역할을 삭제합니다.
        Args:
            role_name (str): 삭제할 IAM 역할의 이름.
        """
        return self.client.delete_role(RoleName=role_name)

    def delete_role_permissions_boundary(self, role_name):
        """
        특정 IAM 역할의 권한 경계를 삭제합니다.
        Args:
            role_name (str): 권한 경계를 삭제할 IAM 역할의 이름.
        """
        return self.client.delete_role_permissions_boundary(RoleName=role_name)

    def delete_role_policy(self, role_name, policy_name):
        """
        특정 IAM 역할의 정책을 삭제합니다.
        Args:
            role_name (str): 정책을 삭제할 IAM 역할의 이름.
            policy_name (str): 삭제할 정책의 이름.
        """
        return self.client.delete_role_policy(
            RoleName=role_name, PolicyName=policy_name
        )

    def delete_saml_provider(self, saml_provider_arn):
        """
        특정 SAML 공급자를 삭제합니다.
        Args:
            saml_provider_arn (str): 삭제할 SAML 공급자의 ARN.
        """
        return self.client.delete_saml_provider(SAMLProviderArn=saml_provider_arn)

    def delete_server_certificate(self, server_certificate_name):
        """
        특정 서버 인증서를 삭제합니다.
        Args:
            server_certificate_name (str): 삭제할 서버 인증서의 이름.
        """
        return self.client.delete_server_certificate(
            ServerCertificateName=server_certificate_name
        )

    def delete_service_linked_role(self, role_name):
        """
        서비스 링크된 역할을 삭제합니다.
        Args:
            role_name (str): 삭제할 서비스 링크된 역할의 이름.
        """
        return self.client.delete_service_linked_role(RoleName=role_name)

    def delete_service_specific_credential(self, user_name, service_name):
        """
        서비스별 자격 증명을 삭제합니다.
        Args:
            user_name (str): 삭제할 서비스별 자격 증명을 소유한 IAM 사용자의 이름.
            service_name (str): 삭제할 서비스별 자격 증명의 서비스 이름.
        """
        return self.client.delete_service_specific_credential(
            UserName=user_name, ServiceName=service_name
        )

    def delete_signing_certificate(self, user_name, certificate_id):
        """
        특정 사용자의 서명 인증서를 삭제합니다.
        Args:
            user_name (str): 서명 인증서를 삭제할 IAM 사용자의 이름.
            certificate_id (str): 삭제할 서명 인증서의 ID.
        """
        return self.client.delete_signing_certificate(
            UserName=user_name, CertificateId=certificate_id
        )

    def delete_ssh_public_key(self, user_name, ssh_public_key_id):
        """
        특정 IAM 사용자의 SSH 공개 키를 삭제합니다.
        Args:
            user_name (str): SSH 공개 키를 삭제할 IAM 사용자의 이름.
            ssh_public_key_id (str): 삭제할 SSH 공개 키의 ID.
        """
        return self.client.delete_ssh_public_key(
            UserName=user_name, SSHPublicKeyId=ssh_public_key_id
        )

    def delete_user(self, user_name):
        """
        특정 IAM 사용자를 삭제합니다.
        Args:
            user_name (str): 삭제할 IAM 사용자의 이름.
        """
        return self.client.delete_user(UserName=user_name)

    def delete_user_permissions_boundary(self, user_name):
        """
        특정 IAM 사용자의 권한 경계를 삭제합니다.
        Args:
            user_name (str): 권한 경계를 삭제할 IAM 사용자의 이름.
        """
        return self.client.delete_user_permissions_boundary(UserName=user_name)

    def delete_user_policy(self, user_name, policy_name):
        """
        특정 IAM 사용자의 정책을 삭제합니다.
        Args:
            user_name (str): 정책을 삭제할 IAM 사용자의 이름.
            policy_name (str): 삭제할 정책의 이름.
        """
        return self.client.delete_user_policy(
            UserName=user_name, PolicyName=policy_name
        )

    def delete_virtual_mfa_device(self, serial_number):
        """
        특정 가상 MFA 장치를 삭제합니다.
        Args:
            serial_number (str): 삭제할 가상 MFA 장치의 일련 번호.
        """
        return self.client.delete_virtual_mfa_device(SerialNumber=serial_number)

    def detach_group_policy(self, group_name, policy_arn):
        """
        특정 IAM 그룹에서 정책을 분리합니다.
        Args:
            group_name (str): 정책을 분리할 IAM 그룹의 이름.
            policy_arn (str): 분리할 정책의 Amazon 리소스 이름 (ARN).
        """
        return self.client.detach_group_policy(
            GroupName=group_name, PolicyArn=policy_arn
        )

    def detach_role_policy(self, role_name, policy_arn):
        """
        특정 IAM 역할에서 정책을 분리합니다.
        Args:
            role_name (str): 정책을 분리할 IAM 역할의 이름.
            policy_arn (str): 분리할 정책의 Amazon 리소스 이름 (ARN).
        """
        return self.client.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

    def detach_user_policy(self, user_name, policy_arn):
        """
        특정 IAM 사용자에서 정책을 분리합니다.
        Args:
            user_name (str): 정책을 분리할 IAM 사용자의 이름.
            policy_arn (str): 분리할 정책의 Amazon 리소스 이름 (ARN).
        """
        return self.client.detach_user_policy(UserName=user_name, PolicyArn=policy_arn)

    def enable_mfa_device(
        self, user_name, serial_number, authentication_code_1, authentication_code_2
    ):
        """
        특정 IAM 사용자의 MFA(Multi-Factor Authentication) 장치를 활성화합니다.
        Args:
            user_name (str): 활성화할 IAM 사용자의 이름.
            serial_number (str): 활성화할 MFA 장치의 일련 번호.
            authentication_code_1 (str): 첫 번째 인증 코드.
            authentication_code_2 (str): 두 번째 인증 코드.
        """
        return self.client.enable_mfa_device(
            UserName=user_name,
            SerialNumber=serial_number,
            AuthenticationCode1=authentication_code_1,
            AuthenticationCode2=authentication_code_2,
        )

    def generate_credential_report(self):
        """
        IAM 사용자의 자격 증명 보고서를 생성합니다.
        """
        return self.client.generate_credential_report()

    def generate_organizations_access_report(
        self, entity_path=None, organizations_policy_id=None, report_format="TXT"
    ):
        """
        조직 엑세스 보고서를 생성합니다.
        Args:
            entity_path (str): 보고서 생성에 포함할 조직 엔터티의 경로.
            organizations_policy_id (str): 생성할 보고서에 대한 정책 ID.
            report_format (str): 생성할 보고서 형식 (기본값: 'TXT', 'CSV' 또는 'TXT' 선택 가능).
        """
        return self.client.generate_organizations_access_report(
            EntityPath=entity_path,
            OrganizationsPolicyId=organizations_policy_id,
            ReportFormat=report_format,
        )

    def generate_service_last_accessed_details(self, job_id=None):
        """
        서비스의 마지막 액세스 세부 정보를 생성합니다.
        Args:
            job_id (str): 세부 정보 생성 작업의 ID.
        """
        return self.client.generate_service_last_accessed_details(JobId=job_id)

    def get_access_key_last_used(self, access_key_id):
        """
        특정 액세스 키의 마지막 사용 정보를 가져옵니다.
        Args:
            access_key_id (str): 정보를 조회할 액세스 키의 ID.
        """
        return self.client.get_access_key_last_used(AccessKeyId=access_key_id)

    def get_account_authorization_details(self, filter=None):
        """
        AWS 계정의 권한 상세 정보를 가져옵니다.
        Args:
            filter (list): 가져올 상세 정보 유형의 목록 (기본값: 모든 유형 가져옴).
        """
        return self.client.get_account_authorization_details(Filter=filter)

    def get_account_password_policy(self):
        """
        AWS 계정의 비밀번호 정책을 가져옵니다.
        """
        return self.client.get_account_password_policy()

    def get_account_summary(self):
        """
        AWS 계정의 요약 정보를 가져옵니다.
        """
        return self.client.get_account_summary()

    def get_context_keys_for_custom_policy(self, policy_input_list):
        """
        사용자 지정 정책을 위한 컨텍스트 키를 가져옵니다.
        Args:
            policy_input_list (list): 컨텍스트 키를 가져올 정책 입력 목록.
        """
        return self.client.get_context_keys_for_custom_policy(
            PolicyInputList=policy_input_list
        )

    def get_context_keys_for_principal_policy(
        self, policy_source_arn, policy_input_list
    ):
        """
        주체 정책에 대한 컨텍스트 키를 가져옵니다.
        Args:
            policy_source_arn (str): 정책의 소스 ARN.
            policy_input_list (list): 컨텍스트 키를 가져올 정책 입력 목록.
        """
        return self.client.get_context_keys_for_principal_policy(
            PolicySourceArn=policy_source_arn, PolicyInputList=policy_input_list
        )

    def get_credential_report(self):
        """
        IAM 사용자의 자격 증명 보고서를 가져옵니다.
        """
        return self.client.get_credential_report()

    def get_group(self, group_name):
        """
        특정 IAM 그룹의 정보를 가져옵니다.
        Args:
            group_name (str): 정보를 조회할 IAM 그룹의 이름.
        """
        return self.client.get_group(GroupName=group_name)

    def get_group_policy(self, group_name, policy_name):
        """
        특정 IAM 그룹의 정책을 가져옵니다.
        Args:
            group_name (str): 정책을 가져올 IAM 그룹의 이름.
            policy_name (str): 가져올 정책의 이름.
        """
        return self.client.get_group_policy(
            GroupName=group_name, PolicyName=policy_name
        )

    def get_instance_profile(self, instance_profile_name):
        """
        특정 IAM 인스턴스 프로필의 정보를 가져옵니다.
        Args:
            instance_profile_name (str): 정보를 조회할 IAM 인스턴스 프로필의 이름.
        """
        return self.client.get_instance_profile(
            InstanceProfileName=instance_profile_name
        )

    def get_login_profile(self, user_name):
        """
        특정 IAM 사용자의 로그인 프로필 정보를 가져옵니다.
        Args:
            user_name (str): 정보를 조회할 IAM 사용자의 이름.
        """
        return self.client.get_login_profile(UserName=user_name)

    def get_mfa_device(self, user_name, serial_number):
        """
        특정 IAM 사용자의 MFA(Multi-Factor Authentication) 장치 정보를 가져옵니다.
        Args:
            user_name (str): 정보를 조회할 IAM 사용자의 이름.
            serial_number (str): 정보를 조회할 MFA 장치의 일련 번호.
        """
        return self.client.get_mfa_device(
            UserName=user_name, SerialNumber=serial_number
        )

    def get_open_id_connect_provider(self, open_id_connect_provider_arn):
        """
        특정 OpenID Connect 공급자 정보를 가져옵니다.
        Args:
            open_id_connect_provider_arn (str): 정보를 조회할 OpenID Connect 공급자의 ARN.
        """
        return self.client.get_open_id_connect_provider(
            OpenIDConnectProviderArn=open_id_connect_provider_arn
        )

    def get_organizations_access_report(
        self, entity_path=None, organizations_policy_id=None, report_format="TXT"
    ):
        """
        조직 엑세스 보고서를 가져옵니다.
        Args:
            entity_path (str): 보고서를 가져올 조직 엔터티의 경로.
            organizations_policy_id (str): 가져올 보고서에 대한 정책 ID.
            report_format (str): 가져올 보고서 형식 (기본값: 'TXT', 'CSV' 또는 'TXT' 선택 가능).
        """
        return self.client.get_organizations_access_report(
            EntityPath=entity_path,
            OrganizationsPolicyId=organizations_policy_id,
            ReportFormat=report_format,
        )

    def get_paginator(self, operation_name):
        """
        지정한 작업에 대한 paginator를 가져옵니다.
        Args:
            operation_name (str): paginator를 가져올 작업의 이름.
        """
        return self.client.get_paginator(operation_name)

    def get_policy(self, policy_arn):
        """
        특정 IAM 정책의 정보를 가져옵니다.
        Args:
            policy_arn (str): 정보를 조회할 IAM 정책의 Amazon 리소스 이름 (ARN).
        """
        return self.client.get_policy(PolicyArn=policy_arn)

    def get_policy_version(self, policy_arn, version_id):
        """
        특정 IAM 정책의 버전 정보를 가져옵니다.
        Args:
            policy_arn (str): 정보를 조회할 IAM 정책의 Amazon 리소스 이름 (ARN).
            version_id (str): 정보를 조회할 정책 버전의 ID.
        """
        return self.client.get_policy_version(
            PolicyArn=policy_arn, VersionId=version_id
        )

    def get_role(self, role_name):
        """
        특정 IAM 역할의 정보를 가져옵니다.
        Args:
            role_name (str): 정보를 조회할 IAM 역할의 이름.
        """
        return self.client.get_role(RoleName=role_name)

    def get_role_policy(self, role_name, policy_name):
        """
        특정 IAM 역할의 정책 정보를 가져옵니다.
        Args:
            role_name (str): 정보를 조회할 IAM 역할의 이름.
            policy_name (str): 가져올 정책의 이름.
        """
        return self.client.get_role_policy(RoleName=role_name, PolicyName=policy_name)

    def get_saml_provider(self, saml_provider_arn):
        """
        특정 SAML 공급자 정보를 가져옵니다.
        Args:
            saml_provider_arn (str): 정보를 조회할 SAML 공급자의 ARN.
        """
        return self.client.get_saml_provider(SAMLProviderArn=saml_provider_arn)

    def get_server_certificate(self, server_certificate_name):
        """
        특정 서버 인증서 정보를 가져옵니다.
        Args:
            server_certificate_name (str): 정보를 조회할 서버 인증서의 이름.
        """
        return self.client.get_server_certificate(
            ServerCertificateName=server_certificate_name
        )

    def get_service_last_accessed_details(self, job_id):
        """
        서비스의 마지막 액세스 세부 정보를 가져옵니다.
        Args:
            job_id (str): 정보를 조회할 작업의 ID.
        """
        return self.client.get_service_last_accessed_details(JobId=job_id)

    def get_service_last_accessed_details_with_entities(
        self, job_id, service_namespace=None
    ):
        """
        서비스의 마지막 액세스 세부 정보를 엔터티와 함께 가져옵니다.
        Args:
            job_id (str): 정보를 조회할 작업의 ID.
            service_namespace (str): 세부 정보를 가져올 서비스 네임스페이스 (옵션).
        """
        return self.client.get_service_last_accessed_details_with_entities(
            JobId=job_id, ServiceNamespace=service_namespace
        )

    def get_service_linked_role_deletion_status(self, deletion_task_id):
        """
        서비스 링크된 역할 삭제 상태를 가져옵니다.
        Args:
            deletion_task_id (str): 삭제 상태를 조회할 작업 ID.
        """
        return self.client.get_service_linked_role_deletion_status(
            DeletionTaskId=deletion_task_id
        )

    def get_ssh_public_key(self, user_name, ssh_public_key_id):
        """
        특정 IAM 사용자의 SSH 공개 키 정보를 가져옵니다.
        Args:
            user_name (str): 정보를 조회할 IAM 사용자의 이름.
            ssh_public_key_id (str): 정보를 조회할 SSH 공개 키의 ID.
        """
        return self.client.get_ssh_public_key(
            UserName=user_name, SSHPublicKeyId=ssh_public_key_id
        )

    def get_user(self, user_name):
        """
        특정 IAM 사용자의 정보를 가져옵니다.
        Args:
            user_name (str): 정보를 조회할 IAM 사용자의 이름.
        """
        return self.client.get_user(UserName=user_name)

    def get_user_policy(self, user_name, policy_name):
        """
        특정 IAM 사용자의 정책 정보를 가져옵니다.
        Args:
            user_name (str): 정보를 조회할 IAM 사용자의 이름.
            policy_name (str): 가져올 정책의 이름.
        """
        return self.client.get_user_policy(UserName=user_name, PolicyName=policy_name)

    def get_waiter(self, waiter_name):
        """
        지정한 웨이터를 가져옵니다.
        Args:
            waiter_name (str): 가져올 웨이터의 이름.
        """
        return self.client.get_waiter(waiter_name)

    def list_access_keys(self, user_name):
        """
        특정 IAM 사용자의 액세스 키 목록을 반환합니다.
        Args:
            user_name (str): IAM 사용자의 이름.
        """

        return self.client.list_access_keys(UserName=user_name)

    def list_account_aliases(self):
        """
        모든 IAM 계정 별명을 반환합니다.
        """
        return self.client.list_account_aliases()

    def list_attached_group_policies(self, group_name):
        """
        특정 IAM 그룹에 연결된 정책 목록을 반환합니다.
        Args:
            group_name (str): IAM 그룹의 이름.
        """
        return self.client.list_attached_group_policies(GroupName=group_name)

    def list_attached_role_policies(self, role_name):
        """
        특정 IAM 역할에 연결된 정책 목록을 반환합니다.
        Args:
            role_name (str): IAM 역할의 이름.
        """
        return self.client.list_attached_role_policies(RoleName=role_name)

    def list_attached_user_policies(self, user_name):
        """
        특정 IAM 사용자에 연결된 정책 목록을 반환합니다.
        Args:
            user_name (str): IAM 사용자의 이름.
        """
        return self.client.list_attached_user_policies(UserName=user_name)

    def list_entities_for_policy(self, policy_arn):
        """
        특정 정책과 연관된 엔터티 (사용자, 그룹, 역할) 목록을 반환합니다.
        Args:
            policy_arn (str): 정책의 Amazon 리소스 이름 (ARN).
        """
        return self.client.list_entities_for_policy(PolicyArn=policy_arn)

    def list_group_policies(self, group_name):
        """
        특정 IAM 그룹에 연결된 정책 목록을 반환합니다.
        Args:
            group_name (str): IAM 그룹의 이름.
        """
        return self.client.list_group_policies(GroupName=group_name)

    def list_groups(self):
        """
        모든 IAM 그룹을 반환합니다.
        """
        return self.client.list_groups()

    def list_groups_for_user(self, user_name):
        """
        특정 IAM 사용자와 연관된 그룹 목록을 반환합니다.
        Args:
            user_name (str): IAM 사용자의 이름.
        """
        return self.client.list_groups_for_user(UserName=user_name)

    def list_instance_profile_tags(self, instance_profile_name):
        """
        특정 인스턴스 프로필의 태그 목록을 반환합니다.
        Args:
            instance_profile_name (str): 인스턴스 프로필의 이름.
        """
        return self.client.list_instance_profile_tags(
            InstanceProfileName=instance_profile_name
        )

    def list_instance_profiles(self):
        """
        모든 IAM 인스턴스 프로필을 반환합니다.
        """
        return self.client.list_instance_profiles()

    def list_instance_profiles_for_role(self, role_name):
        """
        특정 IAM 역할과 연관된 인스턴스 프로필 목록을 반환합니다.
        Args:
            role_name (str): IAM 역할의 이름.
        """
        return self.client.list_instance_profiles_for_role(RoleName=role_name)

    def list_mfa_device_tags(self, serial_number):
        """
        특정 MFA 장치의 태그 목록을 반환합니다.
        Args:
            serial_number (str): MFA 장치의 일련번호.
        """
        return self.client.list_mfa_device_tags(SerialNumber=serial_number)

    def list_mfa_devices(self, user_name):
        """
        특정 IAM 사용자의 MFA 장치 목록을 반환합니다.
        Args:
            user_name (str): IAM 사용자의 이름.
        """
        return self.client.list_mfa_devices(UserName=user_name)

    def list_open_id_connect_provider_tags(self, open_id_connect_provider_arn):
        """
        특정 OpenID Connect 공급자의 태그 목록을 반환합니다.
        Args:
            open_id_connect_provider_arn (str): OpenID Connect 공급자의 ARN.
        """
        return self.client.list_open_id_connect_provider_tags(
            OpenIDConnectProviderArn=open_id_connect_provider_arn
        )

    def list_open_id_connect_providers(self):
        """
        모든 OpenID Connect 공급자를 반환합니다.
        """
        return self.client.list_open_id_connect_providers()

    def list_policies(self):
        """
        모든 IAM 정책을 반환합니다.
        """
        return self.client.list_policies()

    def list_policies_granting_service_access(self, service_name):
        """
        특정 AWS 서비스에 대한 액세스를 부여하는 정책 목록을 반환합니다.
        Args:
            service_name (str): AWS 서비스의 이름.
        """
        return self.client.list_policies_granting_service_access(
            ServiceName=service_name
        )

    def list_policy_tags(self, policy_arn):
        """
        특정 IAM 정책의 태그 목록을 반환합니다.
        Args:
            policy_arn (str): 정책의 Amazon 리소스 이름 (ARN).
        """
        return self.client.list_policy_tags(PolicyArn=policy_arn)

    def list_policy_versions(self, policy_arn):
        """
        특정 IAM 정책의 버전 목록을 반환합니다.
        Args:
            policy_arn (str): 정책의 Amazon 리소스 이름 (ARN).
        """
        return self.client.list_policy_versions(PolicyArn=policy_arn)

    def list_role_policies(self, role_name):
        """
        특정 IAM 역할에 연결된 정책 목록을 반환합니다.
        Args:
            role_name (str): IAM 역할의 이름.
        """
        return self.client.list_role_policies(RoleName=role_name)

    def list_role_tags(self, role_name):
        """
        특정 IAM 역할의 태그 목록을 반환합니다.
        Args:
            role_name (str): IAM 역할의 이름.
        """
        return self.client.list_role_tags(RoleName=role_name)

    def list_roles(self):
        """
        모든 IAM 역할을 반환합니다.
        """
        return self.client.list_roles()

    def list_saml_provider_tags(self, saml_provider_arn):
        """
        특정 SAML 공급자의 태그 목록을 반환합니다.
        Args:
            saml_provider_arn (str): SAML 공급자의 ARN.
        """
        return self.client.list_saml_provider_tags(SAMLProviderArn=saml_provider_arn)

    def list_saml_providers(self):
        """
        모든 SAML 공급자를 반환합니다.
        """
        return self.client.list_saml_providers()

    def list_server_certificate_tags(self, server_certificate_name):
        """
        특정 서버 인증서의 태그 목록을 반환합니다.
        Args:
            server_certificate_name (str): 서버 인증서의 이름.
        """
        return self.client.list_server_certificate_tags(
            ServerCertificateName=server_certificate_name
        )

    def list_server_certificates(self):
        """
        모든 IAM 서버 인증서를 반환합니다.
        """
        return self.client.list_server_certificates()

    def list_service_specific_credentials(self, user_name):
        """
        특정 IAM 사용자의 서비스별 자격 증명 목록을 반환합니다.
        Args:
            user_name (str): IAM 사용자의 이름.
        """
        return self.client.list_service_specific_credentials(UserName=user_name)

    def list_signing_certificates(self, user_name):
        """
        특정 IAM 사용자의 서명 인증서 목록을 반환합니다.
        Args:
            user_name (str): IAM 사용자의 이름.
        """
        return self.client.list_signing_certificates(UserName=user_name)

    def list_ssh_public_keys(self, user_name):
        """
        특정 IAM 사용자의 SSH 공개 키 목록을 반환합니다.
        Args:
            user_name (str): IAM 사용자의 이름.
        """
        return self.client.list_ssh_public_keys(UserName=user_name)

    def list_user_policies(self, user_name):
        """
        특정 IAM 사용자에 대한 인라인 정책 목록을 반환합니다.
        Args:
            user_name (str): IAM 사용자의 이름.
        """
        return self.client.list_user_policies(UserName=user_name)

    def list_user_tags(self, user_name):
        """
        특정 IAM 사용자의 태그 목록을 반환합니다.
        Args:
            user_name (str): IAM 사용자의 이름.
        """
        return self.client.list_user_tags(UserName=user_name)

    def list_users(self):
        """
        모든 IAM 사용자를 반환합니다.
        """
        return self.client.list_users()

    def list_virtual_mfa_devices(self):
        """
        모든 가상 MFA 장치를 반환합니다.
        """
        return self.client.list_virtual_mfa_devices()

    def put_group_policy(self, group_name, policy_name, policy_document):
        """
        특정 IAM 그룹에 정책을 추가합니다.
        Args:
            group_name (str): 정책을 추가할 IAM 그룹의 이름.
            policy_name (str): 추가할 정책의 이름.
            policy_document (str): 추가할 정책의 JSON 형식 문서.
        """
        return self.client.put_group_policy(
            GroupName=group_name, PolicyName=policy_name, PolicyDocument=policy_document
        )

    def put_role_permissions_boundary(self, role_name, permissions_boundary):
        """
        특정 IAM 역할의 권한 경계를 설정합니다.
        Args:
            role_name (str): 권한 경계를 설정할 IAM 역할의 이름.
            permissions_boundary (str): 설정할 권한 경계의 JSON 형식 문서.
        """
        return self.client.put_role_permissions_boundary(
            RoleName=role_name, PermissionsBoundary=permissions_boundary
        )

    def put_role_policy(self, role_name, policy_name, policy_document):
        """
        특정 IAM 역할에 정책을 추가합니다.
        Args:
            role_name (str): 정책을 추가할 IAM 역할의 이름.
            policy_name (str): 추가할 정책의 이름.
            policy_document (str): 추가할 정책의 JSON 형식 문서.
        """
        return self.client.put_role_policy(
            RoleName=role_name, PolicyName=policy_name, PolicyDocument=policy_document
        )

    def put_user_permissions_boundary(self, user_name, permissions_boundary):
        """
        특정 IAM 사용자의 권한 경계를 설정합니다.
        Args:
            user_name (str): 권한 경계를 설정할 IAM 사용자의 이름.
            permissions_boundary (str): 설정할 권한 경계의 JSON 형식 문서.
        """
        return self.client.put_user_permissions_boundary(
            UserName=user_name, PermissionsBoundary=permissions_boundary
        )

    def put_user_policy(self, user_name, policy_name, policy_document):
        """
        특정 IAM 사용자에 정책을 추가합니다.
        Args:
            user_name (str): 정책을 추가할 IAM 사용자의 이름.
            policy_name (str): 추가할 정책의 이름.
            policy_document (str): 추가할 정책의 JSON 형식 문서.
        """
        return self.client.put_user_policy(
            UserName=user_name, PolicyName=policy_name, PolicyDocument=policy_document
        )

    def remove_role_from_instance_profile(self, instance_profile_name, role_name):
        """
        특정 IAM 인스턴스 프로필에서 IAM 역할을 제거합니다.
        Args:
            instance_profile_name (str): IAM 역할을 제거할 IAM 인스턴스 프로필의 이름.
            role_name (str): 제거할 IAM 역할의 이름.
        """
        return self.client.remove_role_from_instance_profile(
            InstanceProfileName=instance_profile_name, RoleName=role_name
        )

    def remove_user_from_group(self, user_name, group_name):
        """
        특정 IAM 사용자를 IAM 그룹에서 제거합니다.
        Args:
            user_name (str): 제거할 IAM 사용자의 이름.
            group_name (str): 제거할 IAM 그룹의 이름.
        """
        return self.client.remove_user_from_group(
            UserName=user_name, GroupName=group_name
        )

    def reset_service_specific_credential(self, user_name, service_name):
        """
        특정 사용자의 서비스별 자격 증명을 재설정합니다.
        Args:
            user_name (str): 서비스별 자격 증명을 재설정할 IAM 사용자의 이름.
            service_name (str): 재설정할 서비스의 이름.
        """
        return self.client.reset_service_specific_credential(
            UserName=user_name, ServiceName=service_name
        )

    def resync_mfa_device(self, user_name, serial_number):
        """
        특정 IAM 사용자의 MFA(Multi-Factor Authentication) 장치를 동기화합니다.
        Args:
            user_name (str): 동기화할 IAM 사용자의 이름.
            serial_number (str): 동기화할 MFA 장치의 일련 번호.
        """
        return self.client.resync_mfa_device(
            UserName=user_name, SerialNumber=serial_number
        )

    def set_default_policy_version(self, policy_arn, version_id):
        """
        특정 IAM 정책의 기본 버전을 설정합니다.
        Args:
            policy_arn (str): 기본 버전으로 설정할 IAM 정책의 Amazon 리소스 이름 (ARN).
            version_id (str): 기본 버전으로 설정할 정책 버전의 ID.
        """
        return self.client.set_default_policy_version(
            PolicyArn=policy_arn, VersionId=version_id
        )

    def set_security_token_service_preferences(
        self, global_endpoint_token_version, endpoint_token_version
    ):
        """
        보안 토큰 서비스 환경 설정을 업데이트합니다.
        Args:
            global_endpoint_token_version (str): 글로벌 엔드포인트의 토큰 버전.
            endpoint_token_version (str): 엔드포인트의 토큰 버전.
        """
        return self.client.set_security_token_service_preferences(
            GlobalEndpointTokenVersion=global_endpoint_token_version,
            EndpointTokenVersion=endpoint_token_version,
        )

    def simulate_custom_policy(self, policy_input_list, action_names):
        """
        사용자 지정 정책 시뮬레이션을 수행합니다.
        Args:
            policy_input_list (list): 시뮬레이션할 정책 입력 목록.
            action_names (list): 시뮬레이션할 액션 이름 목록.
        """
        return self.client.simulate_custom_policy(
            PolicyInputList=policy_input_list, ActionNames=action_names
        )

    def simulate_principal_policy(self, policy_source_arn, action_names):
        """
        주체 정책 시뮬레이션을 수행합니다.
        Args:
            policy_source_arn (str): 정책의 소스 ARN.
            action_names (list): 시뮬레이션할 액션 이름 목록.
        """
        return self.client.simulate_principal_policy(
            PolicySourceArn=policy_source_arn, ActionNames=action_names
        )

    def tag_instance_profile(self, instance_profile_name, tags):
        """
        특정 IAM 인스턴스 프로필에 태그를 추가합니다.
        Args:
            instance_profile_name (str): 태그를 추가할 IAM 인스턴스 프로필의 이름.
            tags (list): 추가할 태그 목록.
        """
        return self.client.tag_instance_profile(
            InstanceProfileName=instance_profile_name, Tags=tags
        )

    def tag_mfa_device(self, serial_number, tags):
        """
        특정 IAM MFA(Multi-Factor Authentication) 장치에 태그를 추가합니다.
        Args:
            serial_number (str): 태그를 추가할 MFA 장치의 일련 번호.
            tags (list): 추가할 태그 목록.
        """
        return self.client.tag_mfa_device(SerialNumber=serial_number, Tags=tags)

    def tag_open_id_connect_provider(self, open_id_connect_provider_arn, tags):
        """
        특정 OpenID Connect 공급자에 태그를 추가합니다.
        Args:
            open_id_connect_provider_arn (str): 태그를 추가할 OpenID Connect 공급자의 ARN.
            tags (list): 추가할 태그 목록.
        """
        return self.client.tag_open_id_connect_provider(
            OpenIDConnectProviderArn=open_id_connect_provider_arn, Tags=tags
        )

    def tag_policy(self, policy_arn, tags):
        """
        특정 IAM 정책에 태그를 추가합니다.
        Args:
            policy_arn (str): 태그를 추가할 IAM 정책의 Amazon 리소스 이름 (ARN).
            tags (list): 추가할 태그 목록.
        """
        return self.client.tag_policy(PolicyArn=policy_arn, Tags=tags)

    def tag_role(self, role_name, tags):
        """
        특정 IAM 역할에 태그를 추가합니다.
        Args:
            role_name (str): 태그를 추가할 IAM 역할의 이름.
            tags (list): 추가할 태그 목록.
        """
        return self.client.tag_role(RoleName=role_name, Tags=tags)

    def tag_saml_provider(self, saml_provider_arn, tags):
        """
        특정 SAML 공급자에 태그를 추가합니다.
        Args:
            saml_provider_arn (str): 태그를 추가할 SAML 공급자의 ARN.
            tags (list): 추가할 태그 목록.
        """
        return self.client.tag_saml_provider(
            SAMLProviderArn=saml_provider_arn, Tags=tags
        )

    def tag_server_certificate(self, server_certificate_name, tags):
        """
        특정 서버 인증서에 태그를 추가합니다.
        Args:
            server_certificate_name (str): 태그를 추가할 서버 인증서의 이름.
            tags (list): 추가할 태그 목록.
        """
        return self.client.tag_server_certificate(
            ServerCertificateName=server_certificate_name, Tags=tags
        )

    def tag_user(self, user_name, tags):
        """
        특정 IAM 사용자에 태그를 추가합니다.
        Args:
            user_name (str): 태그를 추가할 IAM 사용자의 이름.
            tags (list): 추가할 태그 목록.
        """
        return self.client.tag_user(UserName=user_name, Tags=tags)

    def untag_instance_profile(self, instance_profile_name, tag_keys):
        """
        특정 IAM 인스턴스 프로필에서 지정한 태그를 제거합니다.
        Args:
            instance_profile_name (str): 태그를 제거할 IAM 인스턴스 프로필의 이름.
            tag_keys (list): 제거할 태그 키 목록.
        """
        return self.client.untag_instance_profile(
            InstanceProfileName=instance_profile_name, TagKeys=tag_keys
        )

    def untag_mfa_device(self, serial_number, tag_keys):
        """
        특정 IAM MFA(Multi-Factor Authentication) 장치에서 지정한 태그를 제거합니다.
        Args:
            serial_number (str): 태그를 제거할 MFA 장치의 일련 번호.
            tag_keys (list): 제거할 태그 키 목록.
        """
        return self.client.untag_mfa_device(
            SerialNumber=serial_number, TagKeys=tag_keys
        )

    def untag_open_id_connect_provider(self, open_id_connect_provider_arn, tag_keys):
        """
        특정 OpenID Connect 공급자에서 지정한 태그를 제거합니다.
        Args:
            open_id_connect_provider_arn (str): 태그를 제거할 OpenID Connect 공급자의 ARN.
            tag_keys (list): 제거할 태그 키 목록.
        """
        return self.client.untag_open_id_connect_provider(
            OpenIDConnectProviderArn=open_id_connect_provider_arn, TagKeys=tag_keys
        )

    def untag_policy(self, policy_arn, tag_keys):
        """
        특정 IAM 정책에서 지정한 태그를 제거합니다.
        Args:
            policy_arn (str): 태그를 제거할 IAM 정책의 Amazon 리소스 이름 (ARN).
            tag_keys (list): 제거할 태그 키 목록.
        """
        return self.client.untag_policy(PolicyArn=policy_arn, TagKeys=tag_keys)

    def untag_role(self, role_name, tag_keys):
        """
        특정 IAM 역할에서 지정한 태그를 제거합니다.
        Args:
            role_name (str): 태그를 제거할 IAM 역할의 이름.
            tag_keys (list): 제거할 태그 키 목록.
        """
        return self.client.untag_role(RoleName=role_name, TagKeys=tag_keys)

    def untag_saml_provider(self, saml_provider_arn, tag_keys):
        """
        특정 SAML 공급자에서 지정한 태그를 제거합니다.
        Args:
            saml_provider_arn (str): 태그를 제거할 SAML 공급자의 ARN.
            tag_keys (list): 제거할 태그 키 목록.
        """
        return self.client.untag_saml_provider(
            SAMLProviderArn=saml_provider_arn, TagKeys=tag_keys
        )

    def untag_server_certificate(self, server_certificate_name, tag_keys):
        """
        특정 서버 인증서에서 지정한 태그를 제거합니다.
        Args:
            server_certificate_name (str): 태그를 제거할 서버 인증서의 이름.
            tag_keys (list): 제거할 태그 키 목록.
        """
        return self.client.untag_server_certificate(
            ServerCertificateName=server_certificate_name, TagKeys=tag_keys
        )

    def untag_user(self, user_name, tag_keys):
        """
        특정 IAM 사용자에서 지정한 태그를 제거합니다.
        Args:
            user_name (str): 태그를 제거할 IAM 사용자의 이름.
            tag_keys (list): 제거할 태그 키 목록.
        """
        return self.client.untag_user(UserName=user_name, TagKeys=tag_keys)

    def update_access_key(self, user_name, access_key_id, status):
        """
        특정 IAM 사용자의 액세스 키 상태를 업데이트합니다.
        Args:
            user_name (str): 액세스 키 상태를 업데이트할 IAM 사용자의 이름.
            access_key_id (str): 업데이트할 액세스 키의 ID.
            status (str): 업데이트할 액세스 키의 상태 ('Active' 또는 'Inactive').
        """
        return self.client.update_access_key(
            UserName=user_name, AccessKeyId=access_key_id, Status=status
        )

    def update_account_password_policy(
        self,
        minimum_password_length=None,
        require_symbols=None,
        require_numbers=None,
        require_uppercase_characters=None,
        require_lowercase_characters=None,
        allow_users_to_change_password=None,
        max_password_age=None,
        password_reuse_prevention=None,
        hard_expiry=None,
    ):
        """
        AWS 계정의 비밀번호 정책을 업데이트합니다.
        Args (옵션):
            minimum_password_length (int): 비밀번호의 최소 길이 (6 이상).
            require_symbols (bool): 특수 문자가 필요한지 여부.
            require_numbers (bool): 숫자가 필요한지 여부.
            require_uppercase_characters (bool): 대문자가 필요한지 여부.
            require_lowercase_characters (bool): 소문자가 필요한지 여부.
            allow_users_to_change_password (bool): 사용자가 비밀번호를 변경할 수 있는지 여부.
            max_password_age (int): 비밀번호 만료 기간 (0 또는 1 이상).
            password_reuse_prevention (int): 이전 비밀번호 재사용을 방지할 횟수 (0 또는 1 이상).
            hard_expiry (bool): 강제 비밀번호 만료 여부.
        """
        policy_params = {
            "MinimumPasswordLength": minimum_password_length,
            "RequireSymbols": require_symbols,
            "RequireNumbers": require_numbers,
            "RequireUppercaseCharacters": require_uppercase_characters,
            "RequireLowercaseCharacters": require_lowercase_characters,
            "AllowUsersToChangePassword": allow_users_to_change_password,
            "MaxPasswordAge": max_password_age,
            "PasswordReusePrevention": password_reuse_prevention,
            "HardExpiry": hard_expiry,
        }

        return self.client.update_account_password_policy(
            **{k: v for k, v in policy_params.items() if v is not None}
        )

    def update_assume_role_policy(self, role_name, policy_document):
        """
        특정 IAM 역할의 신뢰 정책을 업데이트합니다.
        Args:
            role_name (str): 업데이트할 IAM 역할의 이름.
            policy_document (str): 업데이트할 신뢰 정책의 JSON 형식 문서.
        """
        return self.client.update_assume_role_policy(
            RoleName=role_name, PolicyDocument=policy_document
        )

    def update_group(self, group_name, new_path=None, new_group_name=None):
        """
        특정 IAM 그룹의 정보를 업데이트합니다.
        Args (옵션):
            group_name (str): 업데이트할 IAM 그룹의 이름.
            new_path (str): 그룹의 새 경로.
            new_group_name (str): 그룹의 새 이름.
        """
        group_params = {
            "GroupName": group_name,
            "NewPath": new_path,
            "NewGroupName": new_group_name,
        }

        return self.client.update_group(
            **{k: v for k, v in group_params.items() if v is not None}
        )

    def update_login_profile(
        self, user_name, password=None, password_reset_required=None
    ):
        """
        특정 IAM 사용자의 로그인 프로필을 업데이트합니다.
        Args (옵션):
            user_name (str): 업데이트할 IAM 사용자의 이름.
            password (str): 새 비밀번호.
            password_reset_required (bool): 다음 로그인 시 비밀번호 재설정이 필요한지 여부.
        """
        profile_params = {
            "UserName": user_name,
            "Password": password,
            "PasswordResetRequired": password_reset_required,
        }

        return self.client.update_login_profile(
            **{k: v for k, v in profile_params.items() if v is not None}
        )

    def update_role(
        self,
        role_name,
        new_path=None,
        new_role_name=None,
        description=None,
        max_session_duration=None,
    ):
        """
        특정 IAM 역할의 정보를 업데이트합니다.
        Args (옵션):
            role_name (str): 업데이트할 IAM 역할의 이름.
            new_path (str): 역할의 새 경로.
            new_role_name (str): 역할의 새 이름.
            description (str): 역할의 새 설명.
            max_session_duration (int): 역할의 세션 최대 지속 시간 (3600에서 43200 사이).
        """
        role_params = {
            "RoleName": role_name,
            "NewPath": new_path,
            "NewRoleName": new_role_name,
            "Description": description,
            "MaxSessionDuration": max_session_duration,
        }

        return self.client.update_role(
            **{k: v for k, v in role_params.items() if v is not None}
        )

    def update_role_description(self, role_name, description):
        """
        특정 IAM 역할의 설명을 업데이트합니다.
        Args:
            role_name (str): 업데이트할 IAM 역할의 이름.
            description (str): 역할의 새 설명.
        """
        return self.client.update_role_description(
            RoleName=role_name, Description=description
        )

    def update_saml_provider(self, saml_provider_arn, sso_url, metadata_document):
        """
        특정 SAML 공급자의 정보를 업데이트합니다.
        Args:
            saml_provider_arn (str): 업데이트할 SAML 공급자의 ARN.
            sso_url (str): SSO(Single Sign-On) URL.
            metadata_document (str): 메타데이터 문서.
        """
        return self.client.update_saml_provider(
            SAMLProviderArn=saml_provider_arn,
            SsoUrl=sso_url,
            MetadataDocument=metadata_document,
        )

    def update_server_certificate(
        self, server_certificate_name, new_path=None, new_server_certificate_name=None
    ):
        """
        특정 서버 인증서의 정보를 업데이트합니다.
        Args (옵션):
            server_certificate_name (str): 업데이트할 서버 인증서의 이름.
            new_path (str): 인증서의 새 경로.
            new_server_certificate_name (str): 인증서의 새 이름.
        """
        cert_params = {
            "ServerCertificateName": server_certificate_name,
            "NewPath": new_path,
            "NewServerCertificateName": new_server_certificate_name,
        }

        return self.client.update_server_certificate(
            **{k: v for k, v in cert_params.items() if v is not None}
        )

    def update_service_specific_credential(self, user_name, service_name, status):
        """
        특정 사용자의 서비스별 자격 증명 상태를 업데이트합니다.
        Args:
            user_name (str): 업데이트할 IAM 사용자의 이름.
            service_name (str): 업데이트할 서비스의 이름.
            status (str): 업데이트할 서비스별 자격 증명의 상태 ('Active' 또는 'Inactive').
        """
        return self.client.update_service_specific_credential(
            UserName=user_name, ServiceName=service_name, Status=status
        )

    def update_signing_certificate(self, user_name, certificate_id, status):
        """
        특정 사용자의 서명 인증서 상태를 업데이트합니다.
        Args:
            user_name (str): 업데이트할 IAM 사용자의 이름.
            certificate_id (str): 업데이트할 서명 인증서의 ID.
            status (str): 업데이트할 서명 인증서의 상태 ('Active' 또는 'Inactive').
        """
        return self.client.update_signing_certificate(
            UserName=user_name, CertificateId=certificate_id, Status=status
        )

    def update_ssh_public_key(self, user_name, ssh_public_key_id, status):
        """
        특정 사용자의 SSH 공개 키 상태를 업데이트합니다.
        Args:
            user_name (str): 업데이트할 IAM 사용자의 이름.
            ssh_public_key_id (str): 업데이트할 SSH 공개 키의 ID.
            status (str): 업데이트할 SSH 공개 키의 상태 ('Active' 또는 'Inactive').
        """
        return self.client.update_ssh_public_key(
            UserName=user_name, SSHPublicKeyId=ssh_public_key_id, Status=status
        )

    def update_user(self, user_name, new_path=None, new_user_name=None):
        """
        특정 IAM 사용자의 정보를 업데이트합니다.
        Args (옵션):
            user_name (str): 업데이트할 IAM 사용자의 이름.
            new_path (str): 사용자의 새 경로.
            new_user_name (str): 사용자의 새 이름.
        """
        user_params = {
            "UserName": user_name,
            "NewPath": new_path,
            "NewUserName": new_user_name,
        }

        return self.client.update_user(
            **{k: v for k, v in user_params.items() if v is not None}
        )

    def upload_server_certificate(
        self,
        server_certificate_name,
        certificate_body,
        private_key,
        certificate_chain=None,
        path=None,
    ):
        """
        새 서버 인증서를 업로드합니다.
        Args:
            server_certificate_name (str): 업로드할 서버 인증서의 이름.
            certificate_body (str): 서버 인증서의 본문.
            private_key (str): 서버 인증서의 개인 키.
            certificate_chain (str): 서버 인증서의 인증 체인.
            path (str): 서버 인증서의 경로.
        """
        cert_params = {
            "ServerCertificateName": server_certificate_name,
            "CertificateBody": certificate_body,
            "PrivateKey": private_key,
            "CertificateChain": certificate_chain,
            "Path": path,
        }

        return self.client.upload_server_certificate(
            **{k: v for k, v in cert_params.items() if v is not None}
        )

    def upload_signing_certificate(self, user_name, certificate_body):
        """
        특정 사용자의 서명 인증서를 업로드합니다.
        Args:
            user_name (str): 서명 인증서를 업로드할 IAM 사용자의 이름.
            certificate_body (str): 서명 인증서의 본문.
        """
        return self.client.upload_signing_certificate(
            UserName=user_name, CertificateBody=certificate_body
        )

    def upload_ssh_public_key(self, user_name, ssh_public_key_body):
        """
        특정 사용자의 SSH 공개 키를 업로드합니다.
        Args:
            user_name (str): SSH 공개 키를 업로드할 IAM 사용자의 이름.
            ssh_public_key_body (str): SSH 공개 키의 본문.
        """
        return self.client.upload_ssh_public_key(
            UserName=user_name, SSHPublicKeyBody=ssh_public_key_body
        )
