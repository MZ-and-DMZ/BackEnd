from .aws.router import router as aws_router
from .compliance_ad.router import router as compliance_ad_router
from .compliance_aws.router import router as compliance_aws_router
from .compliance_gcp.router import router as compliance_gcp_router
from .department.router import router as department_router
from .gcp.router import router as gcp_router
from .group.router import router as group_router
from .logging.router import router as logging_router
from .logging_aws.router import router as logging_aws_router
from .logging_gcp.router import router as logging_gcp_router
from .notification.router import router as notification_router
from .position.router import router as position_router
from .recommend.router import router as recommend_router
from .user.router import router as user_router
from .anomaly_detection.router import router as anomaly_detection_router
from .keycloak.router import router as keycloak_router

routers = [
    aws_router,
    gcp_router,
    compliance_ad_router,
    compliance_aws_router,
    compliance_gcp_router,
    department_router,
    group_router,
    logging_router,
    logging_aws_router,
    logging_gcp_router,
    notification_router,
    position_router,
    recommend_router,
    user_router,
    anomaly_detection_router,
    keycloak_router
]
