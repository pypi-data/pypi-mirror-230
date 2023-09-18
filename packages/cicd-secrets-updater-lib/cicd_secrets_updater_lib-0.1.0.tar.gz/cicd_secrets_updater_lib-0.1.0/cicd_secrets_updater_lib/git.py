import os
import subprocess
import urllib
import uuid
from datetime import datetime

import github

from .detect_secrets import (
    delete_secrets_baseline,
    update_secrets_scan,
    audit_secrets
)

from .utilities import (
    levenshtein_distance,
    update_content_with_secrets,
    execute_command
)


def handle_exception(error_message, repo, branch_name, exception):
    """
    Handle an exception
    :param error_message: The error message to print
    :param repo: The repository in which the exception occurred
    :param branch_name: The branch name in which the exception occurred
    :param exception: The exception that occurred
    """

    print(f"{error_message}{repo.name}")

    print(exception)

    # Delete the branch
    delete_branch(repo, branch_name)


def delete_repository(payload, repo):
    """
    delete the repository from the {REPOSITORIES_PATH}/{repo.name} directory
    :param payload: The payload from the request
    :param repo: The repository to delete
    """

    repositories_path = payload.get("repositories_path")

    try:
        subprocess.check_output(
            f"rm -rf {repositories_path}/{repo.name}",
            shell=True,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError:
        print(f"Failed to delete {repositories_path}/{repo.name}")


def delete_branch(repo, branch_name):
    """
    Delete the branch
    :param repo: The repository to delete the branch from
    :param branch_name: The branch name to delete
    :return: None
    """

    try:
        ref = f"heads/{branch_name}"
        branch_ref = repo.get_git_ref(ref)
        branch_ref.delete()

        print(f"Successfully deleted branch {branch_name}")
    except Exception as e:
        print(f"Failed to delete branch {branch_name}")

        print(e)


def close_pull_request(pull_request):
    """
    Close the pull request
    :param pull_request: The pull request to close
    """

    try:
        pull_request.edit(state="closed")
    except Exception as e:
        print(f"Failed to close pull request {pull_request.number}")

        print(e)


def clone_repo_with_token(payload, repo, personal_access_token):
    """
    clone the repository with the personal access token
    :param payload: The payload from the request
    :param repo: The repository to clone
    :param personal_access_token: The personal access token to use
    """

    repositories_path = payload.get("repositories_path")

    # Parse the original clone URL
    parsed_url = urllib.parse.urlparse(repo.clone_url)

    # Insert the personal access token into the URL
    modified_url = f"https://{personal_access_token}@{parsed_url.netloc}{parsed_url.path}"

    try:
        subprocess.check_output(
            f"cd {repositories_path} && git clone {modified_url}",
            shell=True,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError:
        print(f"Failed to clone {repo.name}")

        return


def get_repositories(payload):
    """
    Get the repositories from the organization or owner
    :param payload: The payload from the request
    :return: The repositories from the organization or owner
    """

    g = payload.get("g")
    org = payload.get("org")
    owner = payload.get("owner")

    repositories = []

    if org is not None:
        repositories = g.get_organization(org).get_repos()
    elif owner is not None:
        repositories = g.get_user(owner).get_repos()

    return repositories


def find_repository_that_closely_resembles(payload, repo_name):
    """
    Find the repository that closely resembles the given repository name
    :param payload: The payload from the request
    :param repo_name: The repository name to find
    :return: The repository that closely resembles the given repository name
    """

    repositories = get_repositories(payload)

    # If there are no repositories, return None
    if not repositories:
        return None

    # Compute the edit distance for each repository
    min_distance = float('inf')
    closest_repo = None

    for repo in repositories:
        distance = levenshtein_distance(repo_name, repo.name)

        if distance < min_distance:
            min_distance = distance
            closest_repo = repo

    # Threshold for considering a repository as "closely resembling"
    # This can be adjusted based on requirements.
    threshold = 3

    return closest_repo.name if min_distance <= threshold else None


def create_branch_for_repo(payload, repo_name):
    """
    create a branch off of development
    :param payload: The payload from the request
    :param repo_name: The repository to create the branch for
    :return: The repository and branch that was created
    """

    g = payload.get("g")
    owner = payload.get("owner")
    org = payload.get("org")
    base_branch = payload.get("base_branch")

    try:
        repo = g.get_repo(f"{org or owner}/{repo_name}")
    except Exception as e:
        repo_name = find_repository_that_closely_resembles(payload, repo_name)

        if repo_name is None:
            print(f"Failed to get repository {repo_name}")

            print(e)

            return None, None, None

        repo = g.get_repo(f"{org or owner}/{repo_name}")

    try:
        branch = repo.get_branch(base_branch)
    except Exception as e:
        print(f"Failed to get branch development for {repo_name}")

        print(e)

        return None, None

    # create unique branch name with uuid
    branch_name = f"update-secrets-{uuid.uuid4()}"

    # create branch off of development
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=branch.commit.sha)

    return repo, branch, branch_name


def get_build_yml_content(repo, branch, branch_name):
    """
    Fetch the content of the build.yml file.
    :param repo: The repository to fetch the build.yml file from
    :param branch: The branch to fetch the build.yml file from
    :param branch_name: The branch name to fetch the build.yml file from
    """

    try:
        build_yml = repo.get_contents("build.yml", ref=branch.commit.sha)

        return build_yml, build_yml.decoded_content.decode()

    except github.GithubException as e:
        handle_exception('Failed to get build.yml for', repo, branch_name, e)

        return None, None


def update_build_yml(repo, branch, branch_name, secrets):
    """
    update the build.yml file
    :param repo: The repository to update
    :param branch: The branch to update
    :param branch_name: The branch name to update
    :param secrets: The secrets to update
    :return: True if the build.yml file was updated, False otherwise
    """

    build_yml, original_content = get_build_yml_content(repo, branch, branch_name)

    if not original_content:
        return False

    updated_content = update_content_with_secrets(original_content, secrets)

    if original_content == updated_content:
        print(f"build.yml for {repo.name} has not changed")
        print(f"Skipping {repo.name}")

        return False

    # create commit with updated build.yml
    try:
        repo.update_file(
            path="build.yml",
            message="Update build.yml with encrypted secrets",
            content=updated_content,
            sha=build_yml.sha,
            branch=branch_name
        )

        print(f"Successfully updated build.yml for {repo.name}")

        return True
    except github.GithubException as e:
        handle_exception(
            'Failed to update build.yml for ', repo, branch_name, e
        )

        return False


def clone_and_checkout(payload, repo, access_token, repositories_path, branch_name):
    """
    clone the repository and checkout the branch
    :param payload: The payload from the request
    :param repo: The repository to clone
    :param access_token: The access token to use
    :param repositories_path: The path to where the repositories are cloned
    :param branch_name: The branch name to checkout
    """

    clone_repo_with_token(payload, repo, access_token)

    try:
        execute_command(f"cd {repositories_path}/{repo.name} && git checkout {branch_name}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to checkout {branch_name} for {repo.name}")


def update_repo_baseline(secrets_baseline_path, repo, file, branch, branch_name):
    """
    update the .secrets.baseline file
    :param secrets_baseline_path: The path to the .secrets.baseline file
    :param repo: The repository to update
    :param file: The file to update
    :param branch: The branch to update
    :param branch_name: The branch name to update
    """

    file_content = open(secrets_baseline_path, "rb").read()

    try:
        existing_file = repo.get_contents(file, ref=branch.commit.sha)

        repo.update_file(path=file, message="Update .secrets.baseline", content=file_content, sha=existing_file.sha,
                         branch=branch_name)
    except github.UnknownObjectException:
        try:
            repo.create_file(path=file, message="Add .secrets.baseline", content=file_content, branch=branch_name)

            print(f"Successfully created .secrets.baseline for {repo.name}")
        except github.GithubException as e:
            handle_exception('Failed to create .secrets.baseline for ', repo, branch_name, e)

            return


def update_secrets_baseline(payload, repo, branch, branch_name):
    """
    update the .secrets.baseline file
    :param payload: The payload from the request
    :param repo: The repository to update
    :param branch: The branch to update
    :param branch_name: The branch name to update
    """

    g = payload.get("g")
    access_token = payload.get("access_token")
    repositories_path = payload.get("repositories_path")

    try:
        clone_and_checkout(payload, repo, access_token, repositories_path, branch_name)
        secrets_baseline_path = delete_secrets_baseline(repositories_path, repo)
        repository_path = os.path.dirname(secrets_baseline_path)

        update_secrets_scan(repository_path)
        audit_secrets(repository_path)
        update_repo_baseline(secrets_baseline_path, repo, ".secrets.baseline", branch, branch_name)
    except Exception as e:
        delete_repository(payload, repo)

        print(e)

        return

    delete_repository(payload, repo)

    print(f"Successfully updated .secrets.baseline for {repo.name}")


def generate_pull_request_body(encrypted_secrets):
    """
    Generate the pull request body
    :param encrypted_secrets: The encrypted secrets to add to the pull request
    :return: The pull request body
    """

    application_repo_url = "[cicd-secrets-updater](https://github.ibm.com/nicholas-adamou/cicd-secrets-updater)"
    keys_listed = '\n'.join(f'- `{key}`' for key in encrypted_secrets.keys())
    created_on = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""\
# Update CI/CD `build.yml` with updated encrypted secrets

The following secrets were updated:
{keys_listed}

This pull request was automatically created by {application_repo_url}.
To learn more about this application, please visit {application_repo_url}.

_Created on: {created_on}_."""


def create_pr(repo, body, branch_name, base_branch):
    """
    create a pull request for the given repository and branch with the updated encrypted secrets
    :param repo: The repository to create the pull request for
    :param body: The body of the pull request
    :param branch_name: The branch name to create the pull request for
    :param base_branch: The base branch to create the pull request for
    :return: Whether the pull request was created successfully
    """

    try:
        return repo.create_pull(
            title="Update CI/CD build.yml with updated encrypted secrets",
            body=body,
            head=branch_name,
            base=base_branch
        )
    except github.GithubException as e:
        handle_exception('Failed to create pull request for ', repo, branch_name, e)


def add_reviewers_to_pr(pull_request, team_reviewers, reviewers):
    """
    add reviewers to the pull request
    :param pull_request: The pull request to add the reviewers to
    :param team_reviewers: The team reviewers to add to the pull request
    :param reviewers: The reviewers to add to the pull request
    :return: Whether the reviewers were added successfully
    """

    # sourcery skip: extract-duplicate-method

    if team_reviewers is not None:
        for team in team_reviewers:
            try:
                pull_request.create_review_request(team_reviewers=[team.lower()])
            except github.GithubException:
                print(f"Failed to request team {team} to review the pull request {pull_request.number}")

                close_pull_request(pull_request)

                return False

        print(f"Successfully added team reviewers '{', '.join(team_reviewers)}'")

    if reviewers is not None:
        for reviewer in reviewers:
            try:
                pull_request.create_review_request(reviewers=[reviewer])
            except github.GithubException:
                print(f"Failed to add reviewer {reviewer} to the pull request {pull_request.number}")

                close_pull_request(pull_request)

                return False

        print(f"Successfully added reviewers '{', '.join(reviewers)}'")

    return True


def add_me_as_assignee(g, pull_request):
    """
    add me as an assignee to the pull request
    :param g: The GitHub instance
    :param pull_request: The pull request to add the assignee to
    :return: Whether the assignee was added successfully
    """

    me = g.get_user().login

    try:
        pull_request.add_to_assignees(me)
    except github.GithubException:
        print("Failed to add assignee to the pull request")

        close_pull_request(pull_request)

        return False

    print(f"Successfully added assignee '{g.get_user().name}'")

    return True


def create_pull_request(payload, repo, branch_name, encrypted_secrets):
    """
    create a pull request for the given repository and branch with the updated encrypted secrets
    :param payload: The payload from the request
    :param repo: The repository to create the pull request for
    :param branch_name: The branch name to create the pull request for
    :param encrypted_secrets: The encrypted secrets to add to the pull request
    """

    g = payload.get("g")
    base_branch = payload.get("base_branch")
    team_reviewers = payload.get("team_reviewers")
    reviewers = payload.get("reviewers")

    pull_request_body = generate_pull_request_body(encrypted_secrets)

    pull_request = create_pr(repo, pull_request_body, branch_name, base_branch)

    if not pull_request:
        return

    if not add_reviewers_to_pr(pull_request, team_reviewers, reviewers):
        delete_branch(repo, branch_name)

        return

    if not add_me_as_assignee(g, pull_request):
        delete_branch(repo, branch_name)

        return

    print(f"Successfully created pull request for {repo.name}")

    return pull_request.html_url
