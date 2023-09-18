import json
import requests
from .auth import ShipdeoAuth
from .dto import BaseAddressDto, DestinationDto, ItemDto, OriginDto, ShippingPricing


class IShipping:

    def get_tariff(self, origin, destination, couriers=[], is_cod=False, items=None):
        pass

    def get_airwaybill_info(self, airwaybill: str):
        pass


class ShipdeoService(IShipping):

    def __init__(self, token, is_prod=True, request=None) -> None:
        self.__token = token

        if is_prod:
            self.__base_url = 'https://main-api-production.shipdeo.com'
        else:
            self.__base_url = 'https://main-api-development.shipdeo.com'

        self.__requests = request or requests
        self.__headers = {
            'Authorization': 'Bearer ' + self.__token,
            'Content-Type': 'application/json'
        }
        super().__init__()
        
    def __build_payload_tariff(self, origin: BaseAddressDto, destination: BaseAddressDto, couriers, is_cod, items=None):
        return {
            "couriers": couriers,
            "is_cod": is_cod,
            "origin_lat": origin.lat,
            "origin_long": origin.long,
            "origin_province_name": origin.province_name,
            "origin_subdistrict_code": origin.subdistrict_code,
            "origin_subdistrict_name": origin.subdistrict_name,
            "origin_city_code": origin.city_code,
            "origin_city_name": origin.city_name,
            "origin_postal_code": origin.postal_code,
            "destination_lat": destination.lat,
            "destination_long": destination.long,
            "destination_province_name": destination.province_name,
            "destination_subdistrict_code": destination.subdistrict_code,
            "destination_subdistrict_name": destination.subdistrict_name,
            "destination_city_code": destination.city_code,
            "destination_city_name": destination.city_name,
            "destination_postal_code": destination.postal_code,
            "items": items,
            "isCallWeight": False
        }

    def get_tariff(self, origin: BaseAddressDto, destination: BaseAddressDto, couriers, is_cod, items=None):
       
        payload =  self.__build_payload_tariff(origin, destination, couriers, is_cod, items=items)
        respond = self.__requests.post(self.__base_url + '/v1/couriers/pricing', data=json.dumps(payload), headers=self.__headers)
        
        results = []
        # print(self.__token)
        # print(respond.status_code)

        if respond.status_code == 200:
            # for r in respond.json()['data']:
            #     shipping_price = ShippingPricing(r)
            #     results.append(shipping_price)
            return respond.json()['data']
        elif respond.status_code == 401:
            raise Exception(respond.json()['message'])
        else:
            raise Exception(respond.json())

    def get_couriers(self):
        respond = self.__requests.post(self.__base_url + '/v1/couriers', headers=self.__headers)
        if respond.status_code == 200:
            return respond.json()
    
    def get_orders(self, params):
        respond = self.__requests.get(self.__base_url + '/v1/couriers/orders', headers=self.__headers, params=params)
        if respond.status_code == 200:
            return respond.json()