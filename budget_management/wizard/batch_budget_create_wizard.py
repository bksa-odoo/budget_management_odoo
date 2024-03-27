from odoo import fields, models

class BatchBudgetWizard(models.TransientModel):
    _name = 'batch.budget.create.wizard'
    _description = 'Create multiple budgets from a wizard'
    
    date_from = fields.Date('from')
    date_to = fields.Date('to')
    periods = fields.Selection([('monthly','Monthly'),('quarter','Quarterly')],string='Periods')