import json

class BaseAddressDto:
    lat = None
    long = None
    province_name = None
    province_code = None
    subdistrict_code = None
    subdistrict_name = None
    city_code = None
    city_name = None
    postal_code = None

class OriginDto(BaseAddressDto):
    pass

class DestinationDto(BaseAddressDto):
    pass

class ShippingPricing:
    courier = None
    courier_code = None
    service = None
    price = None
    duration = None
    support_cod = False
    estimation = None
    insurance_value = None
    return_rate = None
    return_level = None

    def __init__(self, data: json) -> None:
        self.courier = data['courier']
        self.courier_code = data['courierCode']
        self.service = data['service']
        self.price = data['price']
        self.duration = data['duration']
        self.support_cod = data['supportCod']
        self.estimation = data['estimation']
        self.insurance_value = data['insuranceValue']
        self.return_rate = data['returnRate']
        self.return_level = data['returnLevel']
    
    def __repr__(self) -> str:
        return "{} {} {}".format(self.courier, self.service, self.price)

class ItemDto:
    name = None
    description = None
    weight = None
    weight_uom = None
    qty = 1
    value = 0
    width = 0
    height = 0
    length = 0
    is_wood_package = False
    dimension_uom = None

    def to_json(self):
        return json.dumps(self.__dict__)
