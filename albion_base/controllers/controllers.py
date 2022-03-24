# -*- coding: utf-8 -*-
from odoo import http, api, models
from odoo.http import request
import json


class RESTCharacterController(http.Controller):
    @http.route('/api/chars/sesterzi/all', type='json', auth='user')
    def get_all_sesterzi(self):
        data = None
        chars = request.env['albion_base.character'].search([])
        if chars:
            dto_sesterzi_list = []
            for c in chars:
                dto = {
                    'Name': c.name,
                    'Sesterzi': c.gold
                }
                dto_sesterzi_list.append(dto)
            data = {'response': dto_sesterzi_list, 'message': 'Success'}
        return data

    @http.route('/api/chars/sesterzi/me', type='json', auth='user')
    def get_char_sesterzi(self, **rec):
        data = None
        if rec['discordName']:
            char_name = rec['discordName'].split("[SENEX]")[1]
            char = request.env['albion_base.character'].search([
                ('name', '=', char_name)
            ])

            if not char:
                dto = {
                    'Name': char_name,
                    'Sesterzi': 0
                }
            else:
                dto = {
                    'Name': char.name,
                    'Sesterzi': char.gold
                }
            data = {'response': dto, 'message': 'Success'}
        return data

    @http.route('/api/chars/sesterzi/trade', type='json', auth='user')
    def trade_sesterzi(self, **rec):
        data = None
        if rec['senderDiscordName'] and rec['receiverDiscordName'] and rec['amountSesterzi']:
            sender_name = rec['senderDiscordName'].split("[SENEX]")[1]
            receiver_name = rec['receiverDiscordName'].split("[SENEX]")[1]
            gold = int(rec['amountSesterzi'])
            sender = request.env['albion_base.character'].search([
                ('name', '=', sender_name)
            ])

            if sender and sender.gold >= gold:
                sender.gold = sender.gold - gold
                receiver = request.env['albion_base.character'].search([
                    ('name', '=', receiver_name)
                ])
                if not receiver:
                    receiver = request.env['albion_base.character'].create({
                        'name': receiver_name,
                    })
                receiver.gold = receiver.gold + gold

                dto = {
                    'Sender': sender.name,
                    'SenderSesterzi': sender.gold,
                    'Receiver': receiver.name,
                    'ReceiverSesterzi': receiver.gold
                }
                data = {'response': dto, 'message': 'Success'}

        return data

    @http.route('/api/chars/sesterzi/pay', type='json', auth='user')
    def pay_sesterzi(self, **rec):
        data = None
        if rec['senderDiscordName'] and rec['amountSesterzi']:
            sender_name = rec['senderDiscordName'].split("[SENEX]")[1]
            gold = int(rec['amountSesterzi'])
            sender = request.env['albion_base.character'].search([
                ('name', '=', sender_name)
            ])

            if sender and sender.gold >= gold:
                sender.gold = sender.gold - gold
                dto = {
                    'Sender': sender.name,
                    'SenderSesterzi': sender.gold,
                }
                data = {'response': dto, 'message': 'Success'}

        return data
