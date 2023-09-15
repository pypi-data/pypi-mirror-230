from odoo import models, fields, _


class PhotovoltaicProduction(models.Model):
    _name = 'photovoltaic.production'
    _sql_constraints = [(
        'uniq_date_plant',
        'unique(date, plant)',
        _('There already is a production for this date and plant!')
    )]

    date = fields.Datetime()

    plant = fields.Many2one('photovoltaic.power.station')

    EAct_exp = fields.Integer(string='Energía activa exportada [kWh]')
    EAct_imp = fields.Integer(string='Energía activa importada [kWh]')

    ERInd_exp = fields.Integer(string='Energía reactiva inductiva exportada [kvarh]')
    ERInd_imp = fields.Integer(string='Energía reactiva inductiva importada [kvarh]')
