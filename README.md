# IdleCompute Data Management Architecture

![Current Version](https://img.shields.io/badge/version-v0.1-blue)
![GitHub contributors](https://img.shields.io/github/contributors/abroniewski/IdleCompute-Data-Management-Architecture)
![GitHub stars](https://img.shields.io/github/stars/abroniewski/IdleCompute-Data-Management-Architecture?style=social)

## Table of contents
- [Getting Started](#getting-started)
	- [Tools Required](#tools-required)
	- [Installation](#installation)
- [Development](#development)
	- [Part 1: Landing Zone](#part-1-landing-zone)
		- [Data Sources](#data-sources)
		- [Data Collector](#data-collector)
		- [Temporal Landing Zone](#temporal-landing-zone)
		- [Data Persistance Loader](#data-persistance-loader)
		- [Persistant Landing](#persistant-landing)
	- [Part 2: Formatted and Exploitation Zone](#part-2-formatted-and-exploitation-zone)
- [Running the App](#running-the-app)
- [Authors](#authors)
	- [Adam Broniewski](#adam-broniewski)
	- [Vlada Kylynnyk](#vlada-kylynnyk)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Getting Started

This project has a single branch: `main`

The project is small and will follow the structure below:

```
	IdelCompute-Data-Management-Architecture
	├── README.md
	├── .gitignore
	└── src
		├── all executbale script files
	└── docs
		├── support documentation and project descriptions
	└── data
		├── raw
		└── processed
```

### Tools Required

You would require the following tools to develop and run the project:

* Access to UPC Virtual Machine
* HDFS

### Installation

Installation steps for virtual environment and HDFS are locate in [here in /docs](https://github.com/abroniewski/IdleCompute-Data-Management-Architecture/tree/main/docs)

## Development

The goal of this project is to develop a theoretical understanding of data management architecture along with a practical implementation of design choices. The work is completed in 2 stages:
1. Landing zone architecture and external data source identification 
2. Formatted and exploitation zone architecture

### Part 1: Landing Zone
The scope is defined by breaking out all the relevant compoenents that need to be implemented.

#### Data Sources

We will use datasets from kaggle that are ~5 MB with ~30 attributes. Datasets will be labelled data with a classification problem challenge.

- CSV
- JSON
    - Potential 1: [arXiv scholarly articles dataset - 3.34GB](https://www.kaggle.com/datasets/Cornell-University/arxiv)
    - Potential 2: [Automatic Ticket Classification - 83.4MB](https://www.kaggle.com/datasets/arunagirirajan/automatic-ticket-classification/code)
- **Assumption:** Dataset could have multiple other sources, types, and formats.

#### Data Collector

IdleCompute compute will have a specification that must be met for data uploads. We would define exactly what the specifications for upload are.

#### Temporal Landing Zone

Is it as simple as uploading the file “as is” in the hard drive of the storage mechanism being used. 

- **Assumption:** The incoming data is assumed to be uploaded from the user through the IdleCompute website directly to the temporal landing zone.

#### Data Persistance Loader

This is the script we are using to transform from the original formats (CSV, XML, JSON) to the file format of our choice.

1. Transform data format from incoming into chosen format
2. Load data from temporal location to permanent location in chosen file system.
- **Suggested by Sergi**: **Parquet + HDFS.** Need to understand exactly why this was suggested and why other options would **not** be used.

#### Persistant Landing

We will need to determine what the format (e.g. Parquet) and schema are (e.g. what the different attributes are named, what the structure looks like, ...what else?) This would be based on the assumed machine learning algorithm used for data analysis.

  
### Part 2: Formatted and Exploitation Zone

This scope has not yet been developed.

## Running the App

Steps and commands for running the app will be included here

* Example steps:
  ```
    Example command
  ```
  
## Authors

#### Adam Broniewski
* [GitHub](https://github.com/abroniewski)
* [LinkedIn](https://www.linkedin.com/in/abroniewski/)
* [Website](https://adambron.com)

#### Vlada Kylynnyk
* [GitHub](https://github.com/Vladka396)

## License

`IdleCompute Data Management Architecture` is open source software [licensed as MIT][license].

## Acknowledgments

....

[//]: # (HyperLinks)

[license]: https://github.com/abroniewski/IdleCompute-Data-Management-Architecture/LICENSE.md
