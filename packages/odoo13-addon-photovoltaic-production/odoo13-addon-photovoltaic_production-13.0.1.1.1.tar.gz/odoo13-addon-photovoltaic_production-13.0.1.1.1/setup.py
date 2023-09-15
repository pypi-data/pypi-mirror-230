import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'depends_override': {
            'photovoltaic_mgmt_extended': ''
        }
    }
)
