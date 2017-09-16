# API notes
## general
- on error, return always http 500, otherwise 200
    - message:    

## websocket: /newsfeed/
### request
-
### response
- id
- keyword
- image
- headline
- lastUpdated

## GET /stories/$ID
### request
-
### response
- id
- created
- updated
- images ...
- headline
- tldr
- article
- videos ...


## GET/stories/$ID/facts
### request
### response
- fact
    - id
    - title
    - content
    - link
    - pictures

## GET/stories/$ID/related
### request
### response
- id
- headline
- keyword
- time



# Tasks
- [ ] provide facts data
- [ ]