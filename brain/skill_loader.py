import importlib
import inspect
import pkgutil

import skills

from skills.base import Skill


def load_skills(platform=None):
    """
    Automatically loads every Skill inside
    the skills package.

    The platform is injected into skills that
    support platform-specific functionality.
    """

    loaded = {}

    for _, module_name, _ in pkgutil.iter_modules(
        skills.__path__
    ):

        if module_name == "base":
            continue

        module = importlib.import_module(
            f"skills.{module_name}"
        )

        for _, obj in inspect.getmembers(
            module,
            inspect.isclass,
        ):

            if (
                issubclass(obj, Skill)
                and obj is not Skill
            ):

                # -------------------------------------------------
                # Try to initialize the skill with the platform.
                # -------------------------------------------------

                try:

                    instance = obj(
                        platform=platform
                    )

                except TypeError:

                    # -------------------------------------------------
                    # Skills that don't need a platform can still
                    # initialize normally.
                    # -------------------------------------------------

                    instance = obj()

                loaded[
                    instance.name.lower()
                ] = instance

    return loaded
