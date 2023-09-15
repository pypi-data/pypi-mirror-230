from odoo import models, fields, _


class PhotovoltaicProductionPowerStationOrder(models.Model):
    _name = 'photovoltaic.production.power.station.order'
    _sql_constraints = [(
        'uniq_plant',
        'unique(plant)',
        _('Only one position for each plant allowed!')
    ), (
        'uniq_position',
        'unique(position)',
        _('Position has to be unique!')
    )]

    plant = fields.Many2one('photovoltaic.power.station')
    position = fields.Integer()
