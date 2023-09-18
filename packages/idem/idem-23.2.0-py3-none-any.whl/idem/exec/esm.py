from typing import Any
from typing import Dict


async def unlock(
    hub,
    provider: str,
    profile: str = "default",
    acct_data: Dict[str, Any] = None,
):
    """
    Remove the lock from the esm profile based on the provider and profile name.
    Generic example:

    .. code-block:: bash

        $ idem exec esm.unlock provider=[provider-name] <profile=[profile-name]>

    Specific example:

    .. code-block:: bash

        $ idem exec esm.unlock provider=aws profile=cloud-1
    """
    # Get the acct data from the kwargs and fallback to the acct_data in the current runtime
    # Get the ESM ctx
    ctx = await _get_esm_ctx(hub, provider, profile, acct_data)

    hub.log.info(f"Unlocking state run on provider {provider} using profile {profile}")

    try:
        await hub.esm[provider].exit_(ctx, None, None)
    except Exception as e:
        hub.log.error(f"{e.__class__.__name__}: {e}")
        return {
            "comment": [f"{e.__class__.__name__}: {e}"],
            "result": False,
            "ret": None,
        }
    hub.log.info("esm.unlock finished successfully")
    return {"result": True, "comment": "esm.unlock completed successfully", "ret": {}}


async def remove(
    hub,
    tag: str,
    provider: str = "local",
    profile: str = "default",
    acct_data: Dict[str, Any] = None,
    cache_dir: str = None,
    serial_plugin: str = "msgpack",
):
    """
    Removes the resource with the given 'tag' from the esm.
    Returns the removed element if found, otherwise no-op. To find the exact tag use 'exec esm.show'.
    Default provider is local cache.
    Generic example:

    .. code-block:: bash

        $ idem exec esm.remove provider=[provider-name] tag=[tag-in-esm] <profile=[profile-name]>

    Specific example:

    .. code-block:: bash

        $ idem exec esm.remove tag="aws.iam.role_|-Create AWS IAM role ReadOnly01_|-ReadOnly01_|-"
        provider=aws profile=cloud-1
    """
    # Get the acct data from the kwargs and fallback to the acct_data in the current runtime
    ctx = await _get_esm_ctx(hub, provider, profile, acct_data)

    # If no profile was specified then use the default profile
    if provider == "local" and not ctx.acct:
        hub.log.debug("Using the default local ESM profile")
        ctx = await hub.idem.acct.ctx(
            "esm.local",
            profile=None,
            acct_data={
                "profiles": {
                    "esm.local": {
                        None: {
                            "run_name": "cli",
                            "cache_dir": hub.OPT.idem.cache_dir
                            if cache_dir is None
                            else cache_dir,
                            "serial_plugin": serial_plugin,
                        }
                    }
                }
            },
        )

    # Enter the context of the Enforced State Manager
    # Do this outside of the try/except so that exceptions don't cause unintentional release of lock in exit
    try:
        handle = await hub.esm[provider].enter(ctx)
    except Exception as e:
        raise RuntimeError(
            f"Fail to enter enforced state management: {e.__class__.__name__}: {e}"
        )

    ret = {}
    try:
        state: Dict[str, Any] = await hub.esm[provider].get_state(ctx) or {}
        if tag in state:
            ret = state.pop(tag)
            comment = f"Removed resource with tag '{tag}' from ESM on provider '{provider}' using profile '{profile}'"
            hub.log.info(comment)
            print(comment)
            await hub.esm[provider].set_state(ctx, state)
        else:
            comment = f"Cannot find resource with tag '{tag}' in ESM on provider '{provider}' using profile '{profile}'"
            print(comment)
            hub.log.info(comment)
    finally:
        # Exit the context of the Enforced State Manager
        try:
            await hub.esm[provider].exit_(ctx, handle, None)
        except Exception as e:
            raise RuntimeError(
                f"Fail to exit enforced state management: {e.__class__.__name__}: {e}"
            )

    return {"result": True, "comment": f"{comment}", "ret": ret}


