import React, {Component} from 'react';
import Cookies from "js-cookie";
import jwt_decode from "jwt-decode";
import axios from 'axios';

var id = Cookies.get("id_token")
var username = ""
if(id !== undefined) {
    username = jwt_decode(id)["username"]
}
var token = Cookies.get("access_token");
var refresh = Cookies.get("refresh_token");

class Scores extends React.Component {
    constructor(props){
        super(props);
        this.state ={
            rankings: [],
            scoring: [],
            isLoaded: false,
        };
    }

    componentDidMount() {
        let json = JSON.stringify({"Username": username});
        axios.post('https://resource-smartstudy.herokuapp.com/get_score', json, {
            headers: {
                "Content-Type": 'application/json',
                "Authorization": `${token}`
            }
        })

            .then (res => {
                var user = []
                var score = []
                for (var key in res.data) {
                    user.push(key);
                    score.push(parseInt(parseFloat(res.data[key]) * 100));
                }
                this.setState({
                    isLoaded: true,
                    rankings: user,
                    scoring: score,
                });
            })

    }

    render() {
        console.log(this.state.scoring)
        console.log(this.state.rankings)

        return (
            <div>

            </div>
        );
    }
}

export default Scores;