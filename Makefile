install:
	python3 setup.py install 

build: clean
	python3 -m build
	twine check dist/*

clean:
	rm -rf build dist phomemo_printer.egginfo

bump-version:
	current_version=$(cat phomemo_printer/version.py | cut -f ' ' -d 2 | tr -d \")
	major=$(echo "${current_version}" | cut  -d '.' -f 1)
	minor=$(echo "${current_version}" | cut  -d '.' -f 2)
	patch=$(echo "${current_version}" | cut  -d '.' -f 3)
	new_patch=$((${patcH} + 1))
	new_version="${major}.${minor}.${new_patch}"
	sed -i "s/${current_version}/${new_version}/"

release:  build
	python3 -m twine upload dist/*
