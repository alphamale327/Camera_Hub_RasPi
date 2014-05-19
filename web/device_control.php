<?php
$device_command = $_GET["command"]; // Declares the request from index.html as a variable
$textfile = "command.txt"; // Declares the name and location of the .txt file
$fileLocation = "$textfile";
$fh = fopen($fileLocation, 'w   ') or die("Something went wrong!"); // Opens up the .txt file for writing and replaces any previous content
$stringToWrite = "$device_command";
fwrite($fh, $stringToWrite); // Writes it to the .txt file
fclose($fh); 
 
header("Location: index.html"); // Return to frontend (index.html)
?>
\ No newline at end of file
