{
    'name': 'Photovoltaic Production',
    'version': '13.0.1.1.1',
    'depends': ['photovoltaic_mgmt_extended', 'web_tree_dynamic_colored_field'],
    'external_dependencies': {
        'python': [
            'python-dateutil'
        ]
    },
    'author': 'Librecoop',
    'category': 'Sales',
    'description': 'Analyze the production of photovoltaic plants',
    'installable': True,
    'auto_install': True,
    'application': True,
    'data': [
        'security/ir.model.access.csv',
        'wizard/export_csv_wizard.xml',
        'views/photovoltaic_production.xml',
        'views/photovoltaic_production_bill.xml',
        'views/photovoltaic_production_regularization.xml',
        'views/photovoltaic_power_station.xml',
        'views/photovoltaic_production_power_station_order.xml',
    ],
}
