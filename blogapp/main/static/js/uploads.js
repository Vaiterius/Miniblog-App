document.addEventListener("DOMContentLoaded", function() {
    const postSubmitButton = document.querySelector(".submit-post");

    postSubmitButton.addEventListener("click", function() {
        tinymce.activeEditor.uploadImages()
        .then(() => {
            if (fileSizeOkay) {
                document.forms[0].submit();
            } else {
                fileSizeOkay = true;  // reset for next post
            }
        })
    });
});