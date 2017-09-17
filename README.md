# Bubblert

> A simple news aggregation app with fancy UX!

Bubblert is a news aggregation site built on real time data of Thomson Reuters. It aggregates news into categories and makes it easy to find news related information such as additional pictures or facts.

<img src="https://raw.githubusercontent.com/bubblert/bubblert/master/.github/Screen%20Shot%202017-09-17%20at%2002.42.43.png" height="400" />


## Prerequisites

* Docker
* Make

## Setup

```bash
# Get the code, cd into the repo and run one off setup command
git clone git@github.com:bubblert/bubblert.git \
        && cd bubblert \
        && make bootstrap
        && make
```

## Run

```bash
make start
```
