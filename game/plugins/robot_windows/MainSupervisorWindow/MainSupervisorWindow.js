/*
MainSupervisorWindow.js v2

Changelog:
 - Added human loaded indicator
*/


//The total time at the start
var maxTime = 120;

function receive (message){
	//Receive message from the python supervisor
	//Split on comma
	var parts = message.split(",");
	
	//If there is a message
	if (parts.length > 0){
		switch (parts[0]){
			case "startup":
				//Call for set up the robot window
				startup();
				break;
			case "update":
				//Update the information on the robot window every frame (of game time)
				update(parts.slice(1,parts.length + 1));
				break;
			case "loaded0":
				//Robot 0's controller has been loaded
				loadedController(0, parts[1]);
				break;
			case "loaded1":
				//Robot 1's controller has been loaded
				loadedController(1, parts[1]);
				break;
			case "unloaded0":
				//Robot 0's controller has been unloaded
				unloadedController(0);
				break;
			case "unloaded1":
				//Robot 1's controller has been unloaded
				unloadedController(1);
				break;
			case "ended":
				//The game is over
				endGame();
				break;
			case "humanLoaded0":
				//Robot 0's human is loaded
				humanLoadedColour(0);
				break;
			case "humanUnloaded0":
				//Robot 0's human is unloaded
				humanUnloadedColour(0);
				break;
			case "humanLoaded1":
				//Robot 1's human is loaded
				humanLoadedColour(1);
				break;
			case "humanUnloaded1":
				//Robot 1's human is unloaded
				humanUnloadedColour(1);
				break;
		}
	}
}

function humanLoadedColour(id){
	// Changes svg human indicator to gold to indicate a human is loaded
	document.getElementById("human"+id+"a").style.fill = "gold";
	document.getElementById("human"+id+"b").style.fill = "gold";
	document.getElementById("human"+id+"a").style.stroke = "gold";
	document.getElementById("human"+id+"b").style.stroke = "gold";
}
function humanUnloadedColour(id){
	// Changes svg human indicator to black to indicate a human is unloaded
	document.getElementById("human"+id+"a").style.fill = "black";
	document.getElementById("human"+id+"b").style.fill = "black";
	document.getElementById("human"+id+"a").style.stroke = "black";
	document.getElementById("human"+id+"b").style.stroke = "black";
}

function loadedController(id, name){
	//A controller has been loaded into a robot id is 0 or 1 and name is the name of the robot
	if (id == 0){
		//Set name and toggle to unload button for robot 0
		document.getElementById("robot0Name").innerHTML = name;
		document.getElementById("load0").style.display = "none";
		document.getElementById("unload0").style.display = "inline-block";
	}
	if (id == 1){
		//Set name and toggle to unload button for robot 1
		document.getElementById("robot1Name").innerHTML = name;
		document.getElementById("load1").style.display = "none";
		document.getElementById("unload1").style.display = "inline-block";
	}
}

function unloadedController(id){
	//A controller has been unloaded for robot of the given id
	if (id == 0){
		//Reset name and toggle to load button for robot 0
		document.getElementById("robot0File").value = "";
		document.getElementById("robot0Name").innerHTML = "None";
		document.getElementById("unload0").style.display = "none";
		document.getElementById("load0").style.display = "inline-block";
	}
	if (id == 1){
		//Reset name and toggle to load button for robot 1
		document.getElementById("robot1File").value = "";
		document.getElementById("robot1Name").innerHTML = "None";
		document.getElementById("unload1").style.display = "none";
		document.getElementById("load1").style.display = "inline-block";
	}
}

function startup (){
	//Turn on the run button and reset button when the program has loaded
	setEnableButton("runButton", true);
	setEnableButton("resetButton", true);
}

function update (data){
	//Update the ui each frame of the simulation
	//Sets the scores and the timer
	document.getElementById("score0").innerHTML = String(data[0]);
	document.getElementById("score1").innerHTML = String(data[1]);
	document.getElementById("timer").innerHTML = calculateTimeRemaining(data[2]);
}

