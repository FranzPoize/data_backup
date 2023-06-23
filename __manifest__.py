{
    'name': 'Data Backup',
    'version': '16.0.1.0.0',
    "author": "Akretion",
    'license': 'AGPL-3',
    'category': 'Server Tools',
    "website": "https://github.com/OCA/purchase-workflow",
    'summary': 'Allow extracting from all models present in the odoo instance',
    'depends': [
    ],
    'data': [
        'views/data_backup_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'maintainers': ['FranzPoize'],
}
