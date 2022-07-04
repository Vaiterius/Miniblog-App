function followUser(followed_id) {
    fetch("/follow_user", {method: "POST", body: JSON.stringify({followed_id: followed_id})})
    .then(response => {
        return response.json();
    })
    .then(data => {
        console.log("data received: " + data);
        if (data["performed"] === "followed") {
            document.querySelector("#follow-unfollow-button").innerHTML = "Unfollow";
            document.querySelector("#onfollow-status").innerHTML = "Successfully followed person";
            document.querySelector("#onfollow-status").style.color = "green";
        }
        else if (data["performed"] === "unfollowed") {
            document.querySelector("#follow-unfollow-button").innerHTML = "Follow";
            document.querySelector("#onfollow-status").innerHTML = "Successfully unfollowed person";
            document.querySelector("#onfollow-status").style.color = "green";
        }
        else {
            document.querySelector("#onfollow-status").innerHTML = "Error";
            document.querySelector("#onfollow-status").innerHTML = "red";
        }
    })
    .then((error) => {
        console.log("The bruh!!! " + error);
    });
}