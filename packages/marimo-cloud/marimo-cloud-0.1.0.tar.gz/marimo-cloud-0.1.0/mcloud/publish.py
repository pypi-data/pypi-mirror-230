import os
import tarfile
from mcloud.client import create_marimo_client
from mcloud.generated import CreateApplicationRequest
import mcloud.prompter as prompter
from mcloud.config import read_app_config, write_app_config
from rich.console import Console

console = Console()


def read_app_py() -> str:
    """
    Read app.py from current directory

    TODO: make location configurable
    """
    try:
        with open('app.py', 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise Exception('app.py not found in current directory')


def read_requirements_txt() -> str:
    """
    Read requirements.txt from current directory

    TODO: make location configurable
    """
    try:
        with open('requirements.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise ""


def publish() -> None:
    """
    Publish current directory to Marimo
    """
    # Create client
    client = create_marimo_client()
    # Read app config
    app_config = read_app_config()

    # If no app id, ask to link app
    if not app_config.app_id:
        # Ask to link app or create new
        link_or_new = prompter.select(
            "No application linked. Would you like to link an existing application or create a new one?",
            ["Link existing", "Create new", "Cancel"]
        )

        # If cancel, exit
        if link_or_new == "Cancel":
            return
        # If link existing, ask for app id
        elif link_or_new == "Link existing":
            # Select organizations
            orgs = client.list_organizations()
            if len(orgs) == 0:
                console.print("[red]No organizations found[/red]")
                return
            selected_org = prompter.select(
                "Select organization",
                orgs,
                lambda org: org.organization_slug,
            )

            # Select app
            apps = client.list_applications(
                organization_id=selected_org.organization_id)
            if len(apps) == 0:
                console.print("[red]No applications found[/red]")
                return
            selected_app = prompter.select(
                "Select application",
                apps,
                lambda app: f"{app.name} ({app.application_slug})",
            )
        # If create new, ask for app name
        elif link_or_new == "Create new":
            # Select organizations
            orgs = client.list_organizations()
            if len(orgs) == 0:
                console.print("[red]No organizations found[/red]")
                return
            selected_org = prompter.select(
                "Select organization",
                orgs,
                lambda org: org.organization_slug,
            )

            # Ask for app name
            app_name = prompter.text("Enter a name for your application")

            # Ask for app slug
            app_slug = prompter.slug(
                "Enter a slug for your application", default=app_name)

            # Create app
            selected_app = client.create_application(request=CreateApplicationRequest(
                application_slug=app_slug,
                name=app_name,
                organization_id=selected_org.organization_id,
            ))
        else:
            raise Exception("Invalid option selected")

        # Save app id
        app_config.app_id = selected_app.application_id
        app_config.app_slug = selected_app.application_slug
        write_app_config(app_config)

    else:
        # Load app
        app = client.get_application(application_id=app_config.app_id)

        # If slug doesn't match, write new slug its only used for display
        if app.application_slug != app_config.app_slug:
            app_config.app_slug = app.application_slug
            write_app_config(app_config)

        # Confirm app
        confirm = prompter.confirm(
            f"Deploy application [cyan bold]{app.application_slug}[/cyan bold]?"
        )

        if not confirm:
            return

    # Read app.py and requirements.txt
    code = read_app_py()
    requirements = read_requirements_txt()
    file = _tar_inputs()

    with console.status(f"[cyan]Deploying [bold]{app_config.app_slug}[/bold]...[/cyan]"):
        # Start deployment
        try:
            if file is None:
                response = client.create_deployment(
                    application_id=app_config.app_id,
                    code=code,
                    requirements_txt=requirements)
            else:
                response = client.create_deployment_with_file(
                    application_id=app_config.app_id,
                    code=code,
                    requirements_txt=requirements,
                    file=file)
            # TODO: link to deployment when we support that page
            deployment_url = f"https://marimo.io/dashboard/applications/{response.application_id}"
            console.print(f"[green]Application deployed![/green]")
            console.print(
                f"View your application at [cyan]{deployment_url}[/cyan]")
        except Exception as e:
            console.print(f"[red]Error deploying application: {e}[/red]")
            raise e


def _tar_inputs() -> tarfile.TarFile:
    """
    Tar the inputs for the deployment.

    If there is a folder called input or inputs, tar that folder and return the tar file.
    """
    folders = ['input', 'inputs']

    # Check if inputs folder exists
    for folder in folders:
        if os.path.isdir(folder):
            break
    else:
        # No inputs folder found
        return None

    # Create tar file
    tar = tarfile.open("inputs.tar.gz", "w:gz")
    for folder in folders:
        if os.path.isdir(folder):
            tar.add(folder, arcname=os.path.basename(folder))
    # Close tar file
    tar.close()

    # Return tar file
    return open("inputs.tar.gz", "rb")
