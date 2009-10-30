#!/usr/bin/env python

from saml2 import sigver
from saml2 import metadata
from saml2 import time_util
from saml2 import saml
import xmldsig as ds

SIGNED = "tests/saml_signed.xml"
UNSIGNED = "tests/saml_unsigned.xml"
FALSE_SIGNED = "tests/saml_false_signed.xml"
XMLSEC = "/opt/local/bin/xmlsec1"
#PUB_KEY = "tests/test.pem"
PRIV_KEY = "tests/test.key"

def _eq(l1,l2):
    return set(l1) == set(l2)

def test_verify_1():
    xml_response = open(SIGNED).read()
    response = sigver.correctly_signed_response(xml_response)
    assert response

def test_non_verify_1():
    """ unsigned is OK if not good """
    xml_response = open(UNSIGNED).read()
    response = sigver.correctly_signed_response(xml_response)
    assert response

def test_non_verify_2():
    xml_response = open(FALSE_SIGNED).read()
    response = sigver.correctly_signed_response(xml_response)
    assert response == None

SIGNED_VALUE= """Y88SEXrU3emeoaTgEqUKYAvDtWiLpPMx1sClw0GJV98O6A5QRvB14vNs8xnXNFFZ
XVjksKECcqmf10k/2C3oJfaEOaM4w0DgVLXeuJU08irXfdHcoe1g3276F1If1Kh7
63F7ihzh2ZeWV9OOO8tXofR9GCLIpPECbK+3/D4eEDY="""

DIGEST_VALUE = "9cQ0c72QfbQr1KkH9MCwL5Wm1EQ="

def test_sign():
    ass = metadata.make_instance(saml.Assertion, {
        "version": "2.0",
        "identifier": "11111",
        "issue_instant": "2009-10-30T13:20:28Z",
        "signature": sigver.pre_signature_part("11111"),
        "attribute_statement": {
            "attribute": [{
                    "friendly_name": "surName",
                    "attribute_value": "Foo",
                },
                {
                    "friendly_name": "givenName",
                    "attribute_value": "Bar",
                }
                ]
            }
        })
        
    print ass
    sign_ass = sigver.sign_assertion_using_xmlsec("%s" % ass, XMLSEC, 
                                                    key_file=PRIV_KEY)
    sass = saml.assertion_from_string(sign_ass)
    print sass
    assert _eq(sass.keyswv(), ['attribute_statement', 'issue_instant', 
                            'version', 'signature', 'identifier'])
    assert sass.version == "2.0"
    assert sass.identifier == "11111"
    assert time_util.str_to_time(sass.issue_instant)
    sig = sass.signature
    assert sig.signature_value.text == SIGNED_VALUE
    assert len(sig.signed_info.reference) == 1
    assert len(sig.signed_info.reference[0].digest_value) == 1
    assert sig.signed_info.reference[0].digest_value[0].text == DIGEST_VALUE