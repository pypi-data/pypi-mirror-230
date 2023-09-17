# YeXiaoRain-Atcoder-Core

[![linting: yapf](https://img.shields.io/badge/linting-yapf-green)](https://github.com/google/yapf)
[![pages-build-deployment](https://github.com/CroMarmot/yxr-atcoder-core/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/CroMarmot/yxr-atcoder-core/actions/workflows/pages/pages-build-deployment)
[![Unit test](https://github.com/CroMarmot/yxr-atcoder-core/actions/workflows/unit-test.yml/badge.svg)](https://github.com/CroMarmot/yxr-atcoder-core/actions/workflows/unit-test.yml)

![python3.8+](https://shields.io/badge/python-3.8+-green?logo=python)
![requests](https://shields.io/badge/requests-2-green)
![BeautifulSoup4](https://shields.io/badge/BeautifulSoup-4-green)
![lxml](https://shields.io/badge/lxml-4-green)
![yapf](https://shields.io/badge/yapf-0.32-green)
![sphinx](https://shields.io/badge/Sphinx-5-green)

## About

Some Atcoder core api with `python >= 3.8`.

Based on this library, you can easily build command-line programs and intermediate services.

## Docs

[User Document](https://cromarmot.github.io/yxr-atcoder-core/usage/index.html)

[Developer Document](https://cromarmot.github.io/yxr-atcoder-core/dev/index.html)

## Currrent Feature List

- ac_core.auth module
  - fetch_login()
  - is_logged_in()
- ac_core.contest module
  - fetch_standing()
  - fetch_tasks()
  - fetch_tasks_meta()
  - parse_standing()
  - parse_tasks()
- ac_core.language module
  - fetch_language()
- ac_core.problem module
  - parse_task()
- ac_core.result module
  - fetch_result()
  - fetch_result_by_url()
  - parse_result()
- ac_core.submit module
  - fetch_submit()
- ac_core.url module
  - url_2_contest_id()
