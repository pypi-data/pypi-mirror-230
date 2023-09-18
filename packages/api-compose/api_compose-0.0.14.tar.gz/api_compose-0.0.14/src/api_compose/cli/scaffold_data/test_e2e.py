"""
Script


"""
import pytest
from _pytest.capture import CaptureFixture
from typer.testing import CliRunner

from api_compose.cli.main import app

runner = CliRunner()


@pytest.fixture()
def clean_up(capsys: CaptureFixture):
    yield
    with capsys.disabled() as disabled:
        result = runner.invoke(app, ["clean"])


@pytest.mark.unauthenticated
def test_run(
        capsys: CaptureFixture,
        clean_up):
    with capsys.disabled() as disabled:
        result = runner.invoke(app, [
            "run",
            "-f", "can_get_random_user_with_v1"
        ]
                               )
        assert result.exit_code == 0, "Result is non-zero"
