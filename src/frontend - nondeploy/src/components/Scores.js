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
            scores: [],
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
                var arr_val = []
                for (var key in res.data) {
                    arr_val.push(parseInt(parseFloat(res.data[key]) * 100));
                }
                this.setState({
                    isLoaded: true,
                    scores: arr_val
                });
            })

    }

    render() {
        console.log(this.state.scores)
        console.log(this.state.scores[0])

        var message = "";
        if(this.state.scores[0] > 80 && this.state.scores[1] > 80) {
            message = "You have done an excellent job! Your study effectiveness is extremely high! Try to maintain this!"
        } else if(this.state.scores[1] < 65) {
            message = "You are getting distracted by your external environment. We recommend you to move to a quieter and more isolated location to study, for better results."
        } else if(this.state.scores[0] < 65) {
            message = "You are getting too distracted by irrelevant websites. Try to use an extension to blacklist certain distracting websites for a better study session."
        }else {
            message="You are doing a good job, but you could try to re-organize your study space/minimize web distraction for a better "
        }

        return (
            <div>

                <h5 ClassName="header-score">Your Score:</h5>
                <p>{this.state.scores[2]}</p>
                <h5 ClassName="suggestion-header">Suggestions:</h5>
                <p>{message}</p>
            </div>
        );
    }
}

export default Scores;