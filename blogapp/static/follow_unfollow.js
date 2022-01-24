// AJAX POST request upon button click to follow or unfollow selected user.
function followUnfollow(username, action) {
    // Check if browser supports Fetch API, log and display error if it doesn't.
    if (!("fetch" in window)) {
        var message = "Fetch API not found, please upgrade your browser";
        console.log(message);
        document.querySelector("#onclick-status").innerHTML = message;
        document.querySelector("#onclick-status").style.backgroundColor = "red";
        return;
    }

    // To pass in headers object.
    let fetchRequest = {
        cache: "no-cache",
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({"username": username, "action": action})
    }

    // Send and receive data indicating if current user was able to follow user.
    fetch("/follow_unfollow", fetchRequest)
    .then(function(response) {  // Ensure status response was 200.
        // if (response.status !== 200 || response.status !== 201) {
        //     var message1 = `Response status not OK. Status code: ${response.status}`
        //     console.log(message1);
        //     document.querySelector("#onclick-status").innerHTML = message1;
        //     document.querySelector("#onclick-status").style.color = "red";
        //     return;
        // }
        return response.json();
    })
    .then(function(data) {  // Everything went well.
        console.log(`Data received: ${data}`);
        var message, newButtonText;
        if (action === "follow") {
            message = `Now following ${username}`;
            newButtonText = "Unfollow";
        }
        else if (action === "unfollow") {
            message = `Unfollowed ${username}`;
            newButtonText = "Follow";
        }
        console.log(message);
        document.querySelector("#follow-unfollow-button").innerHTML = newButtonText;
        document.querySelector("#onclick-status").innerHTML = message;
        return;
    })
    .catch(function(error) {  // Catch some other kind of unexpected error.
        var message = `Caught unexpected error: ${error}`
            console.log(message);
            document.querySelector("#onclick-status").innerHTML = message;
            document.querySelector("#onclick-status").style.color = "red";
            return;
    });
}

function followUnfollow2(username) {
    fetch ("/follow_test", {method: "POST", body: JSON.stringify({username: username})})
    .then(response => {
        return response.json();
    })
    .then(data => {
        console.log("data received: " + data);
        if (data["performed"] === "followed") {
            document.querySelector("#follow-unfollow-button").innerHTML = "Unfollow";
            document.querySelector("#onclick-status").innerHTML = "Successfully followed person";
            document.querySelector("#onclick-status").style.color = "green";
        }
        else if (data["performed"] === "unfollowed") {
            document.querySelector("#follow-unfollow-button").innerHTML = "Follow";
            document.querySelector("#onclick-status").innerHTML = "Successfully unfollowed person";
            document.querySelector("#onclick-status").style.color = "green";
        }
        else {
            document.querySelector("#onclick-status").innerHTML = "Error";
            document.querySelector("#onclick-status").innerHTML = "red";
        }
    })
    .then((error) => {
        console.log("The bruh!!!" + error);
    });
}