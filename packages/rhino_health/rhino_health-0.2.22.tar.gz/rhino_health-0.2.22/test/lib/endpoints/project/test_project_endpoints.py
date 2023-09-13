# TODO: Need to setup CI in a way that actually has a backend to hit, right now this depends on cloud and on-prem running locally
import pytest


@pytest.mark.local
class TestProjectEndToEnd:
    def test_get_projects(self, session):
        projects = session.project.get_projects()
        assert len(projects)
        project = projects[0]
        single_project = session.project.get_projects([project.uid])[0]
        params_to_compare = {"uid", "status", "name", "type"}
        assert single_project.dict(include=params_to_compare) == project.dict(
            include=params_to_compare
        )
        # Make sure the helper property can be accessed
        single_project.collaborating_workgroups
