try:
    import colorama

    HAS_LIBS = (True,)
except ImportError as e:
    HAS_LIBS = False, str(e)


def __virtual__(hub):
    return HAS_LIBS


def display(hub, data):
    """
    Display the data from an idem run
    """
    if "comment" in data and "result" in data and not data.get("result"):
        return colorama.Fore.RED + str(data["comment"])

    if "ret" in data:
        return hub.output.nested.display(data["ret"])
    else:
        return hub.output.nested.display(data)
