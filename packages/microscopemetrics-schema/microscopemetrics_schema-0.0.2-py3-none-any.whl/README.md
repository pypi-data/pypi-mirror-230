# microscopemetrics-schema

A schema for microscope-metrics, a python package for microscope QC

## Website

[https://MontpellierRessourcesImagerie.github.io/microscopemetrics-schema](https://MontpellierRessourcesImagerie.github.io/microscopemetrics-schema)

## Repository Structure

* [examples/](examples/) - example data
* [project/](project/) - project files (do not edit these)
* [src/](src/) - source files (edit these)
  * [microscopemetrics_schema](src/microscopemetrics_schema)
    * [schema](src/microscopemetrics_schema/schema) -- LinkML schema
      (edit this)
    * [datamodel](src/microscopemetrics_schema/datamodel) -- generated
      Python datamodel
* [tests/](tests/) - Python tests

## Developer Documentation

<details>
Use the `make` command to generate project artefacts:

* `make all`: make everything
* `make deploy`: deploys site
</details>

## Credits

This project was made with
[linkml-project-cookiecutter](https://github.com/linkml/linkml-project-cookiecutter).
