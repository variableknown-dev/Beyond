import importlib
import inspect
import pkgutil
import threading

import skills

from skills.base import Skill


# Cache loaded skills so we don't repeatedly inspect
# modules and recreate skill instances.
_skill_cache = {}
_skill_cache_lock = threading.RLock()


def load_skills(platform=None):
    """
    Automatically load and cache skills.

    Skills are cached separately for each platform
    to avoid reloading them for every task.
    """

    cache_key = id(platform)

    with _skill_cache_lock:

        # Reuse cached skills if the platform matches.
        cached = _skill_cache.get(cache_key)

        if cached is not None:

            cached_platform, loaded = cached

            if cached_platform is platform:
                return loaded

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

                    try:
                        instance = obj(
                            platform=platform
                        )

                    except TypeError:
                        instance = obj()

                    loaded[
                        instance.name.lower()
                    ] = instance

        # Store the platform reference alongside the skills.
        # Keeping the reference also prevents its ID from
        # being reused while the cache entry exists.
        _skill_cache[cache_key] = (
            platform,
            loaded,
        )

        return loaded
