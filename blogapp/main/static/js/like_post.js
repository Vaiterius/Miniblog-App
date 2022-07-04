// Handle AJAX requests to process user liking/unliking of post
function likePost(post_id) {
    const like_button = document.querySelector("#like-button");
    const num_likes = document.querySelector("#num-likes");

    fetch("/like_post", {method: "POST", body: JSON.stringify({post_id: post_id})})
    .then((response) => response.json())
    .then((data) => {
        console.log("data received: " + data);
        if (data["liked"] === true) {
            like_button.src = "../main/static/images/liked.png";
        }
        else if (data["liked"] === false) {
            like_button.src = "../main/static/images/unliked.png";
        }
        num_likes.innerHTML = data["num_likes"];
    })
    .catch((error) => {
        console.log("The bruh!!! " + error);
        alert("Could not like post.");
    })
}