"""
Unit tests for release workflow structure.

Tests the .github/workflows/release.yml file to ensure it has the correct
structure for uploading release assets with proper content types.
"""

import pytest
import yaml
from pathlib import Path


# Path to the release workflow file
WORKFLOW_PATH = Path(__file__).parent.parent / ".github" / "workflows" / "release.yml"


def load_workflow():
    """Load and parse the release workflow YAML file."""
    with open(WORKFLOW_PATH, 'r') as f:
        return yaml.safe_load(f)


class TestReleaseWorkflowStructure:
    """Test suite for release workflow structure."""

    def test_workflow_file_exists(self):
        """Test that the workflow file exists"""
        assert WORKFLOW_PATH.exists(), f"Workflow not found at {WORKFLOW_PATH}"
        assert WORKFLOW_PATH.is_file(), f"Workflow path is not a file: {WORKFLOW_PATH}"

    def test_workflow_is_valid_yaml(self):
        """Test that the workflow file is valid YAML"""
        try:
            workflow = load_workflow()
            assert workflow is not None, "Workflow YAML is empty"
        except yaml.YAMLError as e:
            pytest.fail(f"Workflow YAML is invalid: {e}")

    def test_workflow_has_create_release_job(self):
        """Test that workflow has create-release job"""
        workflow = load_workflow()
        assert 'jobs' in workflow, "Workflow missing jobs section"
        assert 'create-release' in workflow['jobs'], "Workflow missing create-release job"

    def test_create_release_job_has_required_steps(self):
        """Test that create-release job has all required steps"""
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        assert 'steps' in job, "create-release job missing steps"

        step_names = [step.get('name', '') for step in job['steps']]

        # Check for required steps
        assert 'Create GitHub Release' in step_names, \
            "Missing 'Create GitHub Release' step"
        assert 'Get release upload URL' in step_names, \
            "Missing 'Get release upload URL' step"
        assert 'Upload DEB package' in step_names, \
            "Missing 'Upload DEB package' step"
        assert 'Upload AppImage package' in step_names, \
            "Missing 'Upload AppImage package' step"

    def test_deb_upload_step_uses_correct_content_type(self):
        """
        Test that DEB upload step uses correct content type.
        Validates Requirement 3.3: Upload DEB_Package as Release_Asset
        """
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        steps = job['steps']

        # Find the DEB upload step
        deb_step = None
        for step in steps:
            if step.get('name') == 'Upload DEB package':
                deb_step = step
                break

        assert deb_step is not None, "DEB upload step not found"
        assert 'run' in deb_step, "DEB upload step missing run command"

        # Check that the step uses curl with correct content type
        run_command = deb_step['run']
        assert 'curl' in run_command, "DEB upload should use curl"
        assert 'application/vnd.debian.binary-package' in run_command, \
            "DEB upload missing correct content type"
        assert '--data-binary' in run_command, \
            "DEB upload should use --data-binary"
        assert 'Authorization: token' in run_command, \
            "DEB upload missing authorization header"

    def test_appimage_upload_step_uses_correct_content_type(self):
        """
        Test that AppImage upload step uses correct content type.
        Validates Requirement 3.4: Upload AppImage_Package as Release_Asset
        """
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        steps = job['steps']

        # Find the AppImage upload step
        appimage_step = None
        for step in steps:
            if step.get('name') == 'Upload AppImage package':
                appimage_step = step
                break

        assert appimage_step is not None, "AppImage upload step not found"
        assert 'run' in appimage_step, "AppImage upload step missing run command"

        # Check that the step uses curl with correct content type
        run_command = appimage_step['run']
        assert 'curl' in run_command, "AppImage upload should use curl"
        assert 'application/vnd.appimage' in run_command, \
            "AppImage upload missing correct content type"
        assert '--data-binary' in run_command, \
            "AppImage upload should use --data-binary"
        assert 'Authorization: token' in run_command, \
            "AppImage upload missing authorization header"

    def test_deb_upload_uses_correct_filename(self):
        """Test that DEB upload step uses correct filename pattern"""
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        steps = job['steps']

        deb_step = None
        for step in steps:
            if step.get('name') == 'Upload DEB package':
                deb_step = step
                break

        assert deb_step is not None
        run_command = deb_step['run']

        # Check filename pattern
        assert 'code-launcher_${VERSION}_all.deb' in run_command, \
            "DEB filename pattern incorrect"
        assert 'DEB_FILE=' in run_command, "DEB_FILE variable not set"
        assert 'DEB_NAME=' in run_command, "DEB_NAME variable not set"

    def test_appimage_upload_uses_correct_filename(self):
        """Test that AppImage upload step uses correct filename pattern"""
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        steps = job['steps']

        appimage_step = None
        for step in steps:
            if step.get('name') == 'Upload AppImage package':
                appimage_step = step
                break

        assert appimage_step is not None
        run_command = appimage_step['run']

        # Check filename pattern
        assert 'CodeLauncher-${VERSION}-x86_64.AppImage' in run_command, \
            "AppImage filename pattern incorrect"
        assert 'APPIMAGE_FILE=' in run_command, "APPIMAGE_FILE variable not set"
        assert 'APPIMAGE_NAME=' in run_command, "APPIMAGE_NAME variable not set"

    def test_get_release_upload_url_step_exists(self):
        """Test that step to get release upload URL exists"""
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        steps = job['steps']

        get_url_step = None
        for step in steps:
            if step.get('name') == 'Get release upload URL':
                get_url_step = step
                break

        assert get_url_step is not None, "Get release upload URL step not found"
        assert 'run' in get_url_step, "Get URL step missing run command"
        assert 'id' in get_url_step, "Get URL step missing id"
        assert get_url_step['id'] == 'get_release', "Get URL step has wrong id"

        run_command = get_url_step['run']
        assert 'gh api' in run_command, "Should use gh api to get release data"
        assert 'upload_url' in run_command, "Should extract upload_url"
        assert 'GITHUB_OUTPUT' in run_command, "Should output to GITHUB_OUTPUT"

    def test_upload_steps_use_upload_url_from_previous_step(self):
        """Test that upload steps reference the upload URL from get_release step"""
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        steps = job['steps']

        # Find upload steps
        deb_step = None
        appimage_step = None
        for step in steps:
            if step.get('name') == 'Upload DEB package':
                deb_step = step
            elif step.get('name') == 'Upload AppImage package':
                appimage_step = step

        assert deb_step is not None
        assert appimage_step is not None

        # Check that both steps reference the upload URL
        deb_command = deb_step['run']
        appimage_command = appimage_step['run']

        assert '${{ steps.get_release.outputs.upload_url }}' in deb_command, \
            "DEB upload doesn't reference upload URL from get_release step"
        assert '${{ steps.get_release.outputs.upload_url }}' in appimage_command, \
            "AppImage upload doesn't reference upload URL from get_release step"

    def test_upload_steps_have_proper_asset_names(self):
        """Test that upload steps set proper asset names in query parameters"""
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        steps = job['steps']

        deb_step = None
        appimage_step = None
        for step in steps:
            if step.get('name') == 'Upload DEB package':
                deb_step = step
            elif step.get('name') == 'Upload AppImage package':
                appimage_step = step

        assert deb_step is not None
        assert appimage_step is not None

        # Check that asset names are passed as query parameters
        deb_command = deb_step['run']
        appimage_command = appimage_step['run']

        assert '?name=$DEB_NAME' in deb_command, \
            "DEB upload doesn't set asset name in query parameter"
        assert '?name=$APPIMAGE_NAME' in appimage_command, \
            "AppImage upload doesn't set asset name in query parameter"

    def test_create_release_step_comes_before_uploads(self):
        """Test that Create GitHub Release step comes before upload steps"""
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        steps = job['steps']

        step_names = [step.get('name', '') for step in steps]

        create_index = step_names.index('Create GitHub Release')
        get_url_index = step_names.index('Get release upload URL')
        deb_index = step_names.index('Upload DEB package')
        appimage_index = step_names.index('Upload AppImage package')

        assert create_index < get_url_index, \
            "Create release must come before getting upload URL"
        assert get_url_index < deb_index, \
            "Get upload URL must come before DEB upload"
        assert get_url_index < appimage_index, \
            "Get upload URL must come before AppImage upload"

    def test_workflow_has_proper_permissions(self):
        """Test that workflow has proper permissions for release creation"""
        workflow = load_workflow()
        assert 'permissions' in workflow, "Workflow missing permissions"
        permissions = workflow['permissions']
        assert 'contents' in permissions, "Missing contents permission"
        assert permissions['contents'] == 'write', \
            "contents permission should be 'write' for release creation"


