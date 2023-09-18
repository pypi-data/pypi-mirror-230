# CHANGELOG.md

## 0.2.6 (2023-09-16)

#### Housekeeping:

- Add `python3.11`: Refreshing the set of currently used interpreters in own CI
- Get rid of `poetry`: After several years - I decide to stop trying to make poetry 
  working. IMO the tool is unreliable. Consumes more of my development time than I get out of it.
- Use gitlab CI for pushing airium packages. That required modifying bumpversion routine.

#### Issues:

- Resolve issue [#5](https://gitlab.com/kamichal/airium/-/issues/5): dependencies cannot be parsed
  by standard package metadata tooling. Thanks to Ben Bariteau @breetz for reporting the 
  problem.

## 0.2.5 (2022-10-12)

#### Feature request [#4](https://gitlab.com/kamichal/airium/-/issues/4):

- Added `source_minify` argument for disabling white-spaces addition to the generated HTML code
- Added `source_line_break_character` for changing line break's style

## 0.2.4 (2022-09-25)

#### Live translator

- Added example with FastAPI and AJAX approach

## 0.2.3 (2021-11-02)

#### Housekeeping:

- Fixed `del` tag support, since it's a python keyword.
- Added `bytes` cast on Airium class.
- Added `python3.10` support.
- Turning development status from Alpha to Beta.
- Added `Django` "template-less" view example in README.md.
- Bump dependencies' version, especially `beautifulsoup4` version, since its parsing
  result changes, and we rely on it in tests.

## 0.2.2 (2021-01-30)

#### Housekeeping:

- Enable usage of setuptools' "extras" feature for specifying additional dependencies.
  Since now, requirements for parsing (transpiling) can be installed with
  `pip install airium[parse]` command call.

## 0.2.1 (2020-12-07)

#### Issues:

- Issue [#2](https://gitlab.com/kamichal/airium/-/issues/2)

  Extra spaces generated when closing `<pre>` elements
    - Reported by: **Pavol Federl** [@federl](https://gitlab.com/federl)

#### Fix:

- Resolving issue #2
- Fix reverse translation for `<pre>` elements

#### Housekeeping:

- Add `pyproject.toml` configuration file for `poetry`
- Add CI pipeline for poetry environment test

## 0.2.0 (2020-10-29)

#### Contributions:

- **Antti Kaihola** [@akaihola](https://gitlab.com/akaihola)
    - [Tag chaining feature](https://gitlab.com/kamichal/airium/-/merge_requests/4)
    - [Supplement type annotations](https://gitlab.com/kamichal/airium/-/merge_requests/2)
    - [`ClassVar` fix](https://gitlab.com/kamichal/airium/-/merge_requests/1)

#### Features:

- Allow chaining of tags when they have only one child.
- Add enough typing hints so Mypy is happy with the code base.

#### Fix:

- Fix incorrect use of `ClassVar` in `forward.py`

## 0.1.6 (2020-09-20)

#### Features:

- add info for missing dependencies for translation

## before

> git is supposed to know what was released before the CHANGELOG.md is started
