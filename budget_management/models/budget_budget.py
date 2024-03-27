from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class BudgetBudget(models.Model):
    _name = 'budget.budget'
    
    name = fields.Char(string="Budget Name", readonly=True, compute="_compute_name",store=True, default=lambda self:('New'))
    date_from = fields.Date('from', required=True)
    date_to = fields.Date('to', required=True)
    responsilbe_id = fields.Many2one('res.users',string="Responsible")
    state = fields.Selection([('draft','Draft'),('confirm','Comfirmed'),('revised','Revised'),('done','Done')],
         string='State',
         default='draft')
    is_favorite = fields.Boolean(string="Is Favorite")
    budget_line_ids = fields.One2many('budget.line','budget_id')
    company_id = fields.Many2one('res.company', 'Company', required=True,
        default=lambda self: self.env.company)
    on_over_budget = fields.Selection([('none','None'),('warning','Warning on Budget'),('restrict','Restriction on creation')], string="On Over Budget",default='none')   
    
    @api.depends('date_from','date_to')
    def _compute_name(self):
        for rec in self:
            rec.name = f"Budget: {rec.date_from} to {rec.date_to}"  
            
    @api.constrains('date_from', 'date_to')
    def _check_unique_budget_dates(self):
        for budget in self:
            # Check if there are any other budgets with overlapping date range
            overlapping_budgets = self.env['budget.budget'].search([
                ('id', '!=', budget.id),
                ('date_from', '<=', budget.date_to),
                ('date_to', '>=', budget.date_from)
            ])
            if overlapping_budgets:
                raise ValidationError("Another budget exists with overlapping date range.")        
            
            
    def action(self):
        print("Selfed: ", self) 
        
    def action_view_budget(self):
        self.ensure_one()
        print("print")            
        # return {
        #     "type": "ir.actions.act_window",
        #     "name": "Budget Form",
        #     "res_model": "budget.budget", # Adjust the model name as necessary
        #     "views": [[True, "form"]],
        #     "target": "new",
        #     "res_id": self.id,
        # }
        
    # actions
    def action_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})  
        
    def action_budget_revise(self):      
        self.ensure_one()
        self.write({'state': 'revised'})
        
    def action_budget_done(self):
        self.ensure_one()
        self.write({'state': 'done'})
        
    def action_budget_confirm(self):
        self.ensure_one()
        self.write({'state': 'confirm'})
            
            