class TestReleaseWorkflowRequirements:
    """Test suite validating specific requirements for task 9.2."""

    def test_requirement_3_3_deb_upload(self):
        """
        Requirement 3.3: THE System SHALL upload the DEB_Package as a Release_Asset
        Task 9.2: Upload DEB package with correct content type
        """
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        steps = job['steps']

        deb_step = None
        for step in steps:
            if step.get('name') == 'Upload DEB package':
                deb_step = step
                break

        assert deb_step is not None, "DEB upload step not found"
        run_command = deb_step['run']
        assert 'application/vnd.debian.binary-package' in run_command, \
            "DEB package not uploaded with correct content type"

    def test_requirement_3_4_appimage_upload(self):
        """
        Requirement 3.4: THE System SHALL upload the AppImage_Package as a Release_Asset
        Task 9.2: Upload AppImage with correct content type
        """
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        steps = job['steps']

        appimage_step = None
        for step in steps:
            if step.get('name') == 'Upload AppImage package':
                appimage_step = step
                break

        assert appimage_step is not None, "AppImage upload step not found"
        run_command = appimage_step['run']
        assert 'application/vnd.appimage' in run_command, \
            "AppImage not uploaded with correct content type"

    def test_task_9_2_proper_asset_names(self):
        """
        Task 9.2: Set proper asset names
        """
        workflow = load_workflow()
        job = workflow['jobs']['create-release']
        steps = job['steps']

        # Check DEB asset name
        deb_step = None
        for step in steps:
            if step.get('name') == 'Upload DEB package':
                deb_step = step
                break

        assert deb_step is not None
        deb_command = deb_step['run']
        assert 'DEB_NAME="code-launcher_${VERSION}_all.deb"' in deb_command, \
            "DEB asset name not properly set"

        # Check AppImage asset name
        appimage_step = None
        for step in steps:
            if step.get('name') == 'Upload AppImage package':
                appimage_step = step
                break

        assert appimage_step is not None
        appimage_command = appimage_step['run']
        assert 'APPIMAGE_NAME="CodeLauncher-${VERSION}-x86_64.AppImage"' in appimage_command, \
            "AppImage asset name not properly set"
