# core_devoops

<p align="center">
<a href="https://github.com/FR-PAR-ECOACT/core_devoops/blob/main/badges/coverage.svg" target="_blank">
    <img src="https://github.com/FR-PAR-ECOACT/core_devoops/blob/main/badges/coverage.svg" alt="Coverage">
</a>
<a href="https://github.com/FR-PAR-ECOACT/core_devoops/blob/main/badges/pylint.svg" target="_blank">
    <img src="https://github.com/FR-PAR-ECOACT/core_devoops/blob/main/badges/pylint.svg" alt="Publish">
</a>
<a href="https://github.com/FR-PAR-ECOACT/core_devoops/actions/workflows/code-quality.yml/badge.svg" target="_blank">
    <img src="https://github.com/FR-PAR-ECOACT/core_devoops/actions/workflows/code-quality.yml/badge.svg" alt="Package version">
</a>
</p>

Low level ecoact generic code. Aimed at being published in open source with poetry

## Installation of this package

This installation is only possible using Docker.

Starting from a project with a Docker file:
* add the module core_devoops in the `requirements.txt` file
* make sure the `.env` file includes all required fields (see `BaseSettings` and `AuthenticationConfiguration`)
* build the new version of the Docker container (typically `docker build --tag xxx .`)
* run it with docker compose (`dc up -d`).
