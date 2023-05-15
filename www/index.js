eel.expose(test_hello_js);
function test_hello_js(attr) {
    console.log("Hello from " + attr + "!")
}
eel.test_hello("Javascript. E")

/* TODO:
    "Image Not Found" / "Failed to generate" placeholder img
    Remove segment option
    Reorder segments option ( drag+drop sounds too hard?? )
*/

function generate_sequence() {
    eel.generate_sequence()
}

// Called automatically after generate_sequence populates
function reload_sequence() {

}

function clear_sequence() {

}

function add_segment(index) {
    len = eel.get_sequence_length()
    if (index < 0 || index >= len) return false;
    img = eel.get_segment_img(index);
    audio = eel.get_segment_audio(index);
    text = eel.get_segment_text(index);
    // TODO
}