import React, { useEffect, useState} from 'react';
import axios from 'axios';
import Cookies from "js-cookie";
import jwt_decode from "jwt-decode";
import RecommendationDisplay from './Recommendation-Display';

var id = Cookies.get("id_token")
var username = ""
if(id !== undefined) {
    username = jwt_decode(id)["username"]
}
var token = Cookies.get("access_token");
var refresh = Cookies.get("refresh_token");
export default function Recommendation () {
    const [scores, getScores] = useState("");

    useEffect (() => {
        getAllScores();
    }, []);

    const getAllScores = () => {
        let json = JSON.stringify({"Username": username});
        axios.post('https://resource-smartstudy.herokuapp.com/get_score', json, {
            headers: {
                "Content-Type": 'application/json',
                "Authorization": `${token}`
            }
        })
            .then ((response) => {
                const allScores = response.data;
                console.log(response.data)
                getScores(allScores);
            })
    }



        return (
            <div>
                <h3>{response.data["scores"]}</h3>
            </div>
        );
    }


