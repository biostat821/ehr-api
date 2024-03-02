# ehr-api

A RESTful HTTP API for managing EHR data.

## Running service locally

```bash
cd src
unicorn api.api:app
```

## Running with Docker

```bash
docker build -t ehr-api .
docker run -p 127.0.0.1:34491:34491 -i -t ehr-api
```

## Using the service

Visit http://127.0.0.1:8000/docs for interactive API explorer.

## Releasing

## Choosing a version number

Use [semantic versioning](https://semver.org/), choosing the appropriate next version number depending on the presence/absense of breaking/non-breaking functionality changes.

## Naming/tagging a release

The release tag should be "v{version_number}".

The release name should be the same as the tag: "v{version_number}".

## Creating a release

This can be done [manually](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository#creating-a-release), or using the [API](https://docs.github.com/en/rest/releases/releases?apiVersion=2022-11-28#create-a-release):

```bash
curl -L \
  -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR-TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/biostat821/ehr-api/releases \
  -d '{"tag_name":"v1.0.0","target_commitish":"master","name":"v1.0.0","draft":false,"prerelease":false,"generate_release_notes":false}'
```
