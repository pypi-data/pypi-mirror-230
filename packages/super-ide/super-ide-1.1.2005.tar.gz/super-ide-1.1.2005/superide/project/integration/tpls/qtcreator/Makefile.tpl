all:
	superide -c qtcreator run

# regenerate project files to reflect platformio.ini changes
project-update:
	@echo "This will overwrite project metadata files.  Are you sure? [y/N] " \
	    && read ans && [ $${ans:-'N'} = 'y' ]
	superide project init --ide qtcreator

# forward any other target (clean, build, etc.) to pio run
{{'%'}}:
	superide -c qtcreator run --target $*
