# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from pytz import timezone

from odoo import models, tools
from odoo.tools.float_utils import float_compare


class MixinLocaldict(models.AbstractModel):
    _name = "mixin.localdict"
    _description = "Mixin for Object With Localdict"

    def _get_default_localdict(self):
        self.ensure_one()
        return {
            "env": self.env,
            "document": self,
            "time": tools.safe_eval.time,
            "datetime": tools.safe_eval.datetime,
            "dateutil": tools.safe_eval.dateutil,
            "timezone": timezone,
            "float_compare": float_compare,
            "b64encode": base64.b64encode,
            "b64decode": base64.b64decode,
        }