function calculateTimeRemaining(done){
	//Create the string for the time remaining (mm:ss) given the amount of time elapsed
	//Convert to an integer
	done = Math.floor(done);
	//Calculate number of seconds remaining
	var remaining = maxTime - done;
	//Calculate seconds part of the time
	var seconds = Math.floor(remaining % 60);
	//Calculate the minutes part of the time
	var mins = Math.floor((remaining - seconds) / 60);
	//Convert parts to strings
	mins = String(mins)
	seconds = String(seconds)
	
	//Add leading 0s if necessary
	for (var i = 0; i < 2 - seconds.length; i++){
		seconds = "0" + seconds;
	}
	
	for (var i = 0; i < 2 - mins.length ; i++){
		mins = "0" + mins;
	}
	
	//Return the time string
	return mins + ":" + seconds;
}

function runPressed(){
	//When the run button is pressed
	//Disable the run button
	setEnableButton("runButton", false);
	//Send a run command
	window.robotWindow.send("run");
	//Enable the pause button
	setEnableButton("pauseButton", true);
	//Disable all the loading buttons (cannot change loaded controllers once simulation starts)
	setEnableButton("load0", false);
	setEnableButton("load1", false);
	setEnableButton("unload0", false);
	setEnableButton("unload1", false);
}

function pausePressed(){
	//When the pause button is pressed
	//Turn off pause button, on run button and send signal to pause
	setEnableButton("pauseButton", false);
	window.robotWindow.send("pause");
	setEnableButton("runButton", true);
}

function resetPressed(){
	//When the reset button is pressed
	//Disable all buttons
	setEnableButton("runButton", false)
	setEnableButton("pauseButton", false);
	setEnableButton("resetButton", false);
	//Send signal to reset everything
	window.robotWindow.send("reset");
}

function openLoadController(robotNumber){
	//When a load button is pressed - opens the file explorer window
	document.getElementById("robot" + String(robotNumber) + "File").click();
}

function setEnableButton(name, state){
	//Set the disabled state of a button (state is if it is enabled as a boolean)
	document.getElementById(name).disabled = !(state);
}

//Set the onload command for the window
window.onload = function(){
	//Connect the window
	window.robotWindow = webots.window();
	//Set the title
	window.robotWindow.setTitle('Simulation Controls');
	//Set which function handles the recieved messages
	window.robotWindow.receive = receive;
	//Set timer to inital time value
	document.getElementById("timer").innerHTML = calculateTimeRemaining(0);
};

function endGame(){
	//Once the game is over turn off both the run and pause buttons
	setEnableButton("runButton", false)
	setEnableButton("pauseButton", false);
}

function unloadPressed(id){
	//Unload button pressed
	//Send the signal for an unload for the correct robot
	if (id == 0){
		window.robotWindow.send("robot0Unload");
	}
	if (id == 1){
		window.robotWindow.send("robot1Unload");
	}
}

function file0Opened(){
	//When file 0 value is changed
	//Get the files
	var files = document.getElementById("robot0File").files;
	
	//If there are files
	if (files.length > 0){
		//Get the first file only
		var file = files.item(0);
		//Split at the .
		var nameParts = file.name.split(".");
		
		//If there are parts to the name
		if (nameParts.length > 1){
			//If the last part is "py" - a python file
			if(nameParts[nameParts.length - 1] == "py"){
				//Create a file reader
				var reader = new FileReader();
				
				//Set the function of the reader when it finishes loading
				reader.onload = (function(reader){
					return function(){
						//Send the signal to the supervisor with the data from the file
						window.robotWindow.send("robot0File," + reader.result);
					}
				})(reader);
				
				//Read the file as udf-8 text
				reader.readAsText(file);
			}else{
				//Tell the user to select a python file
				alert("Please select a python file.");
			}
		}else{
			//Tell the user to select a python file
			alert("Please select a python file.");
		}
		
	}
}

function file1Opened(){
	//The same as function above but for robot 1 (change to be one function with parameter for robot number)
	var files = document.getElementById("robot1File").files;
	
	if (files.length > 0){
		var file = files.item(0);
		
		var nameParts = file.name.split(".");
		
		if (nameParts.length > 1){
			if(nameParts[nameParts.length - 1] == "py"){
				var reader = new FileReader();
		
				reader.onload = (function(reader){
					return function(){
						window.robotWindow.send("robot1File," + reader.result);
					}
				})(reader);
				
				reader.readAsText(file);
			}else{
				alert("Please select a python file.");
			}
		}else{
			alert("Please select a python file.");
		}
		
	}
}