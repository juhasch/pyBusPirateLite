# -*- coding: utf-8 -*-
from pyBusPirateLite.BitBang import BitBang


def test_init():
    bb = BitBang(connect=False)
    assert bb.portname == ''

    
def test_connect():
    bb = BitBang(connect=False)
    bb.connect()
    assert bb.portname != ''

    
def test_enter():
    bb = BitBang(connect=False)
    bb.connect()
    bb.enter()
    assert bb.mode == 'bb'

    
def test_connect_on_init():
    bb = BitBang()
    assert bb.mode == 'bb'
    
    
def test_adc():
    bb = BitBang()
    value = bb.adc
    assert 0.0 <= value <= 5.0

    
def test_selftest():
    bb = BitBang()
    errors = bb.selftest()
    assert errors == 0

    
def test_selftest_complete():
    bb = BitBang()
    errors = bb.selftest(complete=True)
    assert errors == 6
