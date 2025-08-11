# Smart-Mail-Agent Support Bundle - Sun Aug 10 19:30:49 CST 2025

## System
Linux DESKTOP-MP3QVS6 6.6.87.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun  5 18:30:46 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux

PRETTY_NAME="Ubuntu 22.04.5 LTS"
NAME="Ubuntu"
VERSION_ID="22.04"
VERSION="22.04.5 LTS (Jammy Jellyfish)"
VERSION_CODENAME=jammy
ID=ubuntu

Python: Python 3.10.12

## Git repo
origin	https://github.com/YOU-JIE-hub/smart-mail-agent.git (fetch)
origin	https://github.com/YOU-JIE-hub/smart-mail-agent.git (push)
## main...origin/main
 M pipeline/main.py
?? diagnostics/
?? logs.out
?? scripts/run_forever.sh
?? share_bundle/
?? src/utils/imap_login.py
?? tools/make_share_bundle.sh

Recent commits:
9fa61c8 deps: add reportlab and remove pyfpdf to avoid conflicts
13de5ee ci: add smtp online workflow

## Python environment
/home/youjie/projects/smart-mail-agent/.venv/bin/python
Python 3.10.12
pip 25.2 from /home/youjie/projects/smart-mail-agent/.venv/lib/python3.10/site-packages/pip (python 3.10)
Full pip freeze is saved in diagnostics/pip-freeze.txt

