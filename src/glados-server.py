#!/usr/bin/python3
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|
#|	FILE NAME:	glados-server.py							[Python 3 script]
#|
#|	DESCRIPTION:
#|
#|		This script constitutes the main server process executable for the
#|		GLaDOS system.  Within the OS process running this script, threads 
#|		are created to carry out the following functions:
#|
#|			1. Primary "mind" thread for the A.I. itself.
#|
#|			2. Various GLaDOS processes, which may include 'bridge' 
#|				processes for communicating to external systems (e.g.,
#|				Internet-based services), or to local resources (e.g., 
#|				Unix command prompt), or to internal subsystems of
#|				the GLaDOS system itself, such as the memory system,
#|				the settings interface, & the book authoring system.
#|
#|			3. A thread for managing the text-based 'windowing' system
#|				inside of GLaDOS, which is the primary 'GUI' seen by 
#|				the A.I.  (The windowing system itself is not a GLaDOS
#|				process; it is used by the A.I. to interact with GLaDOS
#|				processes.)
#|
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

