{
    "name" : "Budget Management",
    "version" : "17.0.1.0.0",
    "summary" : "Module that helps you with Budget Management",
    "category" : "Finance",
    "author" : "Bibhav Shah",
    "depends" : ['base','account'],
    "data" : [
        'security/ir.model.access.csv',
        
        'wizard/batch_budget_create_wizard.xml',
        
        'views/budget_budget_views.xml',
        'views/budget_line_views.xml',
        'views/budget_budget_menu.xml',
    ]
}