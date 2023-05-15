eel.expose(test_hello_js);
function test_hello_js(attr) {
    console.log("Hello from " + attr + "!")
}

eel.test_hello("Javascript. E")