## Project tree (depth 3, ignoring heavy dirs)
.
├── .dockerignore
├── .editorconfig
├── .env
├── .env.example
├── .flake8
├── .github
│   └── workflows
│       ├── ci.yml
│       ├── docker-ghcr.yml
│       ├── nightly.yml
│       ├── release.yml
│       ├── smtp-online.yml
│       └── test.yml
├── .gitignore
├── .mypy_cache
│   ├── .gitignore
│   ├── 3.11
│   │   ├── @plugins_snapshot.json
│   │   ├── PIL
│   │   ├── __future__.data.json
│   │   ├── __future__.meta.json
│   │   ├── _ast.data.json
│   │   ├── _ast.meta.json
│   │   ├── _asyncio.data.json
│   │   ├── _asyncio.meta.json
│   │   ├── _bisect.data.json
│   │   ├── _bisect.meta.json
│   │   ├── _blake2.data.json
│   │   ├── _blake2.meta.json
│   │   ├── _bz2.data.json
│   │   ├── _bz2.meta.json
│   │   ├── _codecs.data.json
│   │   ├── _codecs.meta.json
│   │   ├── _collections_abc.data.json
│   │   ├── _collections_abc.meta.json
│   │   ├── _compat_pickle.data.json
│   │   ├── _compat_pickle.meta.json
│   │   ├── _compression.data.json
│   │   ├── _compression.meta.json
│   │   ├── _contextvars.data.json
│   │   ├── _contextvars.meta.json
│   │   ├── _csv.data.json
│   │   ├── _csv.meta.json
│   │   ├── _ctypes.data.json
│   │   ├── _ctypes.meta.json
│   │   ├── _curses.data.json
│   │   ├── _curses.meta.json
│   │   ├── _decimal.data.json
│   │   ├── _decimal.meta.json
│   │   ├── _frozen_importlib.data.json
│   │   ├── _frozen_importlib.meta.json
│   │   ├── _frozen_importlib_external.data.json
│   │   ├── _frozen_importlib_external.meta.json
│   │   ├── _hashlib.data.json
│   │   ├── _hashlib.meta.json
│   │   ├── _heapq.data.json
│   │   ├── _heapq.meta.json
│   │   ├── _io.data.json
│   │   ├── _io.meta.json
│   │   ├── _locale.data.json
│   │   ├── _locale.meta.json
│   │   ├── _lsprof.data.json
│   │   ├── _lsprof.meta.json
│   │   ├── _markupbase.data.json
│   │   ├── _markupbase.meta.json
│   │   ├── _multibytecodec.data.json
│   │   ├── _multibytecodec.meta.json
│   │   ├── _operator.data.json
│   │   ├── _operator.meta.json
│   │   ├── _pickle.data.json
│   │   ├── _pickle.meta.json
│   │   ├── _queue.data.json
│   │   ├── _queue.meta.json
│   │   ├── _random.data.json
│   │   ├── _random.meta.json
│   │   ├── _sitebuiltins.data.json
│   │   ├── _sitebuiltins.meta.json
│   │   ├── _socket.data.json
│   │   ├── _socket.meta.json
│   │   ├── _sqlite3.data.json
│   │   ├── _sqlite3.meta.json
│   │   ├── _ssl.data.json
│   │   ├── _ssl.meta.json
│   │   ├── _stat.data.json
│   │   ├── _stat.meta.json
│   │   ├── _struct.data.json
│   │   ├── _struct.meta.json
│   │   ├── _thread.data.json
│   │   ├── _thread.meta.json
│   │   ├── _typeshed
│   │   ├── _warnings.data.json
│   │   ├── _warnings.meta.json
│   │   ├── _weakref.data.json
│   │   ├── _weakref.meta.json
│   │   ├── _weakrefset.data.json
│   │   ├── _weakrefset.meta.json
│   │   ├── abc.data.json
│   │   ├── abc.meta.json
│   │   ├── aiohappyeyeballs
│   │   ├── aiohttp
│   │   ├── aiosignal
│   │   ├── annotated_types
│   │   ├── anyio
│   │   ├── argparse.data.json
│   │   ├── argparse.meta.json
│   │   ├── array.data.json
│   │   ├── array.meta.json
│   │   ├── ast.data.json
│   │   ├── ast.meta.json
│   │   ├── asyncio
│   │   ├── atexit.data.json
│   │   ├── atexit.meta.json
│   │   ├── attr
│   │   ├── attrs
│   │   ├── base64.data.json
│   │   ├── base64.meta.json
│   │   ├── bdb.data.json
│   │   ├── bdb.meta.json
│   │   ├── binascii.data.json
│   │   ├── binascii.meta.json
│   │   ├── bisect.data.json
│   │   ├── bisect.meta.json
│   │   ├── bs4
│   │   ├── builtins.data.json
│   │   ├── builtins.meta.json
│   │   ├── bz2.data.json
│   │   ├── bz2.meta.json
│   │   ├── cProfile.data.json
│   │   ├── cProfile.meta.json
│   │   ├── calendar.data.json
│   │   ├── calendar.meta.json
│   │   ├── certifi
│   │   ├── charset_normalizer
│   │   ├── click
│   │   ├── cmath.data.json
│   │   ├── cmath.meta.json
│   │   ├── cmd.data.json
│   │   ├── cmd.meta.json
│   │   ├── codecs.data.json
│   │   ├── codecs.meta.json
│   │   ├── collections
│   │   ├── colorsys.data.json
│   │   ├── colorsys.meta.json
│   │   ├── concurrent
│   │   ├── configparser.data.json
│   │   ├── configparser.meta.json
│   │   ├── contextlib.data.json
│   │   ├── contextlib.meta.json
│   │   ├── contextvars.data.json
│   │   ├── contextvars.meta.json
│   │   ├── copy.data.json
│   │   ├── copy.meta.json
│   │   ├── copyreg.data.json
│   │   ├── copyreg.meta.json
│   │   ├── csv.data.json
│   │   ├── csv.meta.json
│   │   ├── ctypes
│   │   ├── curses
│   │   ├── cycler
│   │   ├── dataclasses.data.json
│   │   ├── dataclasses.meta.json
│   │   ├── datetime.data.json
│   │   ├── datetime.meta.json
│   │   ├── decimal.data.json
│   │   ├── decimal.meta.json
│   │   ├── difflib.data.json
│   │   ├── difflib.meta.json
│   │   ├── dis.data.json
│   │   ├── dis.meta.json
│   │   ├── distro
│   │   ├── dns
│   │   ├── dotenv
│   │   ├── email
│   │   ├── email_validator
│   │   ├── encodings
│   │   ├── enum.data.json
│   │   ├── enum.meta.json
│   │   ├── errno.data.json
│   │   ├── errno.meta.json
│   │   ├── faulthandler.data.json
│   │   ├── faulthandler.meta.json
│   │   ├── fcntl.data.json
│   │   ├── fcntl.meta.json
│   │   ├── filecmp.data.json
│   │   ├── filecmp.meta.json
│   │   ├── filelock
│   │   ├── fnmatch.data.json
│   │   ├── fnmatch.meta.json
│   │   ├── fractions.data.json
│   │   ├── fractions.meta.json
│   │   ├── frozenlist
│   │   ├── functools.data.json
│   │   ├── functools.meta.json
│   │   ├── gc.data.json
│   │   ├── gc.meta.json
│   │   ├── genericpath.data.json
│   │   ├── genericpath.meta.json
│   │   ├── getpass.data.json
│   │   ├── getpass.meta.json
│   │   ├── gettext.data.json
│   │   ├── gettext.meta.json
│   │   ├── glob.data.json
│   │   ├── glob.meta.json
│   │   ├── gzip.data.json
│   │   ├── gzip.meta.json
│   │   ├── h11
│   │   ├── hashlib.data.json
│   │   ├── hashlib.meta.json
│   │   ├── heapq.data.json
│   │   ├── heapq.meta.json
│   │   ├── hmac.data.json
│   │   ├── hmac.meta.json
│   │   ├── html
│   │   ├── http
│   │   ├── httpcore
│   │   ├── httpx
│   │   ├── huggingface_hub
│   │   ├── idna
│   │   ├── imaplib.data.json
│   │   ├── imaplib.meta.json
│   │   ├── importlib
│   │   ├── inspect.data.json
│   │   ├── inspect.meta.json
│   │   ├── io.data.json
│   │   ├── io.meta.json
│   │   ├── ipaddress.data.json
│   │   ├── ipaddress.meta.json
│   │   ├── itertools.data.json
│   │   ├── itertools.meta.json
│   │   ├── jinja2
│   │   ├── jiter
│   │   ├── json
│   │   ├── keyword.data.json
│   │   ├── keyword.meta.json
│   │   ├── linecache.data.json
│   │   ├── linecache.meta.json
│   │   ├── locale.data.json
│   │   ├── locale.meta.json
│   │   ├── logging
│   │   ├── markdown_it
│   │   ├── markupsafe
│   │   ├── marshal.data.json
│   │   ├── marshal.meta.json
│   │   ├── math.data.json
│   │   ├── math.meta.json
│   │   ├── matplotlib
│   │   ├── mdurl
│   │   ├── mimetypes.data.json
│   │   ├── mimetypes.meta.json
│   │   ├── mmap.data.json
│   │   ├── mmap.meta.json
│   │   ├── modules
│   │   ├── multidict
│   │   ├── multiprocessing
│   │   ├── netrc.data.json
│   │   ├── netrc.meta.json
│   │   ├── numbers.data.json
│   │   ├── numbers.meta.json
│   │   ├── numpy
│   │   ├── opcode.data.json
│   │   ├── opcode.meta.json
│   │   ├── openai
│   │   ├── operator.data.json
│   │   ├── operator.meta.json
│   │   ├── os
│   │   ├── packaging
│   │   ├── pathlib
│   │   ├── pdb.data.json
│   │   ├── pdb.meta.json
│   │   ├── pickle.data.json
│   │   ├── pickle.meta.json
│   │   ├── pickletools.data.json
│   │   ├── pickletools.meta.json
│   │   ├── pkgutil.data.json
│   │   ├── pkgutil.meta.json
│   │   ├── platform.data.json
│   │   ├── platform.meta.json
│   │   ├── posixpath.data.json
│   │   ├── posixpath.meta.json
│   │   ├── pprint.data.json
│   │   ├── pprint.meta.json
│   │   ├── profile.data.json
│   │   ├── profile.meta.json
│   │   ├── propcache
│   │   ├── pstats.data.json
│   │   ├── pstats.meta.json
│   │   ├── pty.data.json
│   │   ├── pty.meta.json
│   │   ├── pydantic
│   │   ├── pydantic_core
│   │   ├── pydoc.data.json
│   │   ├── pydoc.meta.json
│   │   ├── pyexpat
│   │   ├── pyparsing
│   │   ├── queue.data.json
│   │   ├── queue.meta.json
│   │   ├── random.data.json
│   │   ├── random.meta.json
│   │   ├── re.data.json
│   │   ├── re.meta.json
│   │   ├── reprlib.data.json
│   │   ├── reprlib.meta.json
│   │   ├── resource.data.json
│   │   ├── resource.meta.json
│   │   ├── rich
│   │   ├── safetensors
│   │   ├── select.data.json
│   │   ├── select.meta.json
│   │   ├── selectors.data.json
│   │   ├── selectors.meta.json
│   │   ├── shlex.data.json
│   │   ├── shlex.meta.json
│   │   ├── shutil.data.json
│   │   ├── shutil.meta.json
│   │   ├── signal.data.json
│   │   ├── signal.meta.json
│   │   ├── smtplib.data.json
│   │   ├── smtplib.meta.json
│   │   ├── sniffio
│   │   ├── socket.data.json
│   │   ├── socket.meta.json
│   │   ├── soupsieve
│   │   ├── spam
│   │   ├── sqlite3
│   │   ├── src
│   │   ├── sre_compile.data.json
│   │   ├── sre_compile.meta.json
│   │   ├── sre_constants.data.json
│   │   ├── sre_constants.meta.json
│   │   ├── sre_parse.data.json
│   │   ├── sre_parse.meta.json
│   │   ├── ssl.data.json
│   │   ├── ssl.meta.json
│   │   ├── stat.data.json
│   │   ├── stat.meta.json
│   │   ├── statistics.data.json
│   │   ├── statistics.meta.json
│   │   ├── string
│   │   ├── struct.data.json
│   │   ├── struct.meta.json
│   │   ├── subprocess.data.json
│   │   ├── subprocess.meta.json
│   │   ├── sys
│   │   ├── sysconfig.data.json
│   │   ├── sysconfig.meta.json
│   │   ├── tarfile.data.json
│   │   ├── tarfile.meta.json
│   │   ├── tempfile.data.json
│   │   ├── tempfile.meta.json
│   │   ├── tenacity
│   │   ├── termios.data.json
│   │   ├── termios.meta.json
│   │   ├── textwrap.data.json
│   │   ├── textwrap.meta.json
│   │   ├── threading.data.json
│   │   ├── threading.meta.json
│   │   ├── tiktoken
│   │   ├── time.data.json
│   │   ├── time.meta.json
│   │   ├── timeit.data.json
│   │   ├── timeit.meta.json
│   │   ├── token.data.json
│   │   ├── token.meta.json
│   │   ├── tokenize.data.json
│   │   ├── tokenize.meta.json
│   │   ├── torch
│   │   ├── tornado
│   │   ├── traceback.data.json
│   │   ├── traceback.meta.json
│   │   ├── transformers
│   │   ├── tty.data.json
│   │   ├── tty.meta.json
│   │   ├── types.data.json
│   │   ├── types.meta.json
│   │   ├── typing.data.json
│   │   ├── typing.meta.json
│   │   ├── typing_extensions.data.json
│   │   ├── typing_extensions.meta.json
│   │   ├── typing_inspection
│   │   ├── unicodedata.data.json
│   │   ├── unicodedata.meta.json
│   │   ├── unittest
│   │   ├── urllib
│   │   ├── uuid.data.json
│   │   ├── uuid.meta.json
│   │   ├── warnings.data.json
│   │   ├── warnings.meta.json
│   │   ├── weakref.data.json
│   │   ├── weakref.meta.json
│   │   ├── wsgiref
│   │   ├── xml
│   │   ├── yarl
│   │   ├── zipfile
│   │   ├── zipimport.data.json
│   │   ├── zipimport.meta.json
│   │   ├── zlib.data.json
│   │   ├── zlib.meta.json
│   │   ├── zoneinfo
│   │   └── zstandard
│   └── CACHEDIR.TAG
├── .pre-commit-config.yaml
├── .pytest_cache
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   ├── README.md
│   └── v
│       └── cache
├── =0.9.0
├── =13.0.0
├── DELETE
├── Dockerfile
├── FROM
├── Makefile
├── Makefile.broken
├── README.md
├── SELECT
├── assets
│   └── fonts
│       ├── .keep
│       ├── NotoSansTC-Regular.cw127.pkl
│       ├── NotoSansTC-Regular.pkl
│       ├── NotoSansTC-Regular.ttf
│       ├── NotoSansTC-Regular.ttf:Zone.Identifier
│       └── SourceHanSansTC-Regular.otf
├── bootstrap_project.py
├── cli
│   ├── run_classifier.py
│   ├── run_generate_spam_testcases.py
│   ├── run_llm_filter.py
│   ├── run_main.py
│   ├── run_orchestrator.py
│   ├── run_rule_filter.py
│   ├── run_spam_classifier.py
│   └── run_spam_filter.py
├── config
├── data
│   ├── .keep
│   ├── archive
│   │   └── quotes
│   ├── db
│   │   ├── emails_log.db
│   │   ├── processed_mails.db
│   │   ├── tickets.db
│   │   └── users.db
│   ├── emails_log.db
│   ├── input
│   ├── knowledge
│   │   └── faq.md
│   ├── leads.db
│   ├── output
│   │   ├── final_result.json
│   │   └── mail_7559_out.json
│   ├── quote_log.db
│   ├── testdata
│   │   ├── classifier
│   │   ├── email001.json
│   │   ├── inbox
│   │   ├── pipeline
│   │   └── spam
│   ├── tickets.db
│   ├── train
│   │   ├── Ham.json
│   │   ├── emails_train.json
│   │   ├── emails_train.json:Zone.Identifier
│   │   ├── emails_train_180.json
│   │   └── emails_train_augmented.json:Zone.Identifier
│   └── users.db
├── diagnostics
│   └── support.md
├── docker-compose.yml
├── init_db.py
├── logs.out
├── model
│   ├── bert_spam_classifier
│   │   ├── checkpoint-108
│   │   ├── checkpoint-135
│   │   ├── config.json
│   │   ├── config.json:Zone.Identifier
│   │   ├── model.safetensors
│   │   ├── model.safetensors:Zone.Identifier
│   │   ├── special_tokens_map.json
│   │   ├── special_tokens_map.json:Zone.Identifier
│   │   ├── tokenizer_config.json
│   │   ├── tokenizer_config.json:Zone.Identifier
│   │   ├── vocab.txt
│   │   └── vocab.txt:Zone.Identifier
│   ├── bert_spam_classifier_20250710-0729
│   │   ├── checkpoint-10
│   │   └── checkpoint-5
│   └── roberta-zh-checkpoint
│       ├── checkpoint-166
│       ├── checkpoint-249
│       ├── checkpoint-332
│       ├── checkpoint-375
│       ├── checkpoint-415
│       ├── checkpoint-83
│       ├── config.json
│       ├── label_map.json
│       ├── model.safetensors
│       ├── special_tokens_map.json
│       ├── tokenizer.json
│       ├── tokenizer_config.json
│       ├── train_log.txt
│       ├── training_args.bin
│       └── vocab.txt
├── modules
│   ├── __init__.py
│   ├── apply_diff.py
│   ├── quotation.py
│   ├── quote_logger.py
│   └── sales_notifier.py
├── output
│   └── predict_result.json
├── outputs
├── pipeline
│   ├── main.py
│   └── main1.py
├── project_structure.txt
├── pyproject.toml
├── pytest.ini
├── report.html
├── reports
├── requirements.txt
├── run_leads_test.py
├── run_pipeline.sh
├── scripts
│   ├── __init__.py
│   ├── check_email_log.py
│   ├── dev_seed_emails_log.py
│   ├── docker_entry.sh
│   ├── gen_all_testdata.py
│   ├── gen_testdata_pipeline.py
│   ├── imap_debug.py
│   ├── init_users_db.py
│   ├── list_gmail_folders.py
│   ├── online_check.py
│   ├── run_all.py
│   ├── run_forever.sh
│   ├── run_pipeline.sh
│   ├── run_pipeline_online.py
│   ├── send_test_emails.py
│   ├── test_imap_login.py
│   ├── test_smtp.py
│   └── wsl_docker_help.txt
├── share_bundle
│   ├── .dockerignore
│   ├── .editorconfig
│   ├── .env
│   ├── .env.example
│   ├── .flake8
│   ├── .github
│   │   └── workflows
│   ├── .gitignore
│   ├── .mypy_cache
│   │   ├── .gitignore
│   │   ├── 3.11
│   │   └── CACHEDIR.TAG
│   ├── .pre-commit-config.yaml
│   ├── .pytest_cache
│   │   ├── .gitignore
│   │   ├── CACHEDIR.TAG
│   │   ├── README.md
│   │   └── v
│   ├── =0.9.0
│   ├── =13.0.0
│   ├── DELETE
│   ├── Dockerfile
│   ├── FROM
│   ├── Makefile
│   ├── Makefile.broken
│   ├── README.md
│   ├── SELECT
│   ├── assets
│   │   └── fonts
│   ├── bootstrap_project.py
│   ├── cli
│   │   ├── run_classifier.py
│   │   ├── run_generate_spam_testcases.py
│   │   ├── run_llm_filter.py
│   │   ├── run_main.py
│   │   ├── run_orchestrator.py
│   │   ├── run_rule_filter.py
│   │   ├── run_spam_classifier.py
│   │   └── run_spam_filter.py
│   ├── config
│   ├── data
│   │   ├── .keep
│   │   ├── archive
│   │   ├── db
│   │   ├── emails_log.db
│   │   ├── input
│   │   ├── knowledge
│   │   ├── leads.db
│   │   ├── output
│   │   ├── quote_log.db
│   │   ├── testdata
│   │   ├── tickets.db
│   │   ├── train
│   │   └── users.db
│   ├── docker-compose.yml
│   ├── init_db.py
│   ├── logs.out
│   ├── model
│   │   ├── bert_spam_classifier
│   │   ├── bert_spam_classifier_20250710-0729
│   │   └── roberta-zh-checkpoint
│   ├── modules
│   ├── output
│   ├── outputs
│   ├── pipeline
│   ├── project_structure.txt
│   ├── pyproject.toml
│   ├── pytest.ini
│   ├── report.html
│   ├── reports
│   ├── requirements.txt
│   ├── run_leads_test.py
│   ├── run_pipeline.sh
│   ├── scripts
│   ├── share_bundle
│   │   ├── .github
│   │   ├── .mypy_cache
│   │   ├── .pytest_cache
│   │   ├── assets
│   │   ├── cli
│   │   ├── config
│   │   ├── data
│   │   ├── model
│   │   ├── modules
│   │   ├── output
│   │   ├── outputs
│   │   ├── pipeline
│   │   ├── reports
│   │   ├── scripts
│   │   ├── share_bundle
│   │   ├── spam
│   │   ├── src
│   │   ├── tests
│   │   └── tools
│   ├── spam
│   ├── src
│   ├── subject,
│   ├── test_imap_connect.py
│   ├── tests
│   └── tools
├── spam
│   ├── __init__.py
│   └── spam_filter_orchestrator.py
├── src
│   ├── .env
│   ├── __init__.py
│   ├── action_handler.py
│   ├── classifier.py
│   ├── email_processor.py
│   ├── inference_classifier.py
│   ├── init_db.py
│   ├── log_writer.py
│   ├── modules
│   │   ├── apply_diff.py
│   │   ├── leads_logger.py
│   │   ├── quotation.py
│   │   ├── quote_logger.py
│   │   └── sales_notifier.py
│   ├── requirements.txt
│   ├── send_with_attachment.py
│   ├── spam
│   │   ├── .keep
│   │   ├── feature_extractor.py
│   │   ├── ml_spam_classifier.py
│   │   ├── rule_filter.py
│   │   ├── spam_filter_orchestrator.py
│   │   └── spam_llm_filter.py
│   ├── stats_collector.py
│   ├── support_ticket.py
│   ├── train_classifier.py
│   ├── trainers
│   │   └── train_bert_spam_classifier.py
│   └── utils
│       ├── .keep
│       ├── db_tools.py
│       ├── imap_folder_detector.py
│       ├── imap_login.py
│       ├── log_writer.py
│       ├── logger.py
│       ├── mailer.py
│       ├── pdf_generator.py
│       ├── priority_evaluator.py
│       └── rag_reply.py
├── subject,
├── test_imap_connect.py
├── tests
│   ├── .keep
│   ├── conftest.py
│   ├── test_apply_diff.py
│   ├── test_classifier.py
│   ├── test_init_db.py
│   ├── test_init_emails_log_db.py
│   ├── test_init_processed_mails_db.py
│   ├── test_init_tickets_db.py
│   ├── test_mailer.py
│   ├── test_mailer_online.py
│   ├── test_quotation.py
│   ├── test_quote_logger.py
│   ├── test_sales_notifier.py
│   ├── test_send_with_attachment.py
│   ├── test_spam_filter.py
│   └── test_stats_collector.py
└── tools
    ├── __init__.py
    ├── apply_classifier_fallback_fix_v1.py
    ├── apply_docker_ci_v1.py
    ├── apply_fix_log_writer_v1.py
    ├── apply_fix_round9.py
    ├── apply_imap_debug_v2.py
    ├── apply_mailer_online_tests_v1.py
    ├── bootstrap_gh_ci.sh
    ├── ci.mk
    ├── db_migrate_emails_log.py
    ├── dedupe_requirements.py
    ├── dev_runner.py
    ├── gh_device_login.sh
    ├── git_setup_and_tag.py
    ├── imap_pass_sanitize.py
    ├── make_share_bundle.sh
    ├── project_catalog.py
    ├── push_secrets_from_env.sh
    ├── repo_tidy.py
    ├── set_imap_pass.py
    └── set_smtp_pass.py

