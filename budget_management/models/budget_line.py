from odoo import fields, models, api

class BudgetLine(models.Model):
    _name = 'budget.line'
    
    name = fields.Char(string="Budget Line")
    budget_id = fields.Many2one('budget.budget', string="Budget")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    budget_amt = fields.Monetary(string='Budget Amount')
    budget_achieved = fields.Monetary(string="Achieved Amount")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_plan_id = fields.Many2one('account.analytic.plan', 'Analytic Plan',related='analytic_account_id.plan_id', readonly=True)
    
                