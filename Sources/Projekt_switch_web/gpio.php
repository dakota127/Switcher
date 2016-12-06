<html>
<head>
<title>
Raspberry Pi Webserver
</title>
</head>

<h1>
<font color="red">
Raspberry Pi Webserver
</font>
</h1>

<body>
<div id="nav"><a href="index.php">Hauptseite</a></div>

<h2>
Raspberry Pi GPIO
</h2>


<form action="gpio.php" method ="post">
   <input type="checkbox" name="gpio2" value="2">GPIO 2<br> 
   <input type="checkbox" name="gpio3" value="3">GPIO 3<br> 
   <input type="checkbox" name="gpio4" value="4">GPIO 4<br> 
   <input type="checkbox" name="gpio7" value="7">GPIO 7<br> 
   <input type="checkbox" name="gpio8" value="8">GPIO 8<br> 
   <input type="checkbox" name="gpio9" value="9">GPIO 9<br> 
   <input type="checkbox" name="gpio10" value="10">GPIO 10<br> 
   <input type="checkbox" name="gpio11" value="11">GPIO 11<br> 
   <input type="checkbox" name="gpio14" value="14">GPIO 14<br> 
   <input type="checkbox" name="gpio15" value="15">GPIO 15<br> 
   <input type="checkbox" name="gpio17" value="17">GPIO 17<br> 
   <input type="checkbox" name="gpio18" value="18">GPIO 18<br> 
   <input type="checkbox" name="gpio22" value="22">GPIO 22<br> 
   <input type="checkbox" name="gpio23" value="23">GPIO 23<br> 
   <input type="checkbox" name="gpio24" value="24">GPIO 24<br>
   <input type="checkbox" name="gpio25" value="25">GPIO 25<br> 
   <input type="checkbox" name="gpio27" value="27">GPIO 27<br>  
   <p>
   <input type="Submit" name="Loeschen" value="Loeschen"><br>
   <input type="Submit" name="IO-abfragen" value="I/O Status"><br>
   <br>
   <input type="Submit" name="IO-setzen" value="I/O setzen">
   <input type="Submit" name="IO-loeschen" value="I/O loeschen"><br>
</form>

<?php
		
#Checkboxen prÃ¼fen
	if (isset($_REQUEST['IO-abfragen']))
	{
		for($x = 0; $x < 28; $x++) 
		{	
			if (isset($_POST["gpio$x"])) 
			{
				
				$val_gpio = trim(@shell_exec("cat /sys/class/gpio/gpio$x/value"));
				$dir_gpio = trim(@shell_exec("cat /sys/class/gpio/gpio$x/direction"));
				echo "<u>GPIO $x: </u><br/>";
				
				if ($val_gpio == 0)
				{
					echo('<img src="LED_off.png" alt="LED_off_GPIO">'); 
				}
				elseif ($val_gpio == 1)
				{
					echo('<img src="LED_on.png" alt="LED_on_GPIO">'); 
				}
				
				echo "<br/>";	
				echo "Value: ", $val_gpio;
				echo "<br/>";	
				echo "Direction: ", $dir_gpio;
				echo "<br/>";
				echo "<br/>";
			}
		}		
	}

	
#GPIO einschalten
	if (isset($_REQUEST['IO-setzen']))
	{
		for($x = 0; $x < 28; $x++) 
		{	
			if (isset($_POST["gpio$x"])) 
			{
                $output = shell_exec('ls -lart');
                echo "<pre>$output</pre>";
				shell_exec("echo \"1\" > /sys/class/gpio/gpio$x/value");
			}
		}
	}
	
#GPIO abschalten
	if (isset($_REQUEST['IO-loeschen']))
	{
		for($x = 0; $x < 28; $x++) 
		{	
			if (isset($_POST["gpio$x"])) 
			{
				shell_exec("echo \"0\" > /sys/class/gpio/gpio$x/value");
			}
		}
	}
	
#GPIO freischalten
	if (isset($_REQUEST['LÃ¶schen']))
	{
				
		for($x = 0; $x < 28; $x++) 
		{
			if(isset($_POST["gpio$x"])) echo "unchecked";
		}
	}
 ?>

</body>
</html>