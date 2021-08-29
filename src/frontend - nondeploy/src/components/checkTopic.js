
import React, { Component } from 'react';
import Checkbox from './Checkbox';
import axios from 'axios';
import jwt_decode from "jwt-decode";
import Cookies from "js-cookie";
import './CheckBox-style.css'

var token = Cookies.get("access_token")
var refresh = Cookies.get("refresh_token");

var id = Cookies.get("id_token")
var username = ""
if(id !== undefined) {
    username = jwt_decode(id)["username"]
}
const items = [
    "History",
    "Geography",
    "Arts",
    "Philosophy/Religion",
    "Society/Social Science",
    "Biological/Health Science",
    "Physical Science",
    "Technology",
    "Mathematics"
];

const topics = {
    "History": 0,
    "Geography": 1,
    "Arts": 2,
    "Philosophy/Religion": 3,
    "Society/Social Science": 5,
    "Biological/Health Science": 6,
    "Physical Science": 7,
    "Technology": 8,
    "Mathematics": 9
}

async function refreshAccessToken() {
    let json = JSON.stringify({"ClientID": "react", "ClientSecret": "my secret", "RefreshToken": refresh});
    let response = await axios.post('https://auth-smartstudy.herokuapp.com/refresh_access_token', json,{
        headers: {
            "Content-Type": "application/json"
        }
    })
    var access_token = response.data["access_token"];
    var refresh_token = response.data["refresh_token"];
    var id_token = response.data["id_token"];

    Cookies.set('access_token', access_token, { path: '/'});
    Cookies.set('refresh_token', refresh_token, { path: '/'});
    Cookies.set('id_token', id_token, { path: '/'});
    console.log("Refreshed token to " + refresh_token)

    token = Cookies.get("access_token");
    id = Cookies.get("id_token");
    refresh = Cookies.get("refresh_token");
}

class CheckTopic extends Component {
    componentWillMount = () => {
        this.selectedCheckboxes = new Set();
    }

    toggleCheckbox = label => {
        if (this.selectedCheckboxes.has(label)) {
            this.selectedCheckboxes.delete(label);
        } else {
            this.selectedCheckboxes.add(label);
        }
    }

    handleFormSubmit = formSubmitEvent => {
        formSubmitEvent.preventDefault();
        let result = []
        for (const checkbox of this.selectedCheckboxes) {
            console.log(checkbox, 'is selected.');
            let idx = topics[checkbox.toString()]
            result.push(idx.toString())
        }
        const output = result.join("|");

        (async () => {
            let payload = JSON.stringify({"Username": username, "Topic": output});
            await refreshAccessToken()
           let response = await axios.post('https://resource-smartstudy.herokuapp.com/post_topics', payload, {
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `${token}`
                }
            })
            console.log(response)
            alert("Topics sent!");
        })();

    };



    createCheckbox = label => (
        <Checkbox
            label={label}
            handleCheckboxChange={this.toggleCheckbox}
            key={label}
        />
    )

    createCheckboxes = () => (
        items.map(this.createCheckbox)
    )

    render() {
        return (
            <div className="container">
                <div className="row">
                    <div className="col-sm-12">

                        <form onSubmit={this.handleFormSubmit}>
                            {this.createCheckboxes()}

                            <button className="save-btn" type="submit">Save</button>
                        </form>

                    </div>
                </div>
            </div>
        );
    }
}

export default CheckTopic;