from .aws.router import router as aws_router
from .compliance_aws.router import router as compliance_aws
from .compliance_gcp.router import router as compliance_gcp
from .gcp.router import router as gcp_router
from .group.router import router as group_router
from .logging.router import router as logging_router
from .logging_aws.router import router as logging_aws_router
from .logging_gcp.router import router as logging_gcp_router
from .notification.router import router as notification_router
from .position.router import router as position_router
from .recommend.router import router as recommend_router
from .user.router import router as user_router

routers = [
    aws_router,
    gcp_router,
    compliance_aws,
    compliance_gcp,
    group_router,
    logging_router,
    logging_aws_router,
    logging_gcp_router,
    notification_router,
    position_router,
    recommend_router,
    user_router,
]
