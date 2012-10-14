dir_watcher
===========

File system changes tracking daemon

The main function is to execute program set as option after any modifications to directory or it's contents found.
Tracking following modifications based on pyinotify:
	* a writable file was closed
	* a file/directory was created in watched directory
	* a file/directory was deleted in watched directory
	* a file was modified

Also implements simple logging to file or stdout.

Working on Python >= 2.6 but <= 3.0.
Requirements: pyinotify
