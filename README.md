# Card building project
Mock hackathon project for the walk-through project before the hackathon
## Setup
- Set up a python environment ex:
    - `python -m venv venv`
    - `.\venv\Scripts\activate` (for windows activates the environment)
    - `.\venv\Scripts\activate` (for mac activates the environment)
- Install project dependencies ex:
    - `pip install -r .\requirements.txt`
    - If that give an error that pip in not in path try `python -m pip install -r .\requirements.txt` to run pip through python
- To run the server:
    - navigate to the .\cards directory (cd cards)
    - `python .\manage.py migrate` (make the database)
    - `python .\manage.py runserver` (run the server on localhost)

## Ideas for addons
- Add an additional game to be able to be played (hard)
- Add the ability to play other user decks (hard)
- Add the ability to look at previous games (medium)
- Add an additional card modifier (easier)
- Add additional card packs and difficultly (easier)
- make it prettier (depends)

