# station-card
Generate a card for a measurment station

## Mark the sites
You can mark the sites in the local map with "mark" sub-command, and the new local map figure will be saved to the path as you specified.
```
$ python station_card.py mark stations/smearii/smearii.json stations/smearii/smearii_local.png stations/smearii/smearii_local_mark.png
```

## Generate the station card
You can generate the station card with "card" sub-command, the country map will be generated if not existed.
```
$ python station_card.py card stations/smearii/smearii.json stations/smearii/smearii_country.png stations/smearii/smearii_local_mark.png
```
