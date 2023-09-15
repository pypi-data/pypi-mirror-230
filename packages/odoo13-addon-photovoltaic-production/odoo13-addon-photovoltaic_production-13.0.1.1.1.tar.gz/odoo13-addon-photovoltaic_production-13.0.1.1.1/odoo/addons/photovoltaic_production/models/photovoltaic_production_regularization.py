from odoo import models, fields, api, _
import datetime
from dateutil.relativedelta import relativedelta


class PhotovoltaicProductionRegularization(models.Model):
    _name = 'photovoltaic.production.regularization'
    _sql_constraints = [(
        'uniq_date_plant',
        'unique(production_year, production_month, plant)',
        _('There already is a production for this date and plant!')
    )]

    production_year = fields.Integer()
    production_month = fields.Integer()
    production_date = fields.Char(compute='_compute_production_date', store=True)

    plant = fields.Many2one('photovoltaic.power.station')

    real_production = fields.Integer(compute='_compute_production', store=True)

    billed_production_2 = fields.Integer(
        compute='_compute_production',
        store=True,
        string='M+1',
        help='red: regularization needed\ngreen: inside the margin\nblue: possible negative regularization'
    )
    billed_production_4 = fields.Integer(
        compute='_compute_production',
        store=True,
        string='M+3',
        help='red: regularization needed\ngreen: inside the margin\nblue: possible negative regularization'
    )
    billed_production_12 = fields.Integer(
        compute='_compute_production',
        store=True,
        string='M+11',
        help='red: regularization needed\ngreen: inside the margin\nblue: possible negative regularization'
    )
    latest_production = fields.Integer(compute='_compute_production', store=True)

    r12n_2 = fields.Selection([('red', ''), ('green', ''), ('blue', '')], compute='_compute_r12n', store=True)
    r12n_4 = fields.Selection([('red', ''), ('green', ''), ('blue', '')], compute='_compute_r12n', store=True)
    r12n_12 = fields.Selection([('red', ''), ('green', ''), ('blue', '')], compute='_compute_r12n', store=True)

    r12n_status = fields.Selection([('red', ''), ('green', ''), ('blue', '')], compute='_compute_r12n', store=True)

    # @api.depends('production_year', 'production_month')
    # def _compute_real_production(self):
    #     for record in self:
    #         date = datetime.date(
    #             year=record.production_year,
    #             month=record.production_month,
    #             day=1
    #         )
    #         logger.info(fields.Date.to_date(date))
    #         logger.info(fields.Date.to_date(date.replace(day=31)))

    #         productions = self.env['photovoltaic.production'].search([
    #             ('plant', '=', record.plant.id),
    #             ('date', '>=', fields.Date.to_date(date)),
    #             ('date', '<=', fields.Date.to_date(date.replace(day=31))),
    #         ])
    #         logger.info(productions)

    #         record.real_production = sum(productions.EAct_exp)
    #         logger.info(record.real_production)

    @api.depends('production_year', 'production_month')
    def _compute_production_date(self):
        for record in self:
            record.production_date = f'{record.production_year}/{record.production_month:02}'

    def _get_billed_production(self, record, months):
        bill_date = fields.Date.to_date(
            datetime.date(
                year=record.production_year,
                month=record.production_month,
                day=1
            ) + relativedelta(months=months)
        )

        bill = self.env['photovoltaic.production.bill'].search([
            ('plant', '=', record.plant.id),
            ('production_year', '=', record.production_year),
            ('production_month', '=', record.production_month),
            ('bill_date', '>', bill_date)
        ], order='bill_date')

        if not bill:
            return 0

        record.latest_production = months

        return bill[0].billed_production

    @api.depends('production_year', 'production_month', 'plant')
    def _compute_production(self):
        for record in self:
            date = datetime.date(
                year=record.production_year,
                month=record.production_month,
                day=1
            )

            productions = self.env['photovoltaic.production'].search([
                ('plant', '=', record.plant.id),
                ('date', '>=', fields.Date.to_date(date)),
                ('date', '<', fields.Date.to_date(date + relativedelta(months=1))),
            ])

            record.real_production = sum([p['EAct_exp'] for p in productions.read()])

            record.billed_production_2 = self._get_billed_production(record, 2)
            record.billed_production_4 = record.billed_production_2 + self._get_billed_production(record, 4)
            record.billed_production_12 = record.billed_production_4 + self._get_billed_production(record, 12)

            if record.latest_production < 4:
                record.billed_production_4 = 0

            if record.latest_production < 12:
                record.billed_production_12 = 0

    @api.depends('real_production', 'billed_production_2', 'billed_production_4', 'billed_production_12', 'latest_production')
    def _compute_r12n(self):
        for record in self:
            error_margin = record.real_production * (record.plant.billing_error_margin / 100.0)

            for m in (2, 4, 12):
                prod_m_diff = record.real_production - getattr(record, f'billed_production_{m}')
                if prod_m_diff > error_margin:
                    setattr(record, f'r12n_{m}', 'red')
                elif prod_m_diff >= 0:
                    setattr(record, f'r12n_{m}', 'green')
                else:
                    setattr(record, f'r12n_{m}', 'blue')

            if record.latest_production in (2, 4, 12):
                record.r12n_status = getattr(record, f'r12n_{record.latest_production}')
