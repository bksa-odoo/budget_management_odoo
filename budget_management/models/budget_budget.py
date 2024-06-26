from odoo import fields, models, api,exceptions, _
from odoo.exceptions import UserError, ValidationError

class BudgetBudget(models.Model):
    _name = 'budget.budget'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Budget'
    
    name = fields.Char(string="Budget Name", readonly=True, compute="_compute_name",store=True, default=lambda self:('New'))
    date_from = fields.Date('from', required=True)
    date_to = fields.Date('to', required=True)
    responsible_id = fields.Many2one('res.users',string="Responsible")
    state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('revised','Revised'),('done','Done'),('cancel','Cancelled')],
        string='State',
        default='draft', tracking=True)
    is_favorite = fields.Boolean(string="Is Favorite")
    is_revised = fields.Boolean(string="Is revised")
    budget_line_ids = fields.One2many('budget.line','budget_id')
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company)
    on_over_budget = fields.Selection([('none','None'),('warning','Warning on Budget'),('restrict','Restriction on creation')], string="On Over Budget",default='none')  
    revision_id = fields.Many2one('budget.budget', string='Revision Budget',tracking=True)
    color = fields.Integer('Color Index', default=0)
    is_above_budget = fields.Boolean(related="budget_line_ids.is_above_budget") 
    
    @api.constrains('date_from', 'date_to')
    def _check_overlapping_dates(self):
        for budget in self:
            if not budget.is_revised:
                overlapping_budgets = self.search([
                    ('id', '!=', budget.id),
                    ('date_from', '<=', budget.date_to),
                    ('date_to', '>=', budget.date_from),
                ])
                print(overlapping_budgets)
                if overlapping_budgets:
                    raise ValidationError('Budgets with overlapping dates are not allowed.')  
    
    @api.depends('date_from','date_to')
    def _compute_name(self):
        for rec in self:
            if not rec.is_revised:
                if rec.date_from and rec.date_to:
                    rec.name = f"Budget: {rec.date_from} to {rec.date_to}"
                else:
                    rec.name = 'New'    
            
    @api.constrains('on_over_budget')
    def _check_on_over_budget(self):
        for record in self:
            if record.on_over_budget == 'restriction':
                on_over_budget_lines = self.env['budget.line'].search([
                    ('budget_id', '=', record.id),
                ])
                for line in on_over_budget_lines:
                 if line.achieved_amt > line.budget_amt:
                    raise ValidationError("Cannot create account.analytic.line for this period due to budget restrictions.")                    
            
    # actions
    def action_reset_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})          
    
    def action_budget_revise(self):    
        new_budget_lines = []  
        for line in self.budget_line_ids:
            if line.budget_achieved > line.budget_amt:
                revised_line_vals = {
                    'budget_id': self.id,
                    'budget_amt': line.budget_amt + line.budget_achieved,
                    'budget_achieved': line.budget_achieved,
                    'analytic_account_id': line.analytic_account_id.id,
                }
                new_budget_lines.append((0, 0, revised_line_vals))

        date_str = self.date_from.strftime('%b %Y')
        new_budget_name = f"{self.name} Revised {date_str}"
        revised_budget_vals = {
            'name' : f"{self.name} Revised {date_str}",
            'state': 'draft', 
            'date_from': self.date_from,
            'date_to': self.date_to,
            'budget_line_ids': new_budget_lines,
            'is_revised': True,
        }
        revised_budget = self.env['budget.budget'].create(revised_budget_vals)
        revised_budget.responsible_id = self.responsible_id
        self.revision_id = revised_budget.id
        self.write({'state': 'revised'})
        message_body = """
           A revisied budget is created corresponding to this budget, the revisied budget name is {0}
            """.format(revised_budget.name)
        self.message_post(body=message_body)    

        return {
            'name': 'Revised Budget',
            'view_mode': 'form',
            'res_model': 'budget.budget',
            'res_id': revised_budget.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

        
    def action_budget_done(self):
        self.ensure_one()
        self.write({'state': 'done'})
        
    def action_budget_confirm(self):
        self.ensure_one()
        self.write({'state': 'confirm'})
        
    def action_budget_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancel'})     
        
        
    def action_open_budget_lines(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("budget_management.budget_line_management_action")
        action['display_name'] = self.name
        action['domain'] = [('budget_id', '=', self.id)]
        return action     
            