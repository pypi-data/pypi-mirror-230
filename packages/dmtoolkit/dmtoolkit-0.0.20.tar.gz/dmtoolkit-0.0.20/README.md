# dmtoolkit

!!!!!!!!!!!!!!!!!!!! NOT YET STABLE !!!!!!!!!!!!!!!!!!!!!!!!

![Tests](https://github.com/Sallenmoore/autonomous/actions/workflows/tests.yml/badge.svg)

- **[pypi](https://pypi.org/project/dmtoolkit/)**
- **[github](https://github.com/Sallenmoore/dmtoolkit)**

## Setup

Add the following to your .env file:

```bash
#### OpenAI Config
OPENAI_KEY=

### Cloudinary Config
CLOUD_NAME=
CLOUDINARY_KEY=
CLOUDINARY_SECRET=

### WikiJS Config

WIKIJS_TOKEN = ""
WIKIJS_URL = ""

# DEV OPTIONS

DEBUG=True
TESTING=True
LOG_LEVEL=INFO
```

## Features

- TBD

## Dependencies

- **Languages**
  - [Python 3.10](/Dev/language/python)
- **Frameworks**
  - [Autonomous](https://github.com/Sallenmoore/autonomous)
  - [gql](https://github.com/graphql-python/gql)
- **Containers**
  - [Docker](https://docs.docker.com/)
  - [Docker Compose](https://github.com/compose-spec/compose-spec/blob/master/spec.md)
- **Networking and APIs**
  - [requests](https://requests.readthedocs.io/en/latest/)
  - [OpenAI](https://beta.openai.com/docs/api-reference/introduction)
  - [Cloudinary](https://cloudinary.com/documentation/image_upload_api_reference)
  - [WikiJS](https://docs.requarks.io/en/api)
- **Databases**
  - [TinyDB](https://tinydb.readthedocs.io/en/latest/)
- **Testing**
  - [pytest](/Dev/tools/pytest)
  - [coverage](https://coverage.readthedocs.io/en/6.4.1/cmd.html)
- **Documentation** - Coming Soon
  - [pdoc](https://pdoc.dev/docs/pdoc/doc.html)
  - [highlight.js](https://highlightjs.org/)

---

## Developer Notes

### TODO

- Auto generate API documentation

### Issue Tracking

- None

## Make Commands

### Tests

```sh
make tests
```

### package

1. Update version in `/src/dmtoolkit/__init__.py`
2. ```sh
   make package
   ```