185 directories, 544 files

## Largest 40 files
 984633129 ./.venv/lib/python3.10/site-packages/torch/lib/libtorch_cuda.so
 818346635 ./share_bundle/model/roberta-zh-checkpoint/checkpoint-249/optimizer.pt
 818346635 ./share_bundle/model/roberta-zh-checkpoint/checkpoint-166/optimizer.pt
 818346635 ./model/roberta-zh-checkpoint/checkpoint-83/optimizer.pt
 818346635 ./model/roberta-zh-checkpoint/checkpoint-415/optimizer.pt
 818346635 ./model/roberta-zh-checkpoint/checkpoint-375/optimizer.pt
 818346635 ./model/roberta-zh-checkpoint/checkpoint-332/optimizer.pt
 818346635 ./model/roberta-zh-checkpoint/checkpoint-249/optimizer.pt
 818346635 ./model/roberta-zh-checkpoint/checkpoint-166/optimizer.pt
 818321658 ./share_bundle/model/bert_spam_classifier/checkpoint-135/optimizer.pt
 818321658 ./share_bundle/model/bert_spam_classifier/checkpoint-108/optimizer.pt
 818321658 ./model/bert_spam_classifier/checkpoint-135/optimizer.pt
 818321658 ./model/bert_spam_classifier/checkpoint-108/optimizer.pt
 491106832 ./.venv/lib/python3.10/site-packages/nvidia/cublas/lib/libcublasLt.so.12
 438317848 ./.venv/lib/python3.10/site-packages/nvidia/cudnn/lib/libcudnn_engines_precompiled.so.9
 422171489 ./.venv/lib/python3.10/site-packages/torch/lib/libtorch_cpu.so
 409112544 ./share_bundle/model/roberta-zh-checkpoint/model.safetensors
 409112544 ./share_bundle/model/roberta-zh-checkpoint/checkpoint-249/model.safetensors
 409112544 ./share_bundle/model/roberta-zh-checkpoint/checkpoint-166/model.safetensors
 409112544 ./model/roberta-zh-checkpoint/model.safetensors
 409112544 ./model/roberta-zh-checkpoint/checkpoint-83/model.safetensors
 409112544 ./model/roberta-zh-checkpoint/checkpoint-415/model.safetensors
 409112544 ./model/roberta-zh-checkpoint/checkpoint-375/model.safetensors
 409112544 ./model/roberta-zh-checkpoint/checkpoint-332/model.safetensors
 409112544 ./model/roberta-zh-checkpoint/checkpoint-249/model.safetensors
 409112544 ./model/roberta-zh-checkpoint/checkpoint-166/model.safetensors
 409100240 ./share_bundle/model/bert_spam_classifier_20250710-0729/checkpoint-5/model.safetensors
 409100240 ./share_bundle/model/bert_spam_classifier_20250710-0729/checkpoint-10/model.safetensors
 409100240 ./share_bundle/model/bert_spam_classifier/model.safetensors
 409100240 ./share_bundle/model/bert_spam_classifier/checkpoint-135/model.safetensors
 409100240 ./share_bundle/model/bert_spam_classifier/checkpoint-108/model.safetensors
 409100240 ./model/bert_spam_classifier_20250710-0729/checkpoint-5/model.safetensors
 409100240 ./model/bert_spam_classifier_20250710-0729/checkpoint-10/model.safetensors
 409100240 ./model/bert_spam_classifier/model.safetensors
 409100240 ./model/bert_spam_classifier/checkpoint-135/model.safetensors
 409100240 ./model/bert_spam_classifier/checkpoint-108/model.safetensors
 323094712 ./.venv/lib/python3.10/site-packages/triton/_C/libtriton.so
 293618392 ./.venv/lib/python3.10/site-packages/nvidia/cusparse/lib/libcusparse.so.12
 278925008 ./.venv/lib/python3.10/site-packages/nvidia/cufft/lib/libcufft.so.11
 273386472 ./.venv/lib/python3.10/site-packages/nvidia/nccl/lib/libnccl.so.2

