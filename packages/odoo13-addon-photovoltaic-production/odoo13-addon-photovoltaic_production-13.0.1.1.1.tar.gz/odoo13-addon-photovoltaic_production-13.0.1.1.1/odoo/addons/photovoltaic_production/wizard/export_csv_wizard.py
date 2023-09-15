from odoo import models, fields, _
from io import StringIO
import csv
import datetime
import base64


RETURN_FIELD = {
    'type': 'ir.actions.act_window',
    'res_model': 'export.csv.wizard',
    'view_mode': 'form',
    'views': [(False, 'form')],
    'target': 'new',
}


class FakePlant():
    name = ''
    id = False


class ExportCsvWizard(models.TransientModel):
    _name = 'export.csv.wizard'

    date_begin = fields.Datetime()
    date_end = fields.Datetime()

    period = fields.Selection([
        ('Hour', 'Hour'),
        ('Day', 'Day'),
        ('Week', 'Week'),
        ('Month', 'Month'),
        ('Year', 'Year'),
    ], default='Day')

    plants = fields.Many2many('photovoltaic.power.station')

    leave_gaps = fields.Boolean(default=False, help="If not all plants are selected, leave fields empty according to the order or put them all together")

    filename = fields.Char()
    data = fields.Binary()

    state = fields.Selection(
        [('choose', ''), ('get', '')],
        default='choose'
    )

    def _norm(self, dt):
        date = dt.date() if isinstance(dt, datetime.datetime) else dt

        if self.period == 'Hour':
            return dt.replace(minute=0, second=0)
        elif self.period == 'Day':
            return date
        elif self.period == 'Week':
            return date - datetime.timedelta(days=date.isocalendar().weekday - 1)
        elif self.period == 'Month':
            return date.replace(day=1)
        elif self.period == 'Year':
            return date.replace(month=1, day=1)

    def export(self):
        date_begin = self._norm(self.date_begin or datetime.datetime.now())
        date_end = self._norm(self.date_end or datetime.datetime.now())

        if self.period == 'Hour':
            delta = datetime.timedelta(hours=1)
        elif self.period == 'Day':
            delta = datetime.timedelta(days=1)
        elif self.period == 'Week':
            delta = datetime.timedelta(days=7)
        elif self.period == 'Month':
            delta = datetime.timedelta(days=31)
        elif self.period == 'Year':
            delta = datetime.timedelta(days=366)

        d = date_begin
        dates = [d]
        while d < date_end:
            d = self._norm(d + delta)
            dates.append(d)

        sorted_plants = sorted(self.plants, key=lambda p: p.order.position)

        if self.leave_gaps:
            # Fill the list such that every position has a (fake) plant
            for i, plant in enumerate(sorted_plants):
                if i < plant.order.position:
                    sorted_plants.insert(i, FakePlant())

        table = [
            [_('date')] + [p.name for p in sorted_plants]
        ]
        for date in dates:
            # Hour 00:00 should appear as 23:59
            if self.period == 'Hour' and date.hour == 00 and date.minute == 00:
                date = date - datetime.timedelta(minutes=1)

            table.append([date])

            for plant in sorted_plants:
                # If its not a fake plant
                if not plant.id:
                    table[-1].append('')
                    continue

                date_range_end = self._norm(date + delta)
                # Hour 23:00 should not include the production of 23:59
                if self.period == 'Hour' and date.hour == 23 and date.minute == 00:
                    date_range_end = date_range_end - datetime.timedelta(minutes=1)

                productions = self.env['photovoltaic.production'].search([
                    ('plant', '=', plant.id),
                    ('date', '>=', date),  # already normalized
                    ('date', '<', date_range_end),
                ])

                if len(productions):
                    table[-1].append(sum([
                        prod.EAct_exp
                        for prod
                        in productions
                    ]))
                else:
                    table[-1].append('')

        content = StringIO()
        content.write('sep=,\n')
        csv_writer = csv.writer(content)
        csv_writer.writerows(table)
        content.seek(0)
        self.data = base64.b64encode(bytes(content.read(), 'utf8'))

        self.filename = f'Control de producción {_(self.period)} {date_begin} - {date_end}.csv'
        self.state = 'get'

        RETURN_FIELD.update({'res_id': self.id})
        return RETURN_FIELD

    def _set_range(self):
        today = datetime.date.today()
        self.date_end = self._norm(today) - datetime.timedelta(days=1)
        self.date_begin = self._norm(self.date_end)

    def yesterday(self):
        self.period = 'Day'
        self._set_range()
        RETURN_FIELD.update({'res_id': self.id})
        return RETURN_FIELD

    def last_week(self):
        self.period = 'Week'
        self._set_range()
        RETURN_FIELD.update({'res_id': self.id})
        return RETURN_FIELD

    def last_month(self):
        self.period = 'Month'
        self._set_range()
        RETURN_FIELD.update({'res_id': self.id})
        return RETURN_FIELD

    def last_year(self):
        self.period = 'Year'
        self._set_range()
        RETURN_FIELD.update({'res_id': self.id})
        return RETURN_FIELD

    def all_plants(self):
        self.plants = self.env['photovoltaic.power.station'].search([])
        RETURN_FIELD.update({'res_id': self.id})
        return RETURN_FIELD

    def no_plants(self):
        self.plants = [(5, 0, 0)]
        RETURN_FIELD.update({'res_id': self.id})
        return RETURN_FIELD
