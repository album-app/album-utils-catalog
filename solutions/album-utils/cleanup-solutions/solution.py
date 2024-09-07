###album catalog: album-utils-catalog

from album.runner.api import setup, get_args

env_file = """
channels:
  - conda-forge
dependencies:
  - python=3.10
  - album
"""

def run():
    from album.api import Album
    from packaging.version import Version

    dry_run = get_args().dry_run

    # Initialize the Album instance
    print("Initializing Album instance...")
    album_instance = Album.Builder().build()
    album_instance.load_or_create_collection()    

    # Get all installed solutions
    print("Fetching installed solutions...")
    installed_solutions = album_instance.get_index_as_dict()
    catalogs = installed_solutions.get('catalogs', [])
    print(f"Installed solutions retrieved from {len(catalogs)} catalogs.")

    # Iterate over each catalog
    multiple_versions = {}
    for catalog in catalogs:
        catalog_name = catalog.get('name', 'Unknown Catalog')
        print(f"Processing catalog: {catalog_name}")
        solutions = catalog.get('solutions', [])
        print(f"Number of solutions in {catalog_name} is {len(solutions)}")
        
        # Iterate over each solution in the catalog
        for solution in solutions:
            solution_name = solution['setup']['name']
            group_name = solution['setup']['group']
            version = solution['setup']['version']
            installed = solution['internal']['installed']
            
            # Skip solutions that are not actually installed
            if not installed:
                # print(f"Skipping {solution_name} version {version} (not installed).")
                continue

            full_solution_name = f"{catalog_name}:{group_name}:{solution_name}:{version}"
            # print(f"Processing solution: {full_solution_name}")

            # Group solutions by name and collect versions
            key = f"{catalog_name}:{group_name}:{solution_name}"
            if key not in multiple_versions:
                multiple_versions[key] = []
            multiple_versions[key].append((version, full_solution_name))

    # Filter to keep only solutions with multiple versions
    # String sort is incorrect
    # multiple_versions = {k: sorted(v, key=lambda x: x[0], reverse=True) for k, v in multiple_versions.items() if len(v) > 1}
    
    multiple_versions = {k: sorted(v, key=lambda x: Version(x[0]), reverse=True) for k, v in multiple_versions.items() if len(v) > 1}

    # Display and uninstall solutions with multiple versions
    if not multiple_versions:
        print("No solutions with multiple versions found.")
        return

    cannot_uninstall = []  # List to keep track of solutions that cannot be uninstalled

    for solution, versions in multiple_versions.items():
        print(f"Solution: {solution}")
        print("Installed Versions:")
        for i, (version, full_solution_name) in enumerate(versions):
            indicator = "(Will be uninstalled)" if i > 0 else "(Keep)"
            print(f"  {version} {indicator}")

        # Uninstall all but the newest version
        if not dry_run:
            for version, full_solution_name in versions[1:]:  # Skip the newest version
                try:
                    album_instance.uninstall(full_solution_name)
                    print(f"Uninstalled: {full_solution_name}")
                except RuntimeError as e:
                    print(f"Failed to uninstall {full_solution_name}: {str(e)}")
                    cannot_uninstall.append(full_solution_name)
                except Exception as e:
                    print(f"Unexpected error while uninstalling {full_solution_name}: {str(e)}")
                    cannot_uninstall.append(full_solution_name)

    if dry_run:
        print("Dry run complete. No solutions were uninstalled.")
    else:
        print("Uninstall process complete.")
        if cannot_uninstall:
            print("\nThe following solutions could not be uninstalled due to dependencies:")
            for solution in cannot_uninstall:
                print(f"  {solution}")

setup(
    group="album-utils",
    name="cleanup-solutions",
    version="0.1.4",
    title="Album Solution Cleanup",
    description="Finds all solutions with multiple versions installed and uninstalls all but the newest version. Includes a dry run option.",
    solution_creators=["Kyle Harrington"],
    tags=["cleanup", "album"],
    license="MIT",
    album_api_version="0.5.1",
    args=[
        {
            "name": "dry_run",
            "type": "boolean",
            "required": False,
            "default": True,
            "description": "If True, only display what would be uninstalled. If False, perform the uninstalls."
        }
    ],
    run=run,
    dependencies={
        "environment_file": env_file
    },
)
