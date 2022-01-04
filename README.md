# file-updater

A currently python only, client-server application which can verify the current status of a file on the client through sending the hash value of the currently available file on the server. If the file contents do not match the client can request the file from the server to update his current file to the version of the server. 

# possible use cases

Usable to detect changed and older version files of the client. Can also used for verification purposes only where no updated files will be pushed to the server and different hashes always indicate a changed or broken file.

# future updates

- [ ] advanced usage of docker to allow startup arguments and more
- [ ] versions
- [ ] different hash fuctions
- [ ] changeable send size for updating the files (currently the complete file will be instanty sent -> big ram spikes for the server and client programs)
- [ ] verifying of folders/folder structures -> not every filehash has to be checked to find the broken/changed/old file (will also slightly reduce the network traffic)
- [ ] more programming languages to use the program from / rewriting for usage as a libary(maybe .dll/.lib in c/c++, .jar in java, ...)/module
