from lxml import etree

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
PRAXIS_NS = 'http://www.praxis.com.mx/'


class Respuesta(object):
    def __new__(cls, mensaje_xml):
        respuesta = etree.Element(etree.QName(PRAXIS_NS, 'respuesta'), nsmap={None: PRAXIS_NS})  # noqa: E501
        mensaje = etree.tostring(mensaje_xml, xml_declaration=True, encoding='cp850')
        respuesta.text = mensaje
        return respuesta


class Body(object):
    def __new__(cls, respuesta):
        body = etree.Element(etree.QName(SOAP_NS, 'Body'))
        body.append(respuesta)
        return body


class Envelope(object):
    def __new__(cls, body):
        etree.register_namespace('S', SOAP_NS)
        envelope = etree.Element(etree.QName(SOAP_NS, 'Envelope'))
        envelope.append(body)
        return envelope


class RespuestaRequest(object):
    def __new__(cls, mensaje, as_string=True):
        envelope = Respuesta(mensaje.build_xml())
        if not as_string:
            return envelope
        return etree.tostring(envelope, xml_declaration=True)
