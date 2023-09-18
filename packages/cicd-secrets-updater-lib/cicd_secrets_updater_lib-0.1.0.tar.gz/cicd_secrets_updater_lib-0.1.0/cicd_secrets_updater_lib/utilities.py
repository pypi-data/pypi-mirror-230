import re
import subprocess


def levenshtein_distance(a, b):
    """
    Calculate the Levenshtein distance between two strings
    :param a: The first string
    :param b: The second string
    :return: The Levenshtein distance between the two strings
    """

    if len(a) > len(b):
        a, b = b, a

    distances = range(len(a) + 1)
    for index2, char2 in enumerate(b):
        new_distances = [index2 + 1]

        for index1, char1 in enumerate(a):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min((distances[index1], distances[index1 + 1], new_distances[-1])))

        distances = new_distances

    return distances[-1]


def update_content_with_secrets(content, secrets):
    """
    Update content with the encrypted secrets.
    :param content: The content to update
    :param secrets: The secrets to update the content with
    """

    for key, value in secrets.items():
        content = re.sub(rf"{key}:\s+(.*)", f"{key}: {value}", content)

    return content


def execute_command(command):
    subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
