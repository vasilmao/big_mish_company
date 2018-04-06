# coding:utf-8
import requests
import math


def geocode(address):
    # Собираем запрос для геокодера.
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={address}&format=json".format(**locals())

    # Выполняем запрос.
    response = requests.get(geocoder_request)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        raise RuntimeError(
            """Ошибка выполнения запроса:
            {request}
            Http статус: {status} ({reason})""".format(
                request=geocoder_request, status=response.status_code, reason=response.reason))

    # Получаем первый топоним из ответа геокодера.
    # Согласно описанию ответа он находится по следующему пути:
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


def get_formatted_address(address):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={address}&format=json".format(**locals())
    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
    else:
        raise RuntimeError(
            """Ошибка выполнения запроса:
            {request}
            Http статус: {status} ({reason})""".format(
                request=geocoder_request, status=response.status_code, reason=response.reason))

    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["formatted"] if features else None


def get_postal_code(address):
    geocoder_request = "http://geocode-maps.yandex.ru/1.x/?geocode={address}&format=json".format(**locals())
    response = requests.get(geocoder_request)

    if response:
        json_response = response.json()
    else:
        raise RuntimeError(
            """Ошибка выполнения запроса:
            {request}
            Http статус: {status} ({reason})""".format(
                request=geocoder_request, status=response.status_code, reason=response.reason))

    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    try:
        if features:
            zip_code = features[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
        else:
            zip_code = None
    except KeyError:
        zip_code = None
    return zip_code


# Получаем координаты объекта по его адресу.
def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Широта, преобразованная в плавающее число:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return float(toponym_longitude), float(toponym_lattitude)


# Получаем параметры объекта для рисования карты вокруг него.
def get_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и Широта :
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    # Собираем координаты в параметр ll
    ll = ",".join([toponym_longitude, toponym_lattitude])

    # Рамка вокруг объекта:
    envelope = toponym["boundedBy"]["Envelope"]

    # левая, нижняя, правая и верхняя границы из координат углов:
    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")

    # Вычисляем полуразмеры по вертикали и горизонтали
    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0

    # Собираем размеры в параметр span
    span = "{dx},{dy}".format(**locals())

    return (ll, span)


# Находим ближайшие к заданной точке объекты заданного типа.
def get_nearest_object(point, kind):
    geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/?geocode={ll}&kind={kind}&format=json"
    ll = "{0},{1}".format(point[0], point[1])

    # Выполняем запрос к геокодеру, анализируем ответ.
    geocoder_request = geocoder_request_template.format(**locals())
    response = requests.get(geocoder_request)
    if not response:
        raise RuntimeError(
            """Ошибка выполнения запроса:
            {request}
            Http статус: {status} ({reason})""".format(
                request=geocoder_request, status=response.status_code, reason=response.reason))

    # Преобразуем ответ в json-объект
    json_response = response.json()

    # Получаем первый топоним из ответа геокодера.
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"]["name"] if features else None


def get_nearest_organization(address, ll):
    search_api_server = "https://search-maps.yandex.ru/v1/"  # шаблон
    api_key = "3c4a592e-c4c0-4949-85d1-97291c87825c"  # api-ключ

    search_params = {
        "apikey": api_key,
        "text": address,
        "lang": "ru_RU",
        "ll": ll,
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    if not response:
        raise RuntimeError(
            """Ошибка выполнения запроса:
            {request}
            Http статус: {status} ({reason})""".format(request=search_api_server, status=response.status_code,
                                                       reason=response.reason))

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первую найденную организацию.
    organizations = json_response["features"]
    organization = organizations[0]["properties"]["CompanyMetaData"]
    # Блок информации
    org_name = organization["name"]
    org_address = organization["address"]
    org_point = organizations[0]["geometry"]["coordinates"]
    if round(lonlat_distance(org_point, ll.split(",")), 3) <= 50:  # если расстояние не более 50 метров
        return org_address, org_name, "{},{}".format(org_point[0], org_point[1])


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = [float(x) for x in a]
    b_lon, b_lat = [float(x) for x in b]

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance
