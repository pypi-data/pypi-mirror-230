# rm -r -f ./dist 
# flit build
# python3 -m twine upload --repository testpypi dist/*
# cp README.md ./src/READMD.md
rm -rf ./dist
python3 setup.py sdist
twine upload dist/*
# rm -rf ./src/READMD.md