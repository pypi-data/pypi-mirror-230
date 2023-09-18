import requests


def encrypt_secrets(payload, repo, secrets):
    """
    encrypt the set of secrets for a given repository
    :param payload: The payload from the request
    :param repo: The repository to encrypt the secrets for
    :param secrets: The secrets to encrypt
    :return: The encrypted mvn-repo-username, mvn-repo-password, and private-dependencies
    """

    cicd_adopter_service_url = payload.get("cicd_adopter_service_url")
    org = payload.get("org")
    owner = payload.get("owner")
    access_token = payload.get("access_token")

    # Filter out None values from secrets
    filtered_secrets = {key: value for key, value in secrets.items() if value is not None}

    url = f"{cicd_adopter_service_url}/{org or owner}/{repo.name}/encrypt_all"

    payload = {
        "githubAccessToken": f'{access_token}',
        "plainTexts": dict(filtered_secrets),
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers
    )

    if response.status_code != 200:
        return None  # return None for all secrets if encryption fails

    json = response.json()

    # build encrypted_secrets dictionary off of the keys in filtered_secrets
    # and the values from the json response

    encrypted_secrets = filtered_secrets.copy()

    for key in filtered_secrets:
        encrypted_secrets[key] = json[key]

    return encrypted_secrets
