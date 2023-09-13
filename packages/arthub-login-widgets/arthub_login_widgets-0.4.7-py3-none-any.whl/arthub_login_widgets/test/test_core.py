# Import third-party modules
import pytest

# Import local modules
from arthub_login_widgets.core import LoginWindow


class FakeAPI:
    def __init__(self, mocker, login_status=True):
        self.login_status = login_status
        self.mocker = mocker

    def login(self, account, password):
        return self.mocker.MagicMock(
            is_succeeded=self.mocker.MagicMock(return_value=self.login_status),
            error_message=self.mocker.MagicMock(return_value="login failed."),
        )


class TestLoginWindow:
    @pytest.fixture(autouse=True)
    def setup(self, mocker, qtbot):
        self.widget = LoginWindow(api=FakeAPI(mocker))
        qtbot.addWidget(self.widget)

    def test_show_widget(self):
        self.widget.line_edit_password.setText("xxxx")
        assert self.widget.line_edit_password.text() == "xxxx"

    def test_run_callback(self):
        def _custom_callback(api):
            print("run custom callback...")
            api._custom_callback = "custom callback"
            assert True

        self.widget.line_edit_account.setText("abc")
        self.widget.line_edit_password.setText("abc")
        self.widget.set_callback(_custom_callback)
        self.widget.login()
        assert self.widget._custom_callback == "custom callback"

    def test_login_failed(self, mocker):
        widget = LoginWindow(FakeAPI(mocker=mocker, login_status=False))
        widget.line_edit_account.setText("abc")
        widget.line_edit_password.setText("abc")

        widget.login()
        assert widget.label_prompt.text() == "login failed."
