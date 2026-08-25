from ddgs import DDGS


def search_web(query, max_results=5):
    """
    Searches the web using DDGS and returns a list of results.
    """

    try:
        with DDGS() as ddgs:

            results = list(
                ddgs.text(
                    query,
                    max_results=max_results
                )
            )

        if not results:
            return False, "No results found."

        formatted = []

        for result in results:

            title = result.get("title", "No title")
            body = result.get("body", "")
            url = result.get("href", "")

            formatted.append({
                "title": title,
                "body": body,
                "url": url,
            })

        return True, formatted

    except Exception as e:

        return False, str(e)
