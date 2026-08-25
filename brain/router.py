from brain.skill_loader import load_skills


def route(
    user_input,
    platform=None,
):
    """
    Route a request to the appropriate skill.
    """

    skills = load_skills(platform)

    for skill in skills.values():

        if not skill.can_handle(user_input):
            continue

        if platform is not None:

            for capability in skill.required_capabilities:

                if not platform.has_capability(
                    capability
                ):

                    return (
                        f"Sorry, the "
                        f"'{skill.name}' skill "
                        f"isn't available on "
                        f"{platform.name}."
                    )

        return skill.execute(user_input)

    return None
