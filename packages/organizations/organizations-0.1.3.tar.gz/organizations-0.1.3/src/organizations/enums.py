from enum import Enum


class OrganizationsSwitches(str, Enum):
    Organizations = "organizations manager"
    OrganizationsIssuer = "organizations issuer manager"
    OrganizationsIntermediary = "organizations intermediary manager"
    OrganizationsDID = "organizations dids"
    OperatorsDID = "operators dids"
