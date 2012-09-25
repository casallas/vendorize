"""Copyright (c) 2012 Juan Sebastian Casallas

A quick and dirty module for "vendorizing" osg binaries, libs and plugins under Mac OS X

In English:
Suppose you want to copy osg bins and libs and bundle them with your app, this may be
troublesome due to libraries linked to your own system. Vendorize makes sure all links
become relative for bins, libs and plugins.

Usage:
Just place this file in the root of your copied osg directory (the one you want to bundle)
execute `python vendorize.py` and voilà!

Dependencies:
python-magic (https://github.com/ahupp/python-magic)
Note: You may get away without this extension, say by looking at file extensions or doing
the magic yourself (read the header of each file and determine its type)
"""
from magic import from_file
from subprocess import check_output
from os import listdir

otool_L = ['otool','-L']
otool_D = ['otool','-D']
install_change = ['install_name_tool','-change']
install_id = ['install_name_tool','-id']

def split_path(path):
	'Returns a tuple containing the file path and the file name'
	sp_path = path.rpartition('/')
	return (sp_path[0],sp_path[2])

def file_type(fpath):
	magic_type = from_file(fpath)
	if magic_type.find('executable') > -1:
		return 'exe'
	elif magic_type.find('dynamically linked shared library') > -1:
		return 'dylib'
	elif magic_type.find('bundle') > -1:# so's are considered as bundles
		return 'bundle'
	elif magic_type.find('directory') > -1:# so's are considered as bundles
		return 'dir'
	else:
		return magic_type

def shared_libs(otool_out):
	ans = otool_out.partition('\n\t')[2] # The first line is just the name of the file, skip it
	ans = ans.split('\n\t') # There should be one lib per line
	return [a.partition(' (')[0] for a in ans] # We don't care for whatever is after the parenthesis

def find_vendored_lib(libname,lib_path='lib'):
	"""Searches in "lib/" to see if the specified lib is vendored
		Returns the vendored lib or None if it's not found
	"""
	libname = split_path(libname)[1]
	for lib in listdir(lib_path):
		if lib == libname:
			return lib
	return None

def cmd(args):
	'Prints the command specified in args, executes it, and returns its output'
	print ' '.join(args)
	try:
		return check_output(args)
	except:
		ans = 'ERROR: Failed'
		return None

def used_libs(file):
	"""Returns the names of the shared libraries that the file  uses, as
    well as the shared library ID if the file is a shared library.
    This command calls "otool -L file" underneath.
    The only difference with otool -L, is that version numbers are not displayed"""
	libs = cmd(otool_L+[file])
	return shared_libs(libs)

def lib_id(file):
	"""Display just install name of a shared library.
    This command calls "otool -D file" underneath."""
	libs = cmd(otool_D+[file])
	return shared_libs(libs)[0]

def change_lib(file,old_lib,new_lib):
	"""Changes the dependent shared library install name old to new in the specified file.
	If the file does not contain the old install name, the command is ignored.
	This command calls "install_name_tool -change old_lib new_lib file" underneath
	"""
	print file+':Changing '+old_lib+' to '+new_lib
	if cmd(install_change+[old_lib,new_lib,file]):
		return True
	else:
		return False

def change_id(file,new_id):
	"""Changes the shared library identification name of a dynamic shared library to new_id.
	If  the file is not a dynamic shared library and the command is ignored.
	This command calls "install_name_tool -id new_id file" underneath
    """
	print file+':Changing ID to '+new_id
	if cmd(install_id+[new_id,file]):
		return True
	else:
		return False

def vendorize_bin(file,lib_prefix = '../lib/'):
	"Executes change_lib for each of the file's used_libs"
	for lib in used_libs(file):
		vendored = find_vendored_lib(lib)
		if vendored:
			change_lib(file,lib,'@executable_path/'+lib_prefix+vendored)
		else:
			print "INFO: Shared library "+lib+\
				" for file "+file+" couldn't be vendored"

def vendorize_lib(file,lib_prefix = ''):
	"Executes change_lib for each of the file's used_libs and change_id for the file ID"
	libs = used_libs(file)
	id = lib_id(file)
	for lib in libs:
		vendored = find_vendored_lib(lib)
		if vendored:
			if lib == id:
				change_id(file,vendored)
			else:
				change_lib(file,lib,'@loader_path/'+lib_prefix+vendored)
		else:
			print "INFO: Shared library"+lib+\
				" for file "+file+" couldn't be vendored"

dirs=listdir('./')
for dir in dirs:
	if dir == 'bin':
		files = listdir(dir)
		for file in files:
			fpath = dir+'/'+file
			if file_type(fpath) == 'exe':
				vendorize_bin(fpath)
	elif dir == 'lib':
		files = listdir(dir)
		for file in files:
			fpath = dir+'/'+file
			ftype = file_type(fpath)
			if ftype == 'dylib':
				vendorize_lib(fpath)
			elif ftype == 'dir' and file.find('osgPlugins') > -1:
				for lib in listdir(fpath):
					fpath2 = fpath+'/'+lib
					ftype2 = file_type(fpath2)
					if ftype2 == 'bundle':
						vendorize_lib(fpath2,'../')
