from odoo import fields, models, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class BatchBudgetWizard(models.TransientModel):
    _name = 'batch.budget.create.wizard'
    _description = 'Create multiple budgets from a wizard'
    
    date_from = fields.Date('from')
    date_to = fields.Date('to')
    periods = fields.Selection([('monthly','Monthly'),('quarter','Quarterly')],string='Periods')
    analytic_account_id = fields.Many2many('account.analytic.account', string='Analytic Account')
       
    # def action_create_budgets(self):
    #     self.ensure_one()
    #     budget = self.env['budget.budget']
    #     budget_line = self.env['budget.line']
    #     print("Reached 0")
    #     start_date_str = self.date_from.strftime('%Y-%m-%d')
    #     end_date_str = self.date_to.strftime('%Y-%m-%d')
        
    #     start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #     end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
    #     current_date = start_date
    #     while current_date <= end_date:
    #         if self.periods == 'monthly':
    #             print("Reached 1")
    #             last_day_of_month = current_date + relativedelta(day=31)
    #             last_day_of_month = min(last_day_of_month, end_date)
                
    #             budget_values = {
    #                 'name': f"Budget: {current_date.strftime('%Y-%m-%d')} to {last_day_of_month.strftime('%Y-%m-%d')}",
    #                 'date_from': current_date.strftime('%Y-%m-%d'),
    #                 'date_to': last_day_of_month.strftime('%Y-%m-%d'),
    #             }
    #             budget = budget.create(budget_values)
                
    #             for analytic_plan in self.analytic_plan_id:
    #                 for analytic_account in analytic_plan.account_ids:
    #                     line_values = {
    #                         'budget_id': budget.id,
    #                         'analytic_account_id': analytic_account.id,
    #                     }
    #                     budget_line.create(line_values)
                
    #             current_date += relativedelta(months=1)
    #         elif self.periods == 'quarter':
    #             print("Reached 2")
    #             last_day_of_month = current_date + relativedelta(day=90)
    #             last_day_of_month = min(last_day_of_month, end_date)
                
    #             budget_values = {
    #                 'name': f"Budget: {current_date.strftime('%Y-%m-%d')} to {last_day_of_month.strftime('%Y-%m-%d')}",
    #                 'date_from': current_date.strftime('%Y-%m-%d'),
    #                 'date_to': last_day_of_month.strftime('%Y-%m-%d'),
    #             }
    #             budget = budget.create(budget_values)
                
    #             for analytic_plan in self.analytic_plan_id:
    #                 for analytic_account in analytic_plan.account_ids:
    #                     line_values = {
    #                         'budget_id': budget.id,
    #                         'analytic_account_id': analytic_account.id,
    #                     }
    #                     budget_line.create(line_values)
                
    #             current_date += relativedelta(months=3)
    #     return {
    #         'name': 'Budgets Created',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'budget.budget',
    #         'view_mode': 'tree,form',
    #         'target': 'current',
    #     }
    
    def action_create_budgets(self):
        self.ensure_one()
        budget_obj = self.env['budget.budget']
        budget_line_obj = self.env['budget.line']
        
        # Convert start_date and end_date to string format
        start_date_str = self.date_from.strftime('%Y-%m-%d')
        end_date_str = self.date_to.strftime('%Y-%m-%d')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Create budgets for each month within the specified period
        current_date = start_date
        while current_date <= end_date:
            # Determine the last day of the current month
            last_day_of_month = current_date + relativedelta(day=31)
            last_day_of_month = min(last_day_of_month, end_date)
            
            # Create or update budget with the provided data for the current month
            budget_values = {
                'name': f"Budget : {current_date.strftime('%Y-%m-%d')} to {last_day_of_month.strftime('%Y-%m-%d')}",
                'date_from': current_date.strftime('%Y-%m-%d'),
                'date_to': last_day_of_month.strftime('%Y-%m-%d'),
                # Add other fields here
            }
            budget = budget_obj.create(budget_values)
            
            
            for analytic_plan in self.analytic_account_ids:
                for analytic_account in analytic_plan.account_ids:
                    line_values = {
                        'budget_id': budget.id,
                        'analytic_account_id': analytic_account.id,
                        # Add other fields such as budget_amount and achieved_amount here
                    }
                    budget_line_obj.create(line_values)
            
            # Move to the next month
            
            if self.period == 'monthly':
                current_date += relativedelta(months=1)
            elif self.period == 'quarterly':
                current_date += relativedelta(months=3)
            else: current_date += relativedelta(months=1)
            
        
        # Optionally, perform additional actions or return an action
        return {
            'name': 'Budgets Created',
            'type': 'ir.actions.act_window',
            'res_model': 'budget.budget',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    
    # def action_create_budgets(self):
    #     self.ensure_one()
    #     for line in self:
    #         Budget = self.env['budget.budget']
    #         BudgetLine = self.env['budget.line']
    #         print("Reached 0")
    #         start_date_str = self.date_from.strftime('%Y-%m-%d')
    #         end_date_str = self.date_to.strftime('%Y-%m-%d')
            
    #         start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    #         end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            
    #         current_date = start_date
    #         while current_date <= end_date:
    #             if self.periods == 'monthly':
    #                 print("Reached 1")
    #                 last_day_of_month = current_date + relativedelta(day=31)
    #                 last_day_of_month = min(last_day_of_month, end_date)
                    
    #                 budget_values = {
    #                     'name': f"Budget: {current_date.strftime('%Y-%m-%d')} to {last_day_of_month.strftime('%Y-%m-%d')}",
    #                     'date_from': current_date.strftime('%Y-%m-%d'),
    #                     'date_to': last_day_of_month.strftime('%Y-%m-%d'),
    #                 }
    #                 budget = Budget.create(budget_values)
                    
    #                 for analytic_plan in self.analytic_plan_id:
    #                     for analytic_account in analytic_plan.account_ids:
    #                         line_values = {
    #                             'budget_id': budget.id,
    #                             'analytic_account_id': analytic_account.id,
    #                         }
    #                         BudgetLine.create(line_values)
                    
    #                 current_date += relativedelta(months=1)
    #             elif self.periods == 'quarter':
    #                 print("Reached 2")
    #                 last_day_of_month = current_date + relativedelta(day=90)
    #                 last_day_of_month = min(last_day_of_month, end_date)
                    
    #                 budget_values = {
    #                     'name': f"Budget: {current_date.strftime('%Y-%m-%d')} to {last_day_of_month.strftime('%Y-%m-%d')}",
    #                     'date_from': current_date.strftime('%Y-%m-%d'),
    #                     'date_to': last_day_of_month.strftime('%Y-%m-%d'),
    #                 }
    #                 budget = Budget.create(budget_values)
                    
    #                 for analytic_plan in self.analytic_plan_id:
    #                     for analytic_account in analytic_plan.account_ids:
    #                         line_values = {
    #                             'budget_id': budget.id,
    #                             'analytic_account_id': analytic_account.id,
    #                         }
    #                         BudgetLine.create(line_values)
                    
    #                 current_date += relativedelta(months=3)
    #         return {
    #             'name': 'Budgets Created',
    #             'type': 'ir.actions.act_window',
    #             'res_model': 'budget.budget',
    #             'view_mode': 'tree,form',
    #             'target': 'current',
    #         }
    
        
   
    