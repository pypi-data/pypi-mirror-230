# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, fields, models


class MixinDataRequirement(models.AbstractModel):
    _name = "mixin.data_requirement"
    _description = "Data Requirement Mixin"

    _data_requirement_create_page = False
    _data_requirement_page_xpath = "//page[last()]"

    data_requirement_ids = fields.Many2many(
        string="Data Requirements",
        comodel_name="data_requirement",
    )
    data_requirement_status = fields.Selection(
        string="Data Requirement Status",
        selection=[
            ("not_needed", "Not Needed"),
            ("open", "In Progress"),
            ("done", "Done"),
        ],
        compute="_compute_data_requirement_status",
        store=True,
    )

    @api.depends(
        "data_requirement_ids",
        "data_requirement_ids.state",
    )
    def _compute_data_requirement_status(self):
        for record in self:
            result = "not_needed"
            num_of_data_requirement = len(record.data_requirement_ids)
            num_of_done_data_requirement = len(
                record.data_requirement_ids.filtered(lambda r: r.state == "done")
            )

            if (
                num_of_data_requirement != 0
                and num_of_data_requirement != num_of_done_data_requirement
            ):
                result = "open"
            elif (
                num_of_data_requirement != 0
                and num_of_data_requirement == num_of_done_data_requirement
            ):
                result = "done"

            record.data_requirement_status = result

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "form" and self._data_requirement_create_page:
            doc = etree.XML(res["arch"])
            node_xpath = doc.xpath(self._data_requirement_page_xpath)
            if node_xpath:
                str_element = self.env["ir.qweb"]._render(
                    "ssi_data_requirement_mixin.data_requirement"
                )
                for node in node_xpath:
                    new_node = etree.fromstring(str_element)
                    node.addnext(new_node)

            View = self.env["ir.ui.view"]

            if view_id and res.get("base_model", self._name) != self._name:
                View = View.with_context(base_model_name=res["base_model"])
            new_arch, new_fields = View.postprocess_and_fields(doc, self._name)
            res["arch"] = new_arch
            new_fields.update(res["fields"])
            res["fields"] = new_fields
        return res
