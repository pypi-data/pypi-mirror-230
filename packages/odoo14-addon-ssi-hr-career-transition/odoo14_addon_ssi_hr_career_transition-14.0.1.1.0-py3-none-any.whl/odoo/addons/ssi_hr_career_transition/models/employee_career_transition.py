# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.ssi_decorator import ssi_decorator


class HrCareerTransition(models.Model):
    _name = "employee_career_transition"
    _description = "Career Transition"
    _inherit = [
        "mixin.transaction_confirm",
        "mixin.transaction_ready",
        "mixin.transaction_done",
        "mixin.transaction_cancel",
        "mixin.employee_document",
    ]

    # Multiple Approval Attribute
    _approval_from_state = "draft"
    _approval_to_state = "ready"
    _approval_state = "confirm"
    _after_approved_method = "action_ready"

    # Attributes related to add element on view automatically
    _automatically_insert_view_element = True

    # Attributes related to add element on form view automatically
    _automatically_insert_multiple_approval_page = True
    _statusbar_visible_label = "draft,confirm,ready,done"
    _policy_field_order = [
        "confirm_ok",
        "ready_ok",
        "approve_ok",
        "reject_ok",
        "restart_approval_ok",
        "cancel_ok",
        "restart_ok",
        "done_ok",
        "manual_number_ok",
    ]

    _header_button_order = [
        "action_confirm",
        "action_approve_approval",
        "action_reject_approval",
        "action_done",
        "%(ssi_transaction_cancel_mixin.base_select_cancel_reason_action)d",
        "action_restart",
    ]

    # Attributes related to add element on search view automatically
    _state_filter_order = [
        "dom_draft",
        "dom_confirm",
        "dom_reject",
        "dom_done",
        "dom_cancel",
    ]

    _order = "effective_date desc, employee_id, id"

    # Sequence attribute
    _create_sequence_state = "ready"

    type_id = fields.Many2one(
        comodel_name="employee_career_transition_type",
        string="Career Transition Type",
        required=True,
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    reason_id = fields.Many2one(
        comodel_name="employee_career_transition_type.reason",
        string="Reason",
        ondelete="restrict",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    allowed_reason_ids = fields.Many2many(
        comodel_name="employee_career_transition_type.reason",
        string="Allowed Reasons",
        compute="_compute_allowed_reason_ids",
        compute_sudo=True,
        store=False,
    )
    require_reason = fields.Boolean(
        related="type_id.require_reason",
        string="Require Reason",
        store=False,
    )
    effective_date = fields.Date(
        string="Effective Date",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    # need_previous_history = fields.Boolean(
    #     string="Need Previous History",
    #     related="type_id.need_previous_history",
    # )
    # previous_history_id = fields.Many2one(
    #     comodel_name="employee_career_transition",
    #     string="Previous History",
    #     ondelete="restrict",
    #     readonly=True,
    # )
    change_company = fields.Boolean(
        string="Change Company",
        related="type_id.change_company",
    )
    require_company = fields.Boolean(
        string="Require Company",
        related="type_id.require_company",
    )
    change_manager = fields.Boolean(
        string="Change Manager",
        related="type_id.change_manager",
    )
    require_manager = fields.Boolean(
        string="Require Manager",
        related="type_id.require_manager",
    )
    change_job = fields.Boolean(
        string="Change Job Position",
        related="type_id.change_job",
    )
    require_job = fields.Boolean(
        string="Require Job Position",
        related="type_id.require_job",
    )
    change_department = fields.Boolean(
        string="Change Department",
        related="type_id.change_department",
    )
    require_department = fields.Boolean(
        string="Require Department",
        related="type_id.require_department",
    )
    change_employment_status = fields.Boolean(
        string="Change Employee Status",
        related="type_id.change_employment_status",
    )
    require_employment_status = fields.Boolean(
        string="Require Employee Status",
        related="type_id.require_employment_status",
    )
    previous_history_id = fields.Many2one(
        comodel_name="employee_career_transition",
        string="Previous History",
        ondelete="restrict",
        readonly=True,
    )
    archieve = fields.Boolean(
        string="Archieve",
        default=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    previous_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Previous Company",
        ondelete="restrict",
        readonly=True,
    )
    previous_department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Previous Department",
        ondelete="restrict",
        readonly=True,
    )
    previous_job_id = fields.Many2one(
        comodel_name="hr.job",
        string="Previous Job Position",
        ondelete="restrict",
        readonly=True,
    )
    previous_manager_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Previous Manager",
        ondelete="restrict",
        readonly=True,
    )
    previous_employment_status_id = fields.Many2one(
        comodel_name="hr.employment_status",
        string="Previous Employment Status",
        ondelete="restrict",
        readonly=True,
    )
    new_company_id = fields.Many2one(
        comodel_name="res.company",
        string="New Company",
        ondelete="restrict",
    )
    new_department_id = fields.Many2one(
        comodel_name="hr.department",
        string="New Department",
        ondelete="restrict",
    )
    new_job_id = fields.Many2one(
        comodel_name="hr.job",
        string="New Job Position",
        ondelete="restrict",
    )
    new_manager_id = fields.Many2one(
        comodel_name="hr.employee",
        string="New Manager",
        ondelete="restrict",
    )
    new_employment_status_id = fields.Many2one(
        comodel_name="hr.employment_status",
        string="New Employment Status",
        ondelete="restrict",
        readonly=True,
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("ready", "Ready to Start"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("reject", "Rejected"),
        ],
        default="draft",
        copy=False,
    )

    @api.model
    def _get_policy_field(self):
        res = super(HrCareerTransition, self)._get_policy_field()
        policy_field = [
            "confirm_ok",
            "ready_ok",
            "approve_ok",
            "reject_ok",
            "restart_approval_ok",
            "cancel_ok",
            "restart_ok",
            "done_ok",
            "manual_number_ok",
        ]
        res += policy_field
        return res

    @api.depends("type_id")
    def _compute_allowed_reason_ids(self):
        for record in self:
            result = []
            if record.type_id:
                reasons = self.env["employee_career_transition_type.reason"].search(
                    [("type_id", "=", record.type_id.id)]
                )
                result = reasons.ids

            record.allowed_reason_ids = result

    @api.onchange(
        "employee_id",
        "archieve",
    )
    def onchange_previous_history_id(self):
        self.previous_history_id = False
        if not self.archieve and self.employee_id:
            criteria = [
                ("employee_id", "=", self.employee_id.id),
                ("state", "in", ["ready", "done"]),
            ]
            histories = self.search(criteria)
            if len(histories) > 0:
                self.previous_history_id = histories[-1]

    @api.onchange("previous_history_id")
    def onchange_previous_company_id(self):
        self.previous_company_id = False
        if self.previous_history_id:
            self.previous_company_id = self.previous_history_id.new_company_id

    @api.depends("previous_company_id")
    def onchange_new_company_id(self):
        self.new_company_id = self.previous_company_id

    @api.onchange("previous_history_id")
    def onchange_previous_department_id(self):
        self.previous_department_id = False
        if self.previous_history_id:
            self.previous_department_id = self.previous_history_id.new_department_id

    @api.depends("previous_department_id")
    def onchange_new_department_id(self):
        self.new_department_id = self.previous_department_id

    @api.onchange("previous_history_id")
    def onchange_previous_manager_id(self):
        self.previous_manager_id = False
        if self.previous_history_id:
            self.previous_manager_id = self.previous_history_id.new_manager_id

    @api.depends("previous_manager_id")
    def onchange_new_manager_id(self):
        self.new_manager_id = self.previous_manager_id

    @api.onchange("previous_history_id")
    def onchange_previous_job_id(self):
        self.previous_job_id = False
        if self.previous_history_id:
            self.previous_job_id = self.previous_history_id.new_job_id

    @api.depends("previous_job_id")
    def onchange_new_job_id(self):
        self.new_job_id = self.previous_job_id

    @api.onchange("previous_history_id")
    def onchange_previous_employment_status_id(self):
        self.previous_employment_status_id = False
        if self.previous_history_id:
            self.previous_employment_status_id = (
                self.previous_history_id.new_employment_status_id
            )

    @api.depends("previous_employment_status_id")
    def onchange_new_employment_status_id(self):
        self.new_employment_status_id = self.previous_employment_status_id

    @ssi_decorator.post_done_action
    def _01_change_employee_information(self):
        if self.archieve:
            return True

        self.write({self.employee_id: self._prepare_change_employee_information()})

    def _prepare_change_employee_information(self):
        result = [
            ("company_id", "=", self.new_company_id.id),
            ("department_id", "=", self.new_department_id.id),
            ("job_id", "=", self.new_job_id.id),
            ("manager_id", "=", self.new_manager_id.id),
            ("employment_status_id", "=", self.new_employment_status_id.id),
        ]
        return result

    @ssi_decorator.post_cancel_action
    def _01_revert_employee_information(self):
        if self.archieve:
            return True

        self.write({self.employee_id: self._prepare_revert_employee_information()})

    def _prepare_revert_employee_information(self):
        result = [
            ("company_id", "=", self.previous_company_id.id),
            ("department_id", "=", self.previous_department_id.id),
            ("job_id", "=", self.previous_job_id.id),
            ("manager_id", "=", self.previous_manager_id.id),
            ("employment_status_id", "=", self.previous_employment_status_id.id),
        ]
        return result

    @ssi_decorator.post_cancel_check
    def _01_check_latest_history_when_cancel(self):
        if self.id != self.employee_id.latest_career_transition_id.id:
            if not self.archieve:
                if self.state == "done":
                    error_message = _(
                        """
                    Context: Cancel employee career transition
                    Database ID: %s
                    Problem: Employee career transition is not latest transition
                    Solution: Find and cancel latest transition first
                    """
                        % (self.id)
                    )
                    raise ValidationError(error_message)
