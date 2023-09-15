from traitlets import default, Callable
from traitlets.config import LoggingConfigurable
import configparser
import inspect
import asyncio
import concurrent.futures
from typing import Dict


class JupyterServerParameters(LoggingConfigurable):
    handle_parameters_hook = Callable(
        help="""
        An optional hook function that you can implement to handle parameters
        passed to the `/parameters` endpoint. This maybe a coroutine.
        Example::
            def my_hook(self, parameters):
                self.log.info(f"The secret key is {parameters['key']}")
            c.JupyterServerParameters.handle_parameters_hook = my_hook
        """
    ).tag(config=True)


    @default("handle_parameters_hook")
    def _handle_parameters_hook_default(self, _, params):
        self.log.debug(f"Received {params!r} parameters")

    async def handle_parameters(self, params):
        await self.maybe_future(self.handle_parameters_hook(self, params))

    # Copied from jupyterhub/utils.py
    def maybe_future(self, obj):
        """Return an asyncio Future
        Use instead of gen.maybe_future
        For our compatibility, this must accept:
        - asyncio coroutine (gen.maybe_future doesn't work in tornado < 5)
        - tornado coroutine (asyncio.ensure_future doesn't work)
        - scalar (asyncio.ensure_future doesn't work)
        - concurrent.futures.Future (asyncio.ensure_future doesn't work)
        - tornado Future (works both ways)
        - asyncio Future (works both ways)
        """
        if inspect.isawaitable(obj):
            # already awaitable, use ensure_future
            return asyncio.ensure_future(obj)
        elif isinstance(obj, concurrent.futures.Future):
            return asyncio.wrap_future(obj)
        else:
            # could also check for tornado.concurrent.Future
            # but with tornado >= 5.1 tornado.Future is asyncio.Future
            f = asyncio.Future()
            f.set_result(obj)
            return f

    def to_dict(config: configparser) -> Dict:
        obj = []
        for section in config.sections():
            dict = {}
            dict['repoURL'] = section
            for opt in config.options(section):
                dict[opt] = config.get(section, opt)
            obj.append(dict)
        return obj