async def show(
    hub,
    provider: str = "local",
    profile: str = "default",
    acct_data: Dict[str, Any] = None,
    cache_dir: str = None,
    serial_plugin: str = "msgpack",
):
    """
    Displays the content of ESM. Default provider is local cache.
    Generic example:

    .. code-block:: bash

        $ idem exec esm.show provider=[provider-name] <profile=[profile-name]>

    Specific example:

    .. code-block:: bash

        $ idem exec esm.show provider=aws profile=cloud-1
    """
    # Get the ESM ctx
    ctx = await _get_esm_ctx(hub, provider, profile, acct_data)

    # If no profile was specified then use the default profile
    if provider == "local" and not ctx.acct:
        hub.log.debug("Using the default local ESM profile")
        ctx = await hub.idem.acct.ctx(
            "esm.local",
            profile=None,
            acct_data={
                "profiles": {
                    "esm.local": {
                        None: {
                            "run_name": "cli",
                            "cache_dir": hub.OPT.idem.cache_dir
                            if cache_dir is None
                            else cache_dir,
                            "serial_plugin": serial_plugin,
                        }
                    }
                }
            },
        )

    # Enter the context of the Enforced State Manager
    # Do this outside of the try/except so that exceptions don't cause unintentional release of lock in exit
    try:
        handle = await hub.esm[provider].enter(ctx)
    except Exception as e:
        raise RuntimeError(
            f"Fail to enter enforced state management: {e.__class__.__name__}: {e}"
        )

    try:
        state: Dict[str, Any] = await hub.esm[provider].get_state(ctx) or {}
        for tag in state:
            print(f"{tag}: {state.get(tag)}")
    finally:
        # Exit the context of the Enforced State Manager
        try:
            await hub.esm[provider].exit_(ctx, handle, None)
        except Exception as e:
            raise RuntimeError(
                f"Fail to exit enforced state management: {e.__class__.__name__}: {e}"
            )

    return {"result": True, "comment": [], "ret": {}}


async def validate(
    hub,
    provider: str = "local",
    profile: str = "default",
    acct_data: Dict[str, Any] = None,
    cache_dir: str = None,
    serial_plugin: str = "msgpack",
):
    """
    Validates access and that the version of the ESM is up to date.
    Default provider is local cache.
    Generic example:

    .. code-block:: bash

        $ idem exec esm.validate provider=[provider-name] <profile=[profile-name]>

    Specific example:

    .. code-block:: bash

        $ idem exec esm.validate provider=aws profile=cloud-1
    """
    ret = {"result": True, "comment": [], "ret": {}}
    # Validate you can log in to ESM and the version is compatible.
    ctx = await _get_esm_ctx(hub, provider, profile, acct_data)

    # If no profile was specified then use the default profile
    if provider == "local" and not ctx.acct:
        hub.log.debug("Using the default local ESM profile")
        ctx = await hub.idem.acct.ctx(
            "esm.local",
            profile=None,
            acct_data={
                "profiles": {
                    "esm.local": {
                        None: {
                            "run_name": "cli",
                            "cache_dir": hub.OPT.idem.cache_dir
                            if cache_dir is None
                            else cache_dir,
                            "serial_plugin": serial_plugin,
                        }
                    }
                }
            },
        )

    # Enter the context of the Enforced State Manager
    # Do this outside of the try/except so that exceptions don't cause unintentional release of lock in exit
    try:
        handle = await hub.esm[provider].enter(ctx)
    except Exception as e:
        ret["result"] = False
        ret[
            "comment"
        ] = f"Fail to enter enforced state management: {e.__class__.__name__}: {e}"
        return ret

    try:
        state: Dict[str, Any] = await hub.esm[provider].get_state(ctx) or {}
        if state and state.get(hub.idem.managed.ESM_METADATA_KEY):
            metadata = state.get(hub.idem.managed.ESM_METADATA_KEY)
            esm_version = tuple(metadata.get("version", (1, 0, 0)))
            if esm_version != hub.esm.VERSION:
                msg = f"ESM version {esm_version} does not match recent version {hub.esm.VERSION}"
                ret["result"] = False
            else:
                msg = f"ESM is up to date. Version: {esm_version}."
            ret["comment"] = msg
    except Exception as e:
        ret["result"] = False
        ret[
            "comment"
        ] = f"Fail to check meta data of enforced state management: {e.__class__.__name__}: {e}"
    finally:
        # Exit the context of the Enforced State Manager
        try:
            await hub.esm[provider].exit_(ctx, handle, None)
        except Exception as e:
            raise RuntimeError(
                f"Fail to exit enforced state management: {e.__class__.__name__}: {e}"
            )

    print(f"{ret['comment']}")
    return ret


def version(hub):
    """
    Get the latest supported esm version from idem
    """
    return {
        "result": True,
        "comment": None,
        "ret": ".".join(str(x) for x in hub.esm.VERSION),
    }


async def _get_esm_ctx(
    hub,
    provider: str = "local",
    profile: str = "default",
    acct_data: Dict[str, Any] = None,
):
    # Get the acct data from the kwargs and fallback to the acct_data in the current runtime
    # Get the ESM ctx
    return await hub.idem.acct.ctx(
        f"esm.{provider}",
        profile=profile,
        acct_key=hub.OPT.acct.get("acct_key"),
        acct_file=hub.OPT.acct.get("acct_file"),
        acct_blob=hub.OPT.acct.get("acct_blob"),
        acct_data=acct_data,
    )
