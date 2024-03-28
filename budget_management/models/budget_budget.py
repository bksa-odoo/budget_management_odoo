from odoo import fields, models, api,exceptions, _
from odoo.exceptions import UserError, ValidationError

class BudgetBudget(models.Model):
    _name = 'budget.budget'
    _inherit = ['mail.thread','mail.activity.mixin']
    
    name = fields.Char(string="Budget Name", readonly=True, compute="_compute_name",store=True, default=lambda self:('New'), copy=True)
    date_from = fields.Date('from', required=True, copy=True)
    date_to = fields.Date('to', required=True, copy=True)
    responsible_id = fields.Many2one('res.users',string="Responsible", copy=True)
    state = fields.Selection([('draft','Draft'),('confirm','Comfirmed'),('revised','Revised'),('done','Done')],
         string='State',
         default='draft', tracking=True)
    is_favorite = fields.Boolean(string="Is Favorite")
    budget_line_ids = fields.One2many('budget.line','budget_id',copy=True)
    company_id = fields.Many2one('res.company', 'Company',default=lambda self: self.env.company)
    on_over_budget = fields.Selection([('none','None'),('warning','Warning on Budget'),('restrict','Restriction on creation')], string="On Over Budget",default='none')  
    revision_id = fields.Many2one('budget.budget', string='Revision Budget',tracking=True)
    color = fields.Integer('Color Index', default=1)
    is_above_budget = fields.Boolean(related="budget_line_ids.is_above_budget") 
    
    @api.depends('date_from','date_to')
    def _compute_name(self):
        for rec in self:
            rec.name = f"Budget: {rec.date_from} to {rec.date_to}"  
            
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
                }
                new_budget_lines.append((0, 0, revised_line_vals))

        date_str = self.date_from.strftime('%b %Y')
        new_budget_name = f"{self.name} Revised {date_str}"
        revised_budget_vals = {
            'state': 'draft', 
            'date_from': self.date_from,
            'date_to': self.date_to,
            'budget_line_ids': new_budget_lines,
        }
        revised_budget = self.env['budget.budget'].create(revised_budget_vals)
        revised_budget.name = new_budget_name
        revised_budget.responsible_id = self.responsible_id
        self.revision_id = revised_budget.id
        self.write({'state': 'revised'})


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
        
        
    def action_open_budget_lines(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("budget_management.budget_line_management_action")
        return action     
            