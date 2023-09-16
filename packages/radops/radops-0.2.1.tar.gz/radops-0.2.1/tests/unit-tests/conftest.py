import pytest

from radops.settings import settings, using_pydantic_v1


@pytest.fixture
def settings_fixture(tmp_path):
    """Fixture use to setup temporary folder and sets
    local mode to true (so no interaction with s3)
    """
    settings.base_path = tmp_path
    settings.model_config["env_file"] = tmp_path / ".env"
    if using_pydantic_v1:
        settings.Config.env_file = settings.model_config["env_file"]
    settings.s3_endpoint_url = None
    settings.validate_base_path(settings.base_path)
    return settings
