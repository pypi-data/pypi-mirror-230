from lxml import etree
from pydantic import BaseModel

from spei import types
from spei.utils import to_snake_case, to_upper_camel_case  # noqa: WPS347


class Respuesta(BaseModel):
    categoria: types.CategoriaOrdenPago

    id: str
    fecha_oper: int
    err_codigo: types.CodigoError
    err_descripcion: str

    class Config:  # noqa: WPS306, WPS431
        use_enum_values = True

    def build_xml(self):
        qname = etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type')
        mensaje = etree.Element('mensaje', {qname: 'mensaje'}, categoria=self.categoria)  # noqa: E501
        respuesta = etree.SubElement(mensaje, 'respuesta')

        for element, value in self.dict(exclude={'categoria'}).items():  # noqa: WPS110
            if element in self.__fields__:
                upper_camel_case_element = to_upper_camel_case(element)
                subelement = etree.SubElement(respuesta, upper_camel_case_element)
                subelement.text = str(value)

        return mensaje

    @classmethod
    def parse_xml(cls, respuesta_xml):
        respuesta = etree.fromstring(respuesta_xml)  # noqa: S320
        for element in respuesta.getchildren():
            response = element.find('{http://www.praxis.com.mx/}respuesta')

        mensaje_xml = etree.fromstring(bytes(response.text, encoding='cp850'))   # noqa: S320, E501
        respuesta = mensaje_xml.find('respuesta')

        respuesta_data = {
            'categoria': mensaje_xml.attrib['categoria'],
        }

        for sub_element in respuesta.getchildren():
            tag = to_snake_case(sub_element.tag)
            respuesta_data[tag] = sub_element.text

        return cls(**respuesta_data)
