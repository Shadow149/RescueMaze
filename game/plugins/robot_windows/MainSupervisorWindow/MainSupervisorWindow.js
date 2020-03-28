/*
MainSupervisorWindow.js v2

Changelog:
 - Added human loaded indicator
*/


//The total time at the start
var maxTime = 8 * 60;

var visable = false;

var robot0Name = "Robot 0"
var robot1Name = "Robot 1"

var scores = [0,0]

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
			case "activityLoaded0":
				activityLoadedColor(0,parts[1],parts[2],parts[3])
				break;
			case "activityUnloaded0":
				activityUnloadedColour(0)
				break;
			case "activityLoaded1":
				activityLoadedColor(1,parts[1],parts[2],parts[3])
				break;
			case "activityUnloaded1":
				activityUnloadedColour(1)
				break;
			case "historyUpdate":
				let msg = message.split(":");
				let history0 = msg[0].split(",").slice(1,msg[0].length-1)
				let history1 = msg[1].split(",")
				updateHistory(history0,history1)
				break;
		}
	}
}

function humanLoadedColour(id){
	// Changes svg human indicator to gold to indicate a human is loaded
	//document.getElementById("human"+id+"a").style.fill = "gold";
	//document.getElementById("human"+id+"b").style.fill = "gold";
	document.getElementById("human"+id+"a").style.stroke = "#edae39";
	document.getElementById("human"+id+"b").style.stroke = "#edae39";
}
function humanUnloadedColour(id){
	// Changes svg human indicator to black to indicate a human is unloaded
	//document.getElementById("human"+id+"a").style.fill = "black";
	//document.getElementById("human"+id+"b").style.fill = "black";
	document.getElementById("human"+id+"a").style.stroke = "black";
	document.getElementById("human"+id+"b").style.stroke = "black";
}

function activityLoadedColor(id,r,g,b){
	document.getElementById("activity"+id).style.stroke = "rgb("+(Number(r)*255).toString()+","+(Number(g)*255).toString()+", "+(Number(b)*255).toString()+")";
}
function activityUnloadedColour(id){
	document.getElementById("activity"+id).style.stroke = "black";
}
function updateHistory(history0,history1){
	let text = ""

	
	let history0End = false;
	let history1End = false;

	let i = history0.length -1;
	let j = history1.length -1;
	

	while(!history0End || !history1End){
		text += "<tr id='historyrow'>";
		if(history0[i] != null){
			text += "<div class='outerDiv'><div class='innerDiv'><td id='historyrowtext'>"+history0[i]+"</td></div></div>";
			i--;
		}else{
			text += "<div class='outerDiv'><div class='innerDiv'><td id='historyrowtext'></td></div></div>"
			history0End = true;
		}
		if(history1[j] != null){
			text += "<div class='outerDiv'><div class='innerDiv'><td id='historyrowtext'>"+history1[j]+"</td></div></div>";
			j--;
		}else{
			text += "<div class='outerDiv'><div class='innerDiv'><td id='historyrowtext'></td></div></div>"
			history1End = true;
		}
		text += "</tr>";
	}
	document.getElementById("history").innerHTML = text;
}

function loadedController(id, name){
	//A controller has been loaded into a robot id is 0 or 1 and name is the name of the robot
	if (id == 0){
		//Set name and toggle to unload button for robot 0
		document.getElementById("robot0Name").innerHTML = name;
		robot0Name = name;
		document.getElementById("load0").style.display = "none";
		document.getElementById("unload0").style.display = "inline-block";
	}
	if (id == 1){
		//Set name and toggle to unload button for robot 1
		document.getElementById("robot1Name").innerHTML = name;
		robot1Name = name;
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
		robot0Name = "Robot 0";
		document.getElementById("unload0").style.display = "none";
		document.getElementById("load0").style.display = "inline-block";
	}
	if (id == 1){
		//Reset name and toggle to load button for robot 1
		document.getElementById("robot1File").value = "";
		document.getElementById("robot1Name").innerHTML = "None";
		robot1Name = "Robot 1";
		document.getElementById("unload1").style.display = "none";
		document.getElementById("load1").style.display = "inline-block";
	}
}

function startup (){
	//Turn on the run button and reset button when the program has loaded
	setEnableButton("runButton", true);
	setEnableButton("pauseButton", false);
	setEnableButton("resetButton", true);
}

function update (data){
	//Update the ui each frame of the simulation
	//Sets the scores and the timer
	document.getElementById("score0").innerHTML = String(data[0]);
	document.getElementById("score1").innerHTML = String(data[1]);

	scores = [data[0],data[1]]

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
	document.getElementById("robot" + robotNumber + "File").click();
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

	if (!visable){
		show_winning_screen()
	}
}

function unloadPressed(id){
	//Unload button pressed
	//Send the signal for an unload for the correct robot
	window.robotWindow.send("robot"+id+"Unload");
}


function fileOpened(id){
	//When file 0 value is changed
	//Get the files
	var files = document.getElementById("robot"+id+"File").files;
	
	//If there are files
	if (files.length > 0){
		//Get the first file only
		var file = files[0];
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
						window.robotWindow.send("robot"+id+"File," + reader.result);
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

function hide_winning_screen(){
	//Disable winner screen
	document.getElementById("winning-screen").style.display = "none";
}

function calculateWinner(name0,name1){
	//if scores are the same
	if (scores[0] == scores[1]){
		//Show draw text
		document.getElementById("winning-team").innerHTML = "Draw!"
	}else {
		//Find index of highest scoring team
		
		if (scores[0] > scores[1]){
			//Show robot 0 win text
			document.getElementById("winning-team").innerHTML = name0 + " wins!"
		} else {
			//Show robot 1 win text
			document.getElementById("winning-team").innerHTML = name1 + " wins!"
		}
	}

}

function show_winning_screen(){
	calculateWinner(robot0Name,robot1Name);
	//Show winning screen
  	document.getElementById("winning-screen").style.display = "inline-block";
  	visable = true;
}

function relocate(id){
	window.robotWindow.send("relocate,"+id.toString());
}