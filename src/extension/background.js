function getCurrentTab(token, username) {
	console.log("in");
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs){
        var currTab = tabs[0];
        var url = currTab.url;
	fetch('https://resource-smartstudy.herokuapp.com/post_browser_data', {
            method: 'post',
            headers: {
                "Content-type": "application/json",
                "Authorization": token
            },
            body: JSON.stringify({"URL": url, "Username":username})
        });
	console.log("success");
    })
}

chrome.runtime.onMessageExternal.addListener(
    function(request, sender, sendResponse) {
        if(request["action"] === "getTab"){
            var accessToken = request["token"]
            var userName = request["username"]
		console.log("inaaaa");
            getCurrentTab(accessToken, userName);
            sendResponse({"status": "success"});
        }else if(request === "testing"){
            console.log("testing success");
            sendResponse({"status": "success"});
        }
    });