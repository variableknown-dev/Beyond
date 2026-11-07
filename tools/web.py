from ddgs import DDGS


def search_web(query, max_results=5, search_type="text"):
    """
    Searches the web using DDGS and returns a list of results.
    """

    try:
        with DDGS() as ddgs:
            if search_type == "news":
                try:
                    results = list(
                        ddgs.news(
                            query,
                            region="wt-wt",
                            max_results=max_results,
                            backend="bing",
                        )
                    )
                except Exception:
                    # Keep other free news backends available if Bing News
                    # is temporarily unreachable.
                    results = list(
                        ddgs.news(
                            query,
                            region="wt-wt",
                            max_results=max_results,
                            backend="auto",
                        )
                    )
            else:
                results = list(
                    ddgs.text(
                        query,
                        max_results=max_results,
                    )
                )

        if not results:
            return False, "No results found."

        formatted = []

        for result in results:

            title = result.get("title", "No title")
            body = result.get("body", "")
            url = result.get("url") or result.get("href", "")
            date = result.get("date", "")
            source = result.get("source", "")

            formatted.append({
                "title": title,
                "body": body,
                "url": url,
                "date": date,
                "source": source,
            })

        return True, formatted

    except Exception as e:

        return False, str(e)
