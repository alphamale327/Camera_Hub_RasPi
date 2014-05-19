<?php
$emailWrite =$_GET["param"]; 
$textfile = "emailAddress.txt";
$fileLocation = "$textfile";
$fh = fopen($fileLocation, 'w   ') or die("Something went wrong!"); // Opens up the .txt file for writing and replaces any previous content
$stringToWrite = "$emailWrite";
fwrite($fh, $stringToWrite); // Writes it to the .txt file
fclose($fh); 
 
header("Location: index.html"); // Return to frontend (index.html)
?>