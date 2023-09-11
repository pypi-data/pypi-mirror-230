# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['openrpc', 'openrpc._discover']

package_data = \
{'': ['*']}

install_requires = \
['jsonrpc2-objects>=3.0.0,<4.0.0',
 'lorem-pysum>=1.4.3,<2.0.0',
 'pydantic>=2.3.0,<3.0.0']

setup_kwargs = {
    'name': 'openrpc',
    'version': '8.1.0',
    'description': 'Transport agnostic framework for developing OpenRPC servers.',
    'long_description': '# Python OpenRPC\n\n![](https://img.shields.io/badge/License-MIT-blue.svg)\n![](https://img.shields.io/badge/code%20style-black-000000.svg)\n![](https://img.shields.io/pypi/v/openrpc.svg)\n![](https://img.shields.io/badge/coverage-100%25-success)\n\n**Documentation**: https://python-openrpc.burkard.cloud\n\n**Source Code**: https://gitlab.com/mburkard/openrpc\n\nPython OpenRPC is a transport agnostic framework for quickly and easily\ndeveloping [OpenRPC](https://open-rpc.org/) servers in Python.\n\n## Requirements\n\n- Python 3.9+\n- [Pydantic](https://docs.pydantic.dev/latest/) for data models.\n\n## Installation\n\nOpenRPC is on PyPI and can be installed with:\n\n```shell\npip install openrpc\n```\n\nOr with [Poetry](https://python-poetry.org/)\n\n```shell\npoetry add openrpc\n```\n\n## Example\n\nThis is a minimal OpenRPC server using a [Sanic](https://sanic.dev/en/) websocket server\nas the transport method.\n\n```python\nimport asyncio\n\nfrom openrpc import RPCServer\nfrom sanic import Request, Sanic, Websocket\n\napp = Sanic("DemoServer")\nrpc = RPCServer(title="DemoServer", version="1.0.0")\n\n\n@rpc.method()\nasync def add(a: int, b: int) -> int:\n    return a + b\n\n\n@app.websocket("/api/v1/")\nasync def ws_process_rpc(_request: Request, ws: Websocket) -> None:\n    async def _process_rpc(request: str) -> None:\n        json_rpc_response = await rpc.process_request_async(request)\n        if json_rpc_response is not None:\n            await ws.send(json_rpc_response)\n\n    async for msg in ws:\n        asyncio.create_task(_process_rpc(msg))\n\n\nif __name__ == "__main__":\n    app.run()\n```\n\nExample In\n\n```json\n{\n  "id": 1,\n  "method": "add",\n  "params": {\n    "a": 1,\n    "b": 3\n  },\n  "jsonrpc": "2.0"\n}\n```\n\nExample Result Out\n\n```json\n{\n  "id": 1,\n  "result": 4,\n  "jsonrpc": "2.0"\n}\n```\n\n## Template App\n\nYou can bootstrap your OpenRPC server by cloning the\n[template app](https://gitlab.com/mburkard/openrpc-app-template).\n\n## Support the Developer\n\n<a href="https://www.buymeacoffee.com/mburkard" target="_blank">\n  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-blue.png" alt="Buy Me a Coffee"\n       width="217"\n       height="60"/>\n</a>\n',
    'author': 'Matthew Burkard',
    'author_email': 'matthewjburkard@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/mburkard/openrpc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
