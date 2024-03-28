from odoo import fields, models, api
from collections import defaultdict

class BudgetLine(models.Model):
    _name = 'budget.line'
    
    name = fields.Char(string="Budget Line")
    budget_id = fields.Many2one('budget.budget', string="Budget")
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    budget_amt = fields.Monetary(string='Budget Amount')
    budget_achieved = fields.Monetary(string="Achieved Amount", readonly=True, compute="_compute_achieved_amount")
    budget_achieved_stored = fields.Monetary(string="Achieved Amount", related='budget_achieved', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_plan_id = fields.Many2one('account.analytic.plan', 'Analytic Plan',related='analytic_account_id.plan_id', readonly=True)
    achieved_percentage = fields.Float(string="Achieved(%)", compute="_compute_achieved_percent")
    is_above_budget = fields.Boolean(compute='_is_above_budget')
    date_from = fields.Date(string="from", related="budget_id.date_from")
    date_to = fields.Date(string="to", related="budget_id.date_to")
    
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
        def get_accounts(line):
            if line.analytic_account_id:
                return 'account.analytic.line', set(line.analytic_account_id.ids)
            return 'account.move.line', set(line.general_budget_id.account_ids.ids)

        def get_query(model, date_from, date_to, account_ids):
            domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('account_id', 'in', list(account_ids)),
            ]
            if model == 'account.move.line':
                fname = '-balance'
                general_account = 'account_id'
                domain += [('parent_state', '=', 'posted')]
            else:
                fname = 'amount'
                general_account = 'general_account_id'

            query = self.env[model]._search(domain)
            query.order = None
            query_str, params = query.select('%s', '%s', '%s', 'account_id', general_account, f'SUM({fname})')
            params = [model, date_from, date_to] + params
            query_str += f" GROUP BY account_id, {general_account}"

            return query_str, params

        groups = defaultdict(lambda: defaultdict(set))
        for line in self:
            model, accounts = get_accounts(line)
            groups[model][(line.budget_id.date_from, line.budget_id.date_to)].update(accounts)

        queries = []
        queries_params = []
        for model, by_date in groups.items():
            for (date_from, date_to), account_ids in by_date.items():
                query, params = get_query(model, date_from, date_to, account_ids)
                queries.append(query)
                queries_params += params

        self.env.cr.execute(" UNION ALL ".join(queries), queries_params)

        agg_general = defaultdict(lambda: defaultdict(float))  
        agg_analytic = defaultdict(lambda: defaultdict(float))
        for model, date_from, date_to, account_id, general_account_id, amount in self.env.cr.fetchall():
            agg_general[(model, date_from, date_to)][(account_id, general_account_id)] += amount
            agg_analytic[(model, date_from, date_to)][account_id] += amount

        for line in self:
            model, accounts = get_accounts(line)
            general_accounts = line.general_budget_id.account_ids
            if general_accounts:
                line.budget_achieved = sum(
                    agg_general.get((model, line.date_from, line.date_to), {}).get((account, general_account), 0)
                    for account in accounts
                    for general_account in general_accounts.ids
                )
            else:
                line.budget_achieved = sum(
                    agg_analytic.get((model, line.budget_id.date_from, line.budget_id.date_to), {}).get(account, 0)
                    for account in accounts
                )        
        
    
                