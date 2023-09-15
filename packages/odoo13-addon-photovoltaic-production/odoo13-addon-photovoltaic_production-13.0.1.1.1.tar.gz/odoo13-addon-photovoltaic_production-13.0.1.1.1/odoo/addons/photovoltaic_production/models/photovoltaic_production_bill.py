from odoo import models, fields, api, _


class PhotovoltaicProductionBill(models.Model):
    _name = 'photovoltaic.production.bill'
    _sql_constraints = [(
        'uniq_bill_number',
        'unique(bill_number)',
        _('There already is a bill number for this date and plant!')
    )]

    bill_date = fields.Date()

    production_year = fields.Integer()
    production_month = fields.Integer()
    production_date = fields.Char(compute='_compute_production_date', store=True)

    plant = fields.Many2one('photovoltaic.power.station')

    billed_production = fields.Integer()
    price = fields.Float()

    bill_number = fields.Char(name='Número de la factura')

    @api.depends('production_year', 'production_month')
    def _compute_production_date(self):
        for record in self:
            record.production_date = f'{record.production_year}/{record.production_month:02}'
