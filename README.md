# Photo Organizer

Script para organização de fotos pela data que foram tiradas.

DE:
```
Photos

├── P1010171.JPG      
├── P1010172.JPG      
├── P1010173.JPG      
├── P1010174.JPG      
├── P1010175.JPG      
├── P1010176.JPG     
``` 

PARA:
```
Photos
├── 2019
│   └── 01
│   │   ├── P1010171.JPG
│   │   ├── P1010172.JPG
│   │   ├── P1010173.JPG
│   └── 02
│   │   ├── P1010174.JPG
│   │   ├── P1010175.JPG
│   └── 03
│   │   ├── P1010176.JPG
```

## Docker

O processo de organização pode ser executado facilmente com docker:

``` bash
#!/bin/bash
docker run \
  --rm \
  --name photo-organize-eduardo \
  -v /mnt/u01/photos:/photos \
  -e TZ=America/Sao_Paulo \
  -e SOURCE_FOLDER=/photos/stage/eduardo \
  -e DESTINATION_FOLDER=/photos/eduardo \
  -e OPERATION=MOVE \
  duduardo23/photo-organizer:1.0.3
```

## Desenvolvimento
### Create virtual env
```
  sudo pip install virtualenv
  virtualenv env1
  env1\Scripts\activate
  pip3 install -r requirements.txt
```
### Active  virtual env
```
  source env/bin/activate
```

### Update dependencies file:
```
  pip3 freeze > requirements.txt
 ```
