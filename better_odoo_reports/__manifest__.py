{
    'name': 'Better Reports - Prism Engine',
    'version': '1.0',
    'category': 'Reporting',
    'summary': 'Generates high-performance interactive SPA financial reports',
    'depends': [
        'base', 
        'web', 
        'account'  # Required because we are now querying the financial ledgers
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/better_report_views.xml',
        'views/better_report_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
