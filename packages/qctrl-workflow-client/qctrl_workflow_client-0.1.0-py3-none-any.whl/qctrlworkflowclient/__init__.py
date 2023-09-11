# Copyright 2023 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

__version__ = "0.1.0"

from .defaults import (
    get_authenticated_client_for_product,
    get_default_api_url,
    get_default_cli_auth,
    get_default_oidc_url,
)
from .functions import (
    core_workflow,
    print_warnings,
)
from .products import (
    Product,
    ProductInfo,
)
from .router import (
    ApiRouter,
    BaseRouter,
    LocalRouter,
)
from .settings import CoreClientSettings
