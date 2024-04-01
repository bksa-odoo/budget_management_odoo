from odoo import fields, models, api, exceptions, _
from datetime import timedelta
import calendar
from odoo.exceptions import UserError, ValidationError


class BatchBudgetWizard(models.TransientModel):
    _name = 'batch.budget.create.wizard'
    _description = 'Create multiple budgets from a wizard'
    
    date_from = fields.Date('from')
    date_to = fields.Date('to')
    periods = fields.Selection([('monthly','Monthly'),('quarter','Quarterly')],string='Periods')
    analytic_plan_id = fields.Many2many('account.analytic.plan', string='Analytic Plan')
    
    def action_create_budgets(self):
        for record in self:
            months = (record.date_to.year - record.date_from.year) * 12 + record.date_to.month - record.date_from.month + 1
            print("Printed from here ---------->",months)

            if record.periods == 'quarter':
                if months%3 != 0:
                    raise ValidationError("The duration given for quarterly budget it not good")
                num_records = months // 3
            elif record.periods == 'monthly':
                num_records = months 

            for i in range(num_records):
                days = 90 if record.periods == 'quarter' else 30
                date_from = record.date_from + timedelta(days=i * days) 
                date_to = date_from + timedelta(days=days) - timedelta(days=1)
                budget_lines = []

                for plan in record.analytic_plan_id:
                    for account in plan.account_ids:
                        budget_line = self.env['budget.line'].create({
                            'budget_amt': 0,
                            'analytic_plan_id':self.analytic_plan_id,
                            'analytic_account_id': account.id,
                        })
                        budget_lines.append(budget_line.id)

                budget = self.env['budget.budget'].create({
                    'date_from': date_from,
                    'date_to': date_to,
                    'budget_line_ids': [(6, 0, budget_lines)],
                })
        return True
    
    @api.constrains('date_from', 'date_to')
    def check_date_range(self):
        for wizard in self:
            if wizard.start_date and wizard.date_to:
                date_from_str = wizard.date_from.strftime('%Y-%m-%d')
                date_to_str = wizard.date_to.strftime('%Y-%m-%d')


                start_year, start_month,  = date_from_str.split('-')
                start_year = int(start_year)
                start_month = int(start_month)


                end_year, end_month,  = date_to_str.split('-')
                end_year = int(end_year)
                end_month = int(end_month)


                if wizard.date_from.day != 1:
                    raise ValidationError("Start date should be the first day of the month")


                last_day_of_month = calendar.monthrange(end_year, end_month)[1]
                if wizard.date_to.day != last_day_of_month:
                    raise ValidationError("End date should be the last day of the month")
    
        
   
    