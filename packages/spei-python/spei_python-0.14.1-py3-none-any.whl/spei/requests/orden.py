from lxml import etree

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
PRAXIS_NS = 'http://www.praxis.com.mx/'


class OrdenPago(object):
    def __new__(cls, mensaje_xml):
        ordenpago = etree.Element(etree.QName(PRAXIS_NS, 'ordenpago'))
        mensaje = etree.tostring(mensaje_xml, xml_declaration=True, encoding='cp850')
        ordenpago.text = etree.CDATA(mensaje)
        return ordenpago


class Body(object):
    def __new__(cls, orden_pago):
        body = etree.Element(etree.QName(SOAP_NS, 'Body'))
        body.append(orden_pago)
        return body


class Envelope(object):
    def __new__(cls, body):
        namespaces_uris = {
            'soapenv': SOAP_NS,
            'prax': PRAXIS_NS,
        }
        envelope = etree.Element(
            etree.QName(SOAP_NS, 'Envelope'),
            nsmap=namespaces_uris,
        )
        envelope.append(body)
        return envelope


class OrdenRequest(object):
    def __new__(cls, mensaje, as_string=True):
        envelope = Envelope(Body(OrdenPago(mensaje.build_xml())))
        if not as_string:
            return envelope
        return etree.tostring(envelope, xml_declaration=True)
