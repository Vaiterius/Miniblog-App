// Expand comment when user clicks on textarea, then compress if cancel.
function onCommentAction(action) {
    const textarea = document.querySelector("#comment-textarea");
    const button = document.querySelector("#comment-button");

    if (action === 'focus') {
        textarea.rows = 3;
        button.style.display = "block";
    } else {
        textarea.rows = 1;
        button.style.display = "none";
    }
}