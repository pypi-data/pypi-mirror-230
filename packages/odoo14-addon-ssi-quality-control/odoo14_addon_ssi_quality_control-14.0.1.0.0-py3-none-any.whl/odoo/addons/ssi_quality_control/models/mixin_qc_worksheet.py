# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from lxml import etree

from odoo import api, fields, models


class MixinQCWorksheet(models.AbstractModel):
    _name = "mixin.qc_worksheet"
    _description = "QC Worksheet Mixin"

    _qc_worksheet_create_page = False
    _qc_worksheet_page_xpath = "//page[last()]"

    qc_worksheet_ids = fields.One2many(
        string="QC Worksheets",
        comodel_name="qc_worksheet",
        inverse_name="object_id",
        domain=lambda self: [("model_name", "=", self._name)],
        auto_join=True,
        readonly=False,
    )

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "form" and self._work_log_create_page:
            doc = etree.XML(res["arch"])
            node_xpath = doc.xpath(self._work_log_page_xpath)
            if node_xpath:
                str_element = self.env["ir.qweb"]._render(
                    "ssi_quality_control.qc_worksheet_page"
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

    def unlink(self):
        qc_worksheet_ids = self.mapped("qc_worksheet_ids")
        qc_worksheet_ids.unlink()
        return super(MixinQCWorksheet, self).unlink()
