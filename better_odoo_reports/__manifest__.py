{
    'name': 'Better Reports - Prism Engine',
    'version': '1.0',
    'category': 'Reporting',
    'summary': 'Generates high-performance interactive SPA reports',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/better_report_views.xml',
        'views/better_report_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}