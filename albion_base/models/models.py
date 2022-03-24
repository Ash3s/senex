# -*- coding: utf-8 -*-
from itertools import count
from odoo import models, fields, api
from odoo.exceptions import UserError


class Equipment(models.Model):
    _name = 'albion_base.equipment'

    name = fields.Char("Nome equipaggiamento")

    category = fields.Selection([
        ('swords', 'Spade'),
        ('axes', 'Asce'),
        ('cloth_armors', 'Armature Tessuto'),
        ('cloth_helms', 'Elmi Tessuto'),
        ('cloth_shoes', 'Scarpe Tessuto'),
        ('leather_armors', 'Armature Pelle'),
        ('leather_helms', 'Elmi Pelle'),
        ('leather_shoes', 'Scarpe Pelle'),
        ('plate_armors', 'Armature Metallo'),
        ('plate_helms', 'Elmi Metallo'),
        ('plate_shoes', 'Scarpe Metallo')
    ], string="Categoria")


class Activity(models.Model):
    _name = 'albion_base.activity'

    name = fields.Char("Nome Attività")
    gold_per_activity = fields.Integer("Sesterzi per Attività")


class CharSpec(models.Model):
    _name = 'albion_base.char_spec'

    name = fields.Char('Nome Equipaggiamento', compute='_compute_name')
    char_id = fields.Many2one('albion_base.character', string='Personaggio', index=True, required=True)
    equipment_id = fields.Many2one('albion_base.equipment', string='Equipaggiamento', index=True, required=True)
    level = fields.Integer("Livello", required=True)

    def _compute_name(self):
        for c in self:
            c.name = "%s-%s" % (c.equipment_id.name or '', c.level or '')


class ActivityLevel(models.Model):
    _name = 'albion_base.activity_level'

    name = fields.Char('Nome Livello Attività', compute='_compute_name')
    char_id = fields.Many2one('albion_base.character', string='Personaggio', index=True)
    activity_id = fields.Many2one('albion_base.activity', string='Attività', index=True)
    attendances = fields.Integer("Partecipazioni")
    level = fields.Integer("Livello", compute='_compute_level')

    def _compute_name(self):
        for a in self:
            a.name = "%s-%s" % (a.activity_id.name or '', a.level or '')

    def _compute_level(self):
        for a in self:
            if a.attendances < 20:
                a.level = 1
            if a.attendances >= 20:
                a.level = 2
            if a.attendances >= 50:
                a.level = 3
            if a.attendances >= 100:
                a.level = 4


class Character(models.Model):
    _name = 'albion_base.character'

    name = fields.Char("Nome Personaggio")
    gold = fields.Integer("Sesterzi")
    notes = fields.Text("Note")
    activity_levels = fields.One2many(string="Livelli Attività", inverse_name='char_id',
                                      comodel_name='albion_base.activity_level')
    specs = fields.One2many(string='Specs', inverse_name='char_id',
                            comodel_name='albion_base.char_spec', onchange='compute_all_specs_percentage')
    user_id = fields.Many2one('res.users', string="Utente Collegato")

    # region Warrior Spec
    swords_spec = fields.Float("Spade")
    axes_spec = fields.Float("Asce")
    gloves_spec = fields.Float("Guanti")
    maces_spec = fields.Float("Mazze")
    hammers_spec = fields.Float("Martelli")
    xbows_spec = fields.Float("Balestre")
    shields_spec = fields.Float("Scudi")
    # endregion
    # region Hunter Spec
    bows_spec = fields.Float("Archi")
    spears_spec = fields.Float("Lance")
    natures_spec = fields.Float("Natura")
    daggers_spec = fields.Float("Pugnali")
    quarterstaffs_spec = fields.Float("Bastoni")
    offhands_spec = fields.Float("Mano secondaria")
    # endregion
    # region Mage Spec
    fires_spec = fields.Float("Fuoco")
    holys_spec = fields.Float("Sacro")
    frosts_spec = fields.Float("Ghiaccio")
    arcanes_spec = fields.Float("Arcano")
    curseds_spec = fields.Float("Dannato")
    channelers_spec = fields.Float("Incanalatori")
    # endregion
    # region Armors
    cloth_armors_spec = fields.Float("Armature Tessuto")
    cloth_helmets_spec = fields.Float("Elmi Tessuto")
    cloth_shoes_spec = fields.Float("Scarpe Tessuto")
    leather_armors_spec = fields.Float("Armature Pelle")
    leather_helmets_spec = fields.Float("Elmi Pelle")
    leather_shoes_spec = fields.Float("Scarpe Pelle")
    plate_armors_spec = fields.Float("Armature Metallo")
    plate_helmets_spec = fields.Float("Elmi Metallo")
    plate_shoes_spec = fields.Float("Scarpe Metallo")

    # endregion

    def add_gold(self, value):
        self.gold = self.gold + value
        return

    @api.model
    @api.depends('specs')
    @api.onchange('specs')
    def compute_all_specs_percentage(self):
        self.swords_spec = self.compute_spec_percentage('swords')
        self.axes_spec = self.compute_spec_percentage('axes')
        self.leather_helmets_spec = self.compute_spec_percentage('leather_helms')
        self.leather_armors_spec = self.compute_spec_percentage('leather_armors')
        self.leather_shoes_spec = self.compute_spec_percentage('leather_shoes')
        self.cloth_helmets_spec = self.compute_spec_percentage('cloth_helms')
        self.cloth_armors_spec = self.compute_spec_percentage('cloth_armors')
        self.cloth_shoes_spec = self.compute_spec_percentage('cloth_shoes')
        self.plate_helmets_spec = self.compute_spec_percentage('plate_helms')
        self.plate_armors_spec = self.compute_spec_percentage('plate_armors')
        self.plate_shoes_spec = self.compute_spec_percentage('plate_shoes')

    def compute_spec_percentage(self, spec_category):
        tot_spec = 0
        equips = self.env['albion_base.equipment'].search([
            ('category', '=', spec_category)
        ])
        if len(equips) == 0:
            return 0
        for e in equips:
            for spec in self.specs:
                if e == spec.equipment_id:
                    spec_level = spec.level
                    if spec.level > 100:
                        spec_level = 100
                    tot_spec = tot_spec + spec_level

        return tot_spec / len(equips)

    def update_gold(self):
        return {
            'name': "Aggiorna Sesterzi",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'albion_base.update_gold_wizard',
            'target': 'new',
            'context': {
                'default_char_id': self.id,
                'default_gold:': self.gold
            }
        }


