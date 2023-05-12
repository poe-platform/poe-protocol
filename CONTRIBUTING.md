# General

- All changes should be made through pull requests
- Pull requests should only be merged once all checks pass
- The repo uses Black for formatting Python code, Prettier for formatting Markdown,
  Pyright for type-checking Python, and a few other tools
- To run the CI checks locally:
  - `pip install pre-commit`
  - `pre-commit run --all` (or `pre-commit install` to install the pre-commit hook)

# Spec changes

All spec changes should come with:

- An enhancement to the [catbot](/docs/catbot.md) document that provides an example of
  how to use the new feature.
- Changes to the `fastapi_poe` and `aiohttp_poe` client libraries so that users can use
  the new feature.

# Releases

To release a new version of the `fastapi-poe` and `aiohttp-poe` client libraries, do the
following:

- Make a PR updating the version number in `aiohttp_poe/pyproject.toml` and
  `fastapi_poe/pyproject.toml` (example:
  https://github.com/poe-platform/poe-protocol/pull/28)
- Merge it once CI passes
- Go to https://github.com/poe-platform/poe-protocol/releases/new and make a new release
  (note this link works only if you have commit access to this repository)
- The tag should be of the form "v0.0.X" for now.

Once the protocol is finalized, the version number should track the protocol version
number, and we'll start maintaining a more organized changelog.
