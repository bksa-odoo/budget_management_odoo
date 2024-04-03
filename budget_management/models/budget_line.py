from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class BudgetLine(models.Model):
    _name = 'budget.line'
    
    budget_id = fields.Many2one('budget.budget', string="Budget")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    budget_amt = fields.Monetary(string='Budget Amount')
    budget_achieved = fields.Monetary(string="Achieved Amt", compute="_compute_achieved_amount")
    budget_achieved_stored = fields.Monetary(string="Achieved Amt", related='budget_achieved', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Accounts')
    analytic_plan_id = fields.Many2one('account.analytic.plan', 'Analytic Plan',related='analytic_account_id.plan_id', readonly=True)
    line_ids = fields.One2many(
        'account.analytic.line',
        'auto_account_id', 
        string="Analytic Lines",
    )
    achieved_percentage = fields.Float(string="Achieved(%)", compute="_compute_achieved_percent")
    is_above_budget = fields.Boolean(compute='_is_above_budget')
    date_from = fields.Date(string="from", related="budget_id.date_from")
    date_to = fields.Date(string="to", related="budget_id.date_to")
    responsible_id = fields.Many2one(string="Responsible", related="budget_id.responsible_id")
    
    @api.depends('analytic_account_id')
    def _compute_display_name(self):
        for line in self:
            line.display_name = line.analytic_account_id.name
    
    @api.depends('budget_amt','budget_achieved')
    def _compute_achieved_percent(self):
        for line in self:
            if line.budget_amt != 0:
                line.achieved_percentage = (line.budget_achieved / line.budget_amt) * 100
            else:
                 line.achieved_percentage = 0
                 
                    
    def _is_above_budget(self):
        for line in self:
            if line.budget_amt >= 0:
                line.is_above_budget = line.budget_amt < line.budget_achieved
            else:
                line.is_above_budget = line.budget_amt > line.budget_achieved                      
                
                
    def action_open_budget_entries(self):
        for line in self:
            plan_id = line.analytic_account_id.plan_id.id
            x_plan_id = f"x_plan{plan_id}_id"

            if plan_id == 1:
                x_plan_id = 'account_id'
            if self.analytic_account_id:
                action = self.env['ir.actions.act_window']._for_xml_id('analytic.account_analytic_line_action_entries')
                action['domain'] = [(x_plan_id, '=', self.analytic_account_id.id),
                                    ('date', '>=', self.budget_id.date_from),
                                    ('date', '<=', self.budget_id.date_to)
                                    ]
            else:
                action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
                action['domain'] = [(x_plan_id, 'in',
                                    self.analytic_account_id.ids),
                                    ('date', '>=', self.budget_id.date_from),
                                    ('date', '<=', self.budget_id.date_to)
                                    ]        
            return action
    
    def _compute_achieved_amount(self):
        for line in self:
            plan_id = line.analytic_account_id.plan_id.id
            x_plan_id = f"x_plan{plan_id}_id"

            if plan_id == 1:
                x_plan_id = 'account_id'
            analytic_lines = self.env['account.analytic.line'].search([
            (x_plan_id, '=', line.analytic_account_id.id),
            ('date', '>=', line.date_from),
            ('date', '<=', line.date_to)
            ])
            
            total_amount = 0
            for analytic_line in analytic_lines:
                if analytic_line.amount < 0:
                    total_amount += (analytic_line.amount * (-1)) 
            line.budget_achieved = total_amount  
         