class Event(models.Model):
    _name = 'albion_base.event'

    name = fields.Char("Evento")
    activity_id = fields.Many2one('albion_base.activity', string="Attività")
    date = fields.Date("Data Evento")
    attendants = fields.One2many(inverse_name='event_id', comodel_name='albion_base.event_attendant',
                                 string="Partecipanti", onchange='compute_attendants')
    attendants_number = fields.Integer("Numero Partecipanti", compute="_compute_attendants_number")

    def _compute_attendants_number(self):
        for e in self:
            num = 0
            for a in e.attendants:
                num = num + 1
            e.attendants_number = num

    @api.model
    @api.depends('attendants')
    @api.onchange('attendants')
    def compute_attendants(self):
        for a in self.attendants:
            if not a.computed:
                a.attend_activity()


class EventAttendant(models.Model):
    _name = 'albion_base.event_attendant'

    name = fields.Char(related='char_id.name')
    char_id = fields.Many2one('albion_base.character', "Personaggio")
    event_id = fields.Many2one('albion_base.event', "Evento")
    gold_value = fields.Integer("Sesterzi")
    computed = fields.Boolean("Calcolato")

    def attend_activity(self):
        if self.char_id:
            activity_level = self.env['albion_base.activity_level'].search([
                ('char_id', '=', self.char_id.id),
                ('activity_id', '=', self.event_id.activity_id.id)
            ])
            if not activity_level:
                activity_level = self.env['albion_base.activity_level'].create({
                    'char_id': self.char_id.id,
                    'activity_id': self.event_id.activity_id.id,
                    'attendances': 0
                })

            activity_level.attendances = activity_level.attendances + 1
            self.gold_value = self.event_id.activity_id.gold_per_activity * activity_level.level
            self.computed = True
            self.char_id.add_gold(self.gold_value)
            return self

    def unlink(self):
        if self.char_id:
            activity_level = self.env['albion_base.activity_level'].search([
                ('char_id', '=', self.char_id.id),
                ('activity_id', '=', self.event_id.activity_id.id)
            ])
            if activity_level:
                activity_level.attendances = activity_level.attendances - 1
            self.char_id.add_gold(-1 * self.gold_value)
        return super(EventAttendant, self).unlink()


class UpdateGoldWizard(models.TransientModel):
    _name = 'albion_base.update_gold_wizard'

    char_id = fields.Many2one('albion_base.character', "Personaggio")
    gold = fields.Integer("Sesterzi")

    def update_gold(self):
        self.char_id.gold = self.gold