## .env (sanitized)
# SMTP 設定（寄信用）
SMTP_USER=***REDACTED***
SMTP_PASS=***REDACTED***
SMTP_HOST=***REDACTED***
SMTP_PORT=***REDACTED***
SMTP_FROM=***REDACTED***

# OpenAI 金鑰
OPENAI_API_KEY=***REDACTED***

# IMAP 設定（讀信用）
REPLY_TO=***REDACTED***
SALES_EMAIL=***REDACTED***
IMAP_HOST=***REDACTED***
IMAP_USER=***REDACTED***
IMAP_PASS=***REDACTED***

# 其他
QUOTE_FONT_PATH=***REDACTED***
# 預設走線上模式（想離線測試就改 1）
OFFLINE=***REDACTED***

## DB / recent email log (first 100 lines)
[migrate] 完成。現有欄位： ['id', 'subject', 'content', 'summary', 'predicted_label', 'confidence', 'action', 'error', 'created_at']
最新信件處理紀錄 (最近 20 筆)：

id   | subject                                                                              | predicted_label | action | error | created_at                      
-----+--------------------------------------------------------------------------------------+-----------------+--------+-------+---------------------------------
3953 | hi 佑杰 你在7月份投遞履歷後，是否有同意「所有」的企業邀約                                                      | 未分類             | ingest |       | 2025-08-10T11:07:42.963492+00:00
3952 | 你下班後快樂嗎？怎麼做才能「真正投入生活」？                                                               | 未分類             | ingest |       | 2025-08-10T11:07:41.859030+00:00
3951 | 您的檔案出現在最近的搜尋結果中                                                                      | 未分類             | ingest |       | 2025-08-10T11:07:39.606868+00:00
3950 | SMA Online Check - SMTP OK                                                           | 未分類             | ingest |       | 2025-08-10T11:07:38.818254+00:00
3949 | SMA Online Check - SMTP OK                                                           | 未分類             | ingest |       | 2025-08-10T11:07:38.464794+00:00
3948 | SMA Online Check - SMTP OK                                                           | 未分類             | ingest |       | 2025-08-09T21:27:25.084113+00:00
3947 | [YOU-JIE-hub/smart-mail-agent] Run failed: CI - main (9fa61c8)                       | 未分類             | ingest |       | 2025-08-09T21:27:23.505999+00:00
3946 | [YOU-JIE-hub/smart-mail-agent] Run failed: Smart-Mail-Agent CI Test - main (9fa61c8) | 未分類             | ingest |       | 2025-08-09T21:27:23.188854+00:00
3945 | [YOU-JIE-hub/smart-mail-agent] Run failed: SMTP Online Test - main (13de5ee)         | 未分類             | ingest |       | 2025-08-09T21:27:22.135085+00:00
3944 | [YOU-JIE-hub/smart-mail-agent] Run failed: SMTP Online Test - main (13de5ee)         | 未分類             | ingest |       | 2025-08-09T21:27:21.681555+00:00
3943 | [YOU-JIE-hub/smart-mail-agent] Run failed: CI - main (13de5ee)                       | 未分類             | ingest |       | 2025-08-09T21:27:21.458070+00:00
3942 | [YOU-JIE-hub/smart-mail-agent] Run failed: Smart-Mail-Agent CI Test - main (13de5ee) | 未分類             | ingest |       | 2025-08-09T21:27:20.323157+00:00
3941 | [GitHub] A personal access token (classic) has been added to your account            | 未分類             | ingest |       | 2025-08-09T21:27:19.823226+00:00
3940 | SMA Online Check - SMTP OK                                                           | 未分類             | ingest |       | 2025-08-09T21:27:19.078325+00:00
3939 | SMA Online Check - SMTP OK                                                           | 未分類             | ingest |       | 2025-08-09T21:27:16.717352+00:00
3938 | SMA Online Check - SMTP OK                                                           | 未分類             | ingest |       | 2025-08-09T21:27:16.057477+00:00
3937 | SMA Online Check - SMTP OK                                                           | 未分類             | ingest |       | 2025-08-09T21:27:15.507544+00:00
3936 | SMA Online Check - SMTP OK                                                           | 未分類             | ingest |       | 2025-08-09T21:27:14.240222+00:00
3935 | SMA Online Check - SMTP OK                                                           | 未分類             | ingest |       | 2025-08-09T21:27:14.040099+00:00
3934 | 安全性快訊                                                                                | 未分類             | ingest |       | 2025-08-09T21:27:13.799289+00:00

信件處理統計報告
- 總筆數：3953
- 被過濾為 Spam：0
- 發生錯誤：0
