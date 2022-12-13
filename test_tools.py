import pytest

from tools import Type
import argparse




def test_price_buy():
    assert Type.valid_price_buy(1) == 1
    assert Type.valid_price_buy('1') == 1
    assert Type.valid_price_buy(1.1) == 1.1
    assert Type.valid_price_buy(0) == 0
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        Type.valid_price_buy(-1) 
    assert "So they are paying you to buy that? Must be an amazing product..." in str(excinfo.value)
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        Type.valid_price_buy('abc') 
        Type.valid_price_buy('2022-01-01') 
        Type.valid_price_buy([1 ,2, 3]) 
        Type.valid_price_buy({1, 2, 3}) 
        Type.valid_price_buy((1, 2, 3)) 
        Type.valid_price_buy({1:'a', 2:'b', 3:'c'}) 
    assert "Please enter a valid number" in str(excinfo.value)   
  

def test_price_sell():
    assert Type.valid_price_sell(1) == 1
    assert Type.valid_price_sell('1') == 1
    assert Type.valid_price_sell(1.1) == 1.1
    assert Type.valid_price_sell(0) == 0
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        Type.valid_price_sell(-1) 
    assert "So you are paying money to sell this? Must be an amazing product..." in str(excinfo.value)
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        Type.valid_price_sell('abc') 
        Type.valid_price_sell('2022-01-01') 
        Type.valid_price_sell([1 ,2, 3]) 
        Type.valid_price_sell({1, 2, 3}) 
        Type.valid_price_sell((1, 2, 3)) 
        Type.valid_price_sell({1:'a', 2:'b', 3:'c'})
    assert "Please enter a valid number" in str(excinfo.value)   


def test_quantity():
    assert Type.valid_quantity(1) == 1
    assert Type.valid_quantity('1') == 1
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        Type.valid_quantity('abc') 
        Type.valid_quantity('2022-01-01') 
        Type.valid_quantity([1 ,2, 3]) 
        Type.valid_quantity({1, 2, 3}) 
        Type.valid_quantity((1, 2, 3)) 
        Type.valid_quantity({1:'a', 2:'b', 3:'c'}) 
        Type.valid_quantity(1.1)
    assert "Please enter a valid number" in str(excinfo.value)
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        Type.valid_quantity(0)
        Type.valid_quantity(-1) 
    assert "Try a value greater than 0." in str(excinfo.value)
        


def test_date_expiration():
    assert Type.valid_date_expiration('2023-01-01') == '2023-01-01'  
    with pytest.raises(TypeError):
        Type.valid_date_expiration(0)
        Type.valid_date_expiration(1.1)
        Type.valid_date_expiration(-1) 
        Type.valid_date_expiration([1 ,2, 3]) 
        Type.valid_date_expiration({1, 2, 3}) 
        Type.valid_date_expiration((1, 2, 3)) 
        Type.valid_date_expiration({1:'a', 2:'b', 3:'c'}) 
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        Type.valid_date_expiration('20230101')
        Type.valid_date_expiration('2023/01/01')
        Type.valid_date_expiration('23-01-01')
        Type.valid_date_expiration('01032023')
        Type.valid_date_expiration('01/03/2023')
        Type.valid_date_expiration('01/03/23')
        Type.valid_date_expiration('2023')
        Type.valid_date_expiration('2023 Jan 01')
        Type.valid_date_expiration('abc')    
    assert "The date should be in the YYYY-MM-dd format." in str(excinfo.value)
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        Type.valid_date_expiration('1900-01-01')
    assert "And who will you sell that to? It's already expired...Go put it back" in str(excinfo.value)

def test_date_report():
    assert Type.valid_date_report('1900-01-01') == '1900-01-01'
    with pytest.raises(TypeError):
        Type.valid_date_report(0)
        Type.valid_date_report(1.1)
        Type.valid_date_report(-1) 
        Type.valid_date_report([1 ,2, 3]) 
        Type.valid_date_report({1, 2, 3}) 
        Type.valid_date_report((1, 2, 3)) 
        Type.valid_date_report({1:'a', 2:'b', 3:'c'}) 
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        Type.valid_date_report('abc') 
        Type.valid_date_report('20230101')
        Type.valid_date_report('2023/01/01')
        Type.valid_date_report('23-01-01')
        Type.valid_date_report('01032023')
        Type.valid_date_report('01/03/2023')
        Type.valid_date_report('01/03/23')
        Type.valid_date_report('2023')
        Type.valid_date_report('2023 Jan 01')
    assert "The date should be in the YYYY-MM-dd format." in str(excinfo.value)
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        Type.valid_date_report('2023-01-01')
    assert "I can't predict the future" in str(excinfo.value)

def test_valid_timeframe():
    assert Type.valid_timeframe(['1900-01-01','2020-01-01']) == True
    assert Type.valid_timeframe(['1900-01-01','1900-01-01']) == True
    assert Type.valid_timeframe(['2020-01-01','1900-01-01']) == False

def test_valid_days():
    assert Type.valid_days(1) == 1
    assert Type.valid_days('1') == 1
    assert Type.valid_days(0) == 0
    assert Type.valid_days('reset') == 'reset'
    assert Type.valid_days(-1) == -1
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        Type.valid_days(1.1) 
        Type.valid_days('2022-01-01') 
        Type.valid_days([1 ,2, 3]) 
        Type.valid_days({1, 2, 3}) 
        Type.valid_days((1, 2, 3)) 
        Type.valid_days({1:'a', 2:'b', 3:'c'}) 
    assert "Please enter a valid number" in str(excinfo.value)




