# NOTE: All targets with a `touch` command use this as a sentinel file.
# Because of the way Makefile works, it uses the left hand side of a rule as a file name
# when checking if a target is up-to-date.
# By creating this sentinel file, we can ensure that targets are only rebuilt when needed.
# The sentinel file must have the same name as the rule.

# Move stuff to antlr-source in preparation for compilation
antlr-copy: $(wildcard ../flash_patcher/antlr/*.g4)
	cp ../flash_patcher/antlr/*.g4 ../flash_patcher/antlr_source
	touch antlr-copy

# Create ANTLR parsers from the CLI tool or jar file
antlr: antlr-copy
	${ANTLR_CMD} -Dlanguage=Python3 -visitor ../flash_patcher/antlr_source/PatchfileLexer.g4
	${ANTLR_CMD} -Dlanguage=Python3 -visitor ../flash_patcher/antlr_source/PatchfileParser.g4
	touch antlr

# Delete all temp files used for compilation.
# We use find to delete all __init__.py and __pycache__ files and folders
# We also use find to delete everything in those directories, except for specific items
# We use rm -f to delete without erroring out if the file does not exist
clean:
	find .. -type d                                  -name __pycache__ -exec rm -r {} +
	find ../flash_patcher/antlr_source -mindepth 1 ! -name '.gitkeep' -delete