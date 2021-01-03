#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#|					 TOP OF FILE:	 console/logPanel.py
#|vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
"""
	FILE NAME:		console/logPanel.py				 [Python module source file]
		
	MODULE NAME:	console.logPanel
	IN PACKAGE:		console
	FULL PATH:		$GIT_ROOT/GLaDOS/src/console/logPanel.py
	MASTER REPO:	https://github.com/mikepfrank/GLaDOS.git
	SYSTEM NAME:	GLaDOS (General Lifeform and Domicile Operating System)
	APP NAME:		GLaDOS.server (Main GLaDOS server application)
	SW COMPONENT:	GLaDOS.console (GLaDOS System Console)


	MODULE DESCRIPTION:
	===================

		This module implements a panel to be displayed on the main system 
		console display for the GLaDOS server application.
		
		This panel displays the last few lines of the system log file,
		color-coded so that different types of log lines will stand out:
		
			Logging
			Level	  Color Scheme
			-------	  ---------------------
			DEBUG	- Bright blue on black.
			INFO	- Magenta on black.
			NORMAL	- Green on black.
			WARNING	- Yellow on black.
			ERROR	- Red on black.
			FATAL	- Bright yellow on red.
"""
#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#| End of module documentation string.
#|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


	#/~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#| 	The following is literally a vertatim example of what the log panel looked 
	#|	like on system startup, in one test:
	#|	
	#|		+--- System Log ------------------------------------------------------------------------------------------------------+---------------------------------------------------------------------------------------------------------------------+
	#|		| ========================+==========================+======================================+==================================================+=========================================================================================== |
	#|		| YYYY-MM-DD hh:mm:ss,msc | SysName.appName.pkgName  | ThreadName: Component      role      |     sourceModuleName.py:ln# : functionName()     | LOGLEVEL: Message text                                                                     |
	#|		| ------------------------+--------------------------+--------------------------------------+--------------------------------------------------+------------------------------------------------------------------------------------------- |
	#|		| 2021-01-02 20:30:16,509 | GLaDOS.server.display    |   Thread-2: GLaDOS.display DisplDrvr |              display.py:1588: paint()            |    DEBUG: display.paint(): Repainting display.                                             |
	#|		| 2021-01-02 20:30:16,509 | GLaDOS.server.display    |   Thread-2: GLaDOS.display DisplDrvr |                panel.py:408 : paint()            |    DEBUG: panelClient.paint(): Repainting panel client                                     |
	#|		| 2021-01-02 20:30:16,509 | GLaDOS.server.display    |   Thread-2: GLaDOS.display DisplDrvr |                panel.py:261 : paint()            |    DEBUG: panel.paint(): Repainting panel 'System Log'.                                    |
	#|		| 2021-01-02 20:30:16,509 | GLaDOS.server.console    |   Thread-2: GLaDOS.display DisplDrvr |              console.py:348 : drawHeader()       |    DEBUG: logPanel.drawHeader(): Drawing header sub-window of log panel...                 |
	#|		| 2021-01-02 20:30:16,509 | GLaDOS.server.console    |   Thread-2: GLaDOS.display DisplDrvr |              console.py:357 : drawHeader()       |    DEBUG: logPanel.drawHeader(): Reading log panel header data from file for first time.   |
	#|		| 2021-01-02 20:30:16,512 | GLaDOS.server.console    |   Thread-2: GLaDOS.display DisplDrvr |              console.py:445 : _init_data()       |    DEBUG: panel._init_data(): Initializing panel content data to empty list.               |
	#|		| 2021-01-02 20:30:16,512 | GLaDOS.server.console    |   Thread-2: GLaDOS.display DisplDrvr |              console.py:292 : launch()           |    DEBUG: logPanel.launch(): Starting the feeder thread.                                   |
	#|		| 2021-01-02 20:30:16,512 | logmaster                |   Thread-3: GLaDOS.console LogFeeder |            logmaster.py:2254: update_context()   |    DEBUG: ThreadActor.update_context(): Updating logging context to role [LogFeeder] & com |
	#|		| 2021-01-02 20:30:16,514 | GLaDOS.server.display    |   Thread-4: GLaDOS.display TUI_Input |              display.py:1722: _runMainloop()     |    DEBUG: display._runMainloop(): Starting main event loop.                                |
	#|		| 2021-01-02 20:30:16,514 | GLaDOS.server.console    |   Thread-3: GLaDOS.console LogFeeder |              console.py:203 : main()             |    DEBUG: logFeeder.main(): Creating 'tail -f' subprocess to feed log panel.               |
	#|		| 2021-01-02 20:30:16,514 | GLaDOS.server.console    |   Thread-3: GLaDOS.console LogFeeder |              console.py:208 : main()             |    DEBUG: logFeeder.main(): Command words are: [tail -n 12 -f log/GLaDOS.server.log]       |
	#|		| 2021-01-02 20:30:16,516 | GLaDOS.server.console    |   Thread-3: GLaDOS.console LogFeeder |              console.py:232 : main()             |    DEBUG: logFeeder.main(): Just added my very first line of log data to the panel.        |
	#|		\-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------/
	#|
	#\~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TO DO: Move log panel related code into here from console.py.

#|^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#|					END OF FILE:	console/logPanel.py
#|%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%