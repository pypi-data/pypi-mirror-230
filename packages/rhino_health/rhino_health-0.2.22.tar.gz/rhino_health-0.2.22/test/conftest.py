import os

import pytest

TEST_USERNAME = os.environ.get("TEST_USERNAME")
TEST_PASSWORD = os.environ.get("TEST_PASSWORD")


def get_session():
    # TODO: We should create new users for each test once we have rate limiting in
    # Import here to avoid importing rhino_health when it isn't available.
    import rhino_health

    sdk_version = rhino_health.SDKVersion.PREVIEW
    base_url = os.environ.get("API_BASE_URL", rhino_health.ApiEnvironment.DEV_URL)
    session = rhino_health.login(
        username=TEST_USERNAME,
        password=TEST_PASSWORD,
        rhino_api_url=base_url,
        sdk_version=sdk_version,
    )
    return session


@pytest.fixture()
def session():
    return get_session()
