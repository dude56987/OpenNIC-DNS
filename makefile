show:
	echo 'Run "make install" as root to install program!'
test: install
	# test diffrent arguments and usages of opennic dns scan
	sudo opennic-dns-scan --help
	sudo opennic-dns-scan
	sudo opennic-dns-scan -s 2
	sudo opennic-dns-scan --remove
run:
	python opennic-dns-scan.py
install: build
	sudo gdebi --non-interactive opennic-dns_UNSTABLE.deb
uninstall:
	sudo apt-get purge opennic-dns
installed-size:
	du -sx --exclude DEBIAN ./debian/
build:
	sudo make build-deb;
build-deb:
	mkdir -p debian;
	mkdir -p debian/DEBIAN;
	mkdir -p debian/usr;
	mkdir -p debian/usr/bin;
	# copy over the binary
	cp -vf opennic-dns-scan.py ./debian/usr/bin/opennic-dns-scan
	# make the program executable
	chmod +rx ./debian/usr/bin/opennic-dns-scan
	chmod go-wx ./debian/usr/bin/opennic-dns-scan
	# Create the md5sums file
	find ./debian/ -type f -print0 | xargs -0 md5sum > ./debian/DEBIAN/md5sums
	# cut filenames of extra junk
	sed -i.bak 's/\.\/debian\///g' ./debian/DEBIAN/md5sums
	sed -i.bak 's/\\n*DEBIAN*\\n//g' ./debian/DEBIAN/md5sums
	sed -i.bak 's/\\n*DEBIAN*//g' ./debian/DEBIAN/md5sums
	rm -v ./debian/DEBIAN/md5sums.bak
	# figure out the package size
	du -sx --exclude DEBIAN ./debian/ > Installed-Size.txt
	# copy over package data
	cp -rv debdata/. debian/DEBIAN/
	# fix permissions in package
	chmod -Rv 775 debian/DEBIAN/
	chmod -Rv ugo+r debian/
	chmod -Rv go-w debian/
	chmod -Rv u+w debian/
	# build the package
	dpkg-deb --build debian
	cp -v debian.deb opennic-dns_UNSTABLE.deb
	rm -v debian.deb
	rm -rv debian
