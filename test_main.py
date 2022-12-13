import pytest

from super import main
from unittest import mock
import sys
from io import StringIO
from tools import Files as Files


@pytest.mark.parametrize("args, output", [
                        ([],"You seem lost. Use the --help command\n"),
                        (['--advance_time', 'reset'], "Date set back to today"),
                        (['--advance_time', '1'], "System date set to"),
                        (['--advance_time', '-1'], "System date set to")
                        ])
def test_parser(args, output):
    with mock.patch('sys.stdout', new_callable=StringIO):
        main(args)
        assert output in sys.stdout.getvalue()
    


@pytest.mark.parametrize("args, output", [
                        (['buy', '--name', 'potato', '--price', '0', '--expiration', '2023-12-01', '--quantity', '1'], "Got that for free? Good for you"),
                        (['buy', '--name', 'potato', '--price', '0.6', '--expiration', '2023-12-01', '--quantity', '1'], "OK"),
                        ])
def test_parser_buy(args, output):
    with mock.patch('sys.stdout', new_callable=StringIO):
        main(args)
        assert output in sys.stdout.getvalue()


@pytest.mark.parametrize("args, output", [
                        # (['sell', '--name', 'potato', '--price', '0.9', '--quantity', '1'], "OK"),
                        # (['sell', '--name', 'potato', '--price', '0.9', '--quantity', '10'], "Product not available"),
                        # (['sell', '--name', 'potato', '--price', '0.9', '--quantity', '10'], "Oops! We only have")
                        (['report', 'inventory', '--now'], "Your inventory for now"),
                        (['report', 'inventory', '--today'], "Today's inventory"),
                        (['report', 'inventory', '--yesterday'], "Yesterday's inventory"),
                        (['report', 'inventory', '--date', '1900-01-01'], "Your inventory for"),
                        (['report', 'inventory', '--timeframe', '1900-01-01', '2022-01-01'], "Your inventory for"),
                        (['report', 'revenue', '--now'], "Today's revenue"),
                        (['report', 'revenue', '--today'], "Today's revenue"),
                        (['report', 'revenue', '--yesterday'], "Yesterday's revenue"),
                        (['report', 'revenue', '--date', '1900-01-01'], "Your revenue for"),
                        (['report', 'revenue', '--timeframe', '1900-01-01', '2022-01-01'], "Your revenue for"),
                        (['report', 'profit', '--now'], "Today's profit"),
                        (['report', 'profit', '--today'], "Today's profit"),
                        (['report', 'profit', '--yesterday'], "Yesterday's profit"),
                        (['report', 'profit', '--date', '1900-01-01'], "Your profit for"),
                        (['report', 'profit', '--timeframe', '1900-01-01', '2022-01-01'], "Your profit for")
                        ])
def test_parser_report(args, output):
    with mock.patch('sys.stdout', new_callable=StringIO):
        main(args)
        assert output in sys.stdout.getvalue()


@pytest.mark.parametrize("args, output", [
                        (['sell', '--name', 'potato', '--price', '0.9'], "OK"),
                        (['sell', '--name', 'goat', '--price', '0.9'], "Product not available"),
                        (['sell', '--name', 'potato', '--price', '0.9', '--quantity', '99999999999999999999999999'], "Oops! We only have")
                        ])
def test_parser_sell(args, output):
    with mock.patch('sys.stdout', new_callable=StringIO):
        main(args)
        assert output in sys.stdout.getvalue()

        

# https://stackoverflow.com/questions/48359957/pytest-with-argparse-how-to-test-user-is-prompted-for-confirmation



