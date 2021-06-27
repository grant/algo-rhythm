# Algo Rhythm

Algorithmic Music Composition with Artificial Neural Nets

![Algo Rhythm Logo](https://cloud.githubusercontent.com/assets/744973/13688861/730e965e-e6d9-11e5-9dc4-40cf089e96e2.png)

See the [project overview](https://docs.google.com/document/d/1C1j9c8HHGg_dk06ioMi8d7d4vOIaILWbKF0PoOqM7ks/edit?usp=sharing) for details about the project.

## Screenshots

![Top Half](https://cloud.githubusercontent.com/assets/744973/13688838/50826a5c-e6d9-11e5-972a-a047bb85434c.png)
![Bottom Half](https://cloud.githubusercontent.com/assets/744973/13688692/4653a704-e6d8-11e5-883f-47cdca2380f1.png)

## Blogpost

A detailed blogpost about this project is here: https://medium.com/@granttimmerman/algo-rhythm-music-composition-using-neural-networks-f89897ff2df7

### How to install

Setup a virtual environment. This keeps dependencies required by projects in separate places.

```sh
pip install virtualenv
virtualenv env
source env/bin/activate
```

Install dependencies

```sh
pip install -r requirements.txt
```

Exit the environment when done.

```sh
deactivate
```

### How to run

```sh
python neural_net.py
```

### Play the MIDI files

OSX

```
brew install timidity
timidity sample.mid
```

PC - Use Windows Media Player

### Jetson

How to ssh into the jetson:

```sh
ssh rnnmusic@eeb003e-jetsontx1.cs.washington.edu
```

Password is on machine.
