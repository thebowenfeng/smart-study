/* global chrome */
import Cookies from "js-cookie";
import axios from "axios";
import jwt_decode from "jwt-decode";
import { Link } from "react-router-dom";
import { Carousel } from "react-responsive-carousel";
import "react-responsive-carousel/lib/styles/carousel.min.css"; // requires a loader
import "./stopWatch-style.css";
import CheckTopic from "./checkTopic";

import { createPopper } from '@popperjs/core';
const popcorn = document.querySelector('#popcorn');
const tooltip = document.querySelector('#tooltip');
createPopper(popcorn, tooltip, {
    placement: 'top',
});

var access = Cookies.get("access_token");
var id = Cookies.get("id_token");
var refresh = Cookies.get("refresh_token");
var username = "";


if (id !== undefined) {
    username = jwt_decode(id)["username"];
}

async function refreshAccessToken() {
    let json = JSON.stringify({
        ClientID: "react",
        ClientSecret: "my secret",
        RefreshToken: refresh,
    });
    let response = await axios.post(
        "https://auth-smartstudy.herokuapp.com/refresh_access_token",
        json,
        {
            headers: {
                "Content-Type": "application/json",
            },
        }
    );
    var access_token = response.data["access_token"];
    var refresh_token = response.data["refresh_token"];
    var id_token = response.data["id_token"];

    Cookies.set("access_token", access_token, { path: "/" });
    Cookies.set("refresh_token", refresh_token, { path: "/" });
    Cookies.set("id_token", id_token, { path: "/" });
    console.log("Refreshed token to " + refresh_token);

    access = Cookies.get("access_token");
    id = Cookies.get("id_token");
    refresh = Cookies.get("refresh_token");
}

function bgListener() {
    var chromeID = Cookies.get("chromeID");
    console.log("bglistner chrome ID: " + chromeID);

    setInterval(async function () {
        let res = await fetch(
            " https://resource-smartstudy.herokuapp.com/get_status",
            {
                method: "post",
                headers: {
                    "Content-type": "application/json",
                    Authorization: access,
                },
                body: JSON.stringify({ Username: username, Status: "start" }),
            }
        );

        console.log(username);
        let data = await res.json();
        let response = {
            data: data,
            status: res.status,
        };
        console.log(response.data);
        var status = response.status;
        if (status === 403) {
            await refreshAccessToken();
        } else {
            if (data["status"] === "yes") {
                try{
                    chrome.runtime.sendMessage(
                        chromeID,
                        {
                            action: "getTab",
                            token: access,
                            username: username,
                        },
                        (response) => {
                            console.log("loop running");
                        }
                    );
                }catch(err){
                    console.log("bad chrome ID");
                }
            } else {
                console.log("stopped");
            }
        }
    }, 1000);
}

bgListener();

function saveChromeID(){
    var btnElem = document.getElementById("fname");
    var extID = btnElem.value;
    Cookies.set("chromeID", extID, { path: '/'});
    alert("Your chrome extension ID: " + extID + " has been saved.")
}

const React = require("react");
const ms = require("pretty-ms");

