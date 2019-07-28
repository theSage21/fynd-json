# Fynd-Json-Classes

## From cli/Test a basic set of features
```bash
pipenv run python soln.py fz.json
```

## In python code

```python
from soln import read_class

fz = read_class('fz')
my_bike = fz(cc=150)
```


## Basic Class Set

- [x] object attributes
- [x] class attributes
- [x] annotations (object and class attributes)
- [x] class docstrings
- [x] methods
    - [x] annotations
    - [x] docstrings
    - [x] super(class,self) style calls
- [x] inheritence
- [x] slots

## Full fledged class set

- [ ] metaclass specifications
- [ ] class decorators
- [ ] method decorators
    - [ ] properties
    - [ ] other decorators
- [ ] super() style calls

## Extended instructions to run

```
sudo apt-get update
sudo apt-get install python-pip git python-dev
curl https://pyenv.run | bash
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
# Restart the shell
pyenv update
pip install pipenv --user
git clone https://github.com/theSage21/fynd-json
cd fynd-json
pipenv install --dev --deploy



pipenv run python soln.py fz.json
```
