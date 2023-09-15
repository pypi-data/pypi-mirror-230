from typing import Any

from lxml import etree
from pydantic import BaseModel, Extra

from spei.types import CategoriaOrdenPago


class Mensaje(BaseModel):
    categoria: CategoriaOrdenPago
    element: Any

    class Config:  # noqa: WPS306, WPS431
        extra = Extra.allow

    @classmethod
    def parse_xml(cls, mensaje_xml):
        orden = etree.fromstring(mensaje_xml)  # noqa: S320
        body = orden.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        ordenpago = body.find('{http://www.praxis.com.mx/}ordenpago')
        respuesta = body.find('{http://www.praxis.com.mx/}respuesta')
        ensesion = body.find('{http://www.praxis.com.mx/}ensesion')

        if ordenpago is not None:
            element = etree.fromstring(ordenpago.text)  # noqa: S320
            categoria = element.attrib['categoria']
            return cls(
                categoria=categoria,
                element=element,
            )

        if respuesta is not None:
            element = etree.fromstring(bytes(respuesta.text, encoding='cp850'))  # noqa: S320, E501
            categoria = element.attrib['categoria']
            return cls(
                categoria=categoria,
                element=element,
            )

        if ensesion is not None:
            return cls(
                categoria=None,
                element=ensesion,
            )
