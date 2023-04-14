# artiqenv2
Contains necessary bits and bobs to run a full artiq environment (with simulation mode optional) on the SQRL system. 

Reminder that when running the artiq software you should do the following:
1) Make sure the Kasli is plugged in
2) Make sure you're in the same folder as your device_db file
3) run 'nix shell', this builds the environment from the flake.nix file or the flake.lock if the .nix has not been changed.
4) run 'artiq_session' this will take you to the artiq gui and enable the machine at the same time
5) any code within the repository/ subfolder should appear in the file explorer. If it does not, that usually means that the program does not contain a class description or that it has the same class description as another and thus is given an arbitrary label. 
