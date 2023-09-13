# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _name = "hr.employee"
    _inherit = ["hr.employee"]

    career_transition_ids = fields.One2many(
        comodel_name="employee_career_transition",
        inverse_name="employee_id",
        string="Career Transitions",
    )
    latest_career_transition_id = fields.Many2one(
        comodel_name="employee_career_transition",
        compute="_compute_career_transition",
        string="Latest Career Transition",
        store=True,
        readonly=True,
    )
    join_career_transition_id = fields.Many2one(
        comodel_name="employee_career_transition",
        compute="_compute_career_transition",
        string="Join Career Transition",
        store=True,
        readonly=True,
    )
    terminate_career_transition_id = fields.Many2one(
        comodel_name="employee_career_transition",
        compute="_compute_career_transition",
        string="Terminate Career Transition",
        store=True,
        readonly=True,
    )
    permanent_career_transition_id = fields.Many2one(
        comodel_name="employee_career_transition",
        compute="_compute_career_transition",
        string="Permanent Career Transition",
        store=True,
        readonly=True,
    )
    work_information_method = fields.Selection(
        string="Work Information Method",
        selection=[
            ("manual", "Manual"),
            ("career_transition", "Form Career Transition"),
        ],
    )
    manual_company_id = fields.Many2one(
        comodel_name="res.company", string="Manual Company"
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        compute="_compute_company_id",
        store=True,
    )
    manual_manager_id = fields.Many2one(
        comodel_name="hr.employee", string="Manual Manager"
    )
    manager_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Manager",
        compute="_compute_manager_id",
        store=True,
    )
    manual_job_id = fields.Many2one(comodel_name="hr.job", string="Manual Job")
    job_id = fields.Many2one(
        comodel_name="hr.job", string="Job", compute="_compute_job_id", store=True
    )
    manual_department_id = fields.Many2one(
        comodel_name="hr.department", string="Manual Department"
    )
    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
        compute="_compute_department_id",
        store=True,
    )
    manual_employment_status_id = fields.Many2one(
        comodel_name="hr.employment_status", string="Manual Employee Status"
    )
    employment_status_id = fields.Many2one(
        comodel_name="hr.employment_status",
        string="Employee Status",
        compute="_compute_employment_status_id",
        store=True,
    )
    manual_date_join = fields.Date(string="Manual Date Join")
    date_join = fields.Date(
        string="Date Join", compute="_compute_date_join", store=True
    )
    manual_date_terminate = fields.Date(string="Manual Date Terminate")
    date_terminate = fields.Date(
        string="Date Terminate", compute="_compute_date_terminate", store=True
    )
    manual_date_permanent = fields.Date(string="Manual Date Permanent")
    date_permanent = fields.Date(
        string="Date Permanent", compute="_compute_date_permanent", store=True
    )

    @api.depends(
        "career_transition_ids",
        "career_transition_ids.state",
        "career_transition_ids.type_id",
    )
    def _compute_career_transition(self):
        for record in self:
            if len(record.career_transition_ids) > 0:
                record.latest_career_transition_id = record.career_transition_ids[0]

            joins = self.env["employee_career_transition"].search(
                [
                    ("state", "=", "done"),
                    ("type_id", "=", record.company_id.join_transition_type_id.id),
                    ("employee_id", "=", record.id),
                ]
            )

            if len(joins) > 0:
                record.join_career_transition_id = joins[0]

            terminates = self.env["employee_career_transition"].search(
                [
                    ("state", "=", "done"),
                    ("type_id", "=", record.company_id.terminate_transition_type_id.id),
                    ("employee_id", "=", record.id),
                ]
            )

            if len(terminates) > 0:
                record.terminate_career_transition_id = terminates[0]

            permanents = self.env["employee_career_transition"].search(
                [
                    ("state", "=", "done"),
                    ("type_id", "=", record.company_id.permanent_transition_type_id.id),
                    ("employee_id", "=", record.id),
                ]
            )

            if len(permanents) > 0:
                record.permanent_career_transition_id = permanents[0]

    @api.depends(
        "work_information_method", "latest_career_transition_id", "manual_company_id"
    )
    def _compute_company_id(self):
        for record in self:
            record.company_id = record.manual_company_id

            if (
                record.work_information_method == "career_transition"
                and record.latest_career_transition_id
            ):
                record.company_id = record.latest_career_transition_id.new_company_id

    @api.depends(
        "work_information_method", "latest_career_transition_id", "manual_department_id"
    )
    def _compute_department_id(self):
        for record in self:
            record.department_id = record.manual_department_id

            if (
                record.work_information_method == "career_transition"
                and record.latest_career_transition_id
            ):
                record.department_id = (
                    record.latest_career_transition_id.new_department_id
                )

    @api.depends(
        "work_information_method", "latest_career_transition_id", "manual_job_id"
    )
    def _compute_job_id(self):
        for record in self:
            record.job_id = record.manual_job_id

            if (
                record.work_information_method == "career_transition"
                and record.latest_career_transition_id
            ):
                record.job_id = record.latest_career_transition_id.new_job_id

    @api.depends(
        "work_information_method", "latest_career_transition_id", "manual_manager_id"
    )
    def _compute_manager_id(self):
        for record in self:
            record.manager_id = record.manual_manager_id

            if (
                record.work_information_method == "career_transition"
                and record.latest_career_transition_id
            ):
                record.manager_id = record.latest_career_transition_id.new_manager_id

    @api.depends(
        "work_information_method",
        "latest_career_transition_id",
        "manual_employment_status_id",
    )
    def _compute_employment_status_id(self):
        for record in self:
            record.employment_status_id = record.manual_employment_status_id

            if (
                record.work_information_method == "career_transition"
                and record.latest_career_transition_id
            ):
                record.employment_status_id = (
                    record.latest_career_transition_id.new_employment_status_id
                )

    @api.depends(
        "work_information_method", "latest_career_transition_id", "manual_date_join"
    )
    def _compute_date_join(self):
        for record in self:
            record.date_join = record.manual_date_join

            if (
                record.work_information_method == "career_transition"
                and record.join_career_transition_id
            ):
                record.date_join = record.join_career_transition_id.effective_date

    @api.depends(
        "work_information_method",
        "latest_career_transition_id",
        "manual_date_terminate",
    )
    def _compute_date_terminate(self):
        for record in self:
            record.date_terminate = record.manual_date_terminate

            if (
                record.work_information_method == "career_transition"
                and record.terminate_career_transition_id
            ):
                record.date_terminate = (
                    record.terminate_career_transition_id.effective_date
                )

    @api.depends(
        "work_information_method",
        "latest_career_transition_id",
        "manual_date_permanent",
    )
    def _compute_date_permanent(self):
        for record in self:
            record.date_permanent = record.manual_date_permanent

            if (
                record.work_information_method == "career_transition"
                and record.permanent_career_transition_id
            ):
                record.date_permanent = (
                    record.permanent_career_transition_id.effective_date
                )
