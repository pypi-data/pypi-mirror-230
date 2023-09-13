from fovus.constants.cli_constants import EMAIL, USERNAME

GENERIC_SUCCESS = "Success!"
OUTPUTS = "==== Outputs ===="

USER_CONFIG_EMAIL_UPDATE_MESSAGE = (
    f"Your config uses the {USERNAME} key instead of the {EMAIL} key or contains both. "
    f"User configs should use the {EMAIL} key instead of the {USERNAME} key. "
    f"\n\t- If both the {EMAIL} key and {USERNAME} key are present, the {EMAIL} key/value pair will be used. "
    f"\n\t- This will not affect CLI behavior."
)
