

import json
import dateutil.parser

from flask_restful import Resource, reqparse, abort

from ..models import MarketOrder


class IngsetV1(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('MarketItems', type=list, location='json', required=True)
        parser.add_argument('LocationId', type=int, location='json', required=True)
        args = parser.parse_args()

        if not all(isinstance(x, str) for x in args['MarketItems']):
            abort(400, description='Not all marketItems are strings.')

        for order in args['MarketItems']:
            order_json = json.loads(order)

            # Even though the enchantment level is included elsewhere in the payload
            # the item ID seems to include it as well in the form of item_id@enchantment_level.
            # Cannot use this as an item ID as it fails the foreign key constraint. So split
            # on the @ character and return just the first part. This does make the assumption
            # that no item ID ever has an @ in it for other purposes... please don't hate me SI.
            item_id = order_json['ItemTypeId'].split('@')[0]

            try:
                MarketOrder.create_or_update(
                    order_id=order_json['Id'],
                    item_id=item_id,
                    location_id=args['LocationId'],
                    quality=order_json['QualityLevel'],
                    enchantment=order_json['EnchantmentLevel'],
                    price=order_json['UnitPriceSilver'],
                    amount=order_json['Amount'],
                    expire=dateutil.parser.parse(order_json['Expires']),
                )

            except KeyError:
                abort(400, description='JSON market order did not have all required fields.')

        return {}, 201
