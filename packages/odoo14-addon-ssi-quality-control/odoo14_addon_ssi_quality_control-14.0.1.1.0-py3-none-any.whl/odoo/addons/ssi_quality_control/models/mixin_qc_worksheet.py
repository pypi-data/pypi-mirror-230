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

    qc_result_computation_method = fields.Selection(
        string="QC Result Computation Method",
        selection=[
            ("auto", "Automatic"),
            ("manual", "Manual"),
        ],
        default="auto",
        required=True,
    )
    qc_auto_result = fields.Boolean(
        string="QC Automatic Result",
        compute="_compute_qc_result",
        store=True,
    )
    qc_manual_result = fields.Boolean(
        string="QC Manual Result",
    )
    qc_final_result = fields.Boolean(
        string="QC Final Result",
        compute="_compute_qc_result",
        store=True,
    )
    qc_worksheet_ids = fields.One2many(
        string="QC Worksheets",
        comodel_name="qc_worksheet",
        inverse_name="object_id",
        domain=lambda self: [("model_name", "=", self._name)],
        auto_join=True,
        readonly=False,
    )

    @api.depends(
        "qc_result_computation_method",
        "qc_manual_result",
        "qc_worksheet_ids",
        "qc_worksheet_ids.state",
        "qc_worksheet_ids.result",
    )
    def _compute_qc_result(self):
        for record in self:
            automatic_result = final_result = False

            for worksheet in record.qc_worksheet_ids.filtered(
                lambda r: r.state == "done"
            ):
                if not worksheet.result:
                    continue

                automatic_result = True

            if record.qc_result_computation_method == "auto":
                final_result = automatic_result
            else:
                final_result = record.qc_manual_result

            record.qc_auto_result = automatic_result
            record.qc_final_result = final_result

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

    def action_open_qc_worksheet(self):
        for record in self.sudo():
            result = record._open_qc_worksheet()
        return result

    def _open_qc_worksheet(self):
        self.ensure_one()

        waction = self.env.ref("ssi_quality_control.qc_worksheet_action").read()[0]
        waction.update({"domain": [("id", "in", self.qc_worksheet_ids.ids)]})
        return waction
