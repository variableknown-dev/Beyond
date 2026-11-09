from brain.skill_loader import load_skills


def route(
    user_input,
    platform=None,
    model_provider=None,
    user_location=None,
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

        if getattr(skill, "supports_location", False):
            return skill.execute(
                user_input,
                model_provider=model_provider,
                user_location=user_location,
            )
        return skill.execute(user_input, model_provider=model_provider)

    return None