class stopWatch extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            time: 0,
            isOn: false,
            start: 0,
        };
        this.startTimer = this.startTimer.bind(this);
        this.stopTimer = this.stopTimer.bind(this);
    }
    startTimer() {
        var chromeID = Cookies.get("chromeID");
        console.log("ChromeID: " + chromeID);

        if(chromeID === undefined){
            alert("Please set your chrome extension ID first")
        }else{
            if (typeof chrome.runtime === "undefined") {
                alert("Please install the chrome extension");
            } else {
                try{
                    chrome.runtime.sendMessage(
                        chromeID,
                        "testing",
                        (response) => {
                            var testResponse = response["status"];
                            if (testResponse === "success") {
                                fetch(
                                    "https://resource-smartstudy.herokuapp.com/set_session_status",
                                    {
                                        method: "post",
                                        headers: {
                                            "Content-type": "application/json",
                                            Authorization: access,
                                        },
                                        body: JSON.stringify({ Username: username, Status: "start" }),
                                    }
                                ).then((response) => {
                                    var data = response.json();
                                    var status = response.status;
                                    if(status === 400){
                                        alert("You did not select any study topics");
                                    }else{
                                        if (status === 403) {
                                            refreshAccessToken().then(async () => {
                                                let payload = JSON.stringify({
                                                    Username: username,
                                                    Status: "start",
                                                });
                                                await axios.post(
                                                    "https://resource-smartstudy.herokuapp.com/set_session_status",
                                                    payload,
                                                    {
                                                        headers: {
                                                            "Content-Type": "application/json",
                                                            Authorization: access,
                                                        },
                                                    }
                                                );
                                            });
                                        }
                                        console.log("sent start request");

                                        this.setState({
                                            isOn: true,
                                            time: this.state.time,
                                            start: Date.now() - this.state.time,
                                        });
                                        this.timer = setInterval(
                                            () =>
                                                this.setState({
                                                    time: Date.now() - this.state.start,
                                                }),
                                            1
                                        );
                                    }
                                });
                            } else {
                                alert(
                                    "The browser is unable to commumicate with the chrome extension"
                                );
                            }
                        }
                    );
                }catch(err){
                    alert("Your extension ID is not valid");
                }
            }
        }
    }
    stopTimer() {
        fetch("https://resource-smartstudy.herokuapp.com/set_session_status", {
            method: "post",
            headers: {
                "Content-type": "application/json",
                Authorization: access,
            },
            body: JSON.stringify({ Username: username, Status: "stop" }),
        }).then((response) => {
            var data = response.json();
            var status = response.status;
            if (status === 403) {
                refreshAccessToken().then(() => {
                    var json = JSON.stringify({ Username: username, Status: "stop" });
                    axios.post(
                        "https://resource-smartstudy.herokuapp.com/set_session_status",
                        json,
                        {
                            headers: {
                                "Content-Type": "application/json",
                                Authorization: access,
                            },
                        }
                    );
                });
            }
        });
        console.log("sent stop request");

        this.setState({ isOn: false });
        clearInterval(this.timer);
        this.setState({ time: 0, isOn: false });
    }
    render() {
        let start =
            this.state.time === 0 ? (
                <button id="startButton" onClick={this.startTimer}>
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="30"
                        height="30"
                        fill="currentColor"
                        class="bi bi-play-fill"
                        viewBox="0 0 16 16"
                    >
                        <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393z" />
                    </svg>
                </button>
            ) : null;
        let stop =
            this.state.time === 0 || !this.state.isOn ? null : (
                <button id="stopButton" onClick={this.stopTimer}>
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="30"
                        height="30"
                        fill="currentColor"
                        class="bi bi-stop-fill"
                        viewBox="0 0 16 16"
                    >
                        <path d="M5 3.5h6A1.5 1.5 0 0 1 12.5 5v6a1.5 1.5 0 0 1-1.5 1.5H5A1.5 1.5 0 0 1 3.5 11V5A1.5 1.5 0 0 1 5 3.5z" />
                    </svg>
                </button>
            );

        //let reset = (this.state.time === 0 || this.state.isOn) ?
        // null :
        //<button onClick={this.resetTimer}>reset</button>

        return (
            <div className="body">
                <div className="home-container align-self-center">
                    <div className="container align-self-center container-fluid">
                        <div className="row">
                            <div className="col-sm">
                                <div className="instructions">
                                    <Carousel>
                                        <div>
                                            <div className="header">
                                                <h3 className="title">What is SmartStudy?</h3>
                                                <p className="text">
                                                    SmartStudy is an AI analytics tool that utilizes Computer Vision,
                                                    Machine Learning and AI to analyze your study effectiveness and provide
                                                    you with personalized recommendation. We also breakdown your study session
                                                    into easy-to-understand graphs, so you can see a summary of your study
                                                    habits at a glance.

                                                    Turn to the next page for instructions on how to use this product ->
                                                </p>
                                            </div>
                                        </div>
                                        <div>
                                            <div className="header">
                                                <h3 className="title">Instructions</h3>
                                                <p className="instruct">
                                                    <ol className="custom-counter">
                                                        <li>Download the chrome extension and Desktop application here: <a className="test" href="https://www.mediafire.com/file/wttujaxa0y7ne59/Product.zip/file">Download</a></li>
                                                        <li>Install the chrome extension on your browser</li>
                                                        <li>Input the extension ID in the box below</li>
                                                        <li>Press start to begin the timer</li>
                                                        <li>Start studying and press stop when you stop studying.</li>
                                                        <li>Visit status to see how well you studied </li>
                                                    </ol>
                                                </p>
                                            </div>
                                        </div>
                                        <div>
                                            <div className="header">
                                                <h3 className="title">Check Status</h3>
                                                <p className="instruct2">
                                                    <button className="btn-grad">
                                                        {" "}
                                                        <Link to="/Status">Click Here</Link>
                                                    </button>
                                                </p>
                                            </div>
                                        </div>
                                    </Carousel>
                                </div>
                                <h3 className="title">Enter your Chrome extension ID: </h3>
                                <input type="text" id="fname" name="fname"></input>
                                <button type="button" id="chromeID" className="btn-grad" onClick={saveChromeID}>Save</button>
                            </div>
                            <div className="col-sm">
                                {" "}
                                <div className="timer">
                                    <div className="header">
                                        <h3 className="title">Timer</h3>
                                        <div className="circle">
                                            <h3 className="time">
                                                {ms(this.state.time, { colonNotation: true })}
                                            </h3>
                                        </div>
                                        {start}
                                        {stop}
                                    </div>

                                    <div class="dropdown"><div className="btn-wrapper">
                                        <a href="#" class="btn-grad" data-toggle="dropdown">Select Study Topics <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chevron-down" viewBox="0 0 16 16">
                                            <path fill-rule="evenodd" d="M1.646 4.646a.5.5 0 0 1 .708 0L8 10.293l5.646-5.647a.5.5 0 0 1 .708.708l-6 6a.5.5 0 0 1-.708 0l-6-6a.5.5 0 0 1 0-.708z"/>
                                        </svg></a>
                                        <div class="dropdown-menu">
                                            <CheckTopic />
                                        </div>
                                    </div></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="area">
                    <ul className="circles">
                        <li></li>
                        <li></li>
                        <li></li>
                        <li></li>
                        <li></li>
                        <li></li>
                        <li></li>
                        <li></li>
                        <li></li>
                        <li></li>
                    </ul>
                </div>
            </div>
        );
    }
}

export default stopWatch;