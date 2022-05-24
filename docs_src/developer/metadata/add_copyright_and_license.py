from openpecha.core.metadata import (
    Copyright,
    CopyrightStatus,
    InitialCreationType,
    LicenseType,
    PechaMetadata,
)

copyright = Copyright(
    status=CopyrightStatus.COPYRIGHTED,
    notice="Copyright 2022 OpenPecha",
    info_url="https://dev.openpecha.org/terms-and-conditions",
)

metadata = PechaMetadata(
    initial_creation_type=InitialCreationType.input,
    copyright=copyright,
    license=LicenseType.CC_BY_NC_SA,
)

print(metadata)
