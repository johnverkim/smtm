import unittest
from smtm import SimulationOperator
from unittest.mock import *
import requests
import threading

class SimulationOperatorTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch("smtm.Operator.initialize")
    def test_initialize_call_simulator_trader_initialize_with_config(self, OperatorInitialize):
        sop = SimulationOperator()
        trader = Mock()
        trader.initialize = MagicMock()
        strategy = Mock()
        dp = Mock()
        analyzer = Mock()
        sop.initialize("apple", "kiwi", dp, strategy, trader, analyzer, "papaya", "pear", "grape")
        OperatorInitialize.assert_called_once_with("apple", "kiwi", dp, strategy, trader, analyzer)
        trader.initialize.assert_called_once_with("apple", end="papaya", count="pear", budget="grape")

    @patch("smtm.Operator.initialize")
    def test_initialize_call_strategy_initialize_with_config(self, OperatorInitialize):
        sop = SimulationOperator()
        trader = Mock()
        strategy = Mock()
        strategy.initialize = MagicMock()
        dp = Mock()
        analyzer = Mock()
        dp.initialize_from_server = MagicMock()
        sop.initialize("apple", "kiwi", dp, strategy, trader, analyzer, "papaya", "pear", "grape")
        OperatorInitialize.assert_called_once_with("apple", "kiwi", dp, strategy, trader, analyzer)
        strategy.initialize.assert_called_once_with("grape")

    @patch("smtm.Operator.initialize")
    def test_initialize_call_simulator_dataProvider_initialize_from_server_correctly(self, OperatorInitialize):
        sop = SimulationOperator()
        trader = Mock()
        strategy = Mock()
        dp = Mock()
        analyzer = Mock()
        dp.initialize_from_server = MagicMock()
        sop.initialize("apple", "kiwi", dp, strategy, trader, analyzer, "papaya", "pear", "grape")
        OperatorInitialize.assert_called_once_with("apple", "kiwi", dp, strategy, trader, analyzer)
        dp.initialize_from_server.assert_called_once_with("apple", end="papaya", count="pear")

    @patch("smtm.Operator.setup")
    def test_setup_call_super_setup(self, OperatorSetup):
        sop = SimulationOperator()
        sop.setup(10)
        OperatorSetup.assert_called_once_with(10)

    @patch("smtm.Operator.start")
    def test_start_call_super_start(self, OperatorStart):
        sop = SimulationOperator()
        sop.start()
        OperatorStart.assert_called_once()

    @patch("smtm.Operator.stop")
    def test_stop_call_super_stop(self, OperatorStop):
        sop = SimulationOperator()
        sop.stop()
        OperatorStop.assert_called_once()

    def test_excute_trading_should_call_get_info_and_set_timer(self):
        timer_mock = Mock()
        threading_mock = Mock()
        threading_mock.Timer = MagicMock(return_value=timer_mock)

        operator = SimulationOperator()
        analyzer_mock = Mock()
        dp_mock = Mock()
        dp_mock.initialize = MagicMock(return_value="")
        dp_mock.get_info = MagicMock(return_value="mango")
        class DummyRequest():
            pass
        dummy_request = DummyRequest()
        dummy_request.price = 500
        strategy_mock = Mock()
        strategy_mock.update_trading_info = MagicMock(return_value="orange")
        strategy_mock.get_request = MagicMock(return_value=dummy_request)
        trader_mock = Mock()
        trader_mock.send_request = MagicMock()
        operator.initialize("apple", threading_mock, dp_mock, strategy_mock, trader_mock, analyzer_mock)
        operator.setup(27)
        operator._excute_trading()
        threading_mock.Timer.assert_called_once_with(27, ANY)
        timer_mock.start.assert_called_once()
        dp_mock.get_info.assert_called_once()

    def test_excute_trading_should_call_trader_send_request_and_strategy_update_result(self):
        timer_mock = Mock()
        threading_mock = Mock()
        threading_mock.Timer = MagicMock(return_value=timer_mock)
        operator = SimulationOperator()
        analyzer_mock = Mock()
        analyzer_mock.put_request = MagicMock()
        analyzer_mock.put_result = MagicMock()
        dp_mock = Mock()
        dp_mock.initialize = MagicMock(return_value="")
        dp_mock.get_info = MagicMock(return_value="mango")
        class DummyRequest():
            pass
        dummy_request = DummyRequest()
        dummy_request.price = 500
        strategy_mock = Mock()
        strategy_mock.update_trading_info = MagicMock(return_value="orange")
        strategy_mock.update_result = MagicMock()
        strategy_mock.get_request = MagicMock(return_value=dummy_request)
        trader_mock = Mock()
        trader_mock.send_request = MagicMock()
        operator.initialize("apple", threading_mock, dp_mock, strategy_mock, trader_mock, analyzer_mock)
        operator.setup(27)
        operator.start()
        analyzer_mock.put_request.assert_called_once_with(dummy_request)
        strategy_mock.update_trading_info.assert_called_once_with(ANY)
        trader_mock.send_request.assert_called_once_with(ANY, ANY)
        trader_mock.send_request.call_args[0][1]("mango")
        strategy_mock.update_result.assert_called_once_with("mango")
        analyzer_mock.put_result.assert_called_once_with("mango")

    def test_excute_trading_should_NOT_call_trader_send_request_when_request_is_invalid(self):
        timer_mock = Mock()
        threading_mock = Mock()
        threading_mock.Timer = MagicMock(return_value=timer_mock)

        operator = SimulationOperator()
        analyzer_mock = Mock()
        dp_mock = Mock()
        dp_mock.initialize = MagicMock(return_value="")
        dp_mock.get_info = MagicMock(return_value="mango")
        class DummyRequest():
            pass
        dummy_request = DummyRequest()
        dummy_request.price = 0
        strategy_mock = Mock()
        strategy_mock.update_trading_info = MagicMock(return_value="orange")
        strategy_mock.get_request = MagicMock(return_value=dummy_request)
        trader_mock = Mock()
        trader_mock.send_request = MagicMock()
        operator.initialize("apple", threading_mock, dp_mock, strategy_mock, trader_mock, analyzer_mock)
        operator.setup(27)
        operator.start()
        trader_mock.send_request.assert_not_called()

    def test_start_should_NOT_call_trader_send_request_when_request_is_None(self):
        timer_mock = Mock()
        threading_mock = Mock()
        threading_mock.Timer = MagicMock(return_value=timer_mock)

        operator = SimulationOperator()
        analyzer_mock = Mock()
        dp_mock = Mock()
        dp_mock.initialize = MagicMock(return_value="")
        dp_mock.get_info = MagicMock(return_value="mango")
        strategy_mock = Mock()
        strategy_mock.update_trading_info = MagicMock(return_value="orange")
        strategy_mock.get_request = MagicMock(return_value=None)
        trader_mock = Mock()
        trader_mock.send_request = MagicMock()
        operator.initialize("apple", threading_mock, dp_mock, strategy_mock, trader_mock, analyzer_mock)
        operator.setup(27)
        operator.start()
        trader_mock.send_request.assert_not_called()