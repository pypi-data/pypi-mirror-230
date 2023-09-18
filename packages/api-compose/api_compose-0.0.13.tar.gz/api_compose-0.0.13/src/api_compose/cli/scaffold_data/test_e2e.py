"""
Script


"""
import pytest
from _pytest.capture import CaptureFixture
from typer.testing import CliRunner

from api_compose.cli.main import app

runner = CliRunner()


@pytest.mark.unauthenticated
def test_run(capsys: CaptureFixture):
    with capsys.disabled() as disabled:
        result = runner.invoke(app, ["run", "-f", "can_get_random_user_with_v1"])
        assert result.exit_code == 0, "Result is non-zero"
