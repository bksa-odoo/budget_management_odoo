from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class BudgetLine(models.Model):
    _name = 'budget.line'
    
    budget_id = fields.Many2one('budget.budget', string="Budget")
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    budget_amt = fields.Monetary(string='Budget Amount')
    budget_achieved = fields.Monetary(string="Achieved Amount", readonly=True, compute="_compute_achieved_amount", store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Accounts')
    analytic_plan_id = fields.Many2one('account.analytic.plan', 'Analytic Plan',related='analytic_account_id.plan_id', readonly=True)
    achieved_percentage = fields.Float(string="Achieved(%)", compute="_compute_achieved_percent")
    is_above_budget = fields.Boolean(compute='_is_above_budget')
    date_from = fields.Date(string="from", related="budget_id.date_from")
    date_to = fields.Date(string="to", related="budget_id.date_to")
    responsible_id = fields.Many2one(string="Responsible", related="budget_id.responsible_id")
    
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
        if self.analytic_account_id:
            action = self.env['ir.actions.act_window']._for_xml_id('analytic.account_analytic_line_action_entries')
            action['domain'] = [('account_id', '=', self.analytic_account_id.id),
                                ('date', '>=', self.budget_id.date_from),
                                ('date', '<=', self.budget_id.date_to)
                                ]
            if self.general_budget_id:
                action['domain'] += [('general_account_id', 'in', self.general_budget_id.account_ids.ids)]
        else:
            action = self.env['ir.actions.act_window']._for_xml_id('account.action_account_moves_all_a')
            action['domain'] = [('account_id', 'in',
                                 self.general_budget_id.account_ids.ids),
                                ('date', '>=', self.budget_id.date_from),
                                ('date', '<=', self.budget_id.date_to)
                                ]        
        return action                        
     
    def _compute_achieved_amount(self):
        for budget in self:
            achieved_amount = 0.0
            for analytic_plan in budget.analytic_plan_id:
                domain = [
                    ('analytic_account_id', 'in', analytic_plan.account_ids.ids),
                    ('amount', '<', 0.0),
                ]
                if budget.date_from:
                    domain.append(('date', '>=', budget.date_from))
                if budget.date_to:
                    domain.append(('date', '<=', budget.date_to))
                
                analytic_lines = self.env['account.analytic.line'].search(domain)
                for line in analytic_lines:
                    achieved_amount += abs(line.amount) 
            
            budget.achieved_amount = achieved_amount
            
    
                