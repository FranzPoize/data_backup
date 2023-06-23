import os

from odoo import models, fields, api

from jinja2 import Environment, FileSystemLoader

class DataBackupList(models.Model):
    _name = "data.backup.list"
    _description = "Data Backup List"

    name = fields.Char(string="Name", required=True)

    model_ids = fields.Many2many(
        comodel_name='data.backup.model',
        string='Model',
    )

    model_id_count = fields.Integer(
        string="Model Count",
        compute='_get_model_id_count',
    )

    def _get_model_id_count(self):
        for rec in self:
            rec.model_id_count = len(rec.model_ids)
    def delete_all_models(self):
        self.env["data.backup.model"].search([]).unlink()
        self.env["data.backup.field"].search([]).unlink()

    def remove_all_backup_models(self):
        self.ensure_one()
        self.write({
            "model_ids": [(5,0)]
        })

    def add_all_backup_models(self):
        self.ensure_one()

        models = self.env["ir.model"].search([]);

        backup_model_ids = []

        for model in models:

            backup_fields = []

            saved_model = self.env["data.backup.model"].search([
                ("model_id", "=", model.id),
            ])

            if saved_model:
                backup_model_ids.append(saved_model.id)
            else:
                for field in model.field_id:
                    saved_field = self.env["data.backup.field"].search([
                        ("field_id", "=", field.id),
                    ])

                    if saved_field:
                        backup_fields.append(saved_field.id)
                    else:
                        new_field = self.env["data.backup.field"].create({
                            "field_id": field.id,
                            "should_backup": False
                        })
                        backup_fields.append(new_field.id)

                new_model = self.env["data.backup.model"].create({
                    "model_id": model.id,
                    "field_ids": [(6, 0, backup_fields)],
                    "should_backup": False,
                });

                backup_model_ids.append(new_model.id)

        self.write({
            "model_ids": [(6,0, backup_model_ids)]
        })

    def get_data_for_backedup_model(self):
        self.ensure_one()
        env = Environment(
                lstrip_blocks=True,
                trim_blocks=True,
                loader=FileSystemLoader(f'{os.path.dirname(__file__)}/../templates/'),
        )
        template = env.get_template('xml_data.template')

        for model in self.model_ids:
            if model.should_backup:
                records = self.env[model.model_id.model].search([])
                print(template.render(model=model, records=records))

class DataBackupField(models.Model):
    _name = "data.backup.field"
    _description = "Data Backup Model Field"

    _inherits = {"ir.model.fields": "field_id"}

    field_id = fields.Many2one(
        comodel_name='ir.model.fields',
        required=True,
        ondelete="cascade",
        string="Field record id",
    )

    name = fields.Char(
        related="field_id.name",
        store=True,
        readonly=True,
    )
    field_description = fields.Char(
        related="field_id.field_description",
        store=True,
        readonly=True,
    )
    ttype = fields.Selection(
        related="field_id.ttype",
        store=True,
        readonly=True,
    )
    required = fields.Boolean(
        related="field_id.required",
        store=True,
        readonly=True,
    )
    state = fields.Selection(
        related="field_id.state",
        store=True,
        readonly=True,
    )

    should_backup = fields.Boolean(
        default=False,
        string="Should backup",
        required=True,
    )

class DataBackupModel(models.Model):
    _name = "data.backup.model"
    _description = "Data Backup Model"

    _inherits = {"ir.model": "model_id"}

    model_id = fields.Many2one(
        comodel_name='ir.model',
        required=True,
        ondelete="cascade",
        string="Model record id",
    )

    field_ids = fields.Many2many(
        comodel_name='data.backup.field',
        string='Fields record id',
    )

    should_backup = fields.Boolean(
        default=False,
        string="Should backup",
        required=True
    )

    def open_record(self):

        self.ensure_one()
        form_id = self.env.ref('data_backup.data_backup_model_form')

        return {
            'type': 'ir.actions.act_window',
            'name': 'title',
            'res_model': 'data.backup.model',
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': form_id.id,
            'context': {},
            'target': 'new',
        }
