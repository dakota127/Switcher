<html>
<head>
<title>
Raspberry Pi Webserver - Dosen Schalten
</title>
<style type="text/css">
.myform {
	font-family: "Lucida Sans Unicode", "Lucida Grande", sans-serif;
	font-size: 14px;
	background-color: #E2D1B6;
	border-top-style: solid;
	border-top-width: thin;
	border-right-style: solid;
	border-right-width: thin;
	border-bottom-style: solid;
	border-bottom-width: thin;
	border-left-style: solid;
	border-left-width: thin;
	padding-right: 10%;
	padding-left: 10%;
	margin-left: 20%;
	margin-right: 20%;
	border-color: #C33;
}
.mynav {
	font-family: Verdana, Geneva, sans-serif;
	font-size: 14px;
	padding: 20px;
}
</style>
</head>



<body>
<h2>
<font color="red">
Raspberry Pi Webserver - Dosen Schalten
</font>
</h2>

<div class="mynav"><a href="index.html">Home</a></div>
<div class="myform">
  <h3>
    Steuerung Schaltdosen
  </h3>
  <p>
  <form action="sw1.php" method ="post">
    <input type="radio" name="dose1" value="A">Dose A<br> 
  <input type="radio" name="dose2" value="B">Dose B<br> 
  <input type="radio" name="dose3" value="C">Dose C<br> 
  <input type="radio" name="dose4" value="D">Dose D<br> 
  </p>
  <p>
    <input type="Submit" name="EIN" value="EIN">
    
    <input type="Submit" name="AUS" value="AUS"><br>
    
    <br>
    <input type="Submit" name="IO-abfragen" value="I/O Status"><br>
   </form>
 
    
  <?php
		
#Checkboxen prüfen
	if (isset($_REQUEST['IO-abfragen']))
	{
		
				
				$val_gpio = trim(@shell_exec("cat swstatus.txt"));
				echo "Status :";
				echo $val_gpio;
	
	}

	
#GPIO einschalten
	if (isset($_REQUEST['EIN']))
	{	    
		    if (isset($_POST["dose1"])) 
			    echo shell_exec("sudo ./switch1.py -D A -A ON");
			if (isset($_POST["dose2"])) 
			    echo shell_exec("sudo ./switch1.py -D B -A ON");
		    if (isset($_POST["dose3"])) 
			    echo shell_exec("sudo ./switch1.py -D C -A ON");
		    if (isset($_POST["dose4"])) 
			    echo shell_exec("sudo ./switch1.py -D D -A ON");
	}
	
#GPIO abschalten
	if (isset($_REQUEST['AUS']))
	{
		    if (isset($_POST["dose1"])) 
			    echo shell_exec("sudo ./switch1.py -D A -A OFF");
			if (isset($_POST["dose2"])) 
			    echo shell_exec("sudo ./switch1.py -D B -A OFF");
		    if (isset($_POST["dose3"])) 
			    echo shell_exec("sudo ./switch1.py -D C -A OFF");
		    if (isset($_POST["dose4"])) 
			    echo shell_exec("sudo ./switch1.py -D D -A OFF");	}
	

 ?>
    
</div>
</body>
</html>