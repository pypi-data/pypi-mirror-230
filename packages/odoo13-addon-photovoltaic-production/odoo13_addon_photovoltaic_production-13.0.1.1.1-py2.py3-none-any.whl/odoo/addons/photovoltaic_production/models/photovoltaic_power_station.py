from odoo import models, fields


class PhotovoltaicPowerStation(models.Model):
    _inherit = 'photovoltaic.power.station'

    production_name = fields.Char()
    billing_error_margin = fields.Float(default='5', string='Billing error margin [%]')

    order = fields.One2many('photovoltaic.production.power.station.order', 'plant')

    link_address = fields.Integer()
    measure_address = fields.Integer()
    measure_key = fields.Integer()
    connection_type = fields.Selection([('gsm', 'GSM'), ('ip', 'IP')])

    ip_address = fields.Char(string='IP address')
    ip_port = fields.Integer(string='IP port')

    phone = fields.Char()
