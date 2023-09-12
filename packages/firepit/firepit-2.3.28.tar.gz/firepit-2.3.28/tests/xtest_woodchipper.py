from firepit.woodchipper import guess_ref_type
from firepit.woodchipper import map_value

import pytest


@pytest.mark.parametrize(
    'sco_type, prop, val, expected', [
        ('network-traffic', 'src_ref.value', '192.0.2.1', 'ipv4-addr'),
        ('network-traffic', 'src_ref.value', '2001:db8:85a3:8d3:1319:8a2e:370:7348', 'ipv6-addr'),
        ('network-traffic', "extensions.'dns-ext'.question.name_ref.value", 'example.com', 'domain-name'),
    ]
)
def test_guess_ref_type(sco_type, prop, val, expected):
    assert guess_ref_type(sco_type, prop, val) == expected


# @pytest.mark.parametrize(
#     'obj, prop, rest, val', [
#         ({'foo.bar': 'baz'}, 'foo', None, 'bar'),
#     ]
# )
# def test_recreate_dict(obj, prop, rest, val):
#     pass


# @pytest.mark.parametrize(
#     'sco, rest, val', [
#         ({'foo.bar': 'baz'}, 'foo', None, 'bar'),
#     ]
# )
# def test_set_obs_prop(observable, path, val, scos, key):
#     pass


# @pytest.fixture
# def scos():
#     return {}


# @pytest.mark.parametrize(
#     'key, val, expected, sco_key', [
#         ('url:value', 'http://example.com', {'type': 'url', 'value': 'http://example.com'}, 'url'),
#     ]
# )
def test_map_url_value():  #scos, key, val, expected, sco_key):
    od = {}
    scos = {}
    map_value('url:value', 'http://example.com', od, scos)
    assert 'url' in scos
    url = scos['url']
    assert url == {'type': 'url', 'value': 'http://example.com'}


def test_map_src_addr():
    od = {}
    scos = {}
    map_value('network-traffic:src_ref.value', '192.0.2.1', od, scos)
    assert 'network-traffic:src_ref' in scos
    ip = scos['network-traffic:src_ref']
    assert ip == {'type': 'ipv4-addr', 'value': '192.0.2.1'}
    assert 'network-traffic' in scos
    conn = scos['network-traffic']
    assert conn == {'type': 'network-traffic', 'src_ref': 'network-traffic:src_ref'}


def test_map_protocol():
    od = {}
    scos = {}
    map_value('network-traffic:protocols', 'tcp', od, scos)
    assert 'network-traffic' in scos
    conn = scos['network-traffic']
    assert conn == {'type': 'network-traffic', 'protocols': ['tcp']}


def test_map_protocols():
    od = {}
    scos = {}
    map_value('network-traffic:protocols', ['ip', 'tcp'], od, scos)
    assert 'network-traffic' in scos
    conn = scos['network-traffic']
    assert conn == {'type': 'network-traffic', 'protocols': ['ip', 'tcp']}


def test_map_user_agent():
    k = "network-traffic:extensions.'http-request-ext'.request_header.'User-Agent'"
    od = {}
    scos = {}
    map_value(k, 'my-user-agent', od, scos)
    assert 'network-traffic' in scos
    conn = scos['network-traffic']
    assert conn == {
        'type': 'network-traffic',
        'extensions': {
            'http-request-ext': {
                'request_header': {
                    'User-Agent': 'my-user-agent'
                }
            }
        }   
    }


def test_map_dns_question():
    k = "network-traffic:extensions.'dns-ext'.question.name_ref.value"
    sco_key = "network-traffic:extensions.'dns-ext'.question.name_ref"
    od = {}
    scos = {}
    map_value(k, 'example.com', od, scos)
    assert 'network-traffic' in scos
    conn = scos['network-traffic']
    assert conn == {
        'type': 'network-traffic',
        'extensions': {
            'dns-ext': {
                'question': {
                    'name_ref': sco_key
                }
            }
        }
    }
    assert sco_key in scos
    name = scos[sco_key]
    assert name == {'type': 'domain-name', 'value': 'example.com